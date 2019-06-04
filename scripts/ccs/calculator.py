#!/usr/bin/env python3

import os
import shutil
import uuid
import subprocess
import threading
import queue
import ruamel.yaml
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
        if revision.contains(tmp_result):
            continue
        
        adding_element = {}
        adding_element["config"] = {}
        adding_element["config"]["parameters"] = tmp_result
        adding_element["config"]["properties"] = local_property_list.copy()
        revision.validate_input(adding_element["config"])
        adding_element["revision"] = revision
        result.append(adding_element)
        
    return result


class Calculator:
    def __init__(self, node_list):
        self.nodes = node_list
    
    def calculate(self, items):
        def NodeFunc(node_id):
            while True:
                try:
                    work_item = input_queue.get_nowait()
                except queue.Empty:
                    output_queue.put(None)
                    break 
                work_dir = "/tmp/ccs/" + str(uuid.uuid4())
                os.mkdir(work_dir)
                os.mkdir(work_dir + "/tmp")
                work_item["config"]["properties"]["cuda_device"] = node_id
                work_item["config"]["properties"]["output_path"] = work_dir
                work_item["config"]["properties"]["tmp_path"] = work_dir + "/tmp"
                yaml = ruamel.yaml.YAML()
                with open(work_dir + "/config.yaml", "w") as outfile:
                    yaml.dump(work_item["config"], outfile)
                
                proc = subprocess.Popen([work_item["revision"].binary(), work_dir + "/config.yaml"])
                result = proc.wait()
                answer = {}
                answer["directory"] = work_dir
                answer["revision"] = work_item["revision"]
                answer["status"] = result 
                output_queue.put(answer)
        
        if not os.path.exists("/tmp/ccs"):
            os.makedirs("/tmp/ccs")
        
        input_queue = queue.SimpleQueue()
        output_queue = queue.SimpleQueue()
        
        for item in items:
            input_queue.put(item)
        
        threads = []
        for item in self.nodes:
            t = threading.Thread(target=NodeFunc, args = (item,))
            t.start()
            threads.append(t)
        
        finished_nodes = 0
        while True:
            res_element = output_queue.get()
            if res_element is None:
                finished_nodes += 1
                if finished_nodes == len(self.nodes):
                    break
                continue
            if res_element["status"] == 0:
                res_element["revision"].add(res_element["directory"])
                
            shutil.rmtree(res_element["directory"])
            
            
        for item in threads:
            item.join()
            