clean:
	rm -rf dist build

dirs:
	mkdir -p dist build

compile: clean
	scripts/compile.sh

test: test-migration compile
	python3 -m unittest discover -s build

dist: transcompile test
	scripts/dist.sh

install: dist
	scripts/install.sh

package: dist
	scripts/package.sh

init-db: dirs
	scripts/empty-db.sh

test-migration: dirs
	scripts/test-migration.sh

transcompile: compile
	scripts/trans-compile.sh
