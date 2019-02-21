.DEFAULT_GOAL := build_test
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(patsubst %/,%,$(dir $(mkfile_path)))

build_test:
	echo $(current_dir)
	mkdir -p $(current_dir)/workkDir/test
	mkdir -p $(current_dir)/workkDir/test/build
	cmake -D CMAKE_BUILD_TYPE=Debug -D EXECUTABLE_OUTPUT_PATH=$(current_dir)/workkDir/test -D LIBRARY_OUTPUT_PATH=$(current_dir)/workkDir/test -B$(current_dir)/workkDir/test/build -H$(current_dir)/
	make -C $(current_dir)/workkDir/test/build -j `nproc` VERBOSE=1
