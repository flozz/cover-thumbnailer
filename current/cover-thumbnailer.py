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
## Copyright (C) 2009  Fabien Loison (flo@flogisoft.com)                  ##
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
## VERSION : 0.7 (Mon, 04 Jan 2010 12:12:54 +0100)                        ##
## WEB SITE : http://software.flogisoft.com/cover-thumbnailer/            ##
##                                                                       ##
#########################################################################


import Image, urllib, os.path, sys, re


#==================================================================== CONF ====
#Base path for cover thumbnailer's pictures
BASE_PATH = '/usr/share/cover-thumbnailer/'

#Cover files list
COVER_FILES = ['cover.png', 'cover.jpg', '.cover.png', '.cover.jpg',
		'Cover.png', 'Cover.jpg', '.Cover.png', '.Cover.jpg',
		'folder.png', 'folder.jpg', '.folder.png', '.folder.jpg',
		'Folder.png', 'Folder.jpg', '.Folder.png', '.Folder.jpg']

#Supported picture ext (ALWAY LAST 4 CHARS !!)
PICTURES_EXT = ['.jpg', '.JPG', 'jpeg', 'JPEG',
		'.png', '.PNG', #None interlaced
		'.gif', '.GIF',
		'.bmp', '.BMP', #Window ans OS/2 bitmap
		'.ico', '.ICO', #Windows icon format
		'.tga', '.TGA', #Truevision Targa format
		'.tif', '.TIF', 'tiff', 'TIFF', #Adobe Tagged Image File Format
		'.psd', '.PSD', #Adobe Photosop format (only version 2.5 and 3.0)
		]

#==============================================================================


