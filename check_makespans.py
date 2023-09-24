#!/usr/bin/env python3 

import sys
import subprocess
import matplotlib.pyplot as plt


versions = sys.argv[1:len(sys.argv)]

num_cores_per_host = 8
min_core_speed = 100
max_core_speed = 200
num_links = 100
min_bandwidth = 100
max_bandwidth = 200
route_length = 10
min_computation = 100
max_computation = 100
min_data_size = 100
max_data_size = 100

energy_plugins = {
        "v3_10":"", 
        "v3_12":"", 
        "v3_14":"", 
        "v3_15":"",  
        "v3_16":"",  
        "v3_20":"--cfg=plugin:host_energy", 
        "v3_24":"--cfg=plugin:host_energy", 
        "v3_34":"--cfg=plugin:host_energy"}


num_workers = 100
num_tasks   = 2000

for version in versions:

    # RUN EXPERIMENT
    num_tasks = num_workers * 200
    num_hosts = int(1 + num_workers / num_cores_per_host)

    seed = 0

    command = f"docker run -it --rm -w /home/simgrid/build_simgrid_{version}/ -v `pwd`:/home/simgrid simgrid_{version} ./master_worker_{version} {num_hosts} {num_cores_per_host} {min_core_speed} {max_core_speed} {num_links} {min_bandwidth} {max_bandwidth} {route_length} {num_workers} {num_tasks} {min_computation} {max_computation} {min_data_size} {max_data_size} {seed} {energy_plugins[version]}"

    try:
        output = subprocess.check_output(command, shell=True).decode('utf-8').splitlines()
    except Exception:
        sys.stderr.write(version + ": Execution failed\n")
        print(command)
        continue
    for line in output:
        if "ALL DONE" in line:
            print(version + ": " + line.split(" ")[1].split("]")[0])



