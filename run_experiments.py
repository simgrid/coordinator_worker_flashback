#!/usr/bin/env python3 

import sys
import subprocess
import matplotlib.pyplot as plt

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

num_trials = 5

scales = range(8, 15)
versions = ["v3_14", "v3_34"]

results = {}
for version in versions:
    results[version] = {}
    # RUN EXPERIMENT
    for scale in scales:

        num_hosts = 2 ** scale
        num_tasks = num_hosts * 20
        num_workers = num_hosts * num_cores_per_host

        sys.stderr.write(f"Runing with {num_tasks} tasks...\n")
        times = []
        mems = []
        for seed in range(0, num_trials):

            command = f"docker run -it --rm -w /home/simgrid/build_simgrid_{version}/ -v `pwd`:/home/simgrid simgrid_{version} /usr/bin/time -v ./master_worker_{version} {num_hosts} {num_cores_per_host} {min_core_speed} {max_core_speed} {num_links} {min_bandwidth} {max_bandwidth} {route_length} {num_workers} {num_tasks} {min_computation} {max_computation} {min_data_size} {max_data_size} {seed} --log=root.thresh:critical"
            print(command)

            output = subprocess.check_output(command, shell=True).decode('utf-8').splitlines()
            for line in output:
                if "Elapsed (wall clock)" in line:
                    tokens = line.split(":")
                    times.append(float(60.0 * float(tokens[-2]) + float(tokens[-1])))
                elif "Maximum resident set size" in line:
                    tokens = line.split(":")
                    mems.append(float(tokens[-1]) / 1024.0)

        results[version][scale] = [times, mems]

# PLOT RESULTS
fontsize = 12
f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(14, 7))
ax2 = ax1.twinx()
plt.grid(axis='y')

lns_handles = []

for version in versions:
    if version == "v3_14":
        line_style = "-"
    else:
        line_style = "--"

    average_times = [sum(results[version][x][0]) / len(results[version][x][0]) for x in scales]

    lns1 = ax1.plot(scales, average_times, 'or'+line_style, linewidth=2, label="Simulation Time " + version)
    for scale in scales:
        print(f"SCALE: {scale}")
        for time in results[version][scale][0]:
            print(f"  - DATA POINT FOR TIME: {time}\n")
            ax1.plot([scale], [time], 'xr', linewidth=2)

    average_footprints = [sum(results[version][x][1]) / len(results[version][x][1]) for x in scales]

    lns2 = ax2.plot(scales, average_footprints, 'ob'+line_style, linewidth=2, label="Maximum RSS " + version)
    for scale in scales:
        for footprint in results[version][scale][1]:
            ax2.plot([scale], [footprint], 'xb', linewidth=2)

    lns_handles.append(lns1)
    lns_handles.append(lns2)

ax1.set_xlabel("Simulation scale", fontsize=fontsize + 1)
ax1.set_ylabel("Time (sec)", fontsize=fontsize + 1)
ax2.set_ylabel("Memory Footprint (MB)", fontsize=fontsize + 1)

ax1.tick_params(axis='x', labelsize=fontsize)
ax1.tick_params(axis='y', labelsize=fontsize)
ax2.tick_params(axis='y', labelsize=fontsize)

lns = lns_handles[0] + lns_handles[1] + lns_handles[2] + lns_handles[3]
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=0, fontsize=fontsize)

figname = f"simgrid_v3_14.pdf"
print("Saving " + figname)
plt.savefig(figname)
