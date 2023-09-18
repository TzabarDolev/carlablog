## The following code is a part of Sensors section at the Carla simulator research blog - https://carlasimblog.wordpress.com/2023/09/16/the-64-division-curse/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

## this code snippet fixes the issue stated here - https://github.com/carla-simulator/carla/issues/6085.

1. # patch for resolution bug - image width should be a full multiplication of 64
# this part should be done online, while creating the images.
if np.remainder(ImageWidth, 64) != 0:
    ImageWidth = np.ceil(ImageWidth / 64) * 64

2. # this part should be done offline, while processing the images
def resolution_bugfix(img, ImageWidth):
  if ImageWidth != img.shape[1]:
      height, width = img.shape[:2]
      left = (width - ImageWidth) // 2
      right = left + ImageWidth
      img = img[:, left:right]
  return img

img = self.resolution_bugfix(img, ImageWidth)
