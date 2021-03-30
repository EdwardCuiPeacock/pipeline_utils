#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:33:59 2021

Recipe utilities

@author: edwardcui
"""
import os
import subprocess
from typing import Dict
import yaml

def get_metadata(metadata_file: str) -> Dict:
    """Return the metadata dictionary."""
    with open(metadata_file, "r") as fid:
        metadata = yaml.safe_load(fid)

    return metadata


def get_config(metadata: Dict, field="system_configurations") -> Dict:
    """Return the pipeline config dictionary."""
    config = {
        k: v_dict["value"] for k, v_dict in metadata[field].items()
    }
    return config


def run_shell_command(command, verbose=True):
    """Run a command and get the outputs."""
    process = subprocess.Popen(command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        encoding="utf-8", 
        errors="replace")

    cached_output = []
    
    while True: # print progress real time
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break

        if output and verbose:
            print(output.strip(), flush=True)

        # save output
        cached_output.append(output.strip())
    
    cached_output = os.linesep.join(cached_output)

    return process.returncode, cached_output

if __name__ == '__main__':
    metadata = yaml.safe_load(open("tfx_template/metadata.yaml", "r"))
    config = get_config(metadata)
