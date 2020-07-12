# Cover Thumbnailer

> This repository is the continuation of the [Bazaar / Launchpad][lp] one. This
> is legacy code that have not been maintained for years, so it may not work
> out of the box and fixes can take time to be released.

Cover thumbnailer is a small Python script which displays music album covers,
preview of pictures which are in a folder and more.

Supported file browser:

* Nautilus¹ (GNOME file browser)
* Thunar (XFCE file browser)
* Caja (MATE file browser)

----

**NOTE¹: Nautilus support**

Since Nautilus started sandboxing thumbnailers, Cover Thumbnailer do not work
out of the box with this file borwser anymore. A button have been added to the
configuration GUI to generate manually the thumbnails for a specific folder.

----

Cover Thumbnailer is free software distributed under the GNU GPL v3+ license,
you are free to modify and redistribute it under the terms of the license.


[lp]: https://launchpad.net/cover-thumbnailer


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

Install Cover thumbnailer using the following command:

    sudo ./install.sh --install


[gh-zip]: https://github.com/flozz/cover-thumbnailer/archive/master.zip


## Uninstalling Cover Thumbnailer

To uninstall Cover thumbnailer, run the following command:

    sudo /usr/share/cover-thumbnailer/uninstall.sh --remove


## Configuring Cover Thumbnailer

Cover Thumbnailer provides a GUI tool to configure it. Just run the following
command to start the tool:

    cover-thumbnailer-gui


## Changelog

* **0.8.4:** Old version imported to github
