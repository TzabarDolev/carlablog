## The following code is a part of Sensors section at my Carla simulator research blog - https://carlablog.carrd.co/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

## this is a simple and short code for raw depth conversion to grascale depth at centimeters units.
## pay attention that if you use int16 for writing the output depth image you can only use depth up to 65355 centimeters even though the simulator gives you data up to 1000 meters.
## Carla's repository has this code under the sensors page - https://carla.readthedocs.io/en/latest/ref_sensors/#depth-camera, but has two mistakes which are corrected at this following code snippet

def process_depth(self, img):

    R = img[:, :, 0]
    G = img[:, :, 1]
    B = img[:, :, 2]

    normalized = (G + B * 256 + R * 256 * 256) / (256 * 256 - 1)
    in_centimeters = 100000 * normalized

    # avoiding zero division
    in_centimeters = np.clip(in_centimeters, 0.1, np.max(in_centimeters))

    return in_centimeters
