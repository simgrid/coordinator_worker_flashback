#!/usr/bin/env python3 

import sys
import pickle
import matplotlib.pyplot as plt

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

def average(l):
    return sum(l) / len(l)

def plot_figure(data, x_axis_label, figname):
    # PLOT RESULTS
    fontsize = 20
    f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(14, 7))
    ax2 = ax1.twinx()
    plt.grid(axis='y')

    lns_handles = []

    for version in data.keys():
        line_style = line_styles[version]

        average_times = [average(data[version][x][0]) for x in data[version].keys()]

        lns1 = ax1.plot(list(data[version].keys()), average_times, 'r' + line_style, linewidth=4,
                        label="Simulation Time " + version)
        for x in data[version].keys():
            to_plot = [min(data[version][x][0]),
                       max(data[version][x][0])]
            for time in to_plot:
                ax1.plot([x], [time], 'r', linewidth=3)
            ax1.plot([x, x], [to_plot[0], to_plot[1]], 'r', linewidth=3)

        average_footprints = [average(data[version][x][1]) for x in data[version].keys()]

        lns2 = ax2.plot(sorted(list(data[version].keys())), average_footprints, 'b' + line_style, linewidth=4,
                        label="Maximum RSS " + version)
                        
        for x in list(data[version].keys()):
            to_plot = [min(data[version][x][1]), max(data[version][x][1])]
            for footprint in to_plot:
                ax2.plot([x], [footprint], 'b', linewidth=3)
            ax2.plot([x, x], [to_plot[0], to_plot[1]], 'b', linewidth=3)

        lns_handles.append(lns1)
        lns_handles.append(lns2)


    ax1.set_xlim([min(data[versions[0]].keys()), max(data[versions[0]].keys())])
    ax1.set_xlabel(f"Number of {x_axis_label}", fontsize=fontsize + 3)
    ax1.set_ylabel("Time (sec)", fontsize=fontsize + 3)
    ax2.set_ylabel("Memory Footprint (MB)", fontsize=fontsize + 3)

    ax1.tick_params(axis='x', labelsize=fontsize + 3)
    ax1.tick_params(axis='y', labelsize=fontsize + 3)
    ax2.tick_params(axis='y', labelsize=fontsize + 3)

    # lns = lns_handles[0] + lns_handles[1] + lns_handles[2] + lns_handles[3] + lns_handles[4] + lns_handles[5]
    lns = lns_handles[0] + lns_handles[1]
    for i in range(1, len(data.keys())):
        print(i)
        lns += lns_handles[i * 2] + lns_handles[i * 2 + 1]

    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=6, fontsize=fontsize + 3)
    f.tight_layout()

    plt.savefig(figname)
    print("Figure saved to: " + figname)

    print("Statistics:")
    version1 = versions[0]
    version2 = versions[1]

    time_ratios = []
    rss_ratios = []
    for x in list(data[version1].keys()):
        time_ratio = average(data[version2][x][0]) / average(
            data[version1][x][0])
        rss_ratio = average(data[version2][x][1]) / average(
            data[version1][x][1])
        time_ratios.append(time_ratio)
        rss_ratios.append(rss_ratio)
    print(f"Time ratios: min={min(time_ratios)}  max={max(time_ratios)}  ave={average(time_ratios)}")
    print(f"RSS ratios: min={min(rss_ratios)}  max={max(rss_ratios)}  ave={average(rss_ratios)}")


if __name__ == "__main__":
    try:
        pickle_file_name = sys.argv[1]
        output_pdf_file = sys.argv[2]
    except Exception:
        sys.stderr.write(f"Usage: {sys.argv[0]} <input pickle file name with results> <output PDF file>\n")
        sys.exit(1)

    with open(pickle_file_name, 'rb') as file:
        results = pickle.load(file)

    versions = list(results.keys())
    num_workunits_values = sorted(list(results[versions[0]].keys()))
    num_workers_values = sorted(list(results[versions[0]][num_workunits_values[0]].keys()))
    num_num_cores_per_host_values = sorted(list(results[versions[0]][num_workunits_values[0]][num_workers_values[0]].keys()))

    if len(num_workunits_values) != 1:
        data = {}
        for version in versions:
            data[version] = {}
            for x in results[version]:
                data[version][x] = results[version][x][num_workers_values[0]][num_num_cores_per_host_values[0]]
        plot_figure(data, "workunits", output_pdf_file)

    elif len(num_workers_values) != 1:
        data = {}
        for version in versions:
            data[version] = {}
            for x in results[version][num_workunits_values[0]]:
                data[version][x] = results[version][num_workunits_values[0]][x][num_num_cores_per_host_values[0]]
        plot_figure(data, "cores", output_pdf_file)
    # elif len(num_num_cores_per_host_values) != 1:
    #     data = {}
    #     for version in versions:
    #         data[version] = {}
    #         for x in results[version][num_workunits_values[0]][num_workers_values[0]]:
    #             data[version][x] = results[version][num_workunits_values[0]][num_workers_values[0]][x]
    #     plot_figure(data, "#cores per host", output_pdf_file)
    else:
        raise "Something went wrong with dimensions..."
