#!/bin/bash

   #########################################################################
 ##                                                                       ##
##           ┏━╸┏━┓╻ ╻┏━╸┏━┓   ╺┳╸╻ ╻╻ ╻┏┳┓┏┓ ┏┓╻┏━┓╻╻  ┏━╸┏━┓            ##
##           ┃  ┃ ┃┃┏┛┣╸ ┣┳┛    ┃ ┣━┫┃ ┃┃┃┃┣┻┓┃┗┫┣━┫┃┃  ┣╸ ┣┳┛            ##
##           ┗━╸┗━┛┗┛ ┗━╸╹┗╸    ╹ ╹ ╹┗━┛╹ ╹┗━┛╹ ╹╹ ╹╹┗━╸┗━╸╹┗╸            ##
##                         — www.flogisoft.com —                          ##
##                                                                        ##
############################################################################
##                                                                        ##
## Cover thumbnailer — Installer                                          ##
##                                                                        ##
## Copyright (C) 2009 - 2024  Fabien Loison <flo at flogisoft dot com>    ##
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
## VERSION : 0.10.2 (Sat Dec 14 18:29:51 CET 2024)                        ##
## WEB SITE : https://github.com/flozz/cover-thumbnailer                  ##
##                                                                       ##
#########################################################################

SOFTWARE="Cover Thumbnailer"
DESC="Displays music album covers in Nautilus and more..."
LOGFILE="/tmp/cover-thumbnailer$1_$$.log"


