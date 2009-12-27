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
## VERSION : 0.6 (Sat, 26 Dec 2009 21:57:53 +0100)                        ##
## WEB SITE : http://software.flogisoft.com/cover-thumbnailer/            ##
##                                                                       ##
#########################################################################


#=============================================================== CONFIG ====
COLOR_ERROR="\033[1;31m"
COLOR_INFO="\033[1;33m"
COLOR_SUCCESS="\033[1;32m"
COLOR_DEFAULT="\033[0m"


#================================================================= LANG ====
lang_en() {
	echo -e "${COLOR_INFO}English Selected$COLOR_DEFAULT"
	#Errors
	LANG_ERROR_ROOT="E: Run this script as root !"
	LANG_ERROR_OLD_VERSION_RM="An error occurred while deleting the old version !"
	LANG_ERROR_INSTALL="An error occurred while installing Cover thumbnailer !"
	LANG_ERROR_RM="An error occurred while uninstalling Cover thumbnailer !"
	#Infos
	LANG_INFOS_WELCOME="Welcome to Cover thumbnailer (un)Installer"
	LANG_INFOS_INSTALLATION_START="Installation started"
	LANG_INFOS_OLD_VERSION="Old version found"
	LANG_INFOS_OLD_VERSION_RM="Removing the old version..."
	LANG_INFOS_HOWTO_UNINSTALL="For uninstalling Cover thumbnailer, run\n/usr/share/cover-thumbnailer/uninstall.sh"
	LANG_INFO_UNINSTALL="Uninstalling Cover thumbnailer..."
	#Success
	LANG_SUCCESS_OLD_VERSION_RM="The old version was successfully removed !"
	LANG_SUCCESS_INSTALL="Cover thumbnailer was successfully installed !"
	LANG_SUCCESS_RM="Cover thumbnailer was successfully uninstalled !"
}

lang_fr() {
	echo -e "${COLOR_INFO}Français sélectionné$COLOR_DEFAULT"
	#Errors
	LANG_ERROR_ROOT="E: Lancez ce script en tant que root !"
	LANG_ERROR_OLD_VERSION_RM="Une erreur est survenue pendant la suppression de l'ancienne version !"
	LANG_ERROR_INSTALL="Une erreur est survenue pendant l'installation de Cover thumbnailer !"
	LANG_ERROR_RM="Une erreur est survenue pendant la désinstallation de Cover thumbnailer !"
	#Infos
	LANG_INFOS_WELCOME="Bienvenue dans l(e) (dés)installateur de Cover thumbnailer"
	LANG_INFOS_INSTALLATION_START="Début de l'installation"
	LANG_INFOS_OLD_VERSION="Ancienne version trouvée"
	LANG_INFOS_OLD_VERSION_RM="Suppression de l'ancienne version..."
	LANG_INFOS_HOWTO_UNINSTALL="Pour désinstaller Cover thumbnailer, lancez\n/usr/share/cover-thumbnailer/uninstall.sh"
	LANG_INFO_UNINSTALL="Désinstallation de Cover thumbnailer..."
	#Success
	LANG_SUCCESS_OLD_VERSION_RM="L'ancienne version à été supprimée avec succès !"
	LANG_SUCCESS_INSTALL="Cover thumbnailer à été installé avec succès !"
	LANG_SUCCESS_RM="Cover thumbnailer à été désinstallé avec succès !"
}


#========================================================== (UN)INSTALL ====
remove_old_version() { #(≤ 0.3.3)
	echo -e "$COLOR_INFO$LANG_INFOS_OLD_VERSION_RM$COLOR_DEFAULT"
	error=0
	gconf-schemas --unregister /usr/share/cover-thumbnailer/cover-thumbnailer.schema || error=1
	rm -rfv /opt/cover_thumbnailer || error=1
	if [ $error == 0 ] ; then {
		echo -e "$COLOR_SUCCESS$LANG_SUCCESS_OLD_VERSION_RM$COLOR_DEFAULT"
	} else {
		echo -e "$COLOR_ERROR$LANG_ERROR_OLD_VERSION_RM$COLOR_DEFAULT"
		exit 4
	} fi
}

