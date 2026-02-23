PACKAGES_FILE ?= packages.txt
PACKAGES := $(shell grep -Ev '^\s*#|^\s*$$' $(PACKAGES_FILE))

.PHONY: show-packages install-packages

show-packages:
	@echo "$(PACKAGES)"

install-packages:
	@echo "apk add $(PACKAGES)"
	@apk add $(PACKAGES)
