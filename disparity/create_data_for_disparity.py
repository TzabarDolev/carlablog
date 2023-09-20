## The following code is a part of disparity measurements section at the Carla simulator research blog - https://carlasimblog.wordpress.com/2023/09/20/disparity-in-stereo-cameras-measuring-understanding-and-its-crucial-role/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import argparse
import random
import time
import numpy as np


try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_b
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_f
    from pygame.locals import K_g
    from pygame.locals import K_h
    from pygame.locals import K_i
    from pygame.locals import K_l
    from pygame.locals import K_m
    from pygame.locals import K_n
    from pygame.locals import K_o
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_t
    from pygame.locals import K_v
    from pygame.locals import K_w
    from pygame.locals import K_x
    from pygame.locals import K_z
    from pygame.locals import K_MINUS
    from pygame.locals import K_EQUALS
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

class CustomTimer:
    def __init__(self):
        try:
            self.timer = time.perf_counter
        except AttributeError:
            self.timer = time.time

    def time(self):
        return self.timer()

class DisplayManager:
    def __init__(self, grid_size, window_size):
        pygame.init()
        pygame.font.init()
        self.display = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.grid_size = grid_size
        self.window_size = window_size
        self.sensor_list = []

    def get_window_size(self):
        return [int(self.window_size[0]), int(self.window_size[1])]

    def get_display_size(self):
        return [int(self.window_size[0]/self.grid_size[1]), int(self.window_size[1]/self.grid_size[0])]

    def get_display_offset(self, gridPos):
        dis_size = self.get_display_size()
        return [int(gridPos[1] * dis_size[0]), int(gridPos[0] * dis_size[1])]

    def add_sensor(self, sensor):
        self.sensor_list.append(sensor)

    def get_sensor_list(self):
        return self.sensor_list

    def render(self):
        if not self.render_enabled():
            return

        for s in self.sensor_list:
            s.render()

        pygame.display.flip()

    def destroy(self):
        for s in self.sensor_list:
            s.destroy()

    def render_enabled(self):
        return self.display != None

class SensorManager:
    def __init__(self, world, display_man, sensor_type, transform, attached, sensor_options, display_pos):
        self.surface = None
        self.world = world
        self.display_man = display_man
        self.display_pos = display_pos
        self.sensor = self.init_sensor(sensor_type, transform, attached, sensor_options)
        self.sensor_options = sensor_options
        self.timer = CustomTimer()

        self.time_processing = 0.01
        self.tics_processing = 0

        self.display_man.add_sensor(self)

    def init_sensor(self, sensor_type, transform, attached, sensor_options):
        if sensor_type == 'RGBCamera':
            camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
            disp_size = self.display_man.get_display_size()
            camera_bp.set_attribute('image_size_x', str(disp_size[0]))
            camera_bp.set_attribute('image_size_y', str(disp_size[1]))
            camera_bp.set_attribute('fov', str(14))

            for key in sensor_options:
                camera_bp.set_attribute(key, sensor_options[key])

            camera = self.world.spawn_actor(camera_bp, transform, attach_to=attached)
            camera.listen(self.save_rgb_image)

            return camera

        elif sensor_type == 'SemanticCamera':
            camera_bp = self.world.get_blueprint_library().find('sensor.camera.semantic_segmentation')
            disp_size = self.display_man.get_display_size()
            camera_bp.set_attribute('image_size_x', str(disp_size[0]))
            camera_bp.set_attribute('image_size_y', str(disp_size[1]))
            camera_bp.set_attribute('fov', str(14))

            for key in sensor_options:
                camera_bp.set_attribute(key, sensor_options[key])

            camera = self.world.spawn_actor(camera_bp, transform, attach_to=attached)
            camera.listen(self.save_semantic_image)

            return camera

        elif sensor_type == 'DepthCamera':
            camera_bp = self.world.get_blueprint_library().find('sensor.camera.depth')
            disp_size = self.display_man.get_display_size()
            camera_bp.set_attribute('image_size_x', str(disp_size[0]))
            camera_bp.set_attribute('image_size_y', str(disp_size[1]))
            camera_bp.set_attribute('fov', str(14))

            for key in sensor_options:
                camera_bp.set_attribute(key, sensor_options[key])

            camera = self.world.spawn_actor(camera_bp, transform, attach_to=attached)
            camera.listen(self.save_depth_image)

            return camera
        
        else:
            return None

    def get_sensor(self):
        return self.sensor

    def save_rgb_image(self, image):
        t_start = self.timer.time()

        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

        t_end = self.timer.time()
        self.time_processing += (t_end-t_start)
        self.tics_processing += 1
        image.save_to_disk('_out/multiple_sensors/raw/%08d_rgb.png' % image.frame)

    def save_depth_image(self, image):
        t_start = self.timer.time()

        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

        t_end = self.timer.time()
        self.time_processing += (t_end - t_start)
        self.tics_processing += 1
        image.save_to_disk('_out/multiple_sensors/raw/%08d_depth.png' % image.frame)

    def save_semantic_image(self, image):
        t_start = self.timer.time()

        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]

        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

        t_end = self.timer.time()
        self.time_processing += (t_end - t_start)
        self.tics_processing += 1
        image.save_to_disk('_out/multiple_sensors/raw/%08d_semantic.png' % image.frame, carla.ColorConverter.CityScapesPalette)


    def render(self):
        if self.surface is not None:
            offset = self.display_man.get_display_offset(self.display_pos)
            self.display_man.display.blit(self.surface, offset)

    def destroy(self):
        self.sensor.destroy()

