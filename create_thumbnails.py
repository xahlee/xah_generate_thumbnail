# -*- coding: utf-8 -*-
# Python

# © 2006-04, …, 2017-09-02 by Xah Lee, ∑ http://xahlee.info/

# generate a thumbnail images.

# • Given a dir: e.g. /Users/xah/web/img/
# • go thru all html files in it. (or a list of html files)
# • Each HTML file has many inline images (<img src="…">). (all inline images are local files)
# • generate thumbnails for those images, in the same directory those images are

# print to stdout. print the path of the html file, followed by paths of the new thumb nails

#--------------------------------------------------
# User Inputs

# path where HTML files and images are at. e.g. "/home/xah/web/xahlee_info/xyz"
# no trailing slash
INPUT_PATH_DIR = "/home/xah/web/xahlee_info/xyz"

# if this this is not empty, then just create thumbnails of these images. each element is full path
# e.g. "/home/xah/web/xahlee_info/img/cat.jpg"
IMAGE_LIST  = [

]

# if this this is not empty, then only these files will be processed. INPUT_PATH_DIR is still needed.
# each element is full path
# e.g. "/home/xah/web/xahlee_info/kbd/logitech_mx_ergo_trackball.html"
FILE_LIST  = [

]

# thumbnail area size, as width times height
THUMBNAIL_SIZE_AREA = 200 * 200
THUMBNAIL_SIZE_AREA = 250 * 250

# NAME_PREFIX is a string that will be in the new thumbnail name. For easy identification of the file as thumb. e.g. "ztn_"
NAME_PREFIX = "ztn_"

# if a image is smaller than this area, don't create thumbnail for it.
MIN_AREA = THUMBNAIL_SIZE_AREA * 1.05

# if True, all thumbnails will be in JPG format. Otherwise, it's the same on the source image format.
# This feature is usedful because stamp sized black & white PNG doesn't look good, may have artifacts.
JPG_ONLY_THUMBNAILS = True

# depth of nested dir to dive into.
MIN_LEVEL = 1; # files and dirs of mydir are level 1.
MAX_LEVEL = 4; # inclusive

# imageMagic/GraphicsMagic “identify” and “convert” program path
GM_ID_PATH = r"/usr/local/bin/identify"
GM_CVT_PATH = r"/usr/local/bin/convert"

#--------------------------------------------------
import re
import subprocess
import os
import sys
# import Image
import os.path

#--------------------------------------------------
## functions

def scale_factor(A, w, h):
    u"""Get the desired scale factor of a image.

    A is a desired area of a image.
    w is the current image width.
    h is the current image height.

    returns s, the scale factor to get to A, such that w*s*h*s==A

    scale_factor(A, w, h) returns a number s such that
    w*s*h*s==A. This is used for getting the scaling factor of a image
    with a desired thumbnail area A. The w and h are width and height
    of a image. The A is the area of desired thumbnail size. When the
    image is scaled by s in both dimensions, it will have desired size
    specified by area A as thumbnail. (will not be exact due to
    rounding of pixels to integers)
    """
    return (float(A)/float(w*h))**0.5

def get_img_dimension(img_path):
    u"""Get the width and height of a image file.

    Returns a tuple: (width, height)
    Each element is a integer.
    """
    wh = subprocess.check_output([GM_ID_PATH, "-format", "%w %h", img_path]).split(" ")
    return (int(wh[0]), int(wh[1]))
    # return Image.open(img_path).size

def create_thumbnail( i_path, new_path, scale_n):
    u"""Create a image from i_path at new_path, with scale scale_n.
scale_n is a real number between 0 and 1.
The i_path and new_path are full paths, including dir and file name.
    """
    subprocess.Popen([GM_CVT_PATH, "-scale", str(round( scale_n * 100,2) ) + "%", "-quality", "90%" , "-sharpen","1", i_path, new_path] ).wait()

def create_thumb2( img_path, n):
    u"""Create scaled version of image at img_path.
n is percentage, a integer. For example, 50, means 50%.
img_path is full path to a image file.
The new file will be created at the same directory and named with dimension prefixed, e.g.
create_thumb2("/home/jane/cat.jpg", 50)
will create
"/home/jane/_300x400_cat.jpg"
    """
    (dirName, fileName) = os.path.split(img_path)
    (w, h) = get_img_dimension(img_path)
    new_path = dirName + "/" + "_" + str( int(round(w * n/100.0))) + "x" + str(int(round(h * n/100.0))) + "_" + fileName
    print(new_path)
    subprocess.Popen([GM_CVT_PATH, "-scale", str(n) + "%", "-sharpen","1", img_path, new_path] ).wait()

def get_inline_img_paths(file_full_path):
    u"""Return a list of inline image paths from a file.

    Arg:
    file_full_path: a full path to a HTML file.

    Returns:
    A list.

    Example return value: ["xx.jpg","../image.png"]
    """
    FF = open(file_full_path,"rb")
    txt_segs = re.split( re.compile(r"<img ", re.U|re.I), unicode(FF.read(), "utf-8"))
