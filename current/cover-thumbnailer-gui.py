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
## Cover thumbnailer GUI                                                  ##
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
## VERSION : 0.7 (Mon, 28 Dec 2009 00:14:22 +0100)                        ##
## WEB SITE : http://software.flogisoft.com/cover-thumbnailer/            ##
##                                                                       ##
#########################################################################

__appname__ = 'cover-thumbnailer-gui'

import pygtk
pygtk.require("2.0")
import gtk

import gettext
gettext.install(__appname__)

import os, re, shutil


#Base path
BASE_PATH = '/usr/share/cover-thumbnailer/'
#BASE_PATH = './share/' #FIXME : dev


class Conf(object):
	'''
	Import configuration from config files.
	'''
	def __init__(self):
		#music
		self.music_paths = []
		self.gnome_music_path = _('<Empty>')
		#pictures
		self.pictures_paths = []
		self.gnome_pictures_path = _('<Empty>')
		#ignored
		self.ignored_paths = []
		self.ignored_dotted = False
		#global
		self.user_homedir = os.environ.get('HOME')
		self.user_gnomeconf = self.user_homedir + '/.config/user-dirs.dirs'
		self.user_conf = self.user_homedir + '/.cover-thumbnailer/cover-thumbnailer.conf'

		#get conf
		self.import_gnome_conf()
		self.import_user_conf()

	def import_gnome_conf(self):
		'''
		Import user folders from GNOME config file.
		'''
		if os.path.isfile(self.user_gnomeconf):
			file = open(self.user_gnomeconf, 'r')
			for line in file:
				if re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line):
					self.gnome_music_path = re.match(r'.*?XDG_MUSIC_DIR.*?=.*?"(.*)".*?', line).group(1).replace('$HOME', self.user_homedir)
				elif re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line):
					self.gnome_pictures_path = re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line).group(1).replace('$HOME', self.user_homedir)
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
				if re.match(r'\s?#.*', line):
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

	def saveConf(self):
		ctconfpath = self.user_homedir + '/.cover-thumbnailer/'
		if not os.path.isdir(ctconfpath):
			os.makedirs(ctconfpath)

		file = open(ctconfpath + 'cover-thumbnailer.conf', 'w')
		file.write('#' + _('Configuration writed by Cover Thumbnailer GUI') + "\n")
		file.write("#" + _('Please edit with caution') + "\n")
		#MUSIC
		file.write("\n[MUSIC]\n")
		if len(self.music_paths) > 0:
			for path in self.music_paths:
				file.write("\tpath = \"" + path + "\"\n")
		#PICTURES
		file.write("\n[PICTURES]\n")
		if len(self.pictures_paths) > 0:
			for path in self.pictures_paths:
				file.write("\tpath = \"" + path + "\"\n")
		#OTHER
		file.write("\n[OTHER]\n")
		#FIXME : Not implemented
		#IGNORED
		#PICTURES
		file.write("\n[IGNORED]\n")
		if self.ignored_dotted:
			file.write("\tdotted = Yes\n")
		else:
			file.write("\tdotted = No\n")
		if len(self.ignored_paths) > 0:
			for path in self.ignored_paths:
				file.write("\tpath = \"" + path + "\"\n")
		#END
		file.write("\n\n")
		file.close()


