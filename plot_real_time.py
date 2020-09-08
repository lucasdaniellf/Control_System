import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

#It takes a bit too long to load, but it works.

fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex='col')


def animate(i):

    data = pd.read_csv('data.csv')
    x = data['time']
    y1 = data['Voltage']
    y2 = data['Set-Point']
    y3 = data['Output']

    ax1.cla()
    ax2.cla()
    ax3.cla()

    ax1.plot(x, y1, label='Voltage', color='red')
    ax2.plot(x, y2, label='Set-Point', color='magenta')
    ax3.plot(x, y3, label='Temperature')
    ax1.set_ylabel('Voltage')
    ax2.set_ylabel('Set-Point')
    ax3.set_ylabel('Temperature')

    ax3.set_xlabel('Time')
    ax1.grid()
    ax2.grid()
    ax3.grid()

ani = FuncAnimation(fig, animate, interval=1000)
plt.show()
