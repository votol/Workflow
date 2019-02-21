#!/usr/bin/env python3
import re

def checkName(in_str):
    if len(in_str) < 1 :
        return False
    search = re.compile(r'[^a-zA-Z0-9_]').search
    return not bool(search(in_str))