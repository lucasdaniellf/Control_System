# Control_System
An Interface for Control Systems


My final Mechanical Engineering project was to develop a control system that would control the temperature on the surface of a alluminum block.
The control system would then be used to maintain fotovoltaic cells at a constant temperature when under the sun (used in projects of Master's degree students in UFS) and also to produce sinusoidal thermal waves (used to analyze thermal properties of biological tissues and also in non-invasive analysis of blood perfusion in organic tissues).

The original project was developed using Peltier Cells, an analog circuit, an Arduino MEGA2560 plataform and Simulink. The Simulink was linked to the Arduino plataform and they acted as the controller of the system.

The Control_System.py takes the place of the simulink. The way it is presented, it has the transfer function and compensators I used in my project, so I could simulate the response and see if the algorithm was working as intended (it is), but it can be used with any control systems, being required only the update of the system equations.

The control system algorithm I used was based in this video "https://www.youtube.com/watch?v=6ivdfKfGp4k".
