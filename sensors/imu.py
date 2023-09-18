## The following code is a part of Sensors section at my Carla simulator research blog - https://carlasimblog.wordpress.com/2023/09/16/understanding-imu-sensors-and-their-role-in-autonomous-driving-simulations-with-carla/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

## In the CARLA Python API, you can extract IMU (Inertial Measurement Unit) sensor data from a vehicle.
## An IMU sensor provides information about the vehicles linear and angular accelerations, as well as its orientation.
## Here's how you can extract IMU sensor data from a vehicle in CARLA

## First, you need to import the necessary modules
import carla
import time
import argparse

## Connect to the CARLA server and spawn a vehicle with an IMU sensor
argparser = argparse.ArgumentParser(
        description='CARLA Sensor tutorial')
argparser.add_argument(
    '--host',
    metavar='H',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument(
    '-p', '--port',
    metavar='P',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)')
argparser.add_argument(
    '--sync',
    action='store_false',
    help='Synchronous mode execution')
argparser.add_argument(
    '--async',
    dest='sync',
    action='store_true',
    help='Asynchronous mode execution')
argparser.set_defaults(sync=True)
argparser.add_argument(
    '--res',
    metavar='WIDTHxHEIGHT',
    default='960x2000',
    help='window resolution (default: 1284x480)')

args = argparser.parse_args()

args.width, args.height = [int(x) for x in args.res.split('x')]

client = carla.Client(args.host, args.port)
client.set_timeout(10.0)

# Load a map and create a new world
world = client.get_world()
vehicle_blueprint = world.get_blueprint_library().find('vehicle.audi.tt')

# Spawn the vehicle
spawn_point = carla.Transform(carla.Location(x=100, y=100, z=1), carla.Rotation())
vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)

# Define a target velocity in meters per second (m/s)
target_velocity = 10.0  # Adjust this value as needed

## Attach an IMU sensor to the vehicle
imu_blueprint = world.get_blueprint_library().find('sensor.other.imu')
imu_transform = carla.Transform(carla.Location(x=0.0, y=0.0, z=0.0), carla.Rotation())
imu_sensor = world.spawn_actor(imu_blueprint, imu_transform, attach_to=vehicle)

## Create a callback function to handle IMU sensor data
def imu_callback(imu_data):
    acceleration = imu_data.accelerometer
    gyroscope = imu_data.gyroscope
    transform = imu_data.transform

    # Print IMU data
    print(f"Acceleration: {acceleration}")
    print(f"Gyroscope: {gyroscope}")
    print(f"Transform: {transform}")

## Register the callback function to receive IMU data
imu_sensor.listen(imu_callback)


## Run a simulation loop to continuously capture IMU data
try:
    while True:
        # Get the current vehicle state
        vehicle_state = vehicle.get_velocity()

        # Calculate the error between the current and target velocity
        velocity_error = target_velocity - vehicle_state.x  # We are using the x component for forward velocity

        # Create a carla.VehicleControl object to control the car
        control = carla.VehicleControl()

        # Set the throttle and brake based on the velocity error
        if velocity_error > 0:
            control.throttle = 0.5  # You can adjust the throttle value
            control.brake = 0.0
        else:
            control.throttle = 0.0
            control.brake = 0.2  # You can adjust the brake value

        # Apply steering (optional)
        control.steer = 0.0  # You can adjust the steering angle if needed

        # Apply the control to the vehicle
        vehicle.apply_control(control)

        # Sleep to control the update rate
        time.sleep(0.1)

finally:
    # Clean up
    vehicle.destroy()
