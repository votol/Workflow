#!/usr/bin/env python3

import argparse
import ruamel.yaml
import os
import uuid
import shutil

parser = argparse.ArgumentParser(description='Creation parameters')
parser.add_argument('-n','--name', required=True, help='name of new project')
args = parser.parse_args()

#prepairing
if os.path.isdir(args.name):
    print("Sorry but project with given name already exists.")
    exit(-1)
yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
work_dir = os.path.dirname(os.path.realpath(__file__))

#creating folder structure
os.mkdir(args.name)
os.mkdir(args.name + "/src")
os.mkdir(args.name + "/workkDir")
os.mkdir(args.name + "/test")


#base description yaml

yaml_stream = open(work_dir + "/resources/description.yaml", "r")
description = yaml.load(yaml_stream)
yaml_stream.close()

description["general"]["uuid"] = str(uuid.uuid4())
description["general"]["name"] = args.name

with open(args.name + "/description.yaml", "w") as outfile:
    yaml.dump(description, outfile)

#generate base CMakeLists.txt
with open(args.name + "/CMakeLists.txt", 'w') as outfile:
    outfile.write("cmake_minimum_required(VERSION 3.0)")
    outfile.write("project(CalcProj)\n")
    outfile.write("add_subdirectory(src)")

#copying files
shutil.copyfile(work_dir + "/resources/sampleProject/CMakeLists.txt", args.name + '/src/CMakeLists.txt')
shutil.copyfile(work_dir + "/resources/sampleProject/Makefile", args.name + '/Makefile')