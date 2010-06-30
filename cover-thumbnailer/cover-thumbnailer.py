#!/usr/bin/python
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
## Copyright (C) 2009 - 2010  Fabien Loison (flo@flogisoft.com)           ##
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
## WEB SITE : http://software.flogisoft.com/cover-thumbnailer/            ##
##                                                                       ##
#########################################################################


"""Generates thumbnails for nautilus' folders.

Cover thumbnailer generates thumbnail that will be displayed instead of the
default folder icons. It has a specific presentation for music and pictures
folders, and a generic one for other folders.

Usage:
    cover-thumbnailer <directory's path> <output thumbnail's path>
"""

__author__ = "Fabien Loison <flo@flogisoft.com>"
__version__ = "0.8"


import Image, urllib, os.path, sys, re


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
        self['music_paths'] = []
        self['music_defaultimg'] = os.path.join(BASE_PATH, "music_default.png")
        self['music_fg'] = os.path.join(BASE_PATH, "music_fg.png")
        self['music_bg'] = os.path.join(BASE_PATH, "music_bg.png")
        #Pictures
        self['pictures_enabled'] = True
        self['pictures_keepdefaulticon'] = False
        self['pictures_usegnomefolder'] = True
        self['pictures_paths'] = []
        self['pictures_defaultimg'] = os.path.join(BASE_PATH, "pictures_default.png")
        self['pictures_fg'] = os.path.join(BASE_PATH, "pictures_fg.png")
        self['pictures_bg'] = os.path.join(BASE_PATH, "pictures_bg.png")
        #Other
        self['other_enabled'] = True
        self['other_fg'] = os.path.join(BASE_PATH, 'other_fg.png')
        #Ignored
        self['ignored_dotted'] = False
        self['ignored_paths'] = []
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
        self.import_gnome_conf()
        self.import_user_conf()

    def import_gnome_conf(self):
        """ Import user folders from GNOME configuration file. """
        if os.path.isfile(self.user_gnomeconf):
            gnome_conf_file = open(self.user_gnomeconf, 'r')
            for line in gnome_conf_file:
                if re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line):
                    match = re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line)
                    path = match.group(1).replace('$HOME', self.user_homedir)
                    #If path == user home dir, don't use it, it's probably a misconfiguration !
                    if not os.path.samefile(path, self.user_homedir):
                        self['music_paths'].append(path)
                elif re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line):
                    match = re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line)
                    path = match.group(1).replace('$HOME', self.user_homedir)
                    #If path == user home dir, don't use it, it's probably a misconfiguration !
                    if not os.path.samefile(path, self.user_homedir):
                        self['pictures_paths'].append(path)
            gnome_conf_file.close()
        else:
            print("W: [%s:Conf.import_gnome_conf] Can't find `user-dirs.dirs' file." % __file__)

    def import_user_conf(self):
        """ Import user configuration file. """
        if os.path.isfile(self.user_conf):
            current_section = "unknown"
            user_conf_file = open(self.user_conf, 'r')
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
    def __init__(self, img_path):
        """The constructor.

        Argument:
            * img_path -- The path of the picture to thumbnail
        """
        self.img = Image.open(img_path).convert('RGBA')
        self.thumb = None

    def create_thumb(self, size=128):
        """ Make a squared thumbnail.

        Croups the picture if necessaries and makes a thumbnail with it.

        Keyword argument:
            * size -- the size of the thumbnail (in pixels).

        NOTE: the size shouldn't be greater than 128 px for a standard
              freedesktop thumbnail.
        """
        width = self.img.size[0]
        height = self.img.size[1]
        if width > height:
            left = int((width - height)/2)
            upper = 0
            right = height + left
            lower = height
        else:
            left = 0
            upper = int((height - width)/2)
            right = width
            lower = width + upper
        self.thumb = self.img.crop((left, upper, right, lower))
        self.thumb.thumbnail((size, size), Image.ANTIALIAS)

    def add_decoration(self, fg_picture):
        """ Add decoration for "other" folders.

        The foreground picture is added at the bottom-left corner.

        Argument:
            * fg_picture -- the foreground picture to add (Must be a rgba png!)
        """
        if os.path.isfile(fg_picture):
            fg = Image.open(fg_picture).convert('RGBA')
            y = self.thumb.size[1] - fg.size[1]
            self.thumb.paste(fg, (0, y), fg)

    def add_music_decoration(self, bg_picture, fg_picture=None):
        """ Add decoration for music folders.

        Argument:
            * bg_picture -- the background picture (Must be a rgba png!)
        Keyword argument:
            * fg_picture -- the foreground picture (Must be a rgba png!)
        """
        if os.path.isfile(bg_picture):
            bg = Image.open(bg_picture)
            x = bg.size[0] - self.thumb.size[0]
            bg.paste(self.thumb, (x, 0), self.thumb)
            self.thumb = bg
        if os.path.isfile(fg_picture):
            fg = Image.open(fg_picture).convert('RGBA')
            self.thumb.paste(fg, (0, 0), fg)

    def add_pictures_decoration(self, pictures, fg_picture=None):
        """ Add decoration for pictures folder.

        Argument:
            * picture -- a list with at least the path of one picture
        Keyword argument:
            * fg_picture -- the foreground picture (Must be a rgba png!)
        """
        if len(pictures) == 1:
            #PIC0
            try:
                pic0 = Image.open(pictures[0]).convert('RGBA')
                #Optimisation with resempling : don't resemple when rotate big
                #pictures (useless and verry slow)
                if pic0.size[0] <= 120 and pic0.size[1] <= 120:   # <= 120x120
                    pic0 = pic0.rotate(-10, resample=Image.BICUBIC, expand=1)
                elif pic0.size[0] <= 256 and pic0.size[1] <= 256: # <= 256x256
                    pic0 = pic0.rotate(-10, resample=Image.BILINEAR, expand=1)
                    pic0.thumbnail((120, 120), Image.ANTIALIAS)
                else:                                             # > 256x256
                    pic0 = pic0.rotate(-10, resample=Image.NONE, expand=1)
                    pic0.thumbnail((120, 120), Image.ANTIALIAS)
                x = (self.thumb.size[0] - pic0.size[0]) / 2
                y = (self.thumb.size[1] - pic0.size[1]) / 2
                self.thumb.paste(pic0, (x, y), pic0)
            except IOError:
                print "E: Can't open '"+pictures[0]+"'."
        elif len(pictures) == 2:
            #PIC0
            try:
                pic0 = Image.open(pictures[0]).convert('RGBA')
                #Optimisation with resempling : don't resemple when rotate big
                #pictures (useless and verry slow)
                if pic0.size[0] <= 105 and pic0.size[1] <= 70:    # <= 105x70
                    pic0 = pic0.rotate(3, resample=Image.BICUBIC, expand=1)
                elif pic0.size[0] <= 256 and pic0.size[1] <= 256: # <= 256x256
                    pic0 = pic0.rotate(3, resample=Image.BILINEAR, expand=1)
                    pic0.thumbnail((105, 70), Image.ANTIALIAS)
                else:                                             # > 256x256
                    pic0 = pic0.rotate(3, resample=Image.NONE, expand=1)
                    pic0.thumbnail((105, 70), Image.ANTIALIAS)
                self.thumb.paste(pic0, (10, 5), pic0)
            except IOError:
                print "E: Can't open '"+pictures[0]+"'."
            #PIC1
            try:
                pic1 = Image.open(pictures[1]).convert('RGBA')
                #Optimisation with resempling : don't resemple when rotate big
                #pictures (useless and verry slow)
                if pic1.size[0] <= 105 and pic1.size[1] <= 70:    # <= 105x70
                    pic1 = pic1.rotate(-5, resample=Image.BICUBIC, expand=1)
                elif pic1.size[0] <= 256 and pic1.size[1] <= 256: # <= 256x256
                    pic1 = pic1.rotate(-5, resample=Image.BILINEAR, expand=1)
                    pic1.thumbnail((105, 70), Image.ANTIALIAS)
                else:                                             # > 256x256
                    pic1 = pic1.rotate(-5, resample=Image.NONE, expand=1)
                    pic1.thumbnail((105, 70), Image.ANTIALIAS)
                x = self.thumb.size[0] - pic1.size[0] - 5
                y = self.thumb.size[1] - pic1.size[1] - 5
                self.thumb.paste(pic1, (x, y), pic1)
            except IOError:
                print "E: Can't open '"+pictures[1]+"'."
        elif len(pictures) >= 3:
            #PIC0
            try:
                pic0 = Image.open(pictures[0]).convert('RGBA')
                pic0.thumbnail((49, 56), Image.ANTIALIAS)
                self.thumb.paste(pic0, (20, 5), pic0)
            except IOError:
                print "E: Can't open '"+pictures[0]+"'."
                pic0 = Image.new('RGBA', (1, 1))
            #PIC1
            try:
                pic1 = Image.open(pictures[1]).convert('RGBA')
                pic1.thumbnail((49, 56), Image.ANTIALIAS)
                x = self.thumb.size[0] - pic1.size[0] - 5
                self.thumb.paste(pic1, (x, 5), pic1)
            except IOError:
                print "E: Can't open '"+pictures[1]+"'."
                pic1 = Image.new('RGBA', (1, 1))
            #PIC2
            try:
                pic2 = Image.open(pictures[2]).convert('RGBA')
                h = self.thumb.size[1] - max(pic0.size[1], pic1.size[1]) - 15
                pic2.thumbnail((103, h), Image.ANTIALIAS)
                x = (self.thumb.size[0] - 15 - pic2.size[0]) / 2 +15
                y = self.thumb.size[1] - pic2.size[1] - 5
                self.thumb.paste(pic2, (x, y), pic2)
            except IOError:
                print "E: Can't open '"+pictures[2]+"'."
        if os.path.isfile(fg_picture):
            fg = Image.open(fg_picture)
            self.thumb.paste(fg, (0, 0), fg)

    def save_thumb(self, output_path, format='PNG'):
        """ Save the thumbnail in a file.

        Argument:
            * output_path -- the output path for the thumbnail
        Keyword argument:
            * format -- the format of the picture (PNG, JPEG,...)

        NOTE : The output format must be a PNG for a standard
               freedesktop thumbnail
        """
        self.thumb.save(output_path, format)


