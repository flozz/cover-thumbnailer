#!/usr/bin/env python3
# -*- coding: utf-8 -*-

   #########################################################################
 ##                                                                       ##
##           ┏━╸┏━┓╻ ╻┏━╸┏━┓   ╺┳╸╻ ╻╻ ╻┏┳┓┏┓ ┏┓╻┏━┓╻╻  ┏━╸┏━┓            ##
##           ┃  ┃ ┃┃┏┛┣╸ ┣┳┛    ┃ ┣━┫┃ ┃┃┃┃┣┻┓┃┗┫┣━┫┃┃  ┣╸ ┣┳┛            ##
##           ┗━╸┗━┛┗┛ ┗━╸╹┗╸    ╹ ╹ ╹┗━┛╹ ╹┗━┛╹ ╹╹ ╹╹┗━╸┗━╸╹┗╸            ##
##                         — www.flogisoft.com —                          ##
##                                                                        ##
############################################################################
##                                                                        ##
## Cover thumbnailer                                                      ##
##                                                                        ##
## Copyright (C) 2009 - 2023  Fabien Loison <http://www.flozz.fr/>        ##
##                                                                        ##
## This program is free software: you can redistribute it and/or modify   ##
## it under the terms of the GNU General Public License as published by   ##
## the Free Software Foundation, either version 3 of the License, or      ##
## (at your option) any later version.                                    ##
##                                                                        ##
## This program is distributed in the hope that it will be useful,        ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of         ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          ##
## GNU General Public License for more details.                           ##
##                                                                        ##
## You should have received a copy of the GNU General Public License      ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>.  ##
##                                                                        ##
############################################################################
##                                                                        ##
## WEB SITE : https://github.com/flozz/cover-thumbnailer                  ##
##                                                                       ##
#########################################################################


"""Generates thumbnails for nautilus' folders.

Cover thumbnailer generates thumbnail that will be displayed instead of the
default folder icons. It has a specific presentation for music and pictures
folders, and a generic one for other folders.

Usage:
    cover-thumbnailer <directory's path> <output thumbnail's path>
"""

__version__ = "{{VERSION}}"
__author__ = "Fabien Loison <http://www.flozz.fr/>"
__copyright__ = "Copyright © 2009 - 2023 Fabien LOISON"


import re
import sys
import os.path
from gi.repository import Gio

try:
    from PIL import Image
except:
    import Image


#==================================================================== CONF ====
#Base path for cover thumbnailer's pictures
if "DEVEL" in os.environ:
    BASE_PATH = "./share/" #For devel
else:
    BASE_PATH = "/usr/share/cover-thumbnailer/"

#Cover files list
COVER_FILES = ["cover.png", "cover.jpg", ".cover.png", ".cover.jpg",
        "Cover.png", "Cover.jpg", ".Cover.png", ".Cover.jpg",
        "folder.png", "folder.jpg", ".folder.png", ".folder.jpg",
        "Folder.png", "Folder.jpg", ".Folder.png", ".Folder.jpg"]

#Supported picture ext (ALWAY LAST 4 CHARS !!)
PICTURES_EXT = [".jpg", ".JPG", "jpeg", "JPEG",
        ".png", ".PNG", #Not interlaced
        ".gif", ".GIF",
        ".bmp", ".BMP", #Window ans OS/2 bitmap
        ".ico", ".ICO", #Windows icon format
        ".tga", ".TGA", #Truevision Targa format
        ".tif", ".TIF", "tiff", "TIFF", #Adobe Tagged Image File Format
        ".psd", ".PSD", #Adobe Photosop format (only version 2.5 and 3.0)
        ]

#==============================================================================


