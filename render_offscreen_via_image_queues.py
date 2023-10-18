## The following code is a part of render off screen via image queues post at the Carla simulator research blog - .
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.


## First, you need to import the necessary modules
import carla
import time
import argparse
import random
import queue


IND = 0


def process_image_rgb(image):
    image.save_to_disk(fr'C:\Users\algo2\Documents\data\test\rgb\{IND}_rgb.png')

def process_image_semantic(image):
    image.save_to_disk(fr'C:\Users\algo2\Documents\data\test\semantic\{IND}_semantic.png')

def process_image_depth(image):
    image.save_to_disk(fr'C:\Users\algo2\Documents\data\test\depth\{IND}_depth.png')

if __name__ == '__main__':

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
    argparser.set_defaults(sync=False)

    args = argparser.parse_args()

    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)

    # Load a map and create a new world
    # Getting the world and
    world = client.get_world()
    settings = world.get_settings()
    settings.no_rendering_mode = True
    settings.synchronous_mode = False
    settings.substepping = True
    ## 0.001 maps us to FPS
    settings.max_substep_delta_time = 0.001
    settings.max_substeps = 10
    world.apply_settings(settings)

    vehicle_blueprint = world.get_blueprint_library().find('vehicle.audi.tt')

    # Define a target velocity in meters per second (m/s)
    target_velocity = 50.0  # Adjust this value as needed

    # Spawn the vehicle
    random_location = random.choice(world.get_map().get_spawn_points())
    spawn_point = carla.Transform(carla.Location(x=0, y=0, z=0), carla.Rotation(pitch=0, yaw=0, roll=0))
    vehicle = world.spawn_actor(vehicle_blueprint, spawn_point)
    rgb_queue = queue.Queue()
    semantic_queue = queue.Queue()
    depth_queue = queue.Queue()
    vehicle.apply_control(carla.VehicleControl(throttle=target_velocity, steer=0))

    camera_bp_rgb = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_bp_rgb.set_attribute('image_size_x', '3840')
    camera_bp_rgb.set_attribute('image_size_y', '2880')
    camera_bp_rgb.set_attribute('fov', '90')
    camera_transform_rgb = carla.Transform(carla.Location(x=0, y=0.0, z=1.6), carla.Rotation(pitch=0, yaw=0, roll=0))
    camera_rgb = world.spawn_actor(camera_bp_rgb, camera_transform_rgb, attach_to=vehicle)

    camera_bp_semantic = world.get_blueprint_library().find('sensor.camera.semantic_segmentation')
    camera_bp_semantic.set_attribute('image_size_x', '3840')
    camera_bp_semantic.set_attribute('image_size_y', '2880')
    camera_bp_semantic.set_attribute('image_size_y', '2880')
    camera_bp_semantic.set_attribute('fov', '90')
    camera_transform_semantic = carla.Transform(carla.Location(x=0, y=0.0, z=1.6), carla.Rotation(pitch=0, yaw=0, roll=0))
    camera_semantic = world.spawn_actor(camera_bp_semantic, camera_transform_semantic, attach_to=vehicle)

    camera_bp_depth = world.get_blueprint_library().find('sensor.camera.depth')
    camera_bp_depth.set_attribute('image_size_x', '3840')
    camera_bp_depth.set_attribute('image_size_y', '2880')
    camera_bp_depth.set_attribute('fov', '90')
    camera_transform_depth = carla.Transform(carla.Location(x=0, y=0.0, z=1.6), carla.Rotation(pitch=0, yaw=0, roll=0))
    camera_depth = world.spawn_actor(camera_bp_depth, camera_transform_depth, attach_to=vehicle)

    camera_rgb.listen(rgb_queue.put)
    camera_depth.listen(depth_queue.put)
    camera_semantic.listen(semantic_queue.put)

    while True:
        world.tick()
        image_rgb = rgb_queue.get()
        process_image_rgb(image_rgb)
        image_depth = depth_queue.get()
        process_image_depth(image_depth)
        image_semantic = semantic_queue.get()
        process_image_semantic(image_semantic)

        IND += 1
