"""
 ----------------------------------------------------
  @Author: tsukasa
  @Affiliation: Waseda University
  @Email: rinsa@suou.waseda.jp
  @Date: 2019-07-12 23:20:19
  @Last Modified by:   tsukasa
  @Last Modified time: 2019-07-13 01:09:49
 ----------------------------------------------------

  Usage:
   python <file_name>.py argvs[1] argvs[2] argvs[3]...

"""


import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from natsort import natsorted

argvs = sys.argv
path = argvs[1]
gtimage = argvs[2]



## load gt
gtimg = np.array(Image.open(gtimage), dtype=np.uint8)



## load layer
list = natsorted(os.listdir(path))
layer_list = []
layer_img = []

for i in list:
  if(i[:5] == "layer"):# and i[-4:]==".png"):
    layer_list.append(i)
    layer_img.append(np.array(Image.open(os.path.join(path, i)), dtype=np.uint8))



## merge image, and add text
merged_image = []
for i, img in enumerate(layer_img):
  basename = layer_list[i][:-4]
  outname = os.path.join(path, "merged_{}.png".format(basename))
  npimg = np.hstack((img, gtimg))
  pilimg = Image.fromarray(npimg)

  # save merged image
  pilimg.save(outname)


  # add text
  height = npimg.shape[0]
  width = npimg.shape[1]
  draw = ImageDraw.Draw(pilimg)
  # draw.rectangle((500, 0, 650, 20), fill=(128, 128, 128))
  font = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 100)
  draw.multiline_text((0+100, 0+40), str("3D BVH: {}".format(basename)), fill=(255, 255, 255), font=font)
  draw.multiline_text((int(width/2)+100, 0+40), str("Actual Model"), fill=(255, 255, 255), font=font)
  pilimg.save(outname)

  # store edited merged image
  merged_image.append(pilimg.resize((int(width/3), int(height/3)), Image.LANCZOS))


# make .gif from list
outpath = os.path.join(path, "result.gif")
merged_image[0].save(outpath, save_all=True, append_images=merged_image[1:], optimize=False, duration=600, loop=0)


