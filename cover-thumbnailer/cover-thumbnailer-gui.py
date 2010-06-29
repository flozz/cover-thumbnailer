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


"""Configuration GUI for Cover Thumbnailer.

Provides a GUI for easily configuring Cover Thumbnailer.
"""

__author__ = "Fabien Loison <flo@flogisoft.com>"
__version__ = "0.8"
__appname__ = "cover-thumbnailer-gui"

import gtk, pygtk
pygtk.require("2.0")

import gettext
gettext.install(__appname__)

import os, re, shutil, gconf


#Base path
if "DEVEL" in os.environ:
    BASE_PATH = "./share/" #For devel
else:
    BASE_PATH = "/usr/share/cover-thumbnailer/"

#GConf key for enabling/disabling Cover thumbnailer
GCONF_KEY = "/desktop/gnome/thumbnailers/inode@directory/enable"

#GConf key for nautilus thumbnails size
GCONF_KEY_NAUTILUS_THUMB_SIZE = "/apps/nautilus/icon_view/thumbnail_size"


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
        self['music_gnomefolderpath'] = _('<None>')
        #Pictures
        self['pictures_enabled'] = True
        self['pictures_keepdefaulticon'] = False
        self['pictures_usegnomefolder'] = True
        self['pictures_paths'] = []
        self['pictures_gnomefolderpath'] = _('<None>')
        #Other
        self['other_enabled'] = True
        #Ignored
        self['ignored_dotted'] = False
        self['ignored_paths'] = []
        #Global
        self.user_homedir = os.environ.get('HOME')
        self.user_gnomeconf = os.path.join(
                self.user_homedir,
                '.config/user-dirs.dirs'
                )
        self.user_conf = os.path.join(
                self.user_homedir,
                '.cover-thumbnailer/cover-thumbnailer.conf'
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
                    self['music_gnomefolderpath'] = path
                elif re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line):
                    match = re.match(r'.*?XDG_PICTURES_DIR.*?=.*?"(.*)".*?', line)
                    path = match.group(1).replace('$HOME', self.user_homedir)
                    self['pictures_gnomefolderpath'] = path
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

    def save_user_conf(self):
        """ Save configuration file. """
        #Check if output folder exists, else create it
        conf_dir = os.path.join(self.user_homedir, ".cover-thumbnailer")
        if not os.path.isdir(conf_dir):
            try:
                os.makedirs(conf_dir)
            except OSError: #Permission denied
                print("E: [%s:Conf.save_user_conf] Can't write configuration directory (permission denied)" % __file__)
                return
        try:
            user_conf_file = open(self.user_conf, 'w')
            #Warning
            user_conf_file.write('#' + _('Configuration written by Cover Thumbnailer GUI') + "\n")
            user_conf_file.write("#" + _('Please edit with caution') + "\n")
            #Music
            user_conf_file.write("\n[MUSIC]\n")
            user_conf_file.write(self._write_bool("music_enabled"))
            user_conf_file.write(self._write_bool("music_keepdefaulticon"))
            user_conf_file.write(self._write_bool("music_usegnomefolder"))
            user_conf_file.write(self._write_list("music_paths"))
            #Pictures
            user_conf_file.write("\n[PICTURES]\n")
            user_conf_file.write(self._write_bool("pictures_enabled"))
            user_conf_file.write(self._write_bool("pictures_keepdefaulticon"))
            user_conf_file.write(self._write_bool("pictures_usegnomefolder"))
            user_conf_file.write(self._write_list("pictures_paths"))
            #Other
            user_conf_file.write("\n[OTHER]\n")
            user_conf_file.write(self._write_bool("other_enabled"))
            #Ignored
            user_conf_file.write("\n[IGNORED]\n")
            user_conf_file.write(self._write_bool("ignored_dotted"))
            user_conf_file.write(self._write_list("ignored_paths"))
            #End
            user_conf_file.write("\n\n") #I like blank lines at the end :)
        except OSError: #Permission denied
            print("E: [%s:Conf.save_user_conf] Can't write configuration (permission denied)" % __file__)
            return
        except IOError: #Input/Output error
            print("E: [%s:Conf.save_user_conf] Can't write configuration (IO error)" % __file__)
            return
        else:
            user_conf_file.close()

    def _write_bool(self, key):
        """ Return the string to write in config file for boolean key
        
        Argument:
          * key -- the name of the CONF key
        """
        wkey = key.split("_")[1]
        if self[key]:
            value = "Yes"
        else:
            value = "No"
        return "\t%s = %s\n" % (wkey, value)

    def _write_list(self, key):
        """ Return the string to write in config file for list key (path)
        
        Argument:
          * key -- the name of the CONF key
        """
        result = ""
        for value in self[key]:
            result += "\tpath = \"%s\"\n" % value
        return result


