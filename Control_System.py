from tkinter import *
import threading
from subprocess import Popen, PIPE
import csv
import numpy as np
import control
from itertools import count
import time

# --------------------------System Definitions---------------------------- #
# In this section you use the transfer function you modeled for your system and also the controllers you are using.

s = control.tf('s')
G = (0.01132 * s + 0.00008335) / ((s + 0.002532) * (s + 0.010928))

Zero = (1 / (s + 0.00763))
Kp = 0.15
Comp = ((403.23 * s + 1) / (2350.17 * s + 1)) * ((94.67 * s + 1) / (16.245 * s + 1))

Comp_Total = control.series(Zero, Kp, Comp)

# ---------------------------------- Variables ---------------------------------#
L1 = None
L2 = None
L3 = None
L4 = None
FRM = None
on_off = False
sair = False
index = count()


set_point = 0
windup = 0
y = 0  # System output
i = 0
dt = 1  # interval of time between each iteration
V_sat = 0  # Controller output


#  These variables are used so we can use them as initial conditions for the system for each 1s iteration
# For the system:
n = len(G.pole())
x_prev = np.zeros(n)

# For the controller:
m = len(Comp_Total.pole())
x_Vprev = np.zeros(m)

# --------------------------------DataSet----------------------------- #

fieldnames = ["time", "Voltage", "Set-Point", "Output"]

with open('data.csv', 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

# ------------------------------------FUNCTIONS-----------------------------------#


def leitor():
    global y, i, t, u, SP

    # y = This 'y' value here, in a real application, would be given by a sensor. If this code was implemented
    # with Arduino, y would be, for example, the temperature read by a termistor.

    # The 0.980 seconds of sleep means that a new measurement of the temperature happens each 0.98 seconds.
    # The idea was to use 1 second between each measurement, but the code never sleeps the exact amount of time that
    # it was supposed to (usually taking 0.002~0.01 second longer to perform). To avoid time drift,
    # the 0.98 seconds was chosen.
    time.sleep(0.980)


def variaveis():
    global e, ligar, SP, i, t, u, y

    ligar = on_off
    SP = float(set_point)
    i = next(index)
    t = i
    u = SP
    e = u - y


# ------------------------------------------------------- #
# -----------------------INTERFACE----------------------- #

def interface():
    global FRM_Real, sair
    root = Tk()
    root.title("Gráfico")
    root.geometry("750x240")

    # -------------------------------------------------------------- #
    # -------------------------------------------------------------- #

    FRM = LabelFrame(root, text='Título', height=150, width=550)
    FRM.grid(row=0, column=0, columnspan=4, rowspan=4, padx=10, pady=10)
    # GRID PROPAGATE WILL NOT WORK IF WIDGETS INSIDE ARE PACK()
    FRM.grid_propagate(flag=False)

    Label(FRM, text='Time', font=("Helvetica", 12)).grid(row=0, column=0)
    Label(FRM, text='Input', font=("Helvetica", 12)).grid(row=0, column=1)
    Label(FRM, text='Set-point', font=("Helvetica", 12)).grid(row=0, column=2)
    Label(FRM, text='Output', font=("Helvetica", 12)).grid(row=0, column=3)

    FRM.grid_columnconfigure(index=0, weight=1)
    FRM.grid_columnconfigure(index=1, weight=1)
    FRM.grid_columnconfigure(index=2, weight=1)
    FRM.grid_columnconfigure(index=3, weight=1)
    # ---------------------------------------------------------------------------------------

    def def_set_point():
        global set_point
        set_point = entry.get()
        entry.delete(0, END)
        print(set_point)

    def start():
        global on_off
        if on_off is False:
            on_off = True
        elif on_off is True:
            on_off = False
        print(on_off)

    def open_graph():
        Popen(['python', 'plot_real_time.py'], stdin=PIPE, stdout=PIPE)

    def exit_root():
        global sair
        sair = True
        root.quit()

    # -----------------------------------------------------------#

    btn_1 = Button(root, text='Start/Pause', pady=5, command=start)
    btn_1.grid(row=0, column=5, sticky=E+W, pady=10)

    entry = Entry(root, text='Set-point', width=25)
    entry.grid(row=1, column=5, pady=2)

    btn_2 = Button(root, text='Set-point', pady=2, command=def_set_point)
    btn_2.grid(row=2, column=5, sticky=N+E+W)

    btn_3 = Button(root, text='Open Graph', pady=5, command=open_graph)
    btn_3.grid(row=3, column=5, sticky=N+E+W)

    btn_5 = Button(root, text='Exit', pady=10, command=exit_root)
    btn_5.grid(row=5, column=5, sticky=E+W, pady=10)

    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=0)
    root.grid_rowconfigure(3, weight=0)
    root.grid_rowconfigure(5, weight=0)

    root.wm_protocol("WM_DELETE_WINDOW", exit_root)
    root.mainloop()