def get_cover_path(folder_path, default_pic=None):
    """ Finds the name of the cover file.

    Search for files like cover.png, Folder.jpg,... in the folder.
    If a cover file is found, returns the path of the cover file, else
    returns the default picture, if given.

    Argument:
        * directory_path -- the folder path
    Keyword argument:
        * default_pic -- the default picture (if we need one)
    """
    cover_path = None
    for cover in COVER_FILES:
        if os.path.isfile(os.path.join(folder_path, cover)):
            cover_path = os.path.join(folder_path, cover)
            break
    if cover_path == None and default_pic != None:
        if os.path.isfile(default_pic):
            cover_path = default_pic
    return cover_path


def get_music_cover_path(folder_path, default_pic=None):
    """ Finds the name of the cover file for music directories

    Argument:
        * directory_path -- the path of the directory
    Keyword argument:
        * default_pic -- the default picture (if we need one)
    """
    #Search for a file like "cover.png" or "folder.jpg"
    cover_path = get_cover_path(folder_path) 

    if cover_path == None:
        #Search for any picture in the directory 
        files = os.listdir(folder_path)
        picture = None
        for file in files:
            if PICTURES_EXT.count(file[-4:]):
                picture = os.path.join(folder_path, file)

        #Search for any picture in subdirectory
        if picture == None:
            files = None
            for root, dirs, files in os.walk(folder_path):
                if picture == None:
                    for file in files:
                        if file[-4:] in PICTURES_EXT:
                            picture = os.path.join(folder_path, root, file)
                            break
                else:
                    break

        #Select default picture if no picture found
        if picture != None:
            cover_path = picture
        else:
            cover_path = default_pic
    return cover_path


