## The following code is a part of Sensors section at the Carla simulator research blog - https://carlasimblog.wordpress.com/2023/09/18/collision-detection-systems-in-cars-enhancing-safety-and-realism-in-carla-simulator/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

import carla
import argparse

# Function to handle collision events
def on_collision(event):
    collision_actor = event.other_actor
    impulse = event.normal_impulse
    intensity = (impulse.x**2 + impulse.y**2 + impulse.z**2)**0.5

    print(f"Collision with {collision_actor.type_id} (ID: {collision_actor.id})")
    print(f"Collision intensity: {intensity} N")

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

# Connect to the Carla world
world = client.get_world()
vehicle_blueprint = world.get_blueprint_library().find('vehicle.audi.tt')

# Spawn the vehicle
spawn_point = carla.Transform(carla.Location(x=100, y=100, z=1), carla.Rotation())
vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)

# Define a target velocity in meters per second (m/s)
target_velocity = 10.0  # Adjust this value as needed

# Create a collision detector sensor
collision_sensor_bp = world.get_blueprint_library().find('sensor.other.collision')
collision_sensor_location = carla.Location(x=1.0, y=0.0, z=1.0)
collision_sensor = world.spawn_actor(collision_sensor_bp, carla.Transform(collision_sensor_location), attach_to=vehicle)

# Listen for collision events and print collision data
collision_sensor.listen(lambda event: on_collision(event))

try:
    # Start the simulation loop (replace this with your own simulation logic)
    while True:
        world.tick()

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
finally:
    # Remove the collision sensor when done
    if collision_sensor.is_alive:
        collision_sensor.destroy()
