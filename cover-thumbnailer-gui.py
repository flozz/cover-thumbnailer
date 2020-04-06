#!/usr/bin/python2
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
## Copyright (C) 2009 - 2011  Fabien Loison <flo at flogisoft dot com>    ##
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
## WEB SITE : http://projects.flogisoft.com/cover-thumbnailer/            ##
##                                                                       ##
#########################################################################


"""Configuration GUI for Cover Thumbnailer.

A GUI for easily configuring Cover Thumbnailer.
"""

__version__ = "0.8.3"
__author__ = "Fabien Loison <flo@flogisoft.com>"
__copyright__ = "Copyright © 2009 - 2011 Fabien LOISON"
__appname__ = "cover-thumbnailer-gui"

import gtk, pygtk
pygtk.require("2.0")

import gettext
gettext.install(__appname__)

import os, re, shutil

# Import the thumbnailer itself as a library (workarounds needed for its name
# having a dash and no .py extension)
class Common(object):
    def __init__(self):
        self.__dict__ = {}
        if "DEVEL" in os.environ:
            common_path = "./cover-thumbnailer.py"
        else:
            common_path = "/usr/bin/cover-thumbnailer"
        execfile(common_path, self.__dict__)
common = Common()

#Base path
if "DEVEL" in os.environ:
    BASE_PATH = "./share/" #For devel
else:
    BASE_PATH = "/usr/share/cover-thumbnailer/"

#GConf key for enabling/disabling Cover thumbnailer
GCONF_KEY = "/desktop/gnome/thumbnailers/inode@directory/enable"

#GConf key for nautilus thumbnails size
GCONF_KEY_NAUTILUS_THUMB_SIZE = "/apps/nautilus/icon_view/thumbnail_size"


class Conf(common.Conf):

    """ Import configuration.

    Import configuration from the GNOME and cover thumbnailer files
    """

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
            user_conf_file.write(self._write_bool("music_cropimg"))
            user_conf_file.write(self._write_bool("music_makemosaic"))
            user_conf_file.write(self._write_list("music_paths"))
            user_conf_file.write(self._write_str("music_bg"))
            user_conf_file.write(self._write_str("music_fg"))
            user_conf_file.write(self._write_str("music_defaultimg"))
            #Pictures
            user_conf_file.write("\n[PICTURES]\n")
            user_conf_file.write(self._write_bool("pictures_enabled"))
            user_conf_file.write(self._write_bool("pictures_keepdefaulticon"))
            user_conf_file.write(self._write_bool("pictures_usegnomefolder"))
            user_conf_file.write(self._write_int("pictures_maxthumbs"))
            user_conf_file.write(self._write_list("pictures_paths"))
            user_conf_file.write(self._write_str("pictures_bg"))
            user_conf_file.write(self._write_str("pictures_fg"))
            #Other
            user_conf_file.write("\n[OTHER]\n")
            user_conf_file.write(self._write_bool("other_enabled"))
            #Ignored
            user_conf_file.write("\n[IGNORED]\n")
            user_conf_file.write(self._write_bool("ignored_dotted"))
            user_conf_file.write(self._write_list("ignored_paths"))
            #Never ignored
            user_conf_file.write("\n[NEVERIGNORED]\n")
            user_conf_file.write(self._write_list("neverignored_paths"))
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

    def _write_int(self, key):
        """ Return the string to write in config file for integer key

        Argument:
          * key -- the name of the CONF key
        """
        wkey = key.split("_")[1]
        value = self[key]
        return "\t%s = %i\n" % (wkey, value)

    def _write_str(self, key):
        """ Return the string to write in config file for string key

        Argument:
          * key -- the name of the CONF key
        """
        wkey = key.split("_")[1]
        value = self[key]
        return "\t%s = \"%s\"\n" % (wkey, value)

class Thumb(common.Thumb):
    def as_pixbuf(self):
        return gtk.gdk.pixbuf_new_from_data(self.thumb.tobytes(), gtk.gdk.COLORSPACE_RGB,
                                            True, 8, self.thumb.width, self.thumb.height,
                                            len(self.thumb.getbands()) * self.thumb.width)