class Conf(dict):

    """ Import configuration.

    Import configuration from the GNOME and cover thumbnailer files
    """

    def __init__(self):
        """ The constructor

        Set the default values
        """
        #Initialize the dictionary
        dict.__init__(self)
        #Music
        self['music_enabled'] = True
        self['music_keepdefaulticon'] = False
        self['music_usegnomefolder'] = True
        self['music_cropimg'] = True
        self['music_makemosaic'] = False
        self['music_paths'] = []
        self['music_defaultimg'] = os.path.join(BASE_PATH, "music_default.png")
        self['music_fg'] = os.path.join(BASE_PATH, "music_fg.png")
        self['music_bg'] = os.path.join(BASE_PATH, "music_bg.png")
        #Pictures
        self['pictures_enabled'] = True
        self['pictures_keepdefaulticon'] = False
        self['pictures_usegnomefolder'] = True
        self['pictures_maxthumbs'] = 3
        self['pictures_paths'] = []
        self['pictures_fg'] = os.path.join(BASE_PATH, "pictures_fg.png")
        self['pictures_bg'] = os.path.join(BASE_PATH, "pictures_bg.png")
        #Other
        self['other_enabled'] = True
        self['other_fg'] = os.path.join(BASE_PATH, 'other_fg.png')
        #Ignored
        self['ignored_dotted'] = False
        self['ignored_paths'] = []
        #Never ignored
        self['neverignored_paths'] = []
        #Global
        self.user_homedir = os.environ.get("HOME")
        self.user_gnomeconf = os.path.join(
                self.user_homedir,
                ".config/user-dirs.dirs"
                )
        self.user_conf = os.path.join(
                self.user_homedir,
                ".cover-thumbnailer/cover-thumbnailer.conf"
                )
        #Read configuration
        self.import_user_conf()
        self.import_gnome_conf()

    def import_gnome_conf(self):
        """ Import user folders from GNOME configuration file. """
        if os.path.isfile(self.user_gnomeconf):
            gnome_conf_file = open(self.user_gnomeconf, 'r')
            for line in gnome_conf_file:
                if re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line) and self['music_usegnomefolder']:
                    match = re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line)
                    path = match.group(1).replace('$HOME', self.user_homedir)
                    #If path == user home dir, don't use it, it's probably a misconfiguration !
                    if os.path.isdir(path) and not os.path.samefile(path, self.user_homedir):
                        self['music_paths'].append(path)
                elif re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line) and self['pictures_usegnomefolder']:
                    match = re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line)
                    path = match.group(1).replace('$HOME', self.user_homedir)
                    #If path == user home dir, don't use it, it's probably a misconfiguration !
                    if os.path.isdir(path) and not os.path.samefile(path, self.user_homedir):
                        self['pictures_paths'].append(path)
            gnome_conf_file.close()
        else:
            print("W: [%s:Conf.import_gnome_conf] Can't find `user-dirs.dirs' file." % __file__)

    def import_user_conf(self):
        """ Import user configuration file. """
        if os.path.isfile(self.user_conf):
            current_section = "unknown"
            user_conf_file = open(self.user_conf, "r")
            for line in user_conf_file:
                #Comments
                if re.match(r"\s*#.*", line):
                    continue
                #Section
                elif re.match(r"\s*\[([a-z]+)\]\s*", line.lower()):
                    match = re.match(r'\s*\[([a-z]+)\]\s*', line.lower())
                    current_section = match.group(1)
                #Boolean key
                elif re.match(r"\s*([a-z]+)\s*=\s*(yes|no|true|false)\s*", line.lower()):
                    match = re.match(r"\s*([a-z]+)\s*=\s*(yes|no|true|false)\s*", line.lower())
                    key = match.group(1)
                    value = match.group(2)
                    if value in ("yes", "true"):
                        value = True
                    else:
                        value = False
                    self[current_section + "_" + key] = value
                #String key : path
                elif re.match(r"\s*(path|PATH|Path)\s*=\s*\"(.+)\"\s*", line):
                    match = re.match(r"\s*(path|PATH|Path)\s*=\s*\"(.+)\"\s*", line)
                    key = "paths"
                    value = match.group(2)
                    self[current_section + "_" + key].append(value)
                #Integer key
                elif re.match(r"\s*([a-z]+)\s*=\s*([0-9]+)\s*", line.lower()):
                    match = re.match(r"\s*([a-z]+)\s*=\s*([0-9]+)\s*", line.lower())
                    key = match.group(1)
                    value = match.group(2)
                    self[current_section + "_" + key] = int(value)

            user_conf_file.close()

            #Replace "~/" by the user home dir
            for path_list in (self['music_paths'], self['pictures_paths'], self['ignored_paths']):
                for i in range(0, len(path_list)):
                    if path_list[i][0] == "~":
                        path_list[i] = os.path.join(self.user_homedir, path_list[i][2:])

            #Import "useGnomeConf" key (for compatibility)
            if "miscellaneous_usegnomeconf" in self:
                self["music_usegnomefolder"] = self["miscellaneous_usegnomeconf"]
                self["pictures_usegnomefolder"] = self["miscellaneous_usegnomeconf"]


