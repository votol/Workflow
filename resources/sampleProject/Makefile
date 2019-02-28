.DEFAULT_GOAL := build_test
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(patsubst %/,%,$(dir $(mkfile_path)))

build_test:
	echo $(current_dir)
	mkdir -p $(current_dir)/workDir/test
	mkdir -p $(current_dir)/workDir/test/build
	cmake -D CMAKE_BUILD_TYPE=Debug -D EXECUTABLE_OUTPUT_PATH=$(current_dir)/workDir/test -D LIBRARY_OUTPUT_PATH=$(current_dir)/workDir/test -B$(current_dir)/workDir/test/build -H$(current_dir)/
	make -C $(current_dir)/workDir/test/build -j `nproc` VERBOSE=1
run_test: build_test
	$(current_dir)/Workflow/scripts/ccs/validateInput.py -i $(current_dir)/test/config.yaml -s $(current_dir)/description.yaml
	$(current_dir)/workDir/test/CalcProj $(current_dir)/test/config.yaml