class MainWin(object):
    """ The configuration GUI """
    def __init__(self):
        win = gtk.Builder()
        win.set_translation_domain(__appname__)
        #FIXME: GtkWarning: Ignoring the separator setting (wtf ?!)
        win.add_from_file(os.path.join(BASE_PATH, "cover-thumbnailer-gui.glade"))

        self.winAbout = win.get_object("winAbout")
        self.winAbout.connect("response", self.on_winAbout_response)
        self.winAbout.set_version(__version__)
        self.winAbout.set_copyright(__copyright__)

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
        #rbMusicCrop and rbMusicPreserve radiobuttons
        self.rbMusicCrop = win.get_object("rbMusicCrop")
        self.rbMusicPreserve = win.get_object("rbMusicPreserve")
        #rbMusicNoMosaic and rbMusicMosaic radiobuttons
        self.rbMusicNoMosaic = win.get_object("rbMusicNoMosaic")
        self.rbMusicMosaic = win.get_object("rbMusicMosaic")
        #thumbnail decorations configuration
        self.imgMusicThPreview = win.get_object("imgMusicThPreview")
        self.btnPickMusicBg = win.get_object("btnPickMusicBg")
        self.btnPickMusicFg = win.get_object("btnPickMusicFg")
        self.btnPickMusicDf = win.get_object("btnPickMusicDf")
        self.btnImageMaxSize = self.btnPickMusicDf.get_child().get_allocation().height
        self.updateMusicThPreview()

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
        #spinbtn_maxThumbs Spin Button
        self.spinbtn_maxThumbs = win.get_object("spinbtn_maxThumbs")
        #thumbnail decorations configuration
        self.imgPicturesThPreview = win.get_object("imgPicturesThPreview")
        self.btnPickPicturesBg = win.get_object("btnPickPicturesBg")
        self.btnPickPicturesFg = win.get_object("btnPickPicturesFg")
        self.updatePicturesThPreview()

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

        ### NEVER IGNORED ###
        #Never ignored path list
        self.trvNeverIgnoredPathList = win.get_object("trvNeverIgnoredPathList")
        self.lsstNeverIgnoredPathList = gtk.ListStore(str)
        self.trvNeverIgnoredPathList.set_model(self.lsstNeverIgnoredPathList)
        self.columnNeverIgnoredPathList = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=0)
        self.trvNeverIgnoredPathList.append_column(self.columnNeverIgnoredPathList)
        #NeverIgnoredRemove button
        self.btnNeverIgnoredRemove = win.get_object("btnNeverIgnoredRemove")

        ### MISCELLANEOUS ###
        #Enable Cover-Thumbnailer checkBox
        self.cbEnableCT = win.get_object("cbEnableCT")
        #Thumbnail size spinbtn
        self.spinbtn_thumbSize = win.get_object("spinbtn_thumbSize")

        ### FileChooser Dialog ###
        self.fileChooser = win.get_object("filechooserdialog")
        self.fileChooserFor = None

        ### Thumbnail Chooser Dialog ###
        self.thumbnailChooser = win.get_object("thumbnailchooserdialog")
        self.thumbnailChooserFor = None # should be a CONF key
        self.thumbnailFilter = gtk.FileFilter()
        self.thumbnailFilter.set_name("Image Files")
        self.thumbnailFilter.add_pixbuf_formats()
        self.thumbnailChooser.add_filter(self.thumbnailFilter)

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
        thumbpath = os.path.join(CONF.user_homedir, '.cache/thumbnails')
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
        if iter_ is not None:
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

    def on_rbMusicCrop_toggled(self, widget):
        CONF['music_cropimg'] = self.rbMusicCrop.get_active()

    def on_rbMusicNoMosaic_toggled(self, widget):
        CONF['music_makemosaic'] = self.rbMusicMosaic.get_active()

    def updateButtonImage(self, button, path):
        img = gtk.image_new_from_file(path)
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        orig_height = float(pixbuf.get_height())
        orig_width = float(pixbuf.get_width())
        scaled_width = int(round(orig_width * self.btnImageMaxSize / orig_height))
        scaled_height = int(round(orig_height * self.btnImageMaxSize / orig_width))
        if scaled_width < scaled_height:
            scaled_height = self.btnImageMaxSize
        else:
            scaled_width = self.btnImageMaxSize
        pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, gtk.gdk.INTERP_HYPER)
        button.set_image(gtk.image_new_from_pixbuf(pixbuf))

    def updateMusicThPreview(self):
        preview = Thumb([CONF['music_defaultimg']])
        preview.music_thumbnail(
                CONF['music_bg'],
                CONF['music_fg'],
                CONF['music_cropimg']
                )
        self.imgMusicThPreview.set_from_pixbuf(preview.as_pixbuf())
        self.updateButtonImage(self.btnPickMusicBg, CONF['music_bg'])
        self.updateButtonImage(self.btnPickMusicFg, CONF['music_fg'])
        self.updateButtonImage(self.btnPickMusicDf, CONF['music_defaultimg'])

    def on_btnPickMusicBg_clicked(self, widget):
        self.show_thumbnail_chooser("music_bg")

    def on_btnPickMusicFg_clicked(self, widget):
        self.show_thumbnail_chooser("music_fg")

    def on_btnPickMusicDf_clicked(self, widget):
        self.show_thumbnail_chooser("music_defaultimg")()

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
        if iter_ is not None:
            self.btnPicturesRemove.set_sensitive(True)

    def on_btnPicturesRemove_clicked(self, widget):
        removePathFromList(
                self.trvPicturesPathList,
                self.lsstPicturesPathList,
                CONF['pictures_paths']
                )
        self.btnPicturesRemove.set_sensitive(False)

    def on_spinbtn_maxThumbs_value_changed(self, widget):
        CONF['pictures_maxthumbs'] = int(self.spinbtn_maxThumbs.get_value())

    def on_cb_useGnomePictures_toggled(self, widget):
        CONF['pictures_usegnomefolder'] = self.cb_useGnomePictures.get_active()

    def updatePicturesThPreview(self):
        preview = Thumb([os.path.join(BASE_PATH, "icon.png")])
        preview.pictures_thumbnail(
                CONF['pictures_bg'],
                CONF['pictures_fg']
                )
        self.imgPicturesThPreview.set_from_pixbuf(preview.as_pixbuf())
        self.updateButtonImage(self.btnPickPicturesBg, CONF['pictures_bg'])
        self.updateButtonImage(self.btnPickPicturesFg, CONF['pictures_fg'])

    def on_btnPickPicturesBg_clicked(self, widget):
        self.show_thumbnail_chooser("pictures_bg")

    def on_btnPickPicturesFg_clicked(self, widget):
        self.show_thumbnail_chooser("pictures_fg")

    #~~~ OTHER ~~~
    def on_cbOtherEnable_toggled(self, widget):
        CONF['other_enabled'] = self.cbOtherEnable.get_active()

    #~~~ IGNORED ~~~
    def on_btnIgnoredAdd_clicked(self, widget):
        self.fileChooserFor = 'ignored'
        self.fileChooser.show()

    def on_trvIgnoredPathList_cursor_changed(self, widget):
        model, iter_ = widget.get_selection().get_selected()
        if iter_ is not None:
            self.btnIgnoredRemove.set_sensitive(True)

    def on_btnIgnoredRemove_clicked(self, widget):
        removePathFromList(self.trvIgnoredPathList, self.lsstIgnoredPathList, CONF['ignored_paths'])
        self.btnIgnoredRemove.set_sensitive(False)

    def on_cbIgnoreHidden_toggled(self, widget):
        CONF['ignored_dotted'] = self.cbIgnoreHidden.get_active()

    #~~~ NEVER IGNORED ~~~
    def on_btnNeverIgnoredAdd_clicked(self, widget):
        self.fileChooserFor = 'neverignored'
        self.fileChooser.show()

    def on_trvNeverIgnoredPathList_cursor_changed(self, widget):
        model, iter_ = widget.get_selection().get_selected()
        if iter_ is not None:
            self.btnNeverIgnoredRemove.set_sensitive(True)

    def on_btnNeverIgnoredRemove_clicked(self, widget):
        removePathFromList(self.trvNeverIgnoredPathList, self.lsstNeverIgnoredPathList, CONF['neverignored_paths'])
        self.btnNeverIgnoredRemove.set_sensitive(False)

    #~~~ MISCELLANEOUS ~~~ #FIXME: No more use GConf
    #def on_cbEnableCT_toggled(self, widget):
    #    gconf_client = gconf.client_get_default()
    #    gconf_client.set_bool(GCONF_KEY, self.cbEnableCT.get_active())

    #def on_spinbtn_thumbSize_value_changed(self, widget):
    #    gconf_client = gconf.client_get_default()
    #    gconf_client.set_int(GCONF_KEY_NAUTILUS_THUMB_SIZE, int(self.spinbtn_thumbSize.get_value()))

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
        elif self.fileChooserFor == 'neverignored':
            addPathToList(self.lsstNeverIgnoredPathList, path, CONF['neverignored_paths'])
        self.fileChooserFor = None

    def on_filechooserdialog_delete_event(self, widget, response):
        self.fileChooser.hide()
        return True #Don't delete

    ### THUMBNAILCHOOSER DIALOG ###
    def show_thumbnail_chooser(self, config_option_name):
        self.thumbnailChooserFor = config_option_name
        self.thumbnailChooser.set_filename(CONF[config_option_name])
        self.thumbnailChooser.show()

    def on_btnThumbnailChooserCancel_clicked(self, widget):
        self.thumbnailChooser.hide()

    def on_btnThumbnailChooserOpen_clicked(self, widget):
        self.thumbnailChooser.hide()
        path = self.thumbnailChooser.get_filename()
        CONF[self.thumbnailChooserFor] = path
        if self.thumbnailChooserFor.startswith("music_"):
            self.updateMusicThPreview()
        elif self.thumbnailChooserFor.startswith("pictures_"):
            self.updatePicturesThPreview()
        self.thumbnailChooserFor = None

    def on_thumbnailChooserdialog_delete_event(self, widget, response):
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
    gui.cb_useGnomeMusic.set_label(_("Enable for GNOME's music folder (%s)") %(CONF['music_gnomefolderpath']))
    gui.cb_useGnomeMusic.set_active(CONF['music_usegnomefolder'])
    if CONF['music_cropimg']:
        gui.rbMusicCrop.set_active(True)
    else:
        gui.rbMusicPreserve.set_active(True)
    if CONF['music_makemosaic']:
        gui.rbMusicMosaic.set_active(True)
    else:
        gui.rbMusicNoMosaic.set_active(True)
    #Pictures
    gui.cbPicturesEnable.set_active(CONF['pictures_enabled'])
    gui.cbPicturesKeepFIcon.set_active(CONF['pictures_keepdefaulticon'])
    for path in CONF['pictures_paths']:
        gui.lsstPicturesPathList.append([path])
    gui.cb_useGnomePictures.set_label(_("Enable for GNOME's picture folder (%s)") %(CONF['pictures_gnomefolderpath']))
    gui.cb_useGnomePictures.set_active(CONF['pictures_usegnomefolder'])
    if CONF['pictures_maxthumbs'] > 4:
        gui.spinbtn_maxThumbs.set_value(4)
    elif CONF['pictures_maxthumbs'] < 1:
        gui.spinbtn_maxThumbs.set_value(1)
    else:
        gui.spinbtn_maxThumbs.set_value(CONF['pictures_maxthumbs'])
    #Other
    gui.cbOtherEnable.set_active(CONF['other_enabled'])
    #Ignored
    gui.cbIgnoreHidden.set_active(CONF['ignored_dotted'])
    for path in CONF['ignored_paths']:
        gui.lsstIgnoredPathList.append([path])
    #Ignored
    for path in CONF['neverignored_paths']:
        gui.lsstNeverIgnoredPathList.append([path])
    #Miscellaneous FIXME: No more use GConf
    #gconf_client = gconf.client_get_default()
    #gui.cbEnableCT.set_active(gconf_client.get_bool(GCONF_KEY))
    #thumb_size = gconf_client.get_int(GCONF_KEY_NAUTILUS_THUMB_SIZE)
    #if thumb_size > 128:
    #    gui.spinbtn_thumbSize.set_value(128)
    #elif thumb_size < 64:
    #    gui.spinbtn_thumbSize.set_value(64)
    #else:
    #    gui.spinbtn_thumbSize.set_value(thumb_size)
    #If GNOME folders == user home dir or not defined,
    #deactivate the option, it's probably a misconfiguration !
    if os.path.isdir(CONF['music_gnomefolderpath']) \
        and os.path.samefile(CONF['music_gnomefolderpath'], CONF.user_homedir) \
        or CONF['music_gnomefolderpath'] == _("<None>"):
        gui.cb_useGnomeMusic.set_active(False)
        gui.cb_useGnomeMusic.set_sensitive(False)
    if os.path.isdir(CONF['pictures_gnomefolderpath']) \
        and os.path.samefile(CONF['pictures_gnomefolderpath'], CONF.user_homedir) \
        or CONF['pictures_gnomefolderpath'] == _("<None>"):
        gui.cb_useGnomePictures.set_active(False)
        gui.cb_useGnomePictures.set_sensitive(False)



if __name__ == "__main__":
    CONF = Conf()
    gui = MainWin()
    gtk.main()


