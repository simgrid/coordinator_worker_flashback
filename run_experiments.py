#!/usr/bin/env python3 

import sys
import subprocess
import matplotlib.pyplot as plt

try:
    min_num_hosts = int(sys.argv[1])
    max_num_hosts = int(sys.argv[2])
    step_num_hosts = int(sys.argv[3])
    num_trials = int(sys.argv[4])
except Exception:
    sys.stderr.write(f"Usage: {sys.argv[0]} <min num hosts (int)> <max num hosts (int)> <step num hosts (int)> <num trials (int)>\n")
    sys.exit(1)

num_cores_per_host = 8
min_core_speed = 100
max_core_speed = 200
num_links = 100
min_bandwidth = 100
max_bandwidth = 200
route_length = 10
min_computation = 100
max_computation = 200
min_data_size = 100
max_data_size = 100

versions = ["v3_14", "v3_34"]

stack_size_in_kb = 100

results = {}
for version in versions:
    results[version] = {}

num_hosts_values = range(min_num_hosts, max_num_hosts+1, step_num_hosts)

for num_hosts in num_hosts_values:
    for version in versions:

        # RUN EXPERIMENT
        num_tasks = num_hosts * 200
        num_workers = num_hosts * num_cores_per_host

        sys.stderr.write(f"Runing with {num_tasks} tasks...\n")
        times = []
        mems = []
        for seed in range(0, num_trials):

            command = f"docker run -it --rm -w /home/simgrid/build_simgrid_{version}/ -v `pwd`:/home/simgrid simgrid_{version} /usr/bin/time -v ./master_worker_{version} {num_hosts} {num_cores_per_host} {min_core_speed} {max_core_speed} {num_links} {min_bandwidth} {max_bandwidth} {route_length} {num_workers} {num_tasks} {min_computation} {max_computation} {min_data_size} {max_data_size} {seed} --log=root.thresh:critical --cfg=contexts/stack-size:{stack_size_in_kb}"
            print(command)

            output = subprocess.check_output(command, shell=True).decode('utf-8').splitlines()
            for line in output:
                if "Elapsed (wall clock)" in line:
                    tokens = line.split(":")
                    times.append(float(60.0 * float(tokens[-2]) + float(tokens[-1])))
                elif "Maximum resident set size" in line:
                    tokens = line.split(":")
                    mems.append(float(tokens[-1]) / 1024.0)

        results[version][num_hosts] = [times, mems]

# PLOT RESULTS
fontsize = 12
f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(14, 7))
ax2 = ax1.twinx()
plt.grid(axis='y')

lns_handles = []

for version in versions:
    if version == "v3_14":
        line_style = ":"
    else:
        line_style = "-"

    average_times = [sum(results[version][x][0]) / len(results[version][x][0]) for x in num_hosts_values]

    lns1 = ax1.plot(num_hosts_values, average_times, 'or'+line_style, linewidth=2, label="Simulation Time " + version)
    for num_hosts in num_hosts_values:
        print(f"NUM_HOSTS: {num_hosts}")
        for time in results[version][num_hosts][0]:
            print(f"  - DATA POINT FOR TIME: {time}\n")
            ax1.plot([num_hosts], [time], 'xr', linewidth=2)

    average_footprints = [sum(results[version][x][1]) / len(results[version][x][1]) for x in num_hosts_values]

    lns2 = ax2.plot(num_hosts_values, average_footprints, 'ob'+line_style, linewidth=2, label="Maximum RSS " + version)
    for num_hosts in num_hosts_values:
        for footprint in results[version][num_hosts][1]:
            ax2.plot([num_hosts], [footprint], 'xb', linewidth=2)

    lns_handles.append(lns1)
    lns_handles.append(lns2)

ax1.set_xlabel("Number of hosts", fontsize=fontsize + 1)
ax1.set_ylabel("Time (sec)", fontsize=fontsize + 1)
ax2.set_ylabel("Memory Footprint (MB)", fontsize=fontsize + 1)

ax1.tick_params(axis='x', labelsize=fontsize)
ax1.tick_params(axis='y', labelsize=fontsize)
ax2.tick_params(axis='y', labelsize=fontsize)

lns = lns_handles[0] + lns_handles[1] + lns_handles[2] + lns_handles[3]
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=0, fontsize=fontsize)

figname = f"simgrid_master_worker_{num_hosts_values[0]}_{num_hosts_values[-1]}.pdf"
plt.savefig(figname)
print("***********************************")
print("RESULT FIGURE SAVED TO: " + figname)