def match_path(path, path_list):
    """ Search if a folder is a sub-folder of another one.

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


if __name__ == "__main__":
    #If we have 2 args
    if len(sys.argv) == 3:
        input_folder = urllib.url2pathname(sys.argv[1]).replace("file://", "")
        output_file = urllib.url2pathname(sys.argv[2]).replace("file://", "")

        CONF = Conf()

        #If it's an ignored folder
        if match_path(input_folder, CONF['ignored_paths']):
            sys.exit(42)

        #If it's a dotted folder
        elif CONF['ignored_dotted'] and re.match(".*/\..*", input_folder):
            sys.exit(42)

        #If it's a music folder
        elif match_path(input_folder, CONF['music_paths']) and CONF['music_enabled']:
            if CONF['music_keepdefaulticon']:
                cover_path = get_music_cover_path(input_folder)
            else:
                cover_path = get_music_cover_path(input_folder, CONF['music_defaultimg'])
            if cover_path != None:
                pic = Thumb(cover_path)
                pic.create_thumb(110)
                pic.add_music_decoration(CONF['music_bg'], CONF['music_fg'])
                pic.save_thumb(output_file, 'PNG')
            elif not CONF['music_keepdefaulticon']:
                print "E: [%s:main] Can't find any cover file and default cover file." % __file__

        #If it's a pictures folder
        elif match_path(input_folder, CONF['pictures_paths']) and CONF['pictures_enabled']:
            #Search for a cover.png, folder.jpg,...
            cover_path = get_cover_path(input_folder)
            if cover_path != None:
                pictures = [cover_path]
            else:
            #List pictures
                files = os.listdir(input_folder)
                pictures = []
                for file_ in files:
                    if PICTURES_EXT.count(file_[-4:]):
                        pictures.append(os.path.join(input_folder, file_))
                    if len(pictures) >= 3:
                        break
            #Create thumbnail
            if len(pictures) > 0:
                pic = Thumb(CONF['pictures_bg'])
                pic.create_thumb(128)
                pic.add_pictures_decoration(pictures, CONF['pictures_fg'])
                pic.save_thumb(output_file, 'PNG')
            elif not CONF['pictures_keepdefaulticon']:
                pic = Thumb(CONF['pictures_defaultimg'])
                pic.create_thumb(128)
                pic.save_thumb(output_file, 'PNG')


        #If it's an other folder
        else:
            cover_path = get_cover_path(input_folder)
            if cover_path != None and CONF['other_enabled']:
                pic = Thumb(cover_path)
                pic.create_thumb(128)
                pic.add_decoration(CONF['other_fg'])
                pic.save_thumb(output_file, "PNG")
            else :
                sys.exit(42)

    else:
        print "Cover thumbnailer - " + __doc__
        sys.exit(1)