class Thumb(object):
    """ Makes thumbnails.

    Generate thumbnails for all kind of folders
    """
    def __init__(self, img_paths):
        """The constructor.

        Argument:
          * img_paths -- a list of picture path
        """
        self.img = []
        for path in img_paths:
            try:
                img = Image.open(path).convert("RGBA")
            except IOError:
                print("E: [%s:Thumb.__init__] Can't open '%s'." % (__file__, path))
            else:
                self.img.append(img)
        self.thumb = None

    def thumbnailize(self, image, twidth=128, theight=128, crop=True):
        """ Make thumbnail.

        Crop the picture if necessaries and return a thumbnail of it.

        Keyword argument:
          * twidth -- the width of the thumbnail (in pixels).
          * theight -- the width of the thumbnail (in pixels).
            NOTE: useless if crop = True
          * crop -- the resize method (True for having a squared thumbnail)

        NOTE: the size shouldn't be greater than 128 px for a standard
              freedesktop thumbnail.
        """
        width = image.size[0]
        height = image.size[1]
        if crop and width >= twidth and height >= theight:
            if width > height:
                left = int((width - height) / 2)
                upper = 0
                right = height + left
                lower = height
            else:
                left = 0
                upper = int((height - width) / 2)
                right = width
                lower = width + upper
            image = image.crop((left, upper, right, lower))
        image.thumbnail((twidth, theight), Image.LANCZOS)
        return image

    def music_thumbnail(self, bg_picture, fg_picture, crop=True):
        """ Makes thumbnails for music folders.

        Argument:
          * bg_picture -- the background picture
          * fg_picture -- the foreground picture
          * crop -- the resize method (True for having a squared thumbnail)
        """
        #Background picture
        bg = Image.open(bg_picture).convert("RGB")
        bg_width = bg.size[0]
        bg_height = bg.size[1]
        #Album cover
        cover = self.thumbnailize(self.img[0], bg_height, crop=crop)
        cover_width = cover.size[0]
        cover_height = cover.size[1]
        #Cover position on background
        delta = bg_width - bg_height #The left border of album
        x = int((bg_width - cover_width + delta) / 2)
        y = int((bg_height - cover_height) / 2)
        #Past cover on background
        bg.paste(cover, (x, y), cover)
        #Forground picture
        fg = Image.open(fg_picture).convert("RGBA")
        #Past forground on background+cover
        bg.paste(fg, (0, 0), fg)
        self.thumb = bg

    def music_thumbnail_mosaic(self, bg_picture, fg_picture, crop=True):
        """ Makes thumbnails composed by more than one cover for music folders.

        Argument:
          * bg_picture -- the background picture
          * fg_picture -- the foreground picture
          * crop -- the resize method (True for having a squared thumbnail)

        NOTE: call this function ONLY if self.img has, at least, two pictures.
        """
        #Background picture
        bg = Image.open(bg_picture).convert("RGB")
        bg_width = bg.size[0]
        bg_height = bg.size[1]
        #Album covers
        covers_thumb = []
        for img in self.img:
            cover_thumb = self.thumbnailize(img, int(bg_height / 2), crop=crop)
            cover_thumb_width = cover_thumb.size[0]
            cover_thumb_height = cover_thumb.size[1]
            covers_thumb.append({
                'cover': cover_thumb,
                'width': cover_thumb_width,
                'height': cover_thumb_height
                })
        #For having 4 covers for the mosaic
        if len(covers_thumb) == 2:
            covers_thumb.append(covers_thumb[1].copy())
            covers_thumb.append(covers_thumb[0].copy())
        elif len(covers_thumb) == 3:
            covers_thumb.append(covers_thumb[0].copy())
        #Covers position on background
        delta = bg_width - bg_height #The left border of album
        covers_thumb[0]['x'] = int(1*(bg_width - delta)/4 - covers_thumb[0]['width']/2 + delta)
        covers_thumb[0]['y'] = int(1*bg_height/4 - covers_thumb[0]['height']/2)
        covers_thumb[1]['x'] = int(3*(bg_width - delta)/4 - covers_thumb[1]['width']/2 + delta)
        covers_thumb[1]['y'] = int(1*bg_height/4 - covers_thumb[1]['height']/2)
        covers_thumb[2]['x'] = int(1*(bg_width - delta)/4 - covers_thumb[2]['width']/2 + delta)
        covers_thumb[2]['y'] = int(3*bg_height/4 - covers_thumb[2]['height']/2)
        covers_thumb[3]['x'] = int(3*(bg_width - delta)/4 - covers_thumb[3]['width']/2 + delta)
        covers_thumb[3]['y'] = int(3*bg_height/4 - covers_thumb[3]['height']/2)
        #Paste covers on background
        for i in range(0, 4):
            bg.paste(covers_thumb[i]['cover'],
                    (covers_thumb[i]['x'], covers_thumb[i]['y']),
                    covers_thumb[i]['cover']
                    )
        #Forground picture
        fg = Image.open(fg_picture).convert("RGBA")
        #Paste forground on background+cover
        bg.paste(fg, (0, 0), fg)
        self.thumb = bg

    def pictures_thumbnail(self, bg_picture, fg_picture, max_pictures=3):
        """ Makes thumbnails for picture folders.

        Arguments:
          * bg_picture -- the background picture
          * fg_picture -- the foreground picture

        Keyword argument:
          * max_pictures -- the maximum number of pictures on the thumbnail
        """
        #Background
        bg = Image.open(bg_picture).convert("RGBA")
        bg_width = bg.size[0]
        bg_height = bg.size[1]
        picts = []
        number_of_pictures = 0
        #One picture
        if len(self.img) == 1 or max_pictures == 1 and len(self.img) > 0:
            number_of_pictures = 1
            thumb = self.thumbnailize(
                    self.img[0],
                    bg_width - 20,
                    bg_height - 20,
                    crop=False
                    )
            x = int((bg_width - thumb.size[0]) / 2)
            y = int((bg_height - thumb.size[1]) / 2)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })
        #Two pictures
        elif len(self.img) == 2 or max_pictures == 2 and len(self.img) > 0:
            number_of_pictures = 2
            #Thumb 0
            thumb = self.thumbnailize(
                    self.img[0],
                    bg_width - 20,
                    int(0.53*bg_height),
                    crop=False
                    )
            picts.append({
                    'thumb': thumb,
                    'x': 10,
                    'y': 5
                    })
            #Thumb 1
            thumb = self.thumbnailize(
                    self.img[1],
                    bg_width - 20,
                    int(0.53*bg_height),
                    crop=False
                    )
            x = bg_width - thumb.size[0] - 10
            y = bg_height - thumb.size[1] - 5
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })
        #Three pictures
        elif len(self.img) == 3 or max_pictures == 3 and len(self.img) > 0:
            number_of_pictures = 3
            #Thumb 0
            thumb = self.thumbnailize(self.img[0], 49, 56, crop=False)
            picts.append({
                    'thumb': thumb,
                    'x': 20,
                    'y': 5
                    })
            #Thumb 1
            thumb = self.thumbnailize(self.img[1], 49, 56, crop=False)
            x = int(bg_width - thumb.size[0] - 5)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': 5
                    })
            #Thumb 2
            h = int(bg_height - max(picts[0]['thumb'].size[1], picts[1]['thumb'].size[1]) - 15)
            thumb = self.thumbnailize(self.img[2], 103, h, crop=False)
            x = int((bg_width - 15 - thumb.size[0])/2 + 15)
            y = int(bg_height - thumb.size[1] - 5)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })
        #Four pictures
        elif len(self.img) == 4 or max_pictures == 4 and len(self.img) > 0:
            number_of_pictures = 4
            #Thumb 0
            thumb = self.thumbnailize(
                    self.img[0],
                    int(bg_width/2 - 7.5),
                    int(bg_height/2 - 7.5),
                    crop=False
                    )
            x = int(1*bg_width/4 - thumb.size[0]/2)
            y = int(1*bg_height/4 - thumb.size[1]/2)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })
            #Thumb 1
            thumb = self.thumbnailize(
                    self.img[1],
                    int(bg_width/2 - 7.5),
                    int(bg_height/2 - 7.5),
                    crop=False
                    )
            x = int(3*bg_width/4 - thumb.size[0]/2)
            y = int(1*bg_height/4 - thumb.size[1]/2)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })
            #Thumb 2
            thumb = self.thumbnailize(
                    self.img[2],
                    int(bg_width/2 - 7.5),
                    int(bg_height/2 - 7.5),
                    crop=False
                    )
            x = int(1*bg_width/4 - thumb.size[0]/2)
            y = int(3*bg_height/4 - thumb.size[1]/2)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })
            #Thumb 3
            thumb = self.thumbnailize(
                    self.img[3],
                    int(bg_width/2 - 7.5),
                    int(bg_height/2 - 7.5),
                    crop=False
                    )
            x = int(3*bg_width/4 - thumb.size[0]/2)
            y = int(3*bg_height/4 - thumb.size[1]/2)
            picts.append({
                    'thumb': thumb,
                    'x': x,
                    'y': y
                    })

        #Paste pictures on background
        for i in range(0, number_of_pictures):
            bg.paste(
                    picts[i]['thumb'],
                    (picts[i]['x'], picts[i]['y']),
                    picts[i]['thumb']
                    )
        #Paste forground on background+pictures
        fg = Image.open(fg_picture).convert("RGBA")
        bg.paste(fg, (0, 0), fg)
        self.thumb = bg

    def other_thumbnail(self, fg_picture):
        """ Makes thumbnails for "other" folders

        Argument:
          * fg_picture -- the foreground picture to add
        """
        fg = Image.open(fg_picture).convert("RGBA")
        size = fg.size[0]
        if len(self.img) == 1:
            image = self.thumbnailize(self.img[0], size, crop=True)
            if image.size[0] == size and image.size[1] == size:
                image.paste(fg, (0, 0), fg)
                self.thumb = image

    def save_thumb(self, output_path, output_format='PNG'):
        """ Save the thumbnail in a file.

        Argument:
          * output_path -- the output path for the thumbnail
        Keyword argument:
          * format -- the format of the picture (PNG, JPEG,...)

        NOTE : The output format must be a PNG for a standard
               freedesktop thumbnail
        """
        if self.thumb is not None:
            self.thumb.save(output_path, output_format)
        else:
            print("E: [%s:Thumb.save_thumb] No thumbnail created" % __file__)


