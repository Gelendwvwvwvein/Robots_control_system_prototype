from controller import Robot, Camera
from PIL import Image
import os

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Initialize cameras
cam_1 = robot.getDevice('camera_1')
cam_1.enable(timestep)
cam_1.recognitionEnable(timestep)

cam_2 = robot.getDevice('camera_2')
cam_2.enable(timestep)
cam_2.recognitionEnable(timestep)

# Directory to save images
script_dir = os.path.dirname(os.path.realpath(__file__))
image_dir = os.path.join(script_dir, "images")
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

def capture_image(camera, filename):
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()
    pil_image = Image.frombytes('RGBA', (width, height), image, 'raw')
    pil_image.save(filename)
    print(f"Saved image: {filename}")

# Main loop:
while robot.step(timestep) != -1:
    # Capture and save image from camera 1 every second
    current_time = robot.getTime()
    if int(current_time) % 1 == 0:  # Capture every second
        image_path = os.path.join(image_dir, "camera_1_image.png")
        
        # Remove previous image if exists
        if os.path.exists(image_path):
            os.remove(image_path)
        
        capture_image(cam_1, image_path)

    # Process sensor data here
    # ...

# Enter here exit cleanup code.
