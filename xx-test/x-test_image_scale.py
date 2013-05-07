# -*- coding: utf-8 -*-
# Python


import re
import subprocess
import os
import sys
import Image

infile = "Maltron_flat_keyboard-s.jpg"
outfile = "Maltron_flat_keyboard-s-out.jpg"

def scale_factor(A, w, h):
    u"""Get the desired scale factor of a image.

    scale_factor(A, w, h) returns a number s such that
    w*s*h*s==A. This is used for getting the scaling factor of a image
    with a desired thumbnail area A. The w and h are width and height
    of a image. The A is the area of desired thumbnail size. When the
    image is scaled by s in both dimensions, it will have desired size
    specified by area A as thumbnail. (will not be exact due to
    rounding of pixels to integers)
    """
    return (float(A)/float(w*h))**0.5

im = Image.open(infile)

widthOld, heightOld = im.size

print widthOld, heightOld

ss = scale_factor(200*200, widthOld, heightOld)

print ss

widthNew, heightNew = int(widthOld * ss), int(heightOld * ss)

print widthNew, heightNew

im.thumbnail((widthNew, heightNew))
im.save(outfile, "JPEG")

# def create_thumbnail( i_path, new_path, scale_n):
#     u"""Create a image from i_path at new_path, with scale scale_n in percent.
# The i_path and new_path are full paths, including dir and file name.
#     """
#     subprocess.Popen([GM_CVT_PATH, 'convert',  '-scale', str(round( scale_n * 100,2) ) + '%', '-sharpen','1', i_path, new_path] ).wait()