class MainWin(object):
    """ The configuration GUI """
    def __init__(self):
        win = gtk.Builder()
        win.set_translation_domain(__appname__)
        #FIXME: GtkWarning: Ignoring the separator setting (wtf ?!)
        win.add_from_file(BASE_PATH + 'cover-thumbnailer-gui.glade')

        self.winAbout = win.get_object("winAbout")
        self.winAbout.connect("response", self.on_winAbout_response)

        ### MUSIC ###
        #Music path list
        self.trvMusicPathList = win.get_object("trvMusicPathList")
        self.lsstMusicPathList = gtk.ListStore(str)
        self.trvMusicPathList.set_model(self.lsstMusicPathList)
        self.columnMusicPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=0)
        self.trvMusicPathList.append_column(self.columnMusicPathList)
        #MusicRemove button
        self.btnMusicRemove = win.get_object("btnMusicRemove")
        #GNOME music folder checkBox
        self.cb_useGnomeMusic = win.get_object("cb_useGnomeMusic")
        #Enable checkBox
        self.cbMusicEnable = win.get_object("cbMusicEnable")
        #KeepIcon checkBox
        self.cbMusicKeepFIcon = win.get_object("cbMusicKeepFIcon")

        ### PICTURES ###
        #Pictures path list
        self.trvPicturesPathList = win.get_object("trvPicturesPathList")
        self.lsstPicturesPathList = gtk.ListStore(str)
        self.trvPicturesPathList.set_model(self.lsstPicturesPathList)
        self.columnPicturesPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=0)
        self.trvPicturesPathList.append_column(self.columnPicturesPathList)
        #PicturesRemove button
        self.btnPicturesRemove = win.get_object("btnPicturesRemove")
        #GNOME picture folder checkBox
        self.cb_useGnomePictures = win.get_object("cb_useGnomePictures")
        #Enable checkBox
        self.cbPicturesEnable = win.get_object("cbPicturesEnable")
        #KeepIcon checkBox
        self.cbPicturesKeepFIcon = win.get_object("cbPicturesKeepFIcon")

        ### OTHER ###
        #Enable checkBox
        self.cbOtherEnable = win.get_object("cbOtherEnable")

        ### IGNORED ###
        #Ignored path list
        self.trvIgnoredPathList = win.get_object("trvIgnoredPathList")
        self.lsstIgnoredPathList = gtk.ListStore(str)
        self.trvIgnoredPathList.set_model(self.lsstIgnoredPathList)
        self.columnIgnoredPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=0)
        self.trvIgnoredPathList.append_column(self.columnIgnoredPathList)
        #IgnoredRemove button
        self.btnIgnoredRemove = win.get_object("btnIgnoredRemove")
        #IgnoreHidden checkBox
        self.cbIgnoreHidden = win.get_object("cbIgnoreHidden")

        ### MISCELLANEOUS ###
        #Enable Cover-Thumbnailer checkBox
        self.cbEnableCT = win.get_object("cbEnableCT")
        self.spinbtn_thumbSize = win.get_object("spinbtn_thumbSize")

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
        CONF.save_user_conf()
        gtk.main_quit()

    def on_btnClearThumbnailCache_clicked(self, widget):
        thumbpath = os.path.join(CONF.user_homedir, '.thumbnails')
        if os.path.isdir(thumbpath):
            shutil.rmtree(thumbpath)

    #~~~ MUSIC ~~~
    def on_cbMusicEnable_toggled(self, widget):
        CONF['music_enabled'] = self.cbMusicEnable.get_active()

    def on_cbMusicKeepFIcon_toggled(self, widget):
        CONF['music_keepdefaulticon'] = self.cbMusicKeepFIcon.get_active()

    def on_btnMusicAdd_clicked(self, widget):
        self.fileChooserFor = 'music'
        self.fileChooser.show()

    def on_trvMusicPathList_cursor_changed(self, widget):
        model, iter_ = widget.get_selection().get_selected()
        if iter_ != None:
            self.btnMusicRemove.set_sensitive(True)

    def on_btnMusicRemove_clicked(self, widget):
        removePathFromList(
                self.trvMusicPathList,
                self.lsstMusicPathList,
                CONF['music_paths']
                )
        self.btnMusicRemove.set_sensitive(False)

    def on_cb_useGnomeMusic_toggled(self, widget):
        CONF['music_usegnomefolder'] = self.cb_useGnomeMusic.get_active()

    #~~~ PICTURES ~~~
    def on_cbPicturesEnable_toggled(self, widget):
        CONF['pictures_enabled'] = self.cbPicturesEnable.get_active()

    def on_cbPicturesKeepFIcon_toggled(self, widget):
        CONF['pictures_keepdefaulticon'] = self.cbPicturesKeepFIcon.get_active()

    def on_btnPicturesAdd_clicked(self, widget):
        self.fileChooserFor = 'pictures'
        self.fileChooser.show()

    def on_trvPicturesPathList_cursor_changed(self, widget):
        model, iter_ = widget.get_selection().get_selected()
        if iter_ != None:
            self.btnPicturesRemove.set_sensitive(True)

    def on_btnPicturesRemove_clicked(self, widget):
        removePathFromList(
                self.trvPicturesPathList,
                self.lsstPicturesPathList,
                CONF['pictures_paths']
                )
        self.btnPicturesRemove.set_sensitive(False)

    def on_cb_useGnomePictures_toggled(self, widget):
        CONF['pictures_usegnomefolder'] = self.cb_useGnomePictures.get_active()

    #~~~ OTHER ~~~
    def on_cbOtherEnable_toggled(self, widget):
        CONF['other_enabled'] = self.cbOtherEnable.get_active()

    #~~~ IGNORED ~~~
    def on_btnIgnoredAdd_clicked(self, widget):
        self.fileChooserFor = 'ignored'
        self.fileChooser.show()

    def on_trvIgnoredPathList_cursor_changed(self, widget):
        model, iter_ = widget.get_selection().get_selected()
        if iter_ != None:
            self.btnIgnoredRemove.set_sensitive(True)

    def on_btnIgnoredRemove_clicked(self, widget):
        removePathFromList(self.trvIgnoredPathList, self.lsstIgnoredPathList, CONF['ignored_paths'])
        self.btnIgnoredRemove.set_sensitive(False)

    def on_cbIgnoreHidden_toggled(self, widget):
        CONF['ignored_dotted'] = self.cbIgnoreHidden.get_active()

    #~~~ MISCELLANEOUS ~~~
    def on_cbEnableCT_toggled(self, widget):
        gconf_client = gconf.client_get_default()
        gconf_client.set_bool(GCONF_KEY, self.cbEnableCT.get_active())

    def on_spinbtn_thumbSize_value_changed(self, widget):
        gconf_client = gconf.client_get_default()
        gconf_client.set_int(GCONF_KEY_NAUTILUS_THUMB_SIZE, int(self.spinbtn_thumbSize.get_value()))

    ### FILECHOOSER DIALOG ###
    def on_btnFileChooserCancel_clicked(self, widget):
        self.fileChooser.hide()

    def on_btnFileChooserOpen_clicked(self, widget):
        self.fileChooser.hide()
        path = self.fileChooser.get_filename()
        if self.fileChooserFor == 'music':
            addPathToList(self.lsstMusicPathList, path, CONF['music_paths'])
        elif self.fileChooserFor == 'pictures':
            addPathToList(self.lsstPicturesPathList, path, CONF['pictures_paths'])
        elif self.fileChooserFor == 'ignored':
            addPathToList(self.lsstIgnoredPathList, path, CONF['ignored_paths'])
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


