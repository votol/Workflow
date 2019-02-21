#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description='Generation parameters')
parser.add_argument('-f','--file', required=True, help='generating file')
parser.add_argument('-d','--description', required=True, help='description yaml file with project schema')
args = parser.parse_args()

f= open(args.file,"w")
f.close()
