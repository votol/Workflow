#!/usr/bin/env python3

import os
import ruamel.yaml

class revision:
    def __init__(self, project, rev, work_dir):
        self.parent = project
        self.revision_id = rev
        self.work_dir = work_dir

class project:
    def __init__(self, uuid, work_dir):
        self.uuid = uuid
        self.work_dir = work_dir
    
    def __str__(self):
        return self.internal_to_str()

    def __repr__(self):
        return self.internal_to_str()
    
    def internal_to_str(self):
        yaml = ruamel.yaml.YAML()
        yaml_stream = open(self.work_dir + "/description.yaml", "r")
        description = yaml.load(yaml_stream)
        yaml_stream.close()
        result = description["name"] + " : " + description["description"][:100]
        result = result.replace("\n", " ")
        return result


class Projects:
    def __init__(self):
        self.main_work_dir = os.path.expanduser("~/.ccs/data")
        
    def projects(self, uuid = None, name = None, descr = None):
        result = []
        for element in os.listdir(self.main_work_dir):
            if os.path.isdir(self.main_work_dir + "/" + element):
                if uuid is not None and uuid != element:
                    continue
                result.append(project(element, self.main_work_dir + "/" + element))
        return result
        