def search_cover(path):
    """ Search for a cover file.

    Search for files like cover.png, .folder.jpg,... in the folder and return
    its name as a list of on item (or an empty list if no pictures were found)

    Argument:
      * path -- the path of the folder
    """
    cover_path = []
    for cover in COVER_FILES:
        if os.path.isfile(os.path.join(path, cover)):
            cover_path.append(os.path.join(path, cover))
            break
    return cover_path


def search_pictures(path):
    """ Search for pictures in the folder

    Search for pictures in the folder and return their name as a list (or an
    empty list if no pictures were found).

    Argument:
      * path -- the path of the folder
    """
    files = os.listdir(path)
    pictures = []
    for file_ in files:
        if file_[-4:] in PICTURES_EXT:
            pictures.append(os.path.join(path, file_))
        if len(pictures) >= 4: #4 pictures max... don't need more
            break
    return pictures


def search_pictures_recursiv(path):
    """ Search recursively for pictures in the folder

    Search for pictures in the subfolders and return their name as a list
    (or an empty list if no pictures were found).

    Argument:
      * path -- the path of the folder
    """
    pictures = []
    for root, dirs, files in os.walk(path):
        if len(pictures) <= 4: #4 pictures max... don't need more
            for file_ in files:
                if file_[-4:] in PICTURES_EXT:
                    pictures.append(os.path.join(path, root, file_))
                    break
        else:
            break
    return pictures


