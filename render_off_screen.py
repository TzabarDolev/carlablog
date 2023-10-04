## The following code is a part of render off screen post at the Carla simulator research blog - https://carlasimblog.wordpress.com/2023/10/04/rendering-images-off-screen-in-the-carla-simulator/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

## First, you need to import the necessary modules
import carla
import time
import argparse

## Connect to the CARLA server
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

# Define a target velocity in meters per second (m/s)
target_velocity = 10.0  # Adjust this value as needed

# Spawn the vehicle
random_location = random.choice(world.get_map().get_spawn_points())
spawn_point = carla.Transform(carla.Location(random_location.location), carla.Rotation(pitch=0, yaw=0, roll=0))
vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)
vehicle.apply_control(carla.VehicleControl(throttle=target_velocity, steer=0))

camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '1920')
camera_bp.set_attribute('image_size_y', '1080')
camera_bp.set_attribute('fov', '90')
camera_transform = carla.Transform(carla.Location(x=0, y=0.0, z=1.8), carla.Rotation(pitch=0, yaw=0, roll=0))

camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

def process_image(image):
    image.save_to_disk(fr'C:\Users\algo2\Documents\data\test\{time.time()}.png')

camera.listen(process_image)

for i in range(100):  # Replace 100 with the desired number of frames
    world.tick()