class MainWin(object):
	def __init__(self):
		win = gtk.Builder()
		win.set_translation_domain(__appname__)
		win.add_from_file(BASE_PATH + 'cover-thumbnailer-gui.glade')

		self.winAbout = win.get_object("winAbout")
		self.winAbout.connect("response", self.on_winAbout_response)

		### MUSIC ###
		#Music path list
		self.trvMusicPathList = win.get_object("trvMusicPathList")
		self.lsstMusicPathList = gtk.ListStore(str)
		self.trvMusicPathList.set_model(self.lsstMusicPathList)
		self.columnMusicPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=False)
		self.trvMusicPathList.append_column(self.columnMusicPathList)
		#MusicRemove button
		self.btnMusicRemove = win.get_object("btnMusicRemove")
		#GNOME music path label
		self.lbMusicGnomeFolder = win.get_object("lbMusicGnomeFolder")

		### PICTURES ###
		#Pictures path list
		self.trvPicturesPathList = win.get_object("trvPicturesPathList")
		self.lsstPicturesPathList = gtk.ListStore(str)
		self.trvPicturesPathList.set_model(self.lsstPicturesPathList)
		self.columnPicturesPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=False)
		self.trvPicturesPathList.append_column(self.columnPicturesPathList)
		#PicturesRemove button
		self.btnPicturesRemove = win.get_object("btnPicturesRemove")
		#GNOME pictures path label
		self.lbPicturesGnomeFolder = win.get_object("lbPicturesGnomeFolder")

		### IGNORED ###
		#Ignored path list
		self.trvIgnoredPathList = win.get_object("trvIgnoredPathList")
		self.lsstIgnoredPathList = gtk.ListStore(str)
		self.trvIgnoredPathList.set_model(self.lsstIgnoredPathList)
		self.columnIgnoredPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=False)
		self.trvIgnoredPathList.append_column(self.columnIgnoredPathList)
		#IgnoredRemove button
		self.btnIgnoredRemove = win.get_object("btnIgnoredRemove")
		#IgnoreHidden checkBox
		self.cbIgnoreHidden = win.get_object("cbIgnoreHidden")

		### FileChooser Dialog ###
		self.fileChooser = win.get_object("filechooserdialog")
		self.fileChooserFor = None

		### ERROR DIALOG file already in list ###
		self.msgdlgErrorPAIL = win.get_object("msgdlgErrorPAIL")

		loadInterface(self) #Put config on the gui
		win.connect_signals(self)

	### WINMAIN ###
	def on_winMain_destroy(self, widget):
		gtk.main_quit()

	def on_btnAbout_clicked(self, widget):
		self.winAbout.show()

	def on_btnCancel_clicked(self, widget):
		gtk.main_quit()

	def on_btnOk_clicked(self, widget):
		conf.saveConf()
		gtk.main_quit()

	def on_btnClearThumbnailCache_clicked(self, widget):
		thumbpath = conf.user_homedir + '/.thumbnails'
		if os.path.isdir(thumbpath):
			shutil.rmtree(thumbpath)

	#~~~ MUSIC ~~~
	def on_btnMusicAdd_clicked(self, widget):
		self.fileChooserFor = 'music'
		self.fileChooser.show()
	
	def on_trvMusicPathList_cursor_changed(self, widget):
		model, iter = widget.get_selection().get_selected()
		if iter != None:
			self.btnMusicRemove.set_sensitive(True)

	def on_btnMusicRemove_clicked(self, widget):
		removePathFromList(self.trvMusicPathList, self.lsstMusicPathList, conf.music_paths)
		self.btnMusicRemove.set_sensitive(False)

	#~~~ PICTURES ~~~
	def on_btnPicturesAdd_clicked(self, widget):
		self.fileChooserFor = 'pictures'
		self.fileChooser.show()

	def on_trvPicturesPathList_cursor_changed(self, widget):
		model, iter = widget.get_selection().get_selected()
		if iter != None:
			self.btnPicturesRemove.set_sensitive(True)

	def on_btnPicturesRemove_clicked(self, widget):
		removePathFromList(self.trvPicturesPathList, self.lsstPicturesPathList, conf.pictures_paths)
		self.btnPicturesRemove.set_sensitive(False)

	#~~~ IGNORED ~~~
	def on_btnIgnoredAdd_clicked(self, widget):
		self.fileChooserFor = 'ignored'
		self.fileChooser.show()

	def on_trvIgnoredPathList_cursor_changed(self, widget):
		model, iter = widget.get_selection().get_selected()
		if iter != None:
			self.btnIgnoredRemove.set_sensitive(True)

	def on_btnIgnoredRemove_clicked(self, widget):
		removePathFromList(self.trvIgnoredPathList, self.lsstIgnoredPathList, conf.ignored_paths)
		self.btnIgnoredRemove.set_sensitive(False)

	def on_cbIgnoreHidden_toggled(self, widget):
		conf.ignored_dotted = self.cbIgnoreHidden.get_active()

	### FILECHOOSER DIALOG ###
	def on_btnFileChooserCancel_clicked(self, widget):
		self.fileChooser.hide()

	def on_btnFileChooserOpen_clicked(self, widget):
		self.fileChooser.hide()
		path = self.fileChooser.get_filename()
		if self.fileChooserFor == 'music':
			addPathToList(self.lsstMusicPathList, path, conf.music_paths)
		elif self.fileChooserFor == 'pictures':
			addPathToList(self.lsstPicturesPathList, path, conf.pictures_paths)
		elif self.fileChooserFor == 'ignored':
			addPathToList(self.lsstIgnoredPathList, path, conf.ignored_paths)
		self.fileChooserFor = None

	def on_filechooserdialog_delete_event(self, widget, response):
		self.fileChooser.hide()
		return True #Don't delete

	### ABOUT DIALOG ###
	def on_winAbout_delete_event(self, widget, event):
		self.winAbout.hide()
		return True #Don't delete

	def on_winAbout_response(self, widget, response):
		if response < 0:
			self.winAbout.hide()
	
	### ERROR DIALOG file already in list ###
	def on_msgdlgErrorPAIL_delete_event(self, widget, event):
		self.msgdlgErrorPAIL.hide()
		return True #Don't delete

	def on_btnErrorPAILClose_clicked(self, widget):
		self.msgdlgErrorPAIL.hide()


def addPathToList(list, path, conflist):
	"""
	@path : string, path to add
	@list : gtkListStore
	@confilst : array
	"""
	if not path in conflist:
		list.append([path])
		conflist.append(path)
	else:
		gui.msgdlgErrorPAIL.show()


def removePathFromList(tree, list, conflist):
	"""
	@tree : gtkTreeView
	@list : gtkListStore
	@confilst : array
	"""
	model, iter = tree.get_selection().get_selected()
	conflist.remove(list.get_value(iter, 0))
	list.remove(iter)


def loadInterface(gui):
	#Music:
	for path in conf.music_paths:
		gui.lsstMusicPathList.append([path])
	gui.lbMusicGnomeFolder.set_text(conf.gnome_music_path)
	#Pictures
	for path in conf.pictures_paths:
		gui.lsstPicturesPathList.append([path])
	gui.lbPicturesGnomeFolder.set_text(conf.gnome_pictures_path)
	#Ignored
	for path in conf.ignored_paths:
		gui.lsstIgnoredPathList.append([path])
	gui.cbIgnoreHidden.set_active(conf.ignored_dotted)


if __name__ == "__main__":
	conf = Conf()
	gui = MainWin()
	gtk.main()

