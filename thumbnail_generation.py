# -*- coding: utf-8 -*-
# Python

# © 2006-04, …, 2013-08-14 by Xah Lee, ∑ http://xahlee.org/

# Given a website gallery of images with hundreds of images, i want to generate a thumbnail page.

# Technically:
# • Given a dir: e.g. /Users/xah/web/img/
# • This dir has many HTML files inside it, some are in sub directories.
# • Each HTML file has many inline images (<img src="…">). (all inline images are local files)

# the program will generate thumbnails for all the inline images in the HTML files. The thumbnail images are generated in a user specified directory.

# the program will output text to stdout. The text is HTML syntax. Each line is of this format:
# <a href="f.html"><img src="thumbnail_relative_path/1.png"><img src="thumbnail_relative_path/2.png"></a>
# where f.html is one of the HTML file, and the 1.png and 2.png are the inline images linked to f.html.

# • The goal is to create thumbnail images of all the inline images in all HTML files under that dir, and print a output that can serve as the index of thumbnails.
# • These thumbnail images destination can be specified, unrelated to the given dir.
# • Thumbnail images must preserve the dir structure they are in. For example, if a inline image's full path is /a/b/c/d/1.img, and the root is given as /a/b, then the thumbnail image's path must retain the c/d, as sub dir under the specified thumbnail destination.
# • if the inline image's size is smaller than a certain given size (specified as area), then skip it.

# Note: only inline images in a HTML file will be considered for thumbnail. Any other images in the given dir or as linked images should be ignored.


#bugs & to dos

# • 2009-06-08. Split up the build_thumbnails function. It's a bit long.

# • 2009-06-08. Possibly rewrite to get rid of imagemagick shell call. Look into: http://www.pythonware.com/library/pil/handbook/index.htm or http://www.libgd.org/


# User Inputs

# path where HTML files and images are at. e.g. “/home/xah/web/xahsl_org/sl”
# no trailing slash
INPUT_PATH_DIR =  "/home/xah/web/xahlee_info/kbd"

# if this this is not empty, then only these files will be processed. INPUT_PATH_DIR is still needed.
file_list  = [

"/home/xah/web/xahlee_info/kbd/dactyl_keyboard.html"

]

# the value is equal or parent of INPUT_PATH_DIR.
# The thumbnails will preserve dir structures. If a image is at  /a/b/c/d/e/f/1.png, and ROOT_DIR is /a/b/c, then the thumbnail will be at ‹thumbnail dir›/d/e/f/1.png
# no trailing slash
ROOT_DIR = INPUT_PATH_DIR

# the destination path of thumbanil images. It will be created. Existing files will be over-written.  e.g. /x/y
# no trailing slash
THUMBNAIL_DIR = INPUT_PATH_DIR + "/tn"

# thumbnail size
THUMBNAIL_SIZE_AREA = 200 * 200

# if a image is smaller than this area, don't create thumbnail for it.
MIN_AREA = 200*200 + 2

# if True, all thumbnails will be in JPG format. Otherwise, it's the same on the source image format.
# This feature is usedful because stamp sized black & white PNG doesn't look good, may have artifacts.
JPG_ONLY_THUMBNAILS = True # True or False

# depth of nested dir to dive into.
MIN_LEVEL = 1; # files and dirs of mydir are level 1.
MAX_LEVEL = 4; # inclusive

OVERWRITE_EXISTING_THUMBNAIL = False # True or False

# imageMagic/GraphicsMagic “identify” or “convert” program path

GM_ID_PATH = r"/usr/bin/convert"
GM_CVT_PATH = r"/usr/bin/convert"


import re
import subprocess
import os
import sys
import Image


## functions

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

def get_img_dimension(img_path):
    u"""Get the width and height of a image file.

    Returns a tuple: (width, height)
    Each element is a integer.
    """
    return Image.open(img_path).size

def create_thumbnail( i_path, new_path, scale_n):
    u"""Create a image from i_path at new_path, with scale scale_n in percent.
The i_path and new_path are full paths, including dir and file name.
    """
    subprocess.Popen([GM_CVT_PATH, "-scale", str(round( scale_n * 100,2) ) + "%", "-sharpen","1", i_path, new_path] ).wait()

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

