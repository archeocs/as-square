clean:
	rm -rf dist build

dirs:
	mkdir -p dist build

compile: clean
	scripts/compile.sh

test: compile
	python3 -m unittest discover -s build

dist: transcompile test
	scripts/dist.sh

install: dist
	scripts/install.sh

package: dist
	scripts/package.sh

init-db: dirs
	scripts/empty-db.sh

transcompile: compile
	scripts/trans-compile.sh
