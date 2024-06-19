# Robots_control_system_prototype
The project implements a prototype of a functionally universal robot manipulator control system in the Webots. The management system accepts tasks in natural language from *Telegram-bot*. The project was implemented using the *IRB 4600-40\2.55 robot*.

The system is developed using *Ubuntu 22.04*, *Python 3.10.12*, *Webots version R2023b*, and *LibreOffice Calc*.

<h3>Visualization of the system operation</h3>
<img src='Control_system/Цыгикало_А_Е ВКР.png'>

<h2>Initialization</h2>

Install all necessary dependencies with the commands:
```
pip install requests==2.31.0 telebot==0.0.5 ezodf==0.3.2 google-generativeai==0.6.0
```
```
pip install --upgrade ikpy
```

Next, to get the *Gemini API key*, you need to create a project on the platform [Google AI Syudio](https://aistudio.google.com/app/apikey).
> If Google AI Studio is not available in your region, use a VPN (for example, a US VPN) when working with this project.

The resulting API must be inserted into the file *'Control_system/main.py'* in line 77 and 104.

Using the Telegram-bot [@BotFather](https://telegram.me/BotFather), you need to create a bot in order to transfer tasks for the robot to the control system.
The resulting API must be inserted into the file *'Control_system/auth_data.py '*.

<h2>Launch</h2>

1\. Run LibreOffice Calc in headless mode with the command:
```
libreoffice --headless --accept="socket,host=localhost,port=2002;urp;" --nofirststartwizard
```

2\. Run the script *'Control_system/main.py'* (enable VPN if necessary).

3\. Send a command formulated in natural language to the bot.

4\. Run the world file *'irb_Main/worlds/new_wor1111111.wbt'* in Webots.
> This step must be completed without delay, immediately after the implementation of the previous step.

<h2>Syntax of functions for manipulation.</h2>

The project includes the possibility of manual remote control from a file *'irb_Main/controllers/inverse_kinematics/way.txt'*.

+ Move to a point *(move)*. When the command is called, the robot's grip shifts towards the specified coordinate. The function is called with the command ***'move (target_x, target_y, target_z)'***
+ Take at the point *(take)*. When the command is called, the capture is simultaneously shifted to a specified point and compressed. The function is called with the command ***'take (target_x, target_y, target_z)'***.
+ Let go *(absolve)*. When the command is called, the grip is smoothly released. In the process of performing the functions of the manipulator joint, they remain static. The function is called with the ***'absolute'*** command.
+ Stop *(stop)*. When the function is called, all joints of the robot stop and take a static position. The function is called with the ***'stop'*** command.

> The x/y/z coordinates of the points in the three-dimensional space of the scene correspond to the coordinates of the points in the Webots system.
