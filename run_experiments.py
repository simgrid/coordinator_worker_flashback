#!/usr/bin/env python3 

import sys
import subprocess
import matplotlib.pyplot as plt

def average(l):
    return sum(l) / len(l)

try:
    min_num_workers = int(sys.argv[1])
    max_num_workers = int(sys.argv[2])
    step_num_workers = int(sys.argv[3])
    min_num_tasks = int(sys.argv[4])
    max_num_tasks = int(sys.argv[5])
    step_num_tasks = int(sys.argv[6])
    num_trials = int(sys.argv[7])
except Exception:
    sys.stderr.write(
        f"Usage: {sys.argv[0]} <min num workers (int)> <max num workers (int)> <step num workers (int)> "
        f"<min num tasks (int)> <max num tasks (int) <step num tasks (int)> "
        f"<num trials (int)> <version> ... <version>\n")
    sys.exit(1)

versions = sys.argv[8:len(sys.argv)]

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
        "v3_35":"--cfg=plugin:host_energy",
        "v3_36":"--cfg=plugin:host_energy"
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
        "v3_35":"-.",
        "v3_36":"-"
        }

#stack_size_in_kb = 100
#"--cfg=contexts/stack-size:{stack_size_in_kb}"

results = {}
for version in versions:
    results[version] = {}

num_workers_values = range(min_num_workers, max_num_workers + 1, step_num_workers)
num_tasks_values = range(min_num_tasks, max_num_tasks + 1, step_num_tasks)

if len(num_workers_values) > 1 and len(num_tasks_values) > 1:
    raise "You can either have multiple worker values or multiple task values, but not both"

for version in versions:
    for num_tasks in num_tasks_values:
        results[version][num_tasks] = {}
        for num_workers in num_workers_values:
            sys.stderr.write(f"Running {num_tasks} tasks with {num_workers} workers...")

            # RUN EXPERIMENT
            # num_tasks = num_workers * 200
            num_hosts = int(1 + num_workers / num_cores_per_host)

            times = []
            mems = []
            for seed in range(0, num_trials):

                command = f"docker run -it --rm -w /home/simgrid/build_simgrid_{version}/ -v `pwd`:/home/simgrid simgrid_{version} /usr/bin/time -v ./master_worker_{version} {num_hosts} {num_cores_per_host} {min_core_speed} {max_core_speed} {num_links} {min_bandwidth} {max_bandwidth} {route_length} {num_workers} {num_tasks} {min_computation} {max_computation} {min_data_size} {max_data_size} {seed} --log=root.thresh:critical {energy_plugins[version]}"
                # print(command)

                try:
                    output = subprocess.check_output(command, shell=True).decode('utf-8').splitlines()
                except Exception:
                    sys.stderr.write(version + ": Execution failed\n")
                    continue
                elapsed_time = 0
                rss_size = 0
                for line in output:
                    if "Elapsed (wall clock)" in line:
                        tokens = line.split(":")
                        elapsed_time = float(60.0 * float(tokens[-2]) + float(tokens[-1]))
                    elif "Maximum resident set size" in line:
                        tokens = line.split(":")
                        rss_size = float(tokens[-1]) / 1024.0
                times.append(elapsed_time)
                mems.append(rss_size)
                sys.stderr.write(f"Version: {version}  Time: {elapsed_time}   RSS: {rss_size}\n")

            if len(times) == 0 or len(mems) == 0:
                results[version][num_tasks][num_workers] = [0, 0]
            else:
                results[version][num_tasks][num_workers] = [times, mems]


# PLOT RESULTS
fontsize = 12
f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(14, 7))
ax2 = ax1.twinx()
plt.grid(axis='y')

lns_handles = []


# HORRIBLE code duplication, but too lazy
if len(num_tasks_values) == 1:
    num_tasks = num_tasks_values[0]
    error_bar_offset_increment = (num_workers_values[1] - num_workers_values[0]) * 0.01
    error_bar_offset = 0
    for version in versions:
        line_style = line_styles[version]

        average_times = [average(results[version][num_tasks][x][0]) for x in num_workers_values]

        lns1 = ax1.plot(num_workers_values, average_times, 'r' + line_style, linewidth=2,
                        label="Simulation Time " + version)
        for num_workers in num_workers_values:
            to_plot = [min(results[version][num_tasks][num_workers][0]), max(results[version][num_tasks][num_workers][0])]
            for time in to_plot:
                ax1.plot([num_workers + error_bar_offset], [time], 'r_', linewidth=2)
            ax1.plot([num_workers + error_bar_offset, num_workers + error_bar_offset], [to_plot[0], to_plot[1]], 'r' + line_style)

        error_bar_offset += error_bar_offset_increment

        average_footprints = [average(results[version][num_tasks][x][1]) for x in num_workers_values]

        lns2 = ax2.plot(num_workers_values, average_footprints, 'b' + line_style, linewidth=2,
                        label="Maximum RSS " + version)
        for num_workers in num_workers_values:
            to_plot = [min(results[version][num_tasks][num_workers][1]),
                       max(results[version][num_tasks][num_workers][1])]
            for footprint in to_plot:
                ax2.plot([num_workers + error_bar_offset], [footprint], 'b_', linewidth=2)
            ax2.plot([num_workers + error_bar_offset, num_workers + error_bar_offset], [to_plot[0], to_plot[1]], 'b' + line_style)

        error_bar_offset += error_bar_offset_increment

        lns_handles.append(lns1)
        lns_handles.append(lns2)

    ax1.set_xlim([num_workers_values[0], num_workers_values[-1]])
    ax1.set_xlabel("Number of workers", fontsize=fontsize + 3)
    ax1.set_ylabel("Time (sec)", fontsize=fontsize + 3)
    ax2.set_ylabel("Memory Footprint (MB)", fontsize=fontsize + 3)

    ax1.tick_params(axis='x', labelsize=fontsize + 3)
    ax1.tick_params(axis='y', labelsize=fontsize + 3)
    ax2.tick_params(axis='y', labelsize=fontsize + 3)

    #lns = lns_handles[0] + lns_handles[1] + lns_handles[2] + lns_handles[3] + lns_handles[4] + lns_handles[5]
    lns = lns_handles[0] + lns_handles[1]
    for i in range(1, len(versions)):
        lns += lns_handles[i*2] + lns_handles[i*2+1]

    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0, fontsize=fontsize+3)

    figname = f"simgrid_master_worker_tasks_{num_tasks}_workers_{num_workers_values[0]}_{num_workers_values[-1]}.pdf"
    plt.savefig(figname)
    print("Figure saved to: " + figname)

    print("Statistics:")
    version1 = versions[0]
    version2 = versions[1]

    time_ratios = []
    rss_ratios = []
    for num_workers in num_workers_values:
        time_ratio = average(results[version2][num_tasks][num_workers][0]) / average(results[version1][num_tasks][num_workers][0])
        rss_ratio = average(results[version2][num_tasks][num_workers][1]) / average(results[version1][num_tasks][num_workers][1])
        time_ratios.append(time_ratio)
        rss_ratios.append(rss_ratio)
    print(f"Time ratios: min={min(time_ratios)}  max={max(time_ratios)}  ave={average(time_ratios)}")
    print(f"RSS ratios: min={min(rss_ratios)}  max={max(rss_ratios)}  ave={average(rss_ratios)}")

