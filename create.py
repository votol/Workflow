#!/usr/bin/env python3

import argparse
import ruamel.yaml
import os
import uuid
import shutil
import subprocess
import scripts.ccs.general as ccs


parser = argparse.ArgumentParser(description='Creation parameters')
parser.add_argument('-n','--name', required=True, help='name of new project')
args = parser.parse_args()

#prepairing
if not ccs.checkName(args.name):
    print("Bad project name.")
    exit(-1)

if os.path.isdir(args.name):
    print("Sorry but project with given name already exists.")
    exit(-1)
yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
work_dir = os.path.dirname(os.path.realpath(__file__))
current_dir = os.getcwd()

#creating folder structure
os.mkdir(args.name)
os.mkdir(args.name + "/src")
os.mkdir(args.name + "/workDir")
os.mkdir(args.name + "/test")

try:
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
        outfile.write("cmake_minimum_required(VERSION 3.0)\n")
        outfile.write("project(CalcProj)\n\n")
        outfile.write("add_subdirectory(src)\n")

    #generate base main file
    with open(args.name + "/src/main.cpp", 'w') as outfile:
        outfile.write("#include \"schema.h\"\n\n")
        outfile.write("int main(int argc, char **argv)\n{\n")
        outfile.write("    return 0;\n}\n")

    #generate .gitignore
    with open(args.name + "/.gitignore", 'w') as outfile:
        outfile.write("workDir\n")
    
    #copying files
    shutil.copyfile(work_dir + "/resources/sampleProject/CMakeLists.txt", args.name + '/src/CMakeLists.txt')
    shutil.copyfile(work_dir + "/resources/sampleProject/Makefile", args.name + '/Makefile')

    #some things with git
    current_dir = os.getcwd()
    os.chdir(current_dir + "/" + args.name)
    subprocess.run(["git init"], shell=True)
    subprocess.run(["git submodule add git@github.com:votol/Workflow.git Workflow"], shell=True)
    subprocess.run(["git add ."], shell=True)
    subprocess.run(["git commit -m \"initial commit\""], shell=True)
    os.chdir(current_dir)
except subprocess.CalledProcessError as e:
    print("Failed to create project: " + e.output)
    os.chdir(current_dir)
    shutil.rmtree(args.name)
except Exception as e:
    print("Failed to create project: " + str(e))
    os.chdir(current_dir)
    shutil.rmtree(args.name)

