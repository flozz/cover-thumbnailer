# Cover Thumbnailer

**Cover thumbnailer** generates folder thumbnails for various file browser on
Linux. It displays music album covers, preview of pictures which are in
a folder and more.

Example with a music folder:

![Screenshot: Nautilus Music folder](./screenshots/screenshot_nautilus_music_folder.png)

Example with a picture folder:

![Screenshot: Nautilus Pictures folder](./screenshots/screenshot_nautilus_picture_folder.png)

Cover Thumbnailer is free software distributed under the GNU GPL v3+ license,
you are free to modify and redistribute it under the terms of the license.

> This repository is the continuation of the [Bazaar / Launchpad][lp] one. This
> project is in "maintenance mode": no new feature will be added, only fixes
> will be released when possible.

> If You are a developer and want to continue the development of this software,
> please [contact me][contact].

[lp]: https://launchpad.net/cover-thumbnailer
[contact]: https://contact.flozz.fr/


## Supported file browser

As far as I know, Cover Thumbnailer currently works with the following file
browsers:

* Nautilus¹ (GNOME file browser)
* Thunar (XFCE file browser)
* Caja (MATE file browser)

----

**NOTE¹: Nautilus support**

Since Nautilus started sandboxing thumbnailers, Cover Thumbnailer do not work
out of the box with this file borwser anymore. A button have been added to the
configuration GUI to generate manually the thumbnails for a specific folder,
see bellow.


## Requirements

Cover Thumbailer dependencies:

* PIL / pillow
* Python bindings for GObject Introspection
* Introspection files for GTK 3.0
* GNU gettext

On Debian / Ubuntu, this can be installed using the following command:

    sudo apt install gettext python3-pil python3-gi gir1.2-gtk-3.0


## Installing Cover Thumbnailer

Clone this repository or [download a zip][gh-zip] from Github:

    git clone https://github.com/flozz/cover-thumbnailer.git

Go to the project folder:

    cd cover-thumbnailer/

Install Cover Thumbnailer using the following command:

    sudo ./install.sh --install


[gh-zip]: https://github.com/flozz/cover-thumbnailer/archive/master.zip


## Uninstalling Cover Thumbnailer

To uninstall Cover thumbnailer, run the following command:

    sudo /usr/share/cover-thumbnailer/uninstall.sh --remove


## Configuring Cover Thumbnailer

Cover Thumbnailer provides a GUI tool to configure it. You will find it in your
application launcher like any other software.

You can also run it with the following command:

    cover-thumbnailer-gui

![Screenshot of Cover Thumnailer configuration tool](./screenshots/screenshot_ctgui.png)


## Generating Thumbnails

If you are using **Thunar** or **Caja**, it should work out of the box: just
open a folder and thumbnails should be generated automatically.

If you are using **Nautilus**, thumbnails cannot be generated automatically in
most recent version of this file browser. You can generate thumbnails manually
using the configuration tool: in the last tab, just click the `"Select a folder
and generate thumbnails"` button.

![Screenshot](./screenshots/screenshot_ctgui_generate.png)

**NOTE:** The thumbnail generation could take a while, just be patient. The
thumbnails should appear after a refresh of the folder.


## Changelog

* **0.8.4:** Old version imported to github
