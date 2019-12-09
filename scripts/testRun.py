#!/usr/bin/env python3

import os
import argparse
import ruamel.yaml
import shutil
import time
import subprocess
import sys
import uuid
work_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, work_dir)
import ccs.validateInput as validation

parser = argparse.ArgumentParser(description='Run parameters')
parser.add_argument('-w','--work', required=True, help='root folder of the project')
args = parser.parse_args()

yaml = ruamel.yaml.YAML()

run_dir = args.work + "/workDir/test"

try:
    # preparing
    yaml_stream = open(args.work + "/description.yaml", "r")
    description = yaml.load(yaml_stream)
    yaml_stream.close()

    yaml_stream = open(args.work + "/test/config.yaml", "r")
    input = yaml.load(yaml_stream)
    yaml_stream.close()

    if (not "properties" in input) or (not isinstance(input["properties"], dict)):
        input["properties"] = {}

    tmp_dir = None
    if not os.path.exists("/tmp/ccs"):
        os.makedirs("/tmp/ccs")
    
    tmp_dir = "/tmp/ccs/" + str(uuid.uuid4())
    os.makedirs(tmp_dir)

    input["properties"]["output_path"] = run_dir

    if not (tmp_dir is None):
        input["properties"]["tmp_path"] = tmp_dir

    if os.path.isfile(run_dir  + "/output.nc"):
        os.remove(run_dir  + "/output.nc")
    validation.validate(input, description)

    with open(run_dir + "/config.yaml", "w") as outfile:
        yaml.dump(input, outfile)

    # running
    with open(run_dir + "/log", "a") as log_file:
        log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ': ' + 'start task \n')
        log_file.flush()
        proc = subprocess.Popen([run_dir+"/CalcProj", run_dir + '/config.yaml'], stdout=log_file,
                                stderr=log_file)
        result = proc.wait()
        log_file.write(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ': ' + 'finished task \n')

    if result == 0:
        if not (tmp_dir is None):
            shutil.rmtree(tmp_dir)
    else:
        raise RuntimeError("calculation finished with error: " + str(result))

except Exception as e:
    print("\x1b[0;31;40mFailed to run: " + str(e) + "\x1b[0m")
    exit(-1)