_install() {
	#Install the software
	#$1 : The installation path if different of /

	#Check if an older version is installed
	if [ -z $1 ] ; then { #Only for --install
		_check_for_old_version
	} fi

	#/usr/bin
	mkdir -pv "$1"/usr/bin 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./cover-thumbnailer.py "$1"/usr/bin/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1
	chmod -v 755 "$1"/usr/bin/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./cover-thumbnailer-gui.py "$1"/usr/bin/cover-thumbnailer-gui 1>> $LOGFILE 2>> $LOGFILE || error=1
	chmod -v 755 "$1"/usr/bin/cover-thumbnailer-gui 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/cover-thumbnailer/
	mkdir -pv "$1"/usr/share/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -rv ./share/* "$1"/usr/share/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/man/man1
	mkdir -pv "$1"/usr/share/man/man1 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./man/cover-thumbnailer.1 "$1"/usr/share/man/man1/ 1>> $LOGFILE 2>> $LOGFILE || error=1
	gzip --best -f "$1"/usr/share/man/man1/cover-thumbnailer.1 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./man/cover-thumbnailer-gui.1 "$1"/usr/share/man/man1/ 1>> $LOGFILE 2>> $LOGFILE || error=1
	gzip --best -f "$1"/usr/share/man/man1/cover-thumbnailer-gui.1 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/doc/cover-thumbnailer
	mkdir -pv "$1"/usr/share/doc/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./README.md "$1"/usr/share/doc/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/locale/xx_XX/LC_MESSAGES
	for file in `find ./locale -name "*.po"` ; do {
		l10elang=`echo $file | sed -r 's#./locale/(.*).po#\1#g'`
		mkdir -pv "$1"/usr/share/locale/$l10elang/LC_MESSAGES/ 1>> $LOGFILE 2>> $LOGFILE || error=1
		msgfmt "$file" -o "$1"/usr/share/locale/$l10elang/LC_MESSAGES/cover-thumbnailer-gui.mo 1>> $LOGFILE 2>> $LOGFILE || error=1
	} done

	#/usr/share/applications
	mkdir -pv "$1"/usr/share/applications/ 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./freedesktop/cover-thumbnailer-gui.desktop "$1"/usr/share/applications/cover-thumbnailer-gui.desktop 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/thumbnailers
	mkdir -pv "$1"/usr/share/thumbnailers/ 1>> $LOGFILE 2>> $LOGFILE || error=1
	cp -v ./freedesktop/cover.thumbnailer "$1"/usr/share/thumbnailers/cover.thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1

	#uninstall.sh
	if [ -z $1 ] ; then {
		cp ./install.sh /usr/share/cover-thumbnailer/uninstall.sh 1>> $LOGFILE 2>> $LOGFILE || error=1
		chmod -v 755 /usr/share/cover-thumbnailer/uninstall.sh 1>> $LOGFILE 2>> $LOGFILE || error=1
	} fi

	if [ "$error" == "1" ] ; then {
		echo "$_RED   E:$_NORMAL An error occurred when installing $SOFTWARE"
		echo "$_RED   E:$_NORMAL See the log file for more informations."
		echo "$_RED   E:$_NORMAL $LOGFILE"
		exit 20
	} else {
		echo "   $_GREEN$SOFTWARE was successfully installed on your computer$_NORMAL"
		rm $LOGFILE 1> /dev/null 2> /dev/null
	} fi
}


_remove() {
	#Remove the software

	#/usr/share/applications
	rm -fv /usr/share/applications/cover-thumbnailer-gui.desktop 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/cover-thumbnailer
	rm -rfv /usr/share/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/doc
	rm -rfv /usr/share/doc/cover-thumbnailer/ 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/man/man1
	rm -vf /usr/share/man/man1/cover-thumbnailer.1.gz 1>> $LOGFILE 2>> $LOGFILE || error=1
	rm -vf /usr/share/man/man1/cover-thumbnailer-gui.1.gz 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/locale/xx_XX/LC_MESSAGES/cover-thumbnailer-gui.mo
	find /usr/share/locale/ \
		-name cover-thumbnailer-gui.mo \
		-exec rm -v '{}' ';' \
		1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/bin
	rm -vf /usr/bin/cover-thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1
	rm -vf /usr/bin/cover-thumbnailer-gui 1>> $LOGFILE 2>> $LOGFILE || error=1

	#/usr/share/thumbnailers
	rm -vf /usr/share/thumbnailers/cover.thumbnailer 1>> $LOGFILE 2>> $LOGFILE || error=1

	if [ "$error" == "1" ] ; then {
		echo "$_RED   E:$_NORMAL An error occurred when removing $SOFTWARE"
		echo "$_RED   E:$_NORMAL See the log file for more informations."
		echo "$_RED   E:$_NORMAL $LOGFILE"
		exit 20
	} else {
		echo "   $_GREEN$SOFTWARE was successfully removed from your computer$_NORMAL"
		rm $LOGFILE 1> /dev/null 2> /dev/null
	} fi
}


_locale() {
	#Extracts strings

	mkdir -pv ./locale/
	xgettext -k_ -kN_ \
		-o ./locale/cover-thumbnailer-gui.pot \
		./cover-thumbnailer-gui.py \
		./share/cover-thumbnailer-gui.glade
	for lcfile in $(find ./locale/ -name "*.po") ; do {
		echo -n "   * $lcfile"
		msgmerge --update $lcfile ./locale/cover-thumbnailer-gui.pot
	} done
}


_check_for_old_version() {
	#Checks if an older version is installed, and try to remove.

	echo "   * Checking for old version..."
	if [ -d /usr/share/cover-thumbnailer/ ] ; then { #Version >= 0.4
		echo "     Version 0.4 or newer found."
			if [ -x /usr/share/cover-thumbnailer/uninstall.sh ] ; then {
				/usr/share/cover-thumbnailer/uninstall.sh --remove 1>> $LOGFILE 2>> $LOGFILE || error=1
				if [ "$error" == "1" ] ; then {
					echo "     E: An error occurred when removing installed version."
					echo "     E: See the log file for more informations."
					echo "     E: $LOGFILE"
					exit 11
				} else {
					echo "     * Old version successfully removed"
				} fi
			} else {
				echo "     E: Can't remove the installed version."
				echo "     E: Remove it manually and run this script again."
				exit 10
			} fi
	} fi
}


_check_dep() {
	#Checks dependencies

	echo "$_BOLD * Checking dependencies...$_NORMAL"
	echo -n "   * Python 3 ............................ "
	test -x /usr/bin/python3 && echo "$_GREEN[OK]$_NORMAL" || { echo "$_RED[Missing]$_NORMAL" ; error=1 ; }
	echo -n "   * Python Imaging Library (PIL) ........ "
	$_PY <<< "$(echo -e "try: from PIL import Image\nexcept: import Image")" 1> /dev/null 2> /dev/null && echo "$_GREEN[OK]$_NORMAL" || { echo "$_RED[Missing]$_NORMAL" ; error=1 ; }
	echo -n "   * Python gi and GTK introspection ..... "
	$_PY <<< "import gi ; gi.require_version('Gtk', '3.0') ; from gi.repository import Gtk" 1> /dev/null 2> /dev/null && echo "$_GREEN[OK]$_NORMAL" || { echo "$_RED[Missing]$_NORMAL" ; error=1 ; }
	echo -n "   * Python gettext support .............. "
	$_PY <<< "import gettext" 1> /dev/null 2> /dev/null && echo "$_GREEN[OK]$_NORMAL" || { echo "$_RED[Missing]$_NORMAL" ; error=1 ; }
	if [ "$error" == "1" ] ; then {
		echo "$_RED   E:$_NORMAL Some dependencies are missing."
		exit 30
	} fi
}


_check_build_dep() {
	#Checks build dependencies

	echo "$_BOLD * Checking build dependencies...$_NORMAL"
	echo -n "   * gettext ............................. "
	test -x /usr/bin/xgettext && echo "$_GREEN[OK]$_NORMAL" || { echo "$_RED[Missing]$_NORMAL" ; error=1 ; }
	if [ "$error" == "1" ] ; then {
		echo "$_RED   E:$_NORMAL Some build dependencies are missing."
		exit 31
	} fi
}


#Go to the script directory
cd "${0%/*}" 1> /dev/null 2> /dev/null

#Force English
export LANG=C
#Header
echo -e "$SOFTWARE - $DESC\n"

#Python
export _PY=/usr/bin/python3

#Action do to
if [ "$1" == "--install" ] || [ "$1" == "-i" ] ; then {
	#Colors
	_RED=$(echo -e "\033[1;31m")
	_GREEN=$(echo -e "\033[1;32m")
	_NORMAL=$(echo -e "\033[0m")
	_BOLD=$(echo -e "\033[1m")
	if [ "$(whoami)" == "root" ] ; then {
		_check_build_dep
		_check_dep
		echo "$_BOLD * Installing $SOFTWARE...$_NORMAL"
		_install
	} else {
		echo "$_BOLD * Installing $SOFTWARE...$_NORMAL"
		echo "$_RED   E:$_NORMAL Need to be root"
		exit 1
	} fi
} elif [ "$1" == "--package" ] || [ "$1" == "-p" ] ; then {
	_check_build_dep
	echo " * Packaging $SOFTWARE..."
	mkdir -p "$2" 1> /dev/null 2> /dev/null #create the output directory if not exists
	#Check if the directory is empty
	if [ $(find "$2" | wc -l) != 1 ] ; then
		echo "E: The destination folder '$2' is not empty..."
		exit 5
	fi
	if [ -d "$2" ] ; then {
		_install "$2"
	} else {
		echo "   E: '$2' is not a directory"
		exit 2
	} fi
} elif [ "$1" == "--remove" ] || [ "$1" == "-r" ] ; then {
	#Colors
	_RED=$(echo -e "\033[1;31m")
	_GREEN=$(echo -e "\033[1;32m")
	_NORMAL=$(echo -e "\033[0m")
	_BOLD=$(echo -e "\033[1m")
	echo "$_BOLD * Removing $SOFTWARE...$_NORMAL"
	if [ "$(whoami)" == "root" ] ; then {
		_remove
	} else {
		echo "$_RED   E:$_NORMAL Need to be root"
		exit 1
	} fi
} elif [ "$1" == "--locale" ] || [ "$1" == "-l" ] ; then {
	#Colors
	_RED=$(echo -e "\033[1;31m")
	_GREEN=$(echo -e "\033[1;32m")
	_NORMAL=$(echo -e "\033[0m")
	_BOLD=$(echo -e "\033[1m")
	echo "$_BOLD * Extracting strings for the translation template...$_NORMAL"
	if [ -x /usr/bin/xgettext ] ; then {
		_locale
	} else {
		echo "$_RED   E:$_NORMAL Can't find xgettext... Please install gettext and try again."
		exit 3
	} fi
} else {
	echo "Arguments:"
	echo "  --install : install $SOFTWARE on your computer."
	echo "  --package <path> : install $SOFTWARE in <path> (Useful for packaging)."
	echo "                     NOTE: <path> with no slash ('/') at the end"
	echo "  --remove : remove $SOFTWARE from your computer."
	echo "  --locale : extract strings to for the translation template."
	exit 4
} fi