def run_simulation(args, client):
    """This function performed one test run using the args parameters
    and connecting to the carla client passed.
    """

    display_manager = None
    vehicle_list = []
    ind = 0
    car_speed = 30  # m/s
    steer = 0
    autopilot_enabled  = True

    try:
        world = client.get_world()
        original_settings = world.get_settings()


        # Instanciating the vehicle to which we attached the sensors
        bp = world.get_blueprint_library().filter('charger_2020')[0]
        vehicle = world.spawn_actor(bp, random.choice(world.get_map().get_spawn_points()))
        vehicle_list.append(vehicle)
        vehicle.set_autopilot(True)

        # Display Manager organize all the sensors an its display in a window
        # If can easily configure the grid and the total window size
        display_manager = DisplayManager(grid_size=[1, 3], window_size=[args.width*3, args.height])

        # Then, SensorManager can be used to spawn RGBCamera, LiDARs and SemanticLiDARs as needed
        # and assign each of them to a grid position, 
        SensorManager(world, display_manager, 'RGBCamera', carla.Transform(carla.Location(x=2, z=1.7), carla.Rotation(yaw=0)),
                      vehicle, {}, display_pos=[0, 0])
        SensorManager(world, display_manager, 'DepthCamera', carla.Transform(carla.Location(x=2, z=1.7), carla.Rotation(yaw=0)),
                      vehicle, {}, display_pos=[0, 1])
        SensorManager(world, display_manager, 'SemanticCamera', carla.Transform(carla.Location(x=2, z=1.7), carla.Rotation(yaw=+0)),
                      vehicle, {}, display_pos=[0, 2])


        #Simulation loop
        call_exit = False
        while True:
            # Carla Tick
            if args.sync:
                world.tick()

            else:
                world.wait_for_tick()

            ind += 1
            if np.mod(ind, 50) == 0:
                # teleport the car to a random location
                random_location = random.choice(world.get_map().get_spawn_points())
                transform = carla.Transform(location=random_location.location,
                                            rotation=random_location.rotation)
                vehicle.set_transform(transform)
                vehicle_list = []
                vehicle_list.append(vehicle)

            # Render received data
            display_manager.render()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    call_exit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE or event.key == K_q:
                        call_exit = True
                        break
                    if event.key == K_r:
                        # teleport the car to a random location
                        random_location = random.choice(world.get_map().get_spawn_points())
                        transform = carla.Transform(location=random_location.location,
                                                    rotation=random_location.rotation)
                        vehicle.set_transform(transform)

                    if event.key == K_c:
                        # spawn objects
                        for i in range(10):
                            bp_car = world.get_blueprint_library().filter('etron')[0]
                            color = random.choice(bp_car.get_attribute('color').recommended_values)
                            bp_car.set_attribute('color', color)
                            car = world.spawn_actor(bp_car, random.choice(world.get_map().get_spawn_points()))
                            car.set_autopilot(True)

                    if event.key == K_d:
                        steer += 0.0002
                        print(fr'steer: {steer}')
                        vehicle.apply_control(
                            carla.VehicleControl(throttle=car_speed, steer=steer))

                    if event.key == K_a:
                        steer -= 0.0002
                        print(fr'steer: {steer}')
                        vehicle.apply_control(
                            carla.VehicleControl(throttle=car_speed, steer=steer))

                    if event.key == K_LEFT:
                        # Get the vehicle's transform
                        vehicle_transform = vehicle.get_transform()

                        # Get the vehicle's rotation quaternion
                        rotation = vehicle_transform.rotation
                        location = vehicle_transform.location

                        # Calculate pitch, yaw, and roll angles
                        pitch, yaw, roll = rotation.pitch, rotation.yaw, rotation.roll
                        desired_rotation = carla.Rotation(pitch=pitch, yaw=yaw-5,
                                                          roll=roll)
                        desired_transform = carla.Transform(location, desired_rotation)
                        vehicle.set_transform(desired_transform)

                    if event.key == K_RIGHT:
                        # Get the vehicle's transform
                        vehicle_transform = vehicle.get_transform()

                        # Get the vehicle's rotation quaternion
                        rotation = vehicle_transform.rotation
                        location = vehicle_transform.location

                        # Calculate pitch, yaw, and roll angles
                        pitch, yaw, roll = rotation.pitch, rotation.yaw, rotation.roll
                        desired_rotation = carla.Rotation(pitch=pitch, yaw=yaw+5,
                                                          roll=roll)
                        desired_transform = carla.Transform(location, desired_rotation)
                        vehicle.set_transform(desired_transform)

                    if event.key == K_DOWN:
                        # Get the vehicle's transform
                        vehicle_transform = vehicle.get_transform()

                        # Get the vehicle's rotation quaternion
                        rotation = vehicle_transform.rotation
                        location = vehicle_transform.location

                        # Calculate pitch, yaw, and roll angles
                        pitch, yaw, roll = rotation.pitch, rotation.yaw, rotation.roll
                        desired_rotation = carla.Rotation(pitch=pitch, yaw=yaw+180,
                                                          roll=roll)
                        desired_transform = carla.Transform(location, desired_rotation)
                        vehicle.set_transform(desired_transform)

                    if event.key == K_s:
                        steer = 0
                        print(fr'steer: {steer}')
                        vehicle.apply_control(
                            carla.VehicleControl(throttle=car_speed, steer=steer))

                    if event.key == K_p:
                        autopilot_enabled = not autopilot_enabled
                        if autopilot_enabled:
                            print("Autopilot mode ON")
                        else:
                            print("Autopilot mode OFF")

                        vehicle.set_autopilot(autopilot_enabled)
                        pygame.display.update()

            if call_exit:
                break

    finally:
        if display_manager:
            display_manager.destroy()

        client.apply_batch([carla.command.DestroyActor(x) for x in vehicle_list])

        world.apply_settings(original_settings)



def main():
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
        default='960x1236',
        help='window resolution (default: 1284x480)')

    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)

        run_simulation(args, client)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    # while True:
    main()