# -----------------------------------------------------------------------------------------------------------------#


def funcionamento():
    global i, index, csv_file, csv_writer,\
        y, windup, dt, x_Vprev, x_prev, e, V_sat,\
        on_off, set_point, sair, ligar, FRM_Real, \
        L1, L2, L3, L4

    if ligar is True:

        # These saturation values were chosen accordingly to what I had when I ran this experiment on a lab. It may
        # vary depending on what the limitations of your energy source is.

        Vmax = 10
        Vmin = 0

        def mysat(V):
            if V > Vmax:
                Vout = Vmax
            elif V < Vmin:
                Vout = Vmin
            else:
                Vout = V
            return Vout

        # ---------------------------------------CONTROLLER RESPONSE--------------------------------------#
        e_in = e + windup
        t_comp, V_comp, x_comp = control.forced_response(Comp_Total, [t - dt, t], e_in, X0=x_Vprev)
        V_sat = mysat(V_comp[-1])
        x_Vprev = x_comp[:, -1]

        # --------------------------------------------SYSTEM RESPONSE-------------------------------------#
        # It's worth mentioning that, if this code is used in a real application, the output would be the V_sat got
        # from above. If using pwm and Arduino, for example, the V_sat would be the the pwm value that the Arduino
        # plataform would use to control the system. This way, there'd be no need to calculate 'y', since 'y' would
        # be obtained from the sensor.

        t_temp, y_temp, x_temp = control.forced_response(G, [t - dt, t], V_sat, X0=x_prev)
        x_prev = x_temp[:, -1]
        y = y_temp[-1]

        print(e)
        # -----------------------------------------------ANTI-WINDUP---------------------------------------------#
        windup = (V_sat - V_comp[-1])*2
        # ----------------------------------------------------------------------------------------------------------#

    elif ligar is False:
        print('Paused')

    with open('data.csv', 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        info = {
            "time": t,
            "Voltage": V_sat,
            "Set-Point": u,
            "Output": y
        }

        csv_writer.writerow(info)
    print(t, V_sat, u, y)

    if sair is not True:
        if L1 is None:
            L1 = Label(FRM, text=t, font=('Helvetica', 11))
            L1.grid(row=2, column=0, sticky=N)
            L2 = Label(FRM, text=round(V_sat, 3), font=('Helvetica', 11))
            L2.grid(row=2, column=1, sticky=N)
            L3 = Label(FRM, text=u, font=('Helvetica', 11))
            L3.grid(row=2, column=2, sticky=N)
            L4 = Label(FRM, text=round(y, 3), font=('Helvetica', 11))
            L4.grid(row=2, column=3, sticky=N)

        elif L1 is not None:

            L1.destroy()
            L2.destroy()
            L3.destroy()
            L4.destroy()

            L1 = Label(FRM, text=t, font=('Helvetica', 11))
            L1.grid(row=2, column=0, sticky=N)
            L2 = Label(FRM, text=round(V_sat, 3), font=('Helvetica', 11))
            L2.grid(row=2, column=1, sticky=N)
            L3 = Label(FRM, text=u, font=('Helvetica', 11))
            L3.grid(row=2, column=2, sticky=N)
            L4 = Label(FRM, text=round(y, 3), font=('Helvetica', 11))
            L4.grid(row=2, column=3, sticky=N)


def geral():
    while sair is not True:
        start = time.time()

        t1 = threading.Thread(target=leitor)
        t2 = threading.Thread(target=variaveis)
        t3 = threading.Thread(target=funcionamento)

        print(time.time() - start)

        start = time.time()
        t1.start()
        time.sleep(0.1)
        t2.start()
        t2.join()
        t3.start()
        t1.join()
        print(time.time() - start)

    else:
        print('Programa Finalizado')
        exit()
# ------------------------------------------------------------------------------------------------------------------- #


t_interface = threading.Thread(target=interface)
t_interface.start()
time.sleep(2)
t_geral = threading.Thread(target=geral)
t_geral.start()
