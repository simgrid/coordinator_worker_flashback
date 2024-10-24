#!/usr/bin/env python3 

import sys
import subprocess
import pickle


if __name__ == "__main__":
    try:
        pickle_file_name = sys.argv[1]
        min_num_cores_per_host = int(sys.argv[2])
        max_num_cores_per_host = int(sys.argv[3])
        step_num_cores_per_host = int(sys.argv[4])
        min_num_hosts = int(sys.argv[5])
        max_num_hosts = int(sys.argv[6])
        step_num_hosts = int(sys.argv[7])
        min_num_workunits = int(sys.argv[8])
        max_num_workunits = int(sys.argv[9])
        step_num_workunits = int(sys.argv[10])
        num_trials = int(sys.argv[11])
    except Exception:
        sys.stderr.write(
            f"Usage: {sys.argv[0]} <pickle file name for results> <min num cores per host> <max num cores per host> "
            f"<stp num cores per host> <min num hosts (int)> <max num hosts (int)> <step num hosts (int)> "
            f"<min num workunits (int)> <max num workunits (int) <step num workunits (int)> "
            f"<num trials (int)> <version> ... <version>\n")
        sys.exit(1)

    versions = sys.argv[12:len(sys.argv)]

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

    num_cores_per_host_values = list(range(min_num_cores_per_host, max_num_cores_per_host+1, step_num_cores_per_host))
    num_hosts_values = list(range(min_num_hosts, max_num_hosts + 1, step_num_hosts))
    num_workunits_values = list(range(min_num_workunits, max_num_workunits + 1, step_num_workunits))

    if len(num_hosts_values) + len(num_workunits_values) + len(num_cores_per_host_values) > 2 + max([len(num_hosts_values), len(num_workunits_values), len(num_cores_per_host_values)]):
        raise "Only one dimension can be varying"

    for num_workunits in num_workunits_values:
        results[num_workunits] = {}
        for num_hosts in num_hosts_values:
            results[num_workunits][num_hosts] = {}
            for num_cores_per_host in num_cores_per_host_values:
                results[num_workunits][num_hosts][num_cores_per_host] = {}
                for version in versions:

                    times = []
                    mems = []
                    for seed in range(0, num_trials):

                        command = f"docker run -it --rm --memory 8000m -w /home/simgrid/build_simgrid_{version}/ -v `pwd`:/home/simgrid simgrid_{version} /usr/bin/time -v ./master_worker_{version} {num_hosts} {num_cores_per_host} {min_core_speed} {max_core_speed} {num_links} {min_bandwidth} {max_bandwidth} {route_length} {num_workunits} {min_computation} {max_computation} {min_data_size} {max_data_size} {seed} --log=root.thresh:critical {energy_plugins[version]}"
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
                        sys.stderr.write(f"{num_workunits} workunits with {num_hosts} {num_cores_per_host}-core hosts: Version {version}  Time: {elapsed_time}   RSS: {rss_size}\n")

                    if len(times) == 0 or len(mems) == 0:
                        results[num_workunits][num_hosts][num_cores_per_host][version] = [0, 0]
                    else:
                        results[num_workunits][num_hosts][num_cores_per_host][version] = [times, mems]

    print(results)
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(results, f)
    sys.stderr.write(f"Pickled results to file {pickle_file_name}\n")
