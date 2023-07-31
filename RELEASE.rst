Things to do while releasing a new version
==========================================

This file is a memo for the maintainer.


0. Checks
---------

* Check Copyright years in ``cover-thumbnailer.py`` (comment and ``__copyright__`` var)
* Check Copyright years in ``cover-thumbnailer-gui.py`` (comment and ``__copyright__`` var)
* Check Copyright years in ``install.sh`` (comment)
* Check Copyright years in ``man/cover-thumbnailer.1`` (copyright section)
* Check Copyright years in ``man/cover-thumbnailer-gui.1`` (copyright section)


1. Release
----------

* Update version number in ``cover-thumbnailer.py`` (``__version__`` var)
* Update version number in ``cover-thumbnailer-gui.py`` (``__version__`` var)
* Update version number in ``install.sh`` (comment)
* Update version number and date in ``man/cover-thumbnailer.1`` (header)
* Update version number and date in ``man/cover-thumbnailer-gui.1`` (header)
* Edit / update changelog in ``README.md``
* Commit / tag (``git commit -m vX.Y.Z && git tag vX.Y.Z && git push && git push --tags``)


2. Publish Github Release
-------------------------

* Make a release on Github
* Add changelog
