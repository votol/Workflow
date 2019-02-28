#!/usr/bin/env python3

import os
import ruamel.yaml
import argparse
import sys
work_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, work_dir)
import general
from typing import List
from typing import Dict

class PropertyDef:
    name = ""
    optional = False
    list = False
    #type should take values: string, int, float, boolean.
    type = "string"


def getProjectProperties(schema_pro: dict) -> Dict[str, PropertyDef]:
    if "properties" not in schema_pro:
        raise ValueError("Bad project description: no properties section")
    if not isinstance(schema_pro["parameters"], list):
        raise ValueError("Bad project description: properties section should be a list")

    supported_types = ["string", "int", "float", "boolean"]

    properties_pro = {}
    #adding build-in properties
    element = PropertyDef()
    element.name = "output_path"
    properties_pro["output_path"] = element
    element = PropertyDef()
    element.name = "tmp_path"
    element.optional = True
    properties_pro["tmp_path"] = element
    for element in schema_pro["properties"]:
        if not isinstance(element, dict):
            raise ValueError("Bad project description: property should be described by map")
        if "name" not in element:
            raise ValueError("Bad project description: property without name")
        if element["name"] in properties_pro:
            raise ValueError("Bad project description: duplicating property")
        if not general.checkName(element["name"]):
            raise RuntimeError("Bad project description: bad name " + element["name"])
        if "type" not in element:
            raise ValueError("Bad project description: type is not defined for property " + element["name"])
        if element["type"] not in supported_types:
            raise ValueError("Bad project description: property " + element["name"] + " has not supported type")
        adding_element = PropertyDef()
        adding_element.name = element["name"]
        adding_element.type = element["type"]
        if "list" in element:
            if not isinstance(element["list"], bool):
                raise ValueError("Bad project description: property description field \"list\" of " + element["name"] + " should be boolean")
            adding_element.list = element["list"]
        if "optional" in element:
            if not isinstance(element["optional"], bool):
                raise ValueError("Bad project description: property description field \"optional\" of " + element["name"] + " should be boolean")
            adding_element.optional = element["optional"]

        properties_pro[element["name"]] = adding_element

    return properties_pro

def getProjectParameters(schema_par: dict) -> List[str]:
    if "parameters" not in schema_par:
        raise ValueError("Bad project description: no parameters section")
    if not isinstance(schema_par["parameters"], list):
        raise ValueError("Bad project description: parameters section should be a list")

    parameters_par = []
    for element in schema_par["parameters"]:
        if not isinstance(element, dict):
            raise ValueError("Bad project description: parameter should be described by map")
        if "name" not in element:
            raise ValueError("Bad project description: parameter without name")
        if element["name"] in parameters_par:
            raise ValueError("Bad project description: duplicating parameters")
        if not general.checkName(element["name"]):
            raise RuntimeError("Bad project description: bad name " + element["name"])
        parameters_par.append(element["name"])
    return parameters_par

def validate(input: dict, schema: dict) -> list:
    if not isinstance(input, dict):
        raise ValueError("Input should be a dictionary")
    if not isinstance(schema, dict):
        raise ValueError("Project description should be a dictionary")

    ### Validate parameters first
    #get required parameters from schema
    parameters = getProjectParameters(schema)
    #validate parameters
    if "parameters" not in input:
        raise ValueError("Bad input: no parameters section")
    if not isinstance(input["parameters"], dict):
        raise ValueError("Bad input: parameter section should be a map {parameter_name : float value}")
    for element in parameters:
        if element not in input["parameters"]:
            raise ValueError("Bad input: parameter " + element + " not found")
        if not isinstance(input["parameters"][element], float) and not isinstance(input["parameters"][element], int):
            raise ValueError("Bad input: parameter value should be float")
        if isinstance(input["parameters"][element], bool):
            raise ValueError("Bad input: parameter value should be float")

    ### Validate properties
    type_checkers = {
        "string": lambda x: isinstance(x, str),
        "int": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "float": lambda x: (isinstance(x, float) or isinstance(x, int)) and not isinstance(x, bool),
        "boolean": lambda x: isinstance(x, bool)
    }

    # get required properties from schema
    properties = getProjectProperties(schema)
    # validate properties
    if "properties" not in input:
        raise ValueError("Bad input: no properties section")
    if not isinstance(input["properties"], dict):
        raise ValueError("Bad input: property section should be a map {property_name : value}")
    for key, descr in properties.items():
        if key not in input["properties"]:
            if not descr.optional:
                raise ValueError("Bad input: property " + key + " not found")
            else:
                continue
        if descr.list:
            if not isinstance(input["properties"][key], list):
                raise ValueError("Bad input: property " + key + " should be list")
            for value in input["properties"][key]:
                if not type_checkers[descr.type](value):
                    raise ValueError("Bad input: one of the values of property " + key + " has bad type")
        else:
            if not type_checkers[descr.type](input["properties"][key]):
                raise ValueError("Bad input: property " + key + " has bad type")

    # special validations
    if not os.path.isdir(os.path.expanduser(input["properties"]["output_path"])):
        raise ValueError("Bad input: property output_path should point to an existing path")
    if "tmp_path" in input["properties"]:
        if not os.path.isdir(os.path.expanduser(input["properties"]["tmp_path"])):
            raise ValueError("Bad input: property tmp_path should point to an existing path")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Validation parameters')
        parser.add_argument('-i', '--input', required=True, help='input file to be checked')
        parser.add_argument('-s', '--schema', required=True, help='description yaml file with project schema')
        args = parser.parse_args()

        yaml = ruamel.yaml.YAML()

        yaml_stream = open(args.schema, "r")
        main_description = yaml.load(yaml_stream)
        yaml_stream.close()

        yaml_stream = open(args.input, "r")
        main_input= yaml.load(yaml_stream)
        yaml_stream.close()

        validate(main_input, main_description)

    except Exception as e:
        print("\x1b[0;31;40mValidation failed: " + str(e) + "\x1b[0m")
        exit(-1)