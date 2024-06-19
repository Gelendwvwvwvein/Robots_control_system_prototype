import sys
import tempfile
import os
import re
try:
    import ikpy
    from ikpy.chain import Chain
except ImportError:
    sys.exit('The "ikpy" Python module is not installed. '
             'To run this sample, please upgrade "pip" and install ikpy with this command: "pip install ikpy"')

import math
from controller import Supervisor

if ikpy.__version__[0] < '3':
    sys.exit('The "ikpy" Python module version is too old. '
             'Please upgrade "ikpy" Python module to version "3.0" or newer with this command: "pip install --upgrade ikpy"')


IKPY_MAX_ITERATIONS = 4

# Initialize the Webots Supervisor.
supervisor = Supervisor()
timeStep = int(4 * supervisor.getBasicTimeStep())

# Create the arm chain from the URDF
filename = None
with tempfile.NamedTemporaryFile(suffix='.urdf', delete=False) as file:
    filename = file.name
    file.write(supervisor.getUrdf().encode('utf-8'))
armChain = Chain.from_urdf_file(filename, active_links_mask=[False, True, True, True, True, True, True, False])

# Initialize the arm motors and encoders.
motors = []
for link in armChain.links:
    if 'motor' in link.name:
        motor = supervisor.getDevice(link.name)
        motor.setVelocity(0.2)
        position_sensor = motor.getPositionSensor()
        position_sensor.enable(timeStep)
        motors.append(motor)

# Get the arm and target nodes.
target = supervisor.getFromDef('TARGET')
arm = supervisor.getSelf()

gripper = supervisor.getFromDef('ROBOTIQ_2F_85_GRIPPER')

gripper_motors = []
gripper_sensors = []
for finger, finger_sensor in zip(['left', 'right'], ['left finger joint', 'right finger']):
    motor = supervisor.getDevice('ROBOTIQ 2F-85 Gripper::' + finger + ' finger joint')
    sensor = supervisor.getDevice('ROBOTIQ 2F-85 Gripper ' + finger_sensor + ' sensor')
    
    gripper_motors.append(motor)
    gripper_sensors.append(sensor) 
    
for motor in gripper_motors:
    motor.setVelocity(0.1)

# Define the length of the end effector
end_effector_length = 0.07 # in meters

def take(target_x, target_y, target_z):
    # Compute the position of the target relatively to the arm,
    # taking into account the length of the end effector.
    # x and y axis are inverted because the arm is not aligned with the Webots global axes.
    x = -(target_y - arm.getPosition()[1])
    y = target_x - arm.getPosition()[0]
    z = target_z - arm.getPosition()[2] + end_effector_length

    # Call "ikpy" to compute the inverse kinematics of the arm.
    initial_position = [0] + [m.getPositionSensor().getValue() for m in motors] + [0]
    ikResults = armChain.inverse_kinematics([x, y, z], max_iter=IKPY_MAX_ITERATIONS, initial_position=initial_position)

    # Recalculate the inverse kinematics of the arm if necessary.
    position = armChain.forward_kinematics(ikResults)
    squared_distance = (position[0, 3] - x)**2 + (position[1, 3] - y)**2 + (position[2, 3] - z)**2
    if math.sqrt(squared_distance) > 0.03:
        ikResults = armChain.inverse_kinematics([x, y, z])

    # Actuate the arm motors with the IK results.
    for i in range(len(motors)):
        motors[i].setPosition(ikResults[i + 1])
        
    # Check if the arm is close to the target position and actuate the gripper.
    if math.sqrt(squared_distance) < 0.05:
        for motor in gripper_motors:
            motor.setPosition(0.8)   # Open the gripper

def absolve():
    # Close the gripper
    for motor in gripper_motors:
        motor.setPosition(0.0)

def move(target_x, target_y, target_z):
    # Compute the position of the target relatively to the arm,
    # taking into account the length of the end effector.
    # x and y axis are inverted because the arm is not aligned with the Webots global axes.
    x = -(target_y - arm.getPosition()[1])
    y = target_x - arm.getPosition()[0]
    z = target_z - arm.getPosition()[2] + end_effector_length

    # Call "ikpy" to compute the inverse kinematics of the arm.
    initial_position = [0] + [m.getPositionSensor().getValue() for m in motors] + [0]
    ikResults = armChain.inverse_kinematics([x, y, z], max_iter=IKPY_MAX_ITERATIONS, initial_position=initial_position)

    # Recalculate the inverse kinematics of the arm if necessary.
    position = armChain.forward_kinematics(ikResults)
    squared_distance = (position[0, 3] - x)**2 + (position[1, 3] - y)**2 + (position[2, 3] - z)**2
    if math.sqrt(squared_distance) > 0.03:
        ikResults = armChain.inverse_kinematics([x, y, z])

    # Actuate the arm motors with the IK results.
    for i in range(len(motors)):
        motors[i].setPosition(ikResults[i + 1])

def stop():
    # Stop all motors
    for motor in motors:
        motor.setVelocity(0)
    # Stop gripper motors
    for motor in gripper_motors:
        motor.setVelocity(0)

# Loop: Move the arm hand to the target or perform absolve or move.
while supervisor.step(timeStep) != -1:
    if os.path.exists("way.txt"):
        with open("way.txt", "r") as file:
            command = file.readline().strip()
            if command.startswith("take"):
                coordinates = re.findall(r'[-+]?\d*\.\d+|\d+', command)
                target_x = float(coordinates[0])
                target_y = float(coordinates[1])
                target_z = float(coordinates[2])
                # print('Target coordinates:', (target_x, target_y, target_z))  
                # Coordinate output
                take(target_x, target_y, target_z)
            elif command == "absolve":
                absolve()
            elif command.startswith("move"):
                coordinates = re.findall(r'[-+]?\d*\.\d+|\d+', command)
                target_x = float(coordinates[0])
                target_y = float(coordinates[1])
                target_z = float(coordinates[2])
                # print('Target coordinates:', (target_x, target_y, target_z))  
                # Coordinate output
                move(target_x, target_y, target_z)
            elif command == "stop":
                stop()