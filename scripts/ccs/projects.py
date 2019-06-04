#!/usr/bin/env python3

import os
import ruamel.yaml
import sqlite3
import numpy as np
import ccs.validateInput as validator
from shutil import copyfile
from netCDF4 import Dataset

class DataItem:
    def __init__(self, item_folder):
        self.workFolder = item_folder
        self.itemNumber = item_folder[item_folder.rindex('/') + 1:]
        if not os.path.isfile(item_folder + "/output.nc"):
            raise ValueError("Bad data item - no data file")
        if not os.path.isfile(item_folder + "/config.yaml"):
            raise ValueError("Bad data item - no config file")

        self.rootgrp = Dataset(self.workFolder + "/output.nc", "r", format="NETCDF4")

    def __str__(self):
        return self.itemNumber

    def __repr__(self):
        return self.itemNumber

    def __getitem__(self, index):
        result = np.array(self.rootgrp.variables[index])
        return result

    def __del__(self):
        self.rootgrp.close()

    def outputs(self):
        result = []
        nc_dims = [dim for dim in self.rootgrp.dimensions]
        nc_vars = [var for var in self.rootgrp.variables]
        for var in nc_vars:
            if var not in nc_dims:
                item = {}
                item["Name"] = var
                item["Dimensions"] = []
                for dim in self.rootgrp.variables[var].dimensions:
                    dim_descr = {}
                    dim_descr["Name"] = dim
                    dim_descr["Size"] = self.rootgrp.dimensions[dim].size
                    item["Dimensions"].append(dim_descr)
                item["Size"] = self.rootgrp.variables[var].size
                result.append(item)

        return result


class revision:
    def __init__(self, project, rev, work_dir):
        self.parent = project
        self.revision_id = rev
        self.work_dir = work_dir
        
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                if col[0] == "data":
                    d[col[0]] = DataItem(self.work_dir + "/" + str(row[idx]))
                else:
                    d[col[0]] = row[idx]
            return d
        if not os.path.isfile(self.work_dir + "/db.sqlite"):
            raise ValueError("Invalid data folder - no sqlite database")
        if not os.path.isfile(self.work_dir + "/description.yaml"):
            raise ValueError("Invalid data folder - no description file")
        
        self.connection = sqlite3.connect("file:" + self.work_dir + "/db.sqlite" + "?mode=ro", uri=True)
        self.connection.row_factory = dict_factory
        
        yaml = ruamel.yaml.YAML()
        yaml_stream = open(self.work_dir + "/description.yaml", "r")
        self.config = yaml.load(yaml_stream)
        yaml_stream.close()
        
        if self.config is None:
            self.config = {}
        
    def __del__(self):
        self.connection.close()
    
    def __str__(self):
        return self.internal_to_str()

    def __repr__(self):
        return self.internal_to_str()
    
    def internal_to_str(self):
        result = self.revision_id + " : " + self.config["general"]["comment"]
        return result
    
    def binary(self):
        return self.config["general"]["binary"]
        
    def parameters(self):
        if "parameters" in self.config:
            return self.config["parameters"]
        else:
            loc_cur = self.connection.cursor()
            tmp = loc_cur.execute("PRAGMA table_info(records)")
            result = []
            for item in tmp:
                if item["name"] != "data" and item["name"] != "metadata":
                    result.append(item["name"])

            return result
    
    def validate_input(self, input_map):
        validator.validate(input_map,self.config)
    
    def get_data(self, sql_string):
        loc_cur = self.connection.cursor()
        return loc_cur.execute(sql_string).fetchall()
    
    def contains(self, input_map):
        parameters = validator.getProjectParameters(self.config)
        if len(parameters) != len(input_map):
            raise ValueError("Input does not agree with project description")
        
        for element in parameters:
            if element not in input_map:
                raise ValueError("Input does not agree with project description")
        
        search_string = "SELECT * FROM records WHERE "
        is_first = True
        for key, value in input_map.items():
            if not is_first:
                search_string += " AND "
            else:
                is_first = False
            search_string += key + " = " + str(value)
        
        return (len(self.get_data(search_string)) > 0)
    
    #input is a path wich contans output.nc, and config.yaml with record data
    def add(self, data_folder):
        if not os.path.isfile(data_folder + "/output.nc"):
            raise ValueError("Bad data item - no data file")
        if not os.path.isfile(data_folder + "/config.yaml"):
            raise ValueError("Bad data item - no config file")
        
        
        yaml = ruamel.yaml.YAML()
        yaml_stream = open(data_folder + "/config.yaml", "r")
        config = yaml.load(yaml_stream)
        yaml_stream.close()
        
        if self.contains(config["parameters"]):
            return
        
        loc_conn = sqlite3.connect("file:" + self.work_dir + "/db.sqlite", uri=True)
        loc_cur = loc_conn.cursor()
        
        existing_ids = loc_cur.execute("SELECT MAX(data) FROM records").fetchall()[0]
        
        new_id = 0
        if existing_ids[0] is None:
            new_id = 1
        else:
            new_id = existing_ids[0] + 1
        
        os.mkdir(self.work_dir + "/" + str(new_id))
        copyfile(data_folder + "/output.nc", self.work_dir + "/" + str(new_id) + "/output.nc")
        copyfile(data_folder + "/config.yaml", self.work_dir + "/" + str(new_id) + "/config.yaml")
        
        sql_string1 = "INSERT INTO records ("
        sql_string2 = "VALUES ("
        for key, value in config['parameters'].items():
            sql_string1 += key + ', '
            sql_string2 += str(value) + ', '
        
        loc_cur.execute(sql_string1 + 'data) ' + sql_string2 + str(new_id) + ')')
        loc_conn.commit()
        loc_conn.close()

class project:
    def __init__(self, uuid, work_dir):
        self.uuid = uuid
        self.work_dir = work_dir
        
        yaml = ruamel.yaml.YAML()
        yaml_stream = open(self.work_dir + "/description.yaml", "r")
        description = yaml.load(yaml_stream)
        yaml_stream.close()
        
        self.name = description["name"]
        self.description = description["description"]
    
    def __str__(self):
        return self.internal_to_str()

    def __repr__(self):
        return self.internal_to_str()
    
    def __getitem__(self, index):
        control_rev = self.revisions()
        if index not in control_rev:
            return None
        result = revision(self, index, self.work_dir + "/" + index) 
        return result
    
    def internal_to_str(self):
        result = self.name + " : " + self.description[:100]
        result = result.replace("\n", " ")
        return result
    
    def revisions(self):
        result = []
        for element in os.listdir(self.work_dir):
            if os.path.isdir(self.work_dir + "/" + element):
                result.append(element)
        return result

class Projects:
    def __init__(self):
        self.main_work_dir = os.path.expanduser("~/.ccs/data")
        
    #uuid, name and descr are strings which defines project which will be in the output.
    #For uuid and name coincidence should be full, descr is a string which is a part of 
    #project description
    def projects(self, uuid = None, name = None, descr = None):
        result = []
        for element in os.listdir(self.main_work_dir):
            if os.path.isdir(self.main_work_dir + "/" + element):
                tmp_project = project(element, self.main_work_dir + "/" + element)
                if uuid is not None and uuid != element:
                    continue
                if name is not None and name != tmp_project.name:
                    continue
                if descr is not None and descr not in tmp_project.description:
                    continue
                
                result.append(tmp_project)
        return result
        