install_ct() {
	#Old version installed ? (≤ 0.3.3)
	if [ -d /opt/cover_thumbnailer/ ] ; then {
		echo -e "$COLOR_INFO$LANG_INFOS_OLD_VERSION$COLOR_DEFAULT"
		remove_old_version
	} fi

	#Old version installed ? (≥ 0.4)
	if [ -d /usr/share/cover-thumbnailer/ ] ; then {
		echo -e "$COLOR_INFO$LANG_INFOS_OLD_VERSION$COLOR_DEFAULT"
		if [ -x /usr/share/cover-thumbnailer/uninstall.sh ] ; then {
			echo -e "$COLOR_INFO$LANG_INFOS_OLD_VERSION_RM$COLOR_DEFAULT"
			/usr/share/cover-thumbnailer/uninstall.sh \
			&& echo -e "$COLOR_SUCCESS$LANG_SUCCESS_OLD_VERSION_RM$COLOR_DEFAULT" \
			|| ( echo -e "$COLOR_ERROR$LANG_ERROR_OLD_VERSION_RM$COLOR_DEFAULT" ; exit 3 )
		} else {
			echo -e "$COLOR_ERROR$LANG_ERROR_OLD_VERSION_RM$COLOR_DEFAULT"
			exit 2
		} fi
	} fi

	#INSTALL
	echo -e "$COLOR_INFO$LANG_INFOS_INSTALLATION_START$COLOR_DEFAULT"
	error=0

	#/usr/share/cover-thumbnailer/
	mkdir -pv /usr/share/cover-thumbnailer || error=1
	cp -rv ./share/* /usr/share/cover-thumbnailer || error=1
	chown -Rv root:root /usr/share/cover-thumbnailer || error=1
	chmod -Rv 644 /usr/share/cover-thumbnailer/ || error=1
	chmod -v 755 /usr/share/cover-thumbnailer || error=1

	#/usr/share/man/man1
	mkdir -pv /usr/share/man/man1 || error=1
	cp -v ./man/cover-thumbnailer.1 /usr/share/man/man1/ || error=1
	chown -v root:root /usr/share/man/man1/cover-thumbnailer.1 || error=1
	chmod -v 644 /usr/share/man/man1/cover-thumbnailer.1 || error=1
	gzip --best /usr/share/man/man1/cover-thumbnailer.1 || error=1

	cp -v ./man/cover-thumbnailer-gui.1 /usr/share/man/man1/ || error=1
	chown -v root:root /usr/share/man/man1/cover-thumbnailer-gui.1 || error=1
	chmod -v 644 /usr/share/man/man1/cover-thumbnailer-gui.1 || error=1
	gzip --best /usr/share/man/man1/cover-thumbnailer-gui.1 || error=1

	#/usr/share/locale/xx_XX/LC_MESSAGES
	#fr
	mkdir -pv /usr/share/locale/fr/LC_MESSAGES || error=1
	cp -v ./locale/fr/LC_MESSAGES/cover-thumbnailer-gui.mo /usr/share/locale/fr/LC_MESSAGES/ || error=1
	chown -v root:root /usr/share/locale/fr/LC_MESSAGES/cover-thumbnailer-gui.mo || error=1
	chmod -v 644 /usr/share/locale/fr/LC_MESSAGES/cover-thumbnailer-gui.mo || error=1

	#/usr/bin
	mkdir -pv /usr/bin || error=1
	cp -v ./cover-thumbnailer.py /usr/bin/cover-thumbnailer || error=1
	chown -v root:root /usr/bin/cover-thumbnailer || error=1
	chmod -v 755 /usr/bin/cover-thumbnailer || error=1

	cp -v ./cover-thumbnailer-gui.py /usr/bin/cover-thumbnailer-gui || error=1
	chown -v root:root /usr/bin/cover-thumbnailer-gui || error=1
	chmod -v 755 /usr/bin/cover-thumbnailer-gui || error=1


	#gconf
	gconf-schemas --register /usr/share/cover-thumbnailer/cover-thumbnailer.schema || error=1

	#uninstall
	cat ./install.sh | sed 's/install_ct #INSTALL/uninstall_ct #UNINSTALL/g' \
	> /usr/share/cover-thumbnailer/uninstall.sh || error=1
	chmod -v 755 /usr/share/cover-thumbnailer/uninstall.sh || error=1

	if [ $error == 0 ] ; then {
		echo -e "$COLOR_SUCCESS$LANG_SUCCESS_INSTALL$COLOR_DEFAULT"
		echo -e "$COLOR_INFO$LANG_INFOS_HOWTO_UNINSTALL$COLOR_DEFAULT"
	} else {
		echo -e "$COLOR_ERROR$LANG_ERROR_INSTALL$COLOR_DEFAULT"
		exit 5
	} fi

}

uninstall_ct() {
	echo -e "$COLOR_INFO$LANG_INFO_UNINSTALL$COLOR_DEFAULT"
	error=0

	#gconf
	gconf-schemas --unregister /usr/share/cover-thumbnailer/cover-thumbnailer.schema || error=1

	#/usr/share/cover-thumbnailer
	rm -rfv /usr/share/cover-thumbnailer || error=1

	#/usr/share/man/man1
	rm -vf /usr/share/man/man1/cover-thumbnailer.1.gz || error=1
	rm -vf /usr/share/man/man1/cover-thumbnailer-gui.1.gz

	#/usr/share/locale/xx_XX/LC_MESSAGES
	#fr
	rm -vf /usr/share/locale/fr/LC_MESSAGES/cover-thumbnailer-gui.mo

	#/usr/bin
	rm -vf /usr/bin/cover-thumbnailer || error=1
	rm -vf /usr/bin/cover-thumbnailer-gui

	if [ $error == 0 ] ; then {
		echo -e "$COLOR_SUCCESS$LANG_SUCCESS_RM$COLOR_DEFAULT"
	} else {
		echo -e "$COLOR_ERROR$LANG_ERROR_RM$COLOR_DEFAULT"
		exit 6
	} fi
}

#================================================================= MAIN ====
#Select language
if [ `echo $LANG | head -c 2` == fr ] ; then {
	lang_fr
} else {
	lang_en
} fi

echo -e "$COLOR_INFO$LANG_INFOS_WELCOME$COLOR_DEFAULT"

#root ?
if [ `whoami` != root ] ; then {
	echo -e "$COLOR_ERROR$LANG_ERROR_ROOT$COLOR_DEFAULT"
	exit 1
} fi

#We go to the scrip directory
cd ${0%/*} 1> /dev/null 2> /dev/null

install_ct #INSTALL

exit 0


