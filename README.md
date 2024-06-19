# Robots_control_system_prototype
The project implements a prototype of a functionally universal robot manipulator control system in the Webots. The management system accepts tasks in natural language from Telegram-bot. The project was implemented using the IRB 4600-40\2.55 robot.

The system is developed using Ubuntu 22.04, Python 3.10.12, Webots version R2023b, and LibreOffice calc.

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
Next, to get the Gemini API key, you need to create a project on the platform <a herf='https://aistudio.google.com/app/apikey'>Google AI Syudio</a>.
