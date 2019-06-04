#!/usr/bin/env python3

import ccs.projects as pr

def buildTask(revision, data_list, property_map = None):
    result = []
    if property_map is None:
        local_property_list = {}
    else:
        local_property_list = property_map.copy()
    
    #adding build in properties which will be managed in calculator
    local_property_list["tmp_path"] = "/tmp"
    local_property_list["output_path"] = "/tmp"
    local_property_list["cuda_device"] = 0
    
    class parameterBuilder:
        def __init__(self, parameters_list):
            self.next = None
            self.parameters_list = parameters_list
            self.length = len(parameters_list)
            self.index = 0
        
        def build(self):
            if self.next == None:
                if self.index == self.length:
                    self.index = 0
                    return None
                else:
                    self.index += 1
                    return self.parameters_list[self.index -1].copy()
            else:
                result = self.next.build()
                if result == None:
                    self.index += 1
                    if self.index == self.length:
                        self.index = 0
                        return None
                    result = self.next.build()
                result.update(self.parameters_list[self.index])
                return result
            
    builders = []
    for element in data_list:
        if len(element) == 0:
            return []
        builder = parameterBuilder(element)
        if len(builders) != 0:
            builders[-1].next = builder
        builders.append(builder)
    
    if len(builders) == 0 :
        return []
    
    while True:
        tmp_result = builders[0].build()
        if tmp_result == None:
            break
        adding_element = {}
        adding_element["config"] = {}
        adding_element["config"]["parameters"] = tmp_result
        adding_element["config"]["properties"] = local_property_list.copy()
        revision.validate_input(adding_element["config"])
        adding_element["revision"] = revision
        result.append(adding_element)
        
    return result


class calculator:
    def __init__(self, node_list, revision):
        return
    
    def calculate(self):
        return