#!/usr/bin/env python3 

import sys
import subprocess
import matplotlib.pyplot as plt

try:
    num_workers = int(sys.argv[1])
    num_tasks = int(sys.argv[2])
except Exception:
    sys.stderr.write(
        f"Usage: {sys.argv[0]} <num workers> <num tasks> <version> ... <version>\n")
    sys.exit(1)

versions = sys.argv[3:len(sys.argv)]

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
        "v3_34":"--cfg=plugin:host_energy",
        "v3_35":"--cfg=plugin:host_energy"
        }

line_styles = {
        "v3_10":":", 
        "v3_12":"-", 
        "v3_14":":", 
        "v3_15":"-", 
        "v3_16":"-", 
        "v3_20":".", 
        "v3_24":"-.", 
        "v3_34":"--",
        "v3_35":"--"
        }

#stack_size_in_kb = 100
#"--cfg=contexts/stack-size:{stack_size_in_kb}"

results = {}
for version in versions:
    results[version] = {}

for version in versions:

    num_hosts = int(1 + num_workers / num_cores_per_host)

    times = []
    mems = []

    command = f"docker run -it --rm -w /home/simgrid/build_simgrid_{version}/ -v `pwd`:/home/simgrid simgrid_{version} /usr/bin/time -v ./master_worker_{version} {num_hosts} {num_cores_per_host} {min_core_speed} {max_core_speed} {num_links} {min_bandwidth} {max_bandwidth} {route_length} {num_workers} {num_tasks} {min_computation} {max_computation} {min_data_size} {max_data_size} 0 --log=root.thresh:critical {energy_plugins[version]}"

    try:
        output = subprocess.check_output(command, shell=True).decode('utf-8').splitlines()
    except Exception:
        sys.stderr.write(version + ": Execution failed\n")
        continue
    for line in output:
        if "Elapsed (wall clock)" in line:
            tokens = line.split(":")
            elapsed = float(60.0 * float(tokens[-2]) + float(tokens[-1]))
        elif "Maximum resident set size" in line:
            tokens = line.split(":")
            memory = float(tokens[-1]) / 1024.0

    sys.stdout.write(f"Version: {version} #actors:{num_workers} #tasks:{num_tasks} time: {elapsed}\n")


