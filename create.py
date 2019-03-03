#!/usr/bin/env python3

import argparse
import ruamel.yaml
import os
import uuid
import shutil
import subprocess
import urllib.request as urllib
import base64, json
import scripts.ccs.general as ccs


parser = argparse.ArgumentParser(description='Creation parameters')
parser.add_argument('-n','--name', required=True, help='name of new project')
parser.add_argument('-r', action='store_true', help='defines if the project should be added to github')
args = parser.parse_args()

#prepairing
if not ccs.checkName(args.name):
    print("Bad project name.")
    exit(-1)

if os.path.isdir(args.name):
    print("Sorry but project with given name already exists.")
    exit(-1)
if args.r:
    #getting token
    username = "votol"
    token = os.environ["GH_TOKEN"]
    url = "https://api.github.com/user/repos"
    #checking if the project already exists
    request = urllib.Request(url)
    b64auth = base64.standard_b64encode(bytes("%s:%s" % (username, token), 'UTF-8'))
    request.add_header("Authorization", "Basic %s" %  b64auth.decode('UTF-8'))
    result = json.loads(urllib.urlopen(request).read().decode())
    for element in result:
        if "votol/" not in element["full_name"]:
            continue
        project_name = element["full_name"].replace("votol/", "")
        if project_name == args.name:
            print("Sorry, project with this name exists on github")
            exit(-1)

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
work_dir = os.path.dirname(os.path.realpath(__file__))
current_dir = os.getcwd()

os.mkdir(args.name)
if args.r:
    url = "https://api.github.com/user/repos"
    param_map = {"name" : args.name, "has_wiki": "false"}
    param_json = json.dumps(param_map).encode('utf8')
    request = urllib.Request(url, data=param_json, headers={'content-type': 'application/json'})
    request.add_header("Authorization", "Basic %s" % b64auth.decode('UTF-8'))
    response = urllib.urlopen(request)
    subprocess.run(["git clone git@github.com:votol/" + args.name + ".git"], shell=True)

else:
    os.mkdir(args.name)

#creating folder structure
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

    #generate base main.cpp
    with open(args.name + "/src/main.cpp", 'w') as outfile:
        #for the moment I will do it so, but maybe I should find better way
        outfile.write("#include <iostream>\n")
        outfile.write("#include \"yaml-cpp/yaml.h\"\n")
        outfile.write("#include \"schema.h\"\n")
        outfile.write("#include \"NetCdfWriter.h\"\n\n")
        outfile.write("int main(int argc, char **argv)\n{\n")
        outfile.write("    YAML::Node config = YAML::LoadFile(argv[1]);\n")
        outfile.write("    std::string output_dir = config[\"properties\"]\n")
        outfile.write("								  [" + args.name + "Schema::PROPERTY_output_path].as<std::string>();\n")
        outfile.write("    std::vector<std::unique_ptr<IOutput> > outputs(0);\n")
        outfile.write("    NetCdfWriter netcdf_writer_instance(\n")
        outfile.write("			output_dir + \"/output.nc\", outputs, 0);\n")
        outfile.write("    return 0;\n}\n")


    #generate .gitignore
    with open(args.name + "/.gitignore", 'w') as outfile:
        outfile.write("workDir\n")
    
    #copying files
    shutil.copyfile(work_dir + "/resources/sampleProject/CMakeLists.txt", args.name + '/src/CMakeLists.txt')
    shutil.copyfile(work_dir + "/resources/sampleProject/OutputInterface.h", args.name + '/src/OutputInterface.h')
    shutil.copyfile(work_dir + "/resources/sampleProject/NetCdfWriter.h", args.name + '/src/NetCdfWriter.h')
    shutil.copyfile(work_dir + "/resources/sampleProject/NetCdfWriter.cpp", args.name + '/src/NetCdfWriter.cpp')
    shutil.copyfile(work_dir + "/resources/sampleProject/Makefile", args.name + '/Makefile')

    #some things with git
    current_dir = os.getcwd()
    os.chdir(current_dir + "/" + args.name)
    if not args.r:
        subprocess.run(["git init"], shell=True)

    subprocess.run(["git submodule add git@github.com:votol/Workflow.git Workflow"], shell=True)
    subprocess.run(["git add ."], shell=True)
    subprocess.run(["git commit -m \"initial commit\""], shell=True)

    if args.r:
        subprocess.run(["git push -u origin master"], shell=True)
except subprocess.CalledProcessError as e:
    print("Failed to create project: " + e.output)
    os.chdir(current_dir)
    shutil.rmtree(args.name)
except Exception as e:
    print("Failed to create project: " + str(e))
    os.chdir(current_dir)
    shutil.rmtree(args.name)

