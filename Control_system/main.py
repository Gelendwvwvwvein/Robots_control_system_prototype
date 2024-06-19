import requests
from datetime import datetime
import telebot
import json
import os  
from googletrans import Translator
import ezodf
import sys
import uno
import base64
import google.generativeai as genai
import threading
import time

user_objects = []
processed_image_data = ""
history_commands = []

def connect_to_libreoffice(port=2002):
    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context)
    try:
        context = resolver.resolve(f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext")
        return context
    except NoConnectException:
        print("Couldn't connect to LibreOffice. Make sure that LibreOffice is running in listening mode.")
        return None

def get_sheet(doc, sheet_name):
    try:
        return doc.Sheets.getByName(sheet_name)
    except UnoException:
        print(f"Лист с именем {sheet_name} не найден.")
        return None

def read_table():
    global user_objects
    while True:
        # Connecting to LibreOffice
        context = connect_to_libreoffice()
        if context is not None:
            desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
            # Uploading a document
            file_path = "../irb_Main/controllers/Table_updating/Сoordinates.ods"
            if os.path.exists(file_path):
                doc = desktop.loadComponentFromURL(f"file://{file_path}", "_blank", 0, ())
                if doc is not None:
                    sheet = get_sheet(doc, "Coordinates")  # The name of the sheet you are using
                    if sheet is not None:
                        # Reading the data from column A
                        column_data = []
                        row = 1  # Starting from the first line (numbering in Python from 0)
                        cell_a = sheet.getCellByPosition(0, row)
                        cell_b = sheet.getCellByPosition(1, row)
                        cell_c = sheet.getCellByPosition(2, row)
                        cell_d = sheet.getCellByPosition(3, row)
                        while cell_a.getString() != "":
                            column_data.append((cell_a.getString(), cell_b.getValue(), cell_c.getValue(), cell_d.getValue()))
                            row += 1
                            cell_a = sheet.getCellByPosition(0, row)
                            cell_b = sheet.getCellByPosition(1, row)
                            cell_c = sheet.getCellByPosition(2, row)
                            cell_d = sheet.getCellByPosition(3, row)
                        # Updating the information in the global variable
                        user_objects = column_data
            else:
                print("The table file was not found.")
        else:
            print("Couldn't connect to LibreOffice.")
        time.sleep(1)  # Pause for one second

def process_image():
    global processed_image_data
    while True:
        # Image Processing
        API_KEY = "YURE_GEMINI_API"
        genai.configure(api_key=API_KEY)

        def image_to_base64(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        image_path = "../irb_Main/controllers/my_controller_camera/images/camera_1_image.png"
        image_base64 = image_to_base64(image_path)

        model_name = 'gemini-1.0-pro-vision-latest'

        prompt = "Describe the location of the objects relative to each other and the robot manipulator shown in the figure. The green ball is an apple. There is also a small cube in the image. When describing an image, do not use the word image. Remember that you are describing the state of the objects in the scene."

        request_data = [
            {"text": prompt},
            {"inline_data": {"data": image_base64, "mime_type": "image/png"}}
        ]

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(request_data)

        # Updating the information in the global variable
        processed_image_data = response.text
        time.sleep(1)  # Pause for one second

def send_request(prompt, user_task, user_objects):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YURE_GEMINI_API"
    headers = {'Content-Type': 'application/json'}
    data = {"contents":[{"parts":[{"text": prompt}, {"text": user_task}, {"text": user_objects}]}]}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Hi! Set a task for the robot")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        user_task = message.text

        # Translating a user's request from original language to English using the Google API
        prompt_translation = send_request("Translate the user's request into English.", user_task, ", ".join([item[0] for item in user_objects]))
        user_task_english = prompt_translation['candidates'][0]['content']['parts'][0]['text']
        
        prompt = f"""
Hello! In this dialogue, you will play the role of a robot manipulator. You have to think as if you are a robot manipulator. 

The user has set the following task for you: "{user_task_english}". What objects might you need to interact with as a robotic manipulator in order to achieve the goal of the task set for you by the user? List all possible subjects for possible interaction within the framework of the task.

In the response, specify only a comma-separated list of objects, without prepositions and other auxiliary words. For example: "object-1, object-2, object-3". 

The list of objects should include only their names. 

You don't need to specify the purpose of the objects in any form at all.

List at least 15 objects that hypothetically can help you solve the task set by the user.
List as many options of objects as possible that fit the conditions of the task.

In the list of objects, do not specify the elements of your technical equipment, information systems that help you process information about the environment, and other sensors.
"""
        
        response = send_request(prompt, user_task, ", ".join([item[0] for item in user_objects]))
        generated_text = response['candidates'][0]['content']['parts'][0]['text']
        objects_array = generated_text.split(", ")

        # Creating an incentive for an action plan
        prompt = f"""
Write a Detailed plan describing which Objects, how and in what order you, as a Robotic Manipulator, will interact to achieve the Goal set by the User.

The goal set by the User sounds like this: "{user_task_english}".

When making a Plan, keep in mind that the following items were found in the Reach of the Robot Manipulator that you are: "{", ".join([item[0] for item in user_objects])}".

In the response, specify the Action Plan. An example of how the response should be designed:
"1. Action-1 with object-1;
2. Action-2 with Object-2;
3. Action-3 with object-1".

Answer specifically, go straight to the Plan without any preliminaries.

Each action must be numbered.

YOUR ANSWER SHOULD NOT CONTAIN AN INTRODUCTION, NOTES OR OTHER SIMILAR CONTENT.

Do not write notes and introductory words at the beginning of the answer.

Start the Answer Right from Point #1.
"""
        response = send_request(prompt, user_task, ", ".join([item[0] for item in user_objects]))
        action_plan = response['candidates'][0]['content']['parts'][0]['text']
        print("The received action plan:")
        print(action_plan)

        # Output of data about objects from the table
        print("\nData about objects from a multimodal map:")
        for item in user_objects:
            print(f"Object name: {item[0]}, x coordinate: {item[1]}, y coordinate: {item[2]}, z coordinate: {item[3]}")

        # Image Processing
        global processed_image_data
        print("Обработанное изображение:")
        print(processed_image_data)

        while True:
            # Creating a prompta for the steps of the plan
            prompt = f"""
You are a robotic manipulator capable of executing 4 commands:

1) Take - invoked by the command 'take(target_x, target_y, target_z)', where target_x, target_y, target_z are the coordinates of the center of the object to be grasped by you, acting as a robotic manipulator;
2) Move - invoked by the command 'move(target_x, target_y, target_z)', where target_x, target_y, target_z are the coordinates of the point to which you, as the manipulator, should move the grasp;
3) Release - invoked by the command 'absolve', upon calling this command, you release the grip;
4) Stop - invoked by the command 'stop', upon calling this command, you halt, fix the joints and links in the current position, and assume a static posture;

You need to execute the following action plan as a robotic manipulator: {action_plan}.

As a robotic manipulator, you have the following constraints:

Most likely, you will drop the object grasped by the end effector when it is moved more than 0.1 m from its previous position.
You plan which command to execute next before each new step. During the execution of the command, you need to analyze textual information about what is currently happening in the scene, the coordinates of objects, and the history of previously executed commands.
To successfully grasp, you need to first approach the object by using the 'move target_x, target_y, target_z' command, and then make the grasp using the 'take target_x, target_y, target_z' command. However, to avoid a situation where you would knock down the object to be grasped during the approach by the end effector, you need to move to a coordinate that is at least 0.005 m away from the object.
When performing the grasp, make sure that you have previously released the gripper. The gripper can be released by the command 'absolve'.
Now you need to specify the next step that you, as a robotic manipulator, will perform to successfully complete the planned action. For this, you are provided with the following additional information:

Current coordinates and names of objects in the scene:
{f"Object name: {item[0]}, x coordinate: {item[1]}, y coordinate: {item[2]}, z coordinate: {item[3]}"}

Text description of what is happening in the scene:
{processed_image_data}

History of previously executed commands:
{history_commands}

In the response, you need to specify only the next command, in accordance with the rules of its usage described earlier in this text. If done incorrectly, the command will not be executed, or it will be executed incorrectly.

Indicate which function of the robotic manipulator will be called next?
"""
            response = send_request(prompt, user_task, ", ".join([item[0] for item in user_objects]))
            local_plan = response['candidates'][0]['content']['parts'][0]['text']
            print("Next step:")
            print(local_plan)
            
            # Saving the generated action to a file, first clearing it
            with open('../irb_Main/controllers/inverse_kinematics/way.txt', 'w') as file:
                file.write(local_plan + "\n")

            # Updating the history of the teams
            history_commands.append(local_plan)
            
            time.sleep(1)  # Pause for one second

    bot.polling()

if __name__ == '__main__':
    from auth_data import token

    # Creating and running threads for reading the table and image processing
    table_thread = threading.Thread(target=read_table)
    image_thread = threading.Thread(target=process_image)

    table_thread.daemon = True
    image_thread.daemon = True

    table_thread.start()
    image_thread.start()

    telegram_bot(token)

