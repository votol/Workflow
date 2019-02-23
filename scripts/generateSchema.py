#!/usr/bin/env python3
import os
import argparse
import ruamel.yaml
import ccs.general as ccs

parser = argparse.ArgumentParser(description='Generation parameters')
parser.add_argument('-f','--file', required=True, help='generating file')
parser.add_argument('-d','--description', required=True, help='description yaml file with project schema')
args = parser.parse_args()

yaml = ruamel.yaml.YAML()

yaml_stream = open(args.description, "r")
description = yaml.load(yaml_stream)
yaml_stream.close()

if not ccs.checkName(description["general"]["name"]):
    print("Bad project name.")
    exit(-1)

try:
    with open(args.file,"w") as outfile:
        outfile.write("#pragma once\n")
        outfile.write("namespace " + description["general"]["name"] + "Schema\n{\n")

        outfile.write("    const char * const NAME = \"" + description["general"]["name"] + "\";\n")
        outfile.write("    const char * const UUID = \"" + description["general"]["uuid"] + "\";\n")

        properties = ["output_path", "tmp_path"]
        outfile.write("    const char * const PROPERTY_output_path = \"output_path\";\n")
        outfile.write("    const char * const PROPERTY_tmp_path = \"tmp_path\";\n")
        for element in description["properties"]:
            if element["name"] in properties:
                raise RuntimeError("Bad schema: duplicating properties")
            if not ccs.checkName(element["name"]):
                raise RuntimeError("Bad property name: " + element["name"])
            outfile.write("    const char * const PROPERTY_" + element["name"] + "= \"" + element["name"] + "\";\n")
            properties.append(element["name"])

        parameters = []
        for element in description["parameters"]:
            if element["name"] in parameters:
                raise RuntimeError("Bad schema: duplicating parameters")
            if not ccs.checkName(element["name"]):
                raise RuntimeError("Bad parameter name: " + element["name"])
            outfile.write("    const char * const PARAMETER_" + element["name"] + "= \"" + element["name"] + "\";\n")
            parameters.append(element["name"])

        outputs = []
        for element in description["outputs"]:
            if element["name"] in parameters:
                raise RuntimeError("Bad schema: duplicating parameters")
            if not ccs.checkName(element["name"]):
                raise RuntimeError("Bad output name: " + element["name"])
            outfile.write("    const char * const OUTPUT_" + element["name"] + "= \"" + element["name"] + "\";\n")
            outputs.append(element["name"])

        outfile.write("}\n")
except RuntimeError as e:
    print(str(e))
    if os.path.isfile(args.file):
        os.remove(args.file)
    exit(-1)
