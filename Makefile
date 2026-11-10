PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
DOCDIR ?= $(PREFIX)/share/doc/shade-cli
LICDIR ?= $(PREFIX)/share/licenses/shade-cli

.PHONY: all install uninstall test

all:
	@echo "Nada que compilar. Ejecuta 'sudo make install' para instalar shade-cli en $(BINDIR)."

test:
	python3 -m unittest discover -s tests

install:
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 bin/shade-cli $(DESTDIR)$(BINDIR)/shade-cli
	install -d $(DESTDIR)$(DOCDIR)
	install -m 644 README.md $(DESTDIR)$(DOCDIR)/README.md
	install -d $(DESTDIR)$(LICDIR)
	install -m 644 LICENSE $(DESTDIR)$(LICDIR)/LICENSE
	@echo "shade-cli instalado con éxito en $(BINDIR)/shade-cli"

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/shade-cli
	rm -rf $(DESTDIR)$(DOCDIR)
	rm -rf $(DESTDIR)$(LICDIR)
	@echo "shade-cli desinstalado de $(BINDIR)/shade-cli"
