clean:
	rm -rf dist build

compile: clean
	scripts/compile.sh

test: compile
	python3 -m unittest discover -s build

dist: test
	scripts/dist.sh

install: dist
	scripts/install.sh

package: dist
	scripts/package.sh
