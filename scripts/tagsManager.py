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
parser.add_argument('-m','--msg', required=False, help='message for new release made')
args = parser.parse_args()

yaml = ruamel.yaml.YAML()

current_dir = os.getcwd()
os.chdir(args.work)
# getting all tags
process = subprocess.Popen(['git tag'], shell=True, stdout=subprocess.PIPE)
out = process.communicate()[0]

all_tags = out.decode('utf-8').splitlines()
rev_tags = []
search = re.compile(r'^rev[1-9][0-9]*$').search
for element in all_tags:
    if bool(search(element)):
        rev_tags.append(element)

#getting rev tag for current commit
process = subprocess.Popen(['git tag -l --points-at HEAD'], shell=True, stdout=subprocess.PIPE)
out = process.communicate()[0]

cur_tags = out.decode('utf-8').splitlines()
cur_rev = None
for element in cur_tags:
    if element in rev_tags:
        cur_rev = element
        break

# generating new revision
if cur_rev is None:
    if args.msg is None:
        print("\x1b[0;31;40mRelease failed: MSG should be set\x1b[0m", file=sys.stderr)
        exit(-1)

    num_list =[]
    for element in rev_tags:
        num_list.append(int(element.replace("rev","")))

    max_value = None
    if not num_list:
        max_value = 0
    else:
        max_value = max(num_list)

    cur_rev = "rev" + str(max_value + 1)
    process = subprocess.Popen(["git tag -a " + cur_rev + " -m '" + args.msg + "'"], shell=True)
    process.wait()
print(cur_rev)
os.chdir(current_dir)