class Conf(object):
	'''
	Import configuration from config files.
	'''
	def __init__(self):
		#music
		self.music_paths = []
		self.music_default = BASE_PATH + 'music_default.png'
		self.music_fg = BASE_PATH + 'music_fg.png'
		self.music_bg = BASE_PATH + 'music_bg.png'
		#pictures
		self.pictures_paths = []
		self.pictures_default = BASE_PATH + 'pictures_default.png'
		self.pictures_fg = BASE_PATH + 'pictures_fg.png'
		self.pictures_bg = BASE_PATH + 'pictures_bg.png'
		#other
		self.other_fg = BASE_PATH + 'other_fg.png'
		#ignored
		self.ignored_paths = ['/tmp']
		self.ignored_dotted = False
		#global
		self.user_homedir = os.environ.get('HOME')
		self.user_gnomeconf = self.user_homedir + '/.config/user-dirs.dirs'
		self.user_conf = self.user_homedir + '/.cover-thumbnailer/cover-thumbnailer.conf'

		#get conf
		self.import_gnome_conf()
		self.import_user_conf()
		self.get_pictures_path()

	def import_gnome_conf(self):
		'''
		Import user folders from GNOME config file.
		'''
		if os.path.isfile(self.user_gnomeconf):
			file = open(self.user_gnomeconf, 'r')
			for line in file:
				if re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line):
					self.music_paths.append(re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line).group(1).replace('$HOME', self.user_homedir))
				elif re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line):
					self.pictures_paths.append(re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line).group(1).replace('$HOME', self.user_homedir))
			file.close()
		else:
			print "W: ["+__file__+":get_music_path] Can't find `user-dirs.dirs' file."
	
	def import_user_conf(self):
		'''
		Import user configuration file.
		'''
		if os.path.isfile(self.user_conf):
			current_section = None
			file = open(self.user_conf, 'r')
			#Read config
			for line in file:
				line = line.replace('\n', '')
				if re.match(r'\s*#.*', line):
					continue
				elif re.match(r'\s*\[music\]\s*', line.lower()):    #[music]
					current_section = 'music'
				elif re.match(r'\s*\[pictures\]\s*', line.lower()): #[pictures]
					current_section = 'pictures'
				elif re.match(r'\s*\[ignored\]\s*', line.lower()):  #[ignored]
					current_section = 'ignored'
				elif re.match(r'\s*(path|PATH)\s*=\s*"(.*)"\s*', line): #path=
					if current_section == 'music':
						self.music_paths.append(re.match(r'\s*(path|PATH)\s*=\s*"(.*)"\s*', line).group(2))
					elif current_section == 'pictures':
						self.pictures_paths.append(re.match(r'\s*(path|PATH)\s*=\s*"(.*)"\s*', line).group(2))
					elif current_section == 'ignored':
						self.ignored_paths.append(re.match(r'\s*(path|PATH)\s*=\s*"(.*)"\s*', line).group(2))
				elif re.match(r'\s*dotted\s*=\s*(yes|no|true|false|1|0)\s*', line.lower()): #doted=
					if current_section == 'ignored':
						value = re.match(r'\s*dotted\s*=\s*(yes|no|true|false|1|0)\s*', line.lower()).group(1)
						if value in ['yes', 'true', '1']:
							self.ignored_dotted = True
						elif value in ['no', 'false', '0']:
							self.ignored_dotted = False
			file.close()

			#Replace all ~ by user home dir
			for i in range(0, len(self.music_paths)):
				if self.music_paths[i][0] == '~':
					self.music_paths[i] = self.user_homedir+self.music_paths[i][1:]
			for i in range(0, len(self.pictures_paths)):
				if self.pictures_paths[i][0] == '~':
					self.pictures_paths[i] = self.user_homedir+self.pictures_paths[i][1:]
			for i in range(0, len(self.ignored_paths)):
				if self.ignored_paths[i][0] == '~':
					self.ignored_paths[i] = self.user_homedir+self.ignored_paths[i][1:]
		
	def get_pictures_path(self):
		'''
		Search if user have put some custom pictures in his home.
		'''
		#Music
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/music_default.png'):
			self.music_default = self.user_homedir + '/.cover-thumbnailer/music_default.png'
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/music_fg.png'):
			self.music_fg = self.user_homedir + '/.cover-thumbnailer/music_fg.png'
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/music_bg.png'):
			self.music_bg = self.user_homedir + '/.cover-thumbnailer/music_bg.png'
		#Pictures
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/pictures_default.png'):
			self.pictures_default = self.user_homedir + '/.cover-thumbnailer/pictures_default.png'
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/pictures_fg.png'):
			self.pictures_fg = self.user_homedir + '/.cover-thumbnailer/pictures_fg.png'
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/pictures_bg.png'):
			self.pictures_bg = self.user_homedir + '/.cover-thumbnailer/pictures_bg.png'
		#other
		if os.path.isfile(self.user_homedir + '/.cover-thumbnailer/other_fg.png'):
			self.other_fg = self.user_homedir + '/.cover-thumbnailer/other_fg.png'



class Thumb(object):
	'''
	Create thumnails
	@img_path : The path of the picture to thumnail
	'''
	def __init__(self, img_path):
		self.img = Image.open(img_path).convert('RGBA')
		self.thumb = None

	def create_thumb(self, size=96):
		'''
		create a square thumbnail
		@size : the size of the thumbnail (in pixels). NOTE: Shouldn't be
		        greater than 128 px for a standard freedesktop thumbnail.
		'''
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
		'''
		Add decoration for most folders. The foreground picture is added
		in the bottom-left corner.
		@fg_picture : The foreground picture to add (Must be a rgba png !)
		'''
		if os.path.isfile(fg_picture): 
			fg = Image.open(fg_picture).convert('RGBA')
			y = self.thumb.size[1] - fg.size[1]
			self.thumb.paste(fg, (0,y), fg)

	def add_music_decoration(self, bg_picture, fg_picture=None):
		'''
		Add decoration for music folders.
		@bg_picture : The background picture (Must be a rgba png !)
		@fg_picture : the foreground picture (Must be a rgba png !)
		'''
		if os.path.isfile(bg_picture):
			bg = Image.open(bg_picture)
			x = bg.size[0] - self.thumb.size[0]
			bg.paste(self.thumb, (x,0), self.thumb)
			self.thumb = bg
		if os.path.isfile(fg_picture): 
			fg = Image.open(fg_picture).convert('RGBA')
			self.thumb.paste(fg, (0,0), fg)

	def add_pictures_decoration(self, pictures, fg_picture=None):
		'''
		Add decoration for pictures folder
		@picture : a list with at least the path of one picture
		@fg_picture : the foreground picture (Must be a rgba png !)
		'''
		if len(pictures) == 1:
			#PIC0
			try:
				pic0 = Image.open(pictures[0]).convert('RGBA')
				pic0 = pic0.rotate(-10, resample=Image.ANTIALIAS, expand=1)
				pic0.thumbnail((120, 120), Image.ANTIALIAS)
				x = (self.thumb.size[0] - pic0.size[0]) / 2
				y = (self.thumb.size[1] - pic0.size[1]) / 2
				self.thumb.paste(pic0, (x,y), pic0)
			except IOError:
				print "E: Can't open '"+pictures[0]+"'."
		elif len(pictures) == 2:
			#PIC0
			try:
				pic0 = Image.open(pictures[0]).convert('RGBA')
				pic0 = pic0.rotate(3, resample=Image.ANTIALIAS, expand=1)
				pic0.thumbnail((105, 70), Image.ANTIALIAS)
				self.thumb.paste(pic0, (10,5), pic0)
			except IOError:
				print "E: Can't open '"+pictures[0]+"'."
			#PIC1
			try:
				pic1 = Image.open(pictures[1]).convert('RGBA')
				pic1 = pic1.rotate(-5, resample=Image.ANTIALIAS, expand=1)
				pic1.thumbnail((105, 70), Image.ANTIALIAS)
				x = self.thumb.size[0] - pic1.size[0] - 5
				y = self.thumb.size[1] - pic1.size[1] - 5
				self.thumb.paste(pic1, (x,y), pic1)
			except IOError:
				print "E: Can't open '"+pictures[1]+"'."
		elif len(pictures) >= 3:
			#PIC0
			try:
				pic0 = Image.open(pictures[0]).convert('RGBA')
				pic0.thumbnail((49, 56), Image.ANTIALIAS)
				self.thumb.paste(pic0, (20,5), pic0)
			except IOError:
				print "E: Can't open '"+pictures[0]+"'."
				pic0 = Image.new('RGBA', (1,1))
			#PIC1
			try:
				pic1 = Image.open(pictures[1]).convert('RGBA')
				pic1.thumbnail((49, 56), Image.ANTIALIAS)
				x = self.thumb.size[0] - pic1.size[0] - 5
				self.thumb.paste(pic1, (x,5), pic1)
			except IOError:
				print "E: Can't open '"+pictures[1]+"'."
				pic1 = Image.new('RGBA', (1,1))
			#PIC2
			try:
				pic2 = Image.open(pictures[2]).convert('RGBA')
				h = self.thumb.size[1] - max(pic0.size[1],pic1.size[1]) - 15
				pic2.thumbnail((103,h), Image.ANTIALIAS)
				x = (self.thumb.size[0] - 15 - pic2.size[0]) / 2 +15
				y = self.thumb.size[1] - pic2.size[1] - 5
				self.thumb.paste(pic2, (x,y), pic2)
			except IOError:
				print "E: Can't open '"+pictures[2]+"'."
		if os.path.isfile(fg_picture):
			fg = Image.open(fg_picture)
			self.thumb.paste(fg, (0,0), fg)

	def save_thumb(self, output, format='PNG'):
		'''
		Save the thumbnail in a file
		@output : the output path for the thumbnail
		@format : the format of the picture (Must be a PNG for a standard
		          freedesktop thumbnail !)
		'''
		self.thumb.save(output, format)


