#!/usr/bin/env python3
import os
import argparse
import ruamel.yaml
import sys
work_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, work_dir)
import ccs.general as ccs
import ccs.validateInput as validation

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

        properties = validation.getProjectProperties(description)
        for element in properties:
            outfile.write("    const char * const PROPERTY_" + element + "= \"" + element + "\";\n")

        parameters = validation.getProjectParameters(description)
        for element in parameters:
            outfile.write("    const char * const PARAMETER_" + element + "= \"" + element + "\";\n")

        if "outputs" not in description:
            raise ValueError("Bad project description: no outputs section")
        if not isinstance(description["outputs"], list):
            raise ValueError("Bad project description: outputs section should be a list")
        outputs = []
        for element in description["outputs"]:
            if not isinstance(element, dict):
                raise ValueError("Bad project description: output should be described by map")
            if "name" not in element:
                raise ValueError("Bad project description: output without name")
            if element["name"] in outputs:
                raise RuntimeError("Bad project description: duplicating output")
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