def match_path(path, path_list):
    """ Test if a folder is a sub-folder of another one in the list.

    Arguments
      * path -- path to check
      * path_list -- list of path
    """
    match = False
    #We add a slash at the end.
    if path[-1:] != "/":
        path += "/"
    for entry in path_list:
        #We add a slash at the end.
        if entry[-1:] != "/":
            entry += "/"
        if re.match(r"^" + entry + ".*", path):
            if path != entry:
                match = True
                break
    return match


def gvfs_uri_to_path(uri):
    """Returns local file path from gvfs URI

    Arguments:
    uri -- the gvfs URI
    """
    if not re.match(r"^[a-zA-Z0-9_-]+://", uri):
        return uri
    gvfs = Gio.Vfs.get_default()
    return gvfs.get_file_for_uri(uri).get_path()


if __name__ == "__main__":
    #If we have 2 args
    if len(sys.argv) == 3:
        INPUT_FOLDER = gvfs_uri_to_path(sys.argv[1])
        OUTPUT_FILE = gvfs_uri_to_path(sys.argv[2])
    else:
        #Display informations and usage
        print("Cover thumbnailer - %s" % __doc__)
        print("Version: %s" % __version__)
        print(__copyright__)
        sys.exit(1)

    #If input path does not exists
    if not os.path.isdir(INPUT_FOLDER):
        print("E: [%s:__main__] '%s' is not a directory" % (__file__, INPUT_FOLDER))
        sys.exit(2)

    #Load configuration
    CONF = Conf()

    #Ignored folders
    if match_path(INPUT_FOLDER, CONF['ignored_paths']) \
    and not match_path(INPUT_FOLDER, CONF['neverignored_paths']):
        sys.exit(0)

    #Folders whose name starts with a dot
    elif CONF['ignored_dotted'] and re.match(r".*/\..*", INPUT_FOLDER):
        sys.exit(0)

    #Music folders
    elif CONF['music_enabled'] and match_path(INPUT_FOLDER, CONF['music_paths']):
        covers = search_cover(INPUT_FOLDER)
        if len(covers) == 0:
            covers = search_pictures(INPUT_FOLDER)
            if len(covers) == 0:
                covers = search_pictures_recursiv(INPUT_FOLDER)
                if len(covers) == 0 and not CONF['music_keepdefaulticon']:
                    covers = [CONF['music_defaultimg']]
        if len(covers) > 0:
            if len(covers) == 1 or not CONF['music_makemosaic']:
                thumbnail = Thumb([covers[0], CONF['music_defaultimg']])
                thumbnail.music_thumbnail(
                        CONF['music_bg'],
                        CONF['music_fg'],
                        CONF['music_cropimg']
                        )
                thumbnail.save_thumb(OUTPUT_FILE, "PNG")
            else:
                thumbnail = Thumb(covers)
                thumbnail.music_thumbnail_mosaic(
                        CONF['music_bg'],
                        CONF['music_fg'],
                        CONF['music_cropimg']
                        )
                thumbnail.save_thumb(OUTPUT_FILE, "PNG")
        elif not CONF['music_keepdefaulticon']:
            thumbnail = Thumb([CONF['music_defaultimg']])
            thumbnail.music_thumbnail(
                    CONF['music_bg'],
                    CONF['music_fg'],
                    CONF['music_cropimg']
                    )
            thumbnail.save_thumb(OUTPUT_FILE, "PNG")

    #Picture folders
    elif CONF['pictures_enabled'] and match_path(INPUT_FOLDER, CONF['pictures_paths']):
        picture_list = search_cover(INPUT_FOLDER)
        if len(picture_list) == 0:
            picture_list = search_pictures(INPUT_FOLDER)
            if len(picture_list) == 0:
                picture_list = search_pictures_recursiv(INPUT_FOLDER)
        thumbnail = Thumb(picture_list)
        thumbnail.pictures_thumbnail(
                CONF['pictures_bg'],
                CONF['pictures_fg'],
                CONF['pictures_maxthumbs']
                )
        thumbnail.save_thumb(OUTPUT_FILE, "PNG")

    #Other folders
    elif CONF['other_enabled']:
        covers = search_cover(INPUT_FOLDER)
        if len(covers) == 1:
            thumbnail = Thumb(covers)
            thumbnail.other_thumbnail(CONF['other_fg'])
            thumbnail.save_thumb(OUTPUT_FILE, "PNG")