def get_cover_path(folder_path, default_pic=None):
	'''
	Find the name of the cover file (Search for files like cover.png,...)
	@directory_path : the path of the directory
	@default_pic : the default picture (if we need one)
	'''
	cover_path = None
	for cover in COVER_FILES:
		if os.path.isfile(folder_path+'/'+cover):
			cover_path = folder_path+'/'+cover
			break
	if cover_path == None and default_pic != None:
		if os.path.isfile(default_pic):
			cover_path = default_pic
	return cover_path


def get_music_cover_path(folder_path, default_pic=None):
	'''
	Find the name of the cover file
	@directory_path : the path of the directory
	@default_pic : the default picture (if we need one)
	'''
	#Search for a file like "cover.png" or "folder.jpg"
	cover_path = get_cover_path(folder_path) 

	if cover_path == None:
		#Search for any picture in the directory 
		files = os.listdir(input)
		picture = None
		for file in files:
			if PICTURES_EXT.count(file[-4:]):
				picture = os.path.join(input, file)

		#Search for any picture in subdirectory
		if picture == None:
			files = None
			for root, dirs, files in os.walk(folder_path): 
				if picture == None:
					for file in files: 
						if file[-4:] in PICTURES_EXT:
							picture = os.path.join(input, root, file)
							break
				else:
					break

		#Select default picture if no picture found
		if picture != None:
			cover_path = picture
		else:
			cover_path = default_pic
	return cover_path


def match_path(path, list):
	'''
	Search if path is a sub-folder of a path in list.
	@path : path to check
	@list : list of path
	'''
	match = False
	#We add a slash at the end.
	if path[-1:] != '/':
		path += '/'
	for entry in list:
		#We add a slash at the end.
		if entry[-1:] != '/':
			entry += '/'
		if re.match(r'^'+entry+'.*', path):
			if path != entry:
				match = True
				break
	return match 


if __name__ == "__main__":
	#If we have 2 args
	if len(sys.argv) == 3:
		input = urllib.url2pathname(sys.argv[1]).replace('file://', '')
		output = urllib.url2pathname(sys.argv[2]).replace('file://', '')

		conf = Conf()

		#If it's an ignored folder
		if match_path(input, conf.ignored_paths):
			sys.exit(42)

		#If it's a dotted folder
		elif conf.ignored_dotted and re.match('.*/\..*', input):
			sys.exit(42)
		
		#If it's the music folder
		elif match_path(input, conf.music_paths):
			cover_path = get_music_cover_path(input, conf.music_default)
			if cover_path != None:
				pic = Thumb(cover_path)
				pic.create_thumb(110)
				pic.add_music_decoration(conf.music_bg, conf.music_fg)
				pic.save_thumb(output, 'PNG')
			else:
				print "E: ["+__file__+":main] Can't find any cover file and default cover file."

		#If it's the pictures folder
		elif match_path(input, conf.pictures_paths):
			#Search for a cover.png, folder.jpg,...
			cover_path = get_cover_path(input)
			if cover_path != None:
				pictures = [cover_path]
			else:
			#List pictures
				files = os.listdir(input)
				pictures = []
				for file in files:
					if PICTURES_EXT.count(file[-4:]):
						pictures.append(os.path.join(input, file))
					if len(pictures) >= 3:
						break
			#Create thumbnail
			if len(pictures) > 0:
				pic = Thumb(conf.pictures_bg)
				pic.create_thumb(128)
				pic.add_pictures_decoration(pictures, conf.pictures_fg)
			else:
				pic = Thumb(conf.pictures_default)
				pic.create_thumb(128)
			pic.save_thumb(output, 'PNG')

		#If it's an other folder
		else:
			cover_path = get_cover_path(input)
			if cover_path != None:
				pic = Thumb(cover_path)
				pic.create_thumb(128)
				pic.add_decoration(conf.other_fg)
				pic.save_thumb(output, 'PNG')
			else :
				sys.exit(42)

	else:
		print "E: ["+__file__+":main] Need two args : the input directory and the output image file."
		sys.exit(1)