else:
    num_workers = num_workers_values[0]
    for version in versions:
        line_style = line_styles[version]

        error_bar_offset_increment = (num_tasks_values[1] - num_tasks_values[0]) * 0.01
        error_bar_offset = 0

        average_times = [average(results[version][x][num_workers][0]) for x in num_tasks_values]

        lns1 = ax1.plot(num_tasks_values, average_times, 'r' + line_style, linewidth=2,
                        label="Simulation Time " + version)
        for num_tasks in num_tasks_values:
            to_plot = [min(results[version][num_tasks][num_workers][0]),
                       max(results[version][num_tasks][num_workers][0])]
            for time in to_plot:
                ax1.plot([num_tasks + error_bar_offset], [time], 'r_', linewidth=2)
            ax1.plot([num_tasks + error_bar_offset, num_tasks + error_bar_offset], [to_plot[0], to_plot[1]], 'r' + line_style)

        error_bar_offset += error_bar_offset_increment

        average_footprints = [average(results[version][x][num_workers][1]) for x in num_tasks_values]

        lns2 = ax2.plot(num_tasks_values, average_footprints, 'b' + line_style, linewidth=2,
                        label="Maximum RSS " + version)
        for num_tasks in num_tasks_values:
            to_plot = [min(results[version][num_tasks][num_workers][1]),
                       max(results[version][num_tasks][num_workers][1])]
            for footprint in to_plot:
                ax2.plot([num_tasks + error_bar_offset], [footprint], 'b_', linewidth=2)
            ax2.plot([num_tasks + error_bar_offset, num_tasks + error_bar_offset], [to_plot[0], to_plot[1]], 'b' + line_style)

        error_bar_offset += error_bar_offset_increment

        lns_handles.append(lns1)
        lns_handles.append(lns2)

    ax1.set_xlabel("Number of tasks", fontsize=fontsize + 3)
    ax1.set_ylabel("Time (sec)", fontsize=fontsize + 3)
    ax2.set_ylabel("Memory Footprint (MB)", fontsize=fontsize + 3)
    ax1.set_xlim([num_tasks_values[0], num_tasks_values[-1]])

    ax1.tick_params(axis='x', labelsize=fontsize + 3)
    ax1.tick_params(axis='y', labelsize=fontsize + 3)
    ax2.tick_params(axis='y', labelsize=fontsize + 3)

    # lns = lns_handles[0] + lns_handles[1] + lns_handles[2] + lns_handles[3] + lns_handles[4] + lns_handles[5]
    lns = lns_handles[0] + lns_handles[1]
    for i in range(1, len(versions)):
        lns += lns_handles[i * 2] + lns_handles[i * 2 + 1]

    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0, fontsize=fontsize+3)

    figname = f"simgrid_master_worker_workers_{num_workers}_tasks_{num_tasks_values[0]}_{num_tasks_values[-1]}.pdf"
    plt.savefig(figname)
    print("Figure saved to: " + figname)

    print("Statistics:")
    version1 = versions[0]
    version2 = versions[1]

    time_ratios = []
    rss_ratios = []
    for num_tasks in num_tasks_values:
        time_ratio = average(results[version2][num_tasks][num_workers][0]) / average(results[version1][num_tasks][num_workers][0])
        rss_ratio = average(results[version2][num_tasks][num_workers][1]) / average(results[version1][num_tasks][num_workers][1])
        time_ratios.append(time_ratio)
        rss_ratios.append(rss_ratio)
    print(f"Time ratios: min={min(time_ratios)}  max={max(time_ratios)}  ave={average(time_ratios)}")
    print(f"RSS ratios: min={min(rss_ratios)}  max={max(rss_ratios)}  ave={average(rss_ratios)}")