def build_thumbnails(dPath, fName, tbPath, rPath, areaA):
    u"""Generate thumbnail images.

    Args:
    dPath: directory full path
    fName: path to a HTML file name that exists under dPath.
    tbPath: the thumbnail images destination dir.
    rPath: is a root dir (substring of dPath), used to build the dir structure for tbPath for
each thumbnail.
    areaA: is the thumbnail image size in terms of its area.

    This function will create thumbnail images in the tbPath. rPath is
    a root dir subset of dPath, used to build the dir structure for
    tbPath for each thumbnail.

    For Example, if
    dPath = "/Users/mary/Public/pictures"
    fName = "trip.html" (this exits under dPath)
    tbPath = "/Users/mary/Public/thumbs"
    rPath = "/Users/mary/Public" (must be a substring of dPath or equal to it.)
    and trip.html contains <img ="Beijin/day1/img1.jpg">
    then a thumbnail will be generated at
    "/Users/mary/Public/thumbs/pictures/Beijin/day1/img1.jpg"

    This function makes a shell call to imagemagick's “convert” and “identify” commands, and assumes that both's path on the disk are set in the global vars “convert” and “identify”.
    """
    # outline:
    # • Read in the file.
    # • Get the img paths from inline images tags, accumulate them into a list.
    # • For each image, find its dimension w and h.
    # • Generate the thumbnail image on disk.

    # Generate a list of image paths. Each element of imgPaths is a full path to a image.
    imgPaths = []
    for im in filter(lambda x : (not x.startswith("http")) and (not x.endswith("icon_sum.gif")), get_inline_img_paths(dPath + "/" + fName)):
        imgPaths.append (link_fullpath(dPath, im))
    # print dPath, fName, tbPath, rPath
    # print imgPaths

    # generate the imgPaths2 list. (Change the image path to the full sized image, if it exists. That is, if image ends in -s.jpg, find one without the "-s".)
    imgPaths2 = []
    for oldPath in imgPaths:
        newPath = oldPath
        (dirName, fileName) = os.path.split(oldPath)
        (fileBaseName, fileExtension) = os.path.splitext(fileName)
        if(re.search(r"-s$",fileBaseName,re.U)):
            p2 = os.path.join(dirName,fileBaseName[0:-2]) + fileExtension
            if os.path.exists(p2): newPath = p2
        imgPaths2.append(newPath)
    # print imgPaths2

    # generate the imgData list. Each element in imgData has the form [image full path, [width, height]].
    img_data = []
    for i_path in imgPaths2:
        (i_w, i_h) = get_img_dimension(i_path)
        if (int(i_w) * int(i_h)) > MIN_AREA:
            img_data.append( [i_path, [i_w, i_h]])
    # print img_data, "\n"

    linkPath = (dPath+"/"+fName)[ len(rPath) + 1:]
    sys.stdout.write('<a href="' + linkPath + '">')

    # create the scaled image files in thumbnail dir. The dir structure is replicated.
    for img_d in img_data:
        # print "Thumbnailing:", img_d
        i_full_path = img_d[0]
        thumb_r_path = i_full_path[ len(rPath) + 1:]
        thumb_f_path = tbPath + "/" + thumb_r_path

        if JPG_ONLY_THUMBNAILS:
            (b,e) = os.path.splitext(thumb_r_path)
            thumb_r_path = b + ".jpg"
            (b,e) = os.path.splitext(thumb_f_path)
            thumb_f_path = b + ".jpg"
        # print "r",thumb_r_path
        # print "f",thumb_f_path

        sys.stdout.write('<img src="' + thumb_f_path + '" alt="" />')

        # make dirs to the thumbnail dir
        (dirName, fileName) = os.path.split(thumb_f_path)
        (fileBaseName, fileExtension) = os.path.splitext(fileName)
        # print "Creating thumbnail:", thumb_f_path
        try:
            os.makedirs(dirName,0775)
        except(OSError):
            pass

        # if not (os.path.exists(thumb_f_path) and (not OVERWRITE_EXISTING_THUMBNAIL)):

        if os.path.exists(thumb_f_path):
            if OVERWRITE_EXISTING_THUMBNAIL:
                create_thumbnail(i_full_path, thumb_f_path, scale_factor(areaA,img_d[1][0],img_d[1][1]))
        else:
            create_thumbnail(i_full_path, thumb_f_path, scale_factor(areaA,img_d[1][0],img_d[1][1]))

    print "</a>"

#################
# main

def dir_handler(dummy, curdir, fileList):
   curdir_level = len(re.split("/",curdir))-len(re.split("/",INPUT_PATH_DIR))
   filess_level = curdir_level + 1
   if MIN_LEVEL <= filess_level <= MAX_LEVEL:
      for fname in fileList:
          if re.search(r"\.html$", fname, re.U) and (not re.search(r"^xx", fname, re.U)):
            # print "processing:", curdir + "/" + fname
            build_thumbnails(curdir, fname, THUMBNAIL_DIR, ROOT_DIR, THUMBNAIL_SIZE_AREA)

while INPUT_PATH_DIR[-1] == "/":
    INPUT_PATH_DIR = INPUT_PATH_DIR[0:-1] # delete trailing slash

if (len(file_list) != 0):
    for fPath in file_list:
        (dirName, fileName) = os.path.split(fPath)
        # print (dirName, fileName)
        build_thumbnails(dirName, fileName, THUMBNAIL_DIR, ROOT_DIR, THUMBNAIL_SIZE_AREA)
else:
    os.path.walk(INPUT_PATH_DIR, dir_handler, "dummy")

# build_thumbnails("/home/xah/web/xahlee_info/kbd", "Microsoft_sculpt_ergonomic_keyboard.html", THUMBNAIL_DIR, ROOT_DIR, THUMBNAIL_SIZE_AREA)

# create_thumbnail( "/home/xah/web/xahlee_info/kbd/i/Microsoft_sculpt_ergonomic_keyboard_41754.jpg", "/home/xah/web/xahlee_info/kbd/tn/i/Microsoft_sculpt_ergonomic_keyboard_41754.jpg", 0.21460759332655016)
