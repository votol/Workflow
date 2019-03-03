#!/usr/bin/env python3
import os
import argparse
import ruamel.yaml
import re
import subprocess
import sys
work_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, work_dir)

parser = argparse.ArgumentParser(description='Run parameters')
parser.add_argument('-w','--work', required=True, help='root folder of the project')
args = parser.parse_args()

yaml = ruamel.yaml.YAML()

current_dir = os.getcwd()
os.chdir(args.work)

process = subprocess.Popen(['git tag'], shell=True, stdout=subprocess.PIPE)
out = process.communicate()[0]

all_tags = out.decode('utf-8').splitlines()
all_tags = ["tmp1", "tmp_rev1", "rev1", "rev1.1", "rev12345", "rev1234asda", "rev", "rev012"]
rev_tags = []
search = re.compile(r'^rev[1-9][0-9]*$').search
for element in all_tags:
    if bool(search(element)):
        rev_tags.append(element)
print(rev_tags)
os.chdir(current_dir)