#    txt_segs = re.split( r"src", unicode(FF.read(), "utf-8"))
    txt_segs.pop(0)
    FF.close()
    linx = []
    for link_block in txt_segs:
        match_result = re.search(ur'\s*src=\s*\"([^\"]+)\"', link_block, re.U)
        if match_result:
            src_str = match_result.group(1).encode("utf-8")
            if re.search(ur"jpg|jpeg|gif|png$", src_str, re.U | re.I):
                linx.append( src_str )
    return linx

def link_fullpath(dir, locallink):
   u"""Get the full path of a relative path.
   link_fullpath(dir, locallink) returns a string that is the full path to the local link. For example, link_fullpath("/Users/t/public_html/a/b", "../image/t.png") returns "Users/t/public_html/a/image/t.png". The returned result will not contain double slash or "../" string.
   """
   result = dir + "/" + locallink
   result = re.sub(r"//+", r"/", result)
   while re.search(r"/[^\/]+\/\.\.", result): result = re.sub(r"/[^\/]+\/\.\.", "", result)
   return result

def get_large_size_image(imgPaths):
    u"""Get larger size images, if it exists.
    imagePaths is a list of image full paths.
    returns a new list.
    If a image file ends in -s.jpg or -s.png, find one without the "-s", if exist.
    """
    imgPaths2 = []
    for oldPath in imgPaths:
        newPath = oldPath
        (dirName, fileName) = os.path.split(oldPath)
        (fileBaseName, fileExtension) = os.path.splitext(fileName)
        if(re.search(r"-s$",fileBaseName,re.U)):
            p2 = os.path.join(dirName,fileBaseName[0:-2]) + fileExtension
            if os.path.exists(p2): newPath = p2
        imgPaths2.append(newPath)
    return imgPaths2

def get_image_paths(html_full_path):
    u"""return a list of image paths. Each element is a full path to a image file embeded in html_full_path
    """
    paths = []
    for im in filter(lambda x : (not x.startswith("http")) , get_inline_img_paths(html_full_path)):
        (dirPath, fileName) = os.path.split(html_full_path)
        paths.append (link_fullpath(dirPath, im))
    return paths

def create_thumb_img (img_paths, img_size_area, min_area, name_prefix):
    u"""create the scaled image files
img_paths is a list of image file full paths
img_size_area is a integer. It's desired image size as area. That is, the new width * height
min_area is a integer. If original image is less than this, do nothing.
name_prefix is a string that will be in the new thumbnail name. For easy identification of the file as thumb. e.g. "ztn_"
2017-09-01
    """
    for img_path in img_paths:
        (width, height) = get_img_dimension(img_path)
        if (int(width) * int(height)) < min_area: continue

        scale_n = scale_factor(img_size_area, width, height)
        (widthNew, heightNew) = int(width * scale_n), int(height * scale_n)

        (dirName, fileName) = os.path.split(img_path)
        # newFileName = name_prefix + str(widthNew) + "x" + str(heightNew) + "_" + fileName

        newFileName = name_prefix + (re.sub(r"\.png", r".jpg", fileName) if JPG_ONLY_THUMBNAILS else fileName)

        thumb_file_path = dirName + "/" + newFileName

        print( thumb_file_path + "\n")

        create_thumbnail(img_path, thumb_file_path, scale_n )

def build_thumbnails(dPath, fName, img_size_area):
    u"""create thumbnail images in the same directory as the image, for all local embedded images in html files.

    dPath: directory path
    fName: a HTML file name that exists under dPath.
    img_size_area: dimension of thumbnail image, specified as area = width*height

    2017-09-01
    """

    sys.stdout.write('\n')
    sys.stdout.write((dPath+"/"+fName))
    sys.stdout.write('\n')
    create_thumb_img (get_large_size_image( get_image_paths(dPath + "/" + fName)), img_size_area, MIN_AREA, NAME_PREFIX)

#################
# main

def dir_handler(dummy, curdir, fileList):
   curdir_level = len(re.split("/",curdir))-len(re.split("/",INPUT_PATH_DIR))
   filess_level = curdir_level + 1
   if MIN_LEVEL <= filess_level <= MAX_LEVEL:
      for fname in fileList:
          if re.search(r"\.html$", fname, re.U) and (not re.search(r"^xx", fname, re.U)):
            build_thumbnails(dirName, fileName, THUMBNAIL_SIZE_AREA)

while INPUT_PATH_DIR[-1] == "/":
    INPUT_PATH_DIR = INPUT_PATH_DIR[0:-1] # delete trailing slash

if (len(IMAGE_LIST) > 0):
    create_thumb_img (IMAGE_LIST, THUMBNAIL_SIZE_AREA, MIN_AREA, NAME_PREFIX)
else:
    if (len(FILE_LIST) > 0):
        for fPath in FILE_LIST:
            (dirName, fileName) = os.path.split(fPath)
            # print (dirName, fileName)
            build_thumbnails(dirName, fileName, THUMBNAIL_SIZE_AREA)
    else:
        os.path.walk(INPUT_PATH_DIR, dir_handler, "dummy")