def addPathToList(gtklist, path, conflist):
    """ Adds the path in the list

    Arguments:
      * path -- the path to add
      * gtklist -- the gtkListStore where we will add the path
      * confilst -- the "Conf" path list
    """
    if not path in conflist:
        gtklist.append([path])
        conflist.append(path)
    else:
        gui.msgdlgErrorPAIL.show()


def removePathFromList(gtktree, gtklist, conflist):
    """ Remove the path from the list

    Arguments:
      * gtktree -- the gtkTreeView
      * gtklist -- the gtkListStore where we will add the path
      * confilst -- the "Conf" path list
    """
    model, iter_ = gtktree.get_selection().get_selected()
    conflist.remove(gtklist.get_value(iter_, 0))
    gtklist.remove(iter_)


def loadInterface(gui):
    """ Put options on the GUI

    Argument:
      * gui -- the gui
    """
    #Music
    gui.cbMusicEnable.set_active(CONF['music_enabled'])
    gui.cbMusicKeepFIcon.set_active(CONF['music_keepdefaulticon'])
    for path in CONF['music_paths']:
        gui.lsstMusicPathList.append([path])
    gui.cb_useGnomeMusic.set_label(_("Enable for GNOME’s music folder (%s)") %(CONF['music_gnomefolderpath']))
    gui.cb_useGnomeMusic.set_active(CONF['music_usegnomefolder'])
    #Pictures
    gui.cbPicturesEnable.set_active(CONF['pictures_enabled'])
    gui.cbPicturesKeepFIcon.set_active(CONF['pictures_keepdefaulticon'])
    for path in CONF['pictures_paths']:
        gui.lsstPicturesPathList.append([path])
    gui.cb_useGnomePictures.set_label(_("Enable for GNOME’s picture folder (%s)") %(CONF['pictures_gnomefolderpath']))
    gui.cb_useGnomePictures.set_active(CONF['pictures_usegnomefolder'])
    #Other
    gui.cbOtherEnable.set_active(CONF['other_enabled'])
    #Ignored
    gui.cbIgnoreHidden.set_active(CONF['ignored_dotted'])
    for path in CONF['ignored_paths']:
        gui.lsstIgnoredPathList.append([path])
    #Miscellaneous
    gconf_client = gconf.client_get_default()
    gui.cbEnableCT.set_active(gconf_client.get_bool(GCONF_KEY))
    thumb_size = gconf_client.get_int(GCONF_KEY_NAUTILUS_THUMB_SIZE)
    if thumb_size > 128:
        gui.spinbtn_thumbSize.set_value(128)
    elif thumb_size < 64:
        gui.spinbtn_thumbSize.set_value(64)
    else:
        gui.spinbtn_thumbSize.set_value(thumb_size)



if __name__ == "__main__":
    CONF = Conf()
    gui = MainWin()
    gtk.main()

