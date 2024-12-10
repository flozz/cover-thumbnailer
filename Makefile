# Variables
SOFTWARE = $(shell awk -F'[ ="]+' '$$1 == "name" {print $$2;exit}' pyproject.toml)
DESCRIPTION = "directory cover thumbnailer for GTK based file viewers"
VERSION := $(shell awk -F'[ ="]+' '$$1 == "version" {print $$2;exit}' pyproject.toml)
DATE := $(shell date +"%a, %d %b %Y")

INSTALL_PATH ?= /
PACKAGE_PATH ?= ./pkg
LOGFILE ?= install.log

# Tools
PYTHON ?= /usr/bin/python3
PIP := $(PYTHON) -m pip
PKG_CONFIG := pkg-config
GTK_VERSION := gtk+-3.0
GI_MODULE := gi

# Colors for output
RED := \033[1;31m
GREEN := \033[1;32m
NORMAL := \033[0m
BOLD := \033[1m

# Targets
.PHONY: all install remove locale check_dep

all: help

help:
	@echo "$(SOFTWARE) v$(VERSION) - $(DESCRIPTION)"
	@echo ""
	@echo "Targets:"
	@echo -e "\t- $(BOLD)install$(NORMAL)          : Install $(SOFTWARE)"
	@echo -e "\t- $(BOLD)remove$(NORMAL)           : Remove $(SOFTWARE)"
	@echo -e "\t- $(BOLD)locale$(NORMAL)           : Extract strings for translation template"
	@echo -e "\t- $(BOLD)package$(NORMAL)          : Generate a package distribution"
	@echo -e "\t- $(BOLD)publish$(NORMAL)          : Publish current version to git"

check_build_deps:
	@echo -e "$(BOLD) * Checking system dependencies...$(NORMAL)"
	@test -x /usr/bin/xgettext || { echo -e "gettext: $(RED)Missing$(NORMAL)" && exit 1; }
	@echo -e "gettext: $(GREEN)Found$(NORMAL)"
	
check_run_deps:
	@$(PYTHON) --version 2>&1 | grep "^Python 3" >/dev/null || { echo -e "Python 3: $(RED)Missing$(NORMAL)" && exit 1; }
	@echo -e "Python 3: $(GREEN)Found$(NORMAL)"
	@$(PYTHON) -c "import $(GI_MODULE)" 2>/dev/null || { echo -e "PyGObject: $(RED)Missing$(NORMAL)"; exit 1; }
	@echo -e "PyGObject: $(GREEN)Found$(NORMAL)"
	@$(PKG_CONFIG) --exists $(GTK_VERSION) || { echo -e "GTK+3: $(RED)Missing$(NORMAL)"; exit 1; }
	@echo -e "GTK+3: $(GREEN)Found$(NORMAL)"

locale: check_build_deps
	@echo "$(BOLD) * Extracting strings for translation...$(NORMAL)"
	@mkdir -pv ./locale/
	@xgettext -k_ -kN_ -o ./locale/cover-thumbnailer-gui.pot ./cover-thumbnailer-gui.py ./share/cover-thumbnailer-gui.glade
	@for lcfile in $$(find ./locale/ -name "*.po"); do \
		echo -n "   * $$lcfile"; \
		msgmerge --update $$lcfile ./locale/cover-thumbnailer-gui.pot; \
	done

_install: locale
	@echo -e "$(BOLD) * $(action) $(SOFTWARE)...$(NORMAL)"
	@mkdir -pv $(INSTALL_PATH)/usr/bin || { echo -e "$(RED)Error creating directory$(NORMAL)" && exit 1; }
	@sed "s/{{VERSION}}/$(VERSION)/g" ./cover-thumbnailer.py > $(INSTALL_PATH)/usr/bin/cover-thumbnailer
	@chmod 755 $(INSTALL_PATH)/usr/bin/cover-thumbnailer
	@sed "s/{{VERSION}}/$(VERSION)/g" ./cover-thumbnailer-gui.py > $(INSTALL_PATH)/usr/bin/cover-thumbnailer-gui
	@chmod 755 $(INSTALL_PATH)/usr/bin/cover-thumbnailer-gui

	@echo -e "$(BOLD) * Creating man entries...$(NORMAL)"
	@mkdir -pv $(INSTALL_PATH)/usr/share/man/man1
	@sed "s/{{VERSION}}/$(VERSION)/g" ./man/cover-thumbnailer.1\
	  | sed "s/{{DATE}}/$(DATE)/g" > $(INSTALL_PATH)/usr/share/man/man1/cover-thumbnailer.1
	@gzip --best -f $(INSTALL_PATH)/usr/share/man/man1/cover-thumbnailer.1
	@sed "s/{{VERSION}}/$(VERSION)/g" ./man/cover-thumbnailer-gui.1\
	  | sed "s/{{DATE}}/$(DATE)/g" > $(INSTALL_PATH)/usr/share/man/man1/cover-thumbnailer-gui.1
	@gzip --best -f $(INSTALL_PATH)/usr/share/man/man1/cover-thumbnailer-gui.1

	@echo -e "$(BOLD) * Generating locales...$(NORMAL)"
	@for file in $$(find ./locale -name "*.po"); do \
		lang=$$(echo $$file | sed -r 's#./locale/(.*).po#\1#g'); \
		mkdir -pv $(INSTALL_PATH)/usr/share/locale/$$lang/LC_MESSAGES; \
		msgfmt $$file -o $(INSTALL_PATH)/usr/share/locale/$$lang/LC_MESSAGES/cover-thumbnailer-gui.mo; \
	done

	@echo -e "$(BOLD) * $(action) application data...$(NORMAL)"
	@mkdir -pv $(INSTALL_PATH)/usr/share/cover-thumbnailer
	@cp -rv ./share/* $(INSTALL_PATH)/usr/share/cover-thumbnailer
	@mkdir -pv $(INSTALL_PATH)/usr/share/doc/cover-thumbnailer
	@cp -v ./README.md $(INSTALL_PATH)/usr/share/doc/cover-thumbnailer

	@echo -e "$(BOLD) * $(action) application files...$(NORMAL)"
	@mkdir -pv $(INSTALL_PATH)/usr/share/applications
	@cp -v ./freedesktop/cover-thumbnailer-gui.desktop $(INSTALL_PATH)/usr/share/applications/cover-thumbnailer-gui.desktop
	@mkdir -pv $(INSTALL_PATH)/usr/share/thumbnailers
	@cp -v ./freedesktop/cover.thumbnailer $(INSTALL_PATH)/usr/share/thumbnailers/cover.thumbnailer
	@echo -e "$(GREEN)$(SOFTWARE) $(action_end) successfully$(NORMAL)"

install: action:="Installing"
install: action_end:="installed"
install: check_run_deps _install

remove:
	@echo "$(BOLD) * Removing $(SOFTWARE)...$(NORMAL)"
	@rm -fv /usr/share/applications/cover-thumbnailer-gui.desktop
	@rm -rfv /usr/share/cover-thumbnailer
	@rm -rfv /usr/share/doc/cover-thumbnailer
	@rm -vf /usr/share/man/man1/cover-thumbnailer.1.gz
	@rm -vf /usr/share/man/man1/cover-thumbnailer-gui.1.gz
	@find /usr/share/locale/ -name cover-thumbnailer-gui.mo -exec rm -v '{}' ';'
	@rm -vf /usr/bin/cover-thumbnailer
	@rm -vf /usr/bin/cover-thumbnailer-gui
	@rm -vf /usr/share/thumbnailers/cover.thumbnailer
	@echo "$(GREEN)$(SOFTWARE) removed successfully$(NORMAL)"

package: INSTALL_PATH:=$(PACKAGE_PATH)
package: action:="Packaging"
package: action_end:="packaged"
package:
	@mkdir -pv $(PACKAGE_PATH)
package: _install

clean:
	@rm -rf $(PACKAGE_PATH)

publish:
	@git commit -m v$(VERSION) && git tag v$(VERSION) && git push && git push --tags
