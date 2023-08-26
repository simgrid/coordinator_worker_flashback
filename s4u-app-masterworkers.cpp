/* Copyright (c) 2010-2023. The SimGrid Team. All rights reserved.          */

/* This program is free software; you can redistribute it and/or modify it
 * under the terms of the license (GNU LGPL) which comes with this package. */

/* ************************************************************************* */
/* Take this tutorial online: https://simgrid.org/doc/latest/Tutorial_Algorithms.html */
/* ************************************************************************* */

#include <simgrid/s4u.hpp>
namespace sg4 = simgrid::s4u;
#include <stdlib.h>

XBT_LOG_NEW_DEFAULT_CATEGORY(s4u_app_masterworker_fun, "Messages specific for this example");


double double_randfrom(double min, double max)
{
    double range = (max - min);
    double div = RAND_MAX / range;
    return min + (rand() / div);
}

// Inclusive
double int_randfrom(int min, int max)
{
    return min + (rand() % (max - min + 1));
}


// master-begin
static void master(std::vector<std::string> args) {
    long num_tasks;
    double min_comp_size, max_comp_size;
    double min_comm_size, max_comm_size;
    long num_workers;

    xbt_assert(args.size()==7, "The master function expects 7 arguments from the XML deployment file");
    xbt_assert(sscanf(args.at(1).c_str(),"%ld", &num_tasks) == 1, "Invalid number of tasks");    /* - Number of tasks      */
    xbt_assert(sscanf(args.at(2).c_str(),"%lf", &min_comp_size) == 1, "Invalid minimum computation size");    /* - Number of tasks      */
    xbt_assert(sscanf(args.at(3).c_str(),"%lf", &max_comp_size) == 1, "Invalid maximum computation size");    /* - Number of tasks      */
    xbt_assert(sscanf(args.at(4).c_str(),"%lf", &min_comm_size) == 1, "Invalid minimum communication size");    /* - Number of tasks      */
    xbt_assert(sscanf(args.at(5).c_str(),"%lf", &max_comm_size) == 1, "Invalid maximum communication size");    /* - Number of tasks      */
    xbt_assert(sscanf(args.at(6).c_str(),"%ld", &num_workers) == 1, "Invalid number of workers");    /* - Number of tasks      */

    std::vector<sg4::Mailbox*> workers;
    for (unsigned int i = 0; i < num_workers; i++) {
        workers.push_back(sg4::Mailbox::by_name("WorkerHost-" + std::to_string(i)));
    }

    XBT_INFO("Got %zu workers and %ld tasks to process", workers.size(), num_tasks);

    for (int i = 0; i < num_tasks; i++) { /* For each task to be executed: */
        /* - Select a worker in a round-robin way */
        auto mailbox = workers[i % workers.size()];

        /* - Send the computation cost to that worker */
        XBT_INFO("Sending task %d of %ld to mailbox '%s'", i, num_tasks, mailbox->get_cname());
        double compute_cost = double_randfrom(min_comp_size, max_comp_size);
        double communication_cost = double_randfrom(min_comm_size, max_comm_size);
        mailbox->put(new double(compute_cost), communication_cost);
    }

    XBT_INFO("All tasks have been dispatched. Request all workers to stop.");
    for (unsigned int i = 0; i < workers.size(); i++) {
        /* The workers stop when receiving a negative compute_cost */
        sg4::Mailbox* mailbox = workers[i % workers.size()];

        mailbox->put(new double(-1.0), 0);
    }
}
// master-end

// worker-begin
static void worker(std::vector<std::string> args)
{
    xbt_assert(args.size() == 1, "The worker expects no argument");

    const sg4::Host* my_host = sg4::this_actor::get_host();
    sg4::Mailbox* mailbox    = sg4::Mailbox::by_name(my_host->get_name());

    double compute_cost;
    do {
        auto msg     = mailbox->get_unique<double>();
        compute_cost = *msg;

        if (compute_cost > 0) /* If compute_cost is valid, execute a computation of that cost */
            sg4::this_actor::execute(compute_cost);
    } while (compute_cost > 0); /* Stop when receiving an invalid compute_cost */

    XBT_INFO("Exiting now.");
}
// worker-end


void create_platform_file(std::string filepath,
                          int num_hosts,
                          int num_cores_per_host,
                          double min_core_speed,
                          double max_core_speed,
                          int num_links,
                          double min_link_bandwidth,
                          double max_link_bandwidth,
                          int route_length) {

    FILE *pf = fopen(filepath.c_str(), "w");

    // XML Header
    fprintf(pf, "<?xml version='1.0'?>\n");
    fprintf(pf, "<!DOCTYPE platform SYSTEM \"https://simgrid.org/simgrid.dtd\">\n");
    fprintf(pf, "<platform version=\"4.1\">\n");
    fprintf(pf, "<zone id=\"world\" routing=\"Full\">\n\n");

    // Create master hosts
    fprintf(pf, "  <host id=\"MasterHost\" speed=\"1Mf\" core=\"1\">\n\n");
    fprintf(pf, "    <prop id=\"wattage_per_state\" value=\"100.0:93.33333333333333:200.0, 93.0:90.0:170.0, 90.0:90.0:150.0\" />\n");
    fprintf(pf, "    <prop id=\"wattage_off\" value=\"10\" />\n");
    fprintf(pf, "  </host>\n");

    // Create worker hosts
    for (int i=0; i < num_hosts; i++) {
        fprintf(pf, "  <host id=\"WorkerHost-%d\" speed=\"%.2lfMf\" core=\"%d\">\n", i, double_randfrom(min_core_speed, max_core_speed), num_cores_per_host);
        fprintf(pf, "    <prop id=\"wattage_per_state\" value=\"100.0:93.33333333333333:200.0, 93.0:90.0:170.0, 90.0:90.0:150.0\" />\n");
        fprintf(pf, "    <prop id=\"wattage_off\" value=\"10\" />\n");
        fprintf(pf, "  </host>\n");
    }

    // Create links
    fprintf(pf, "\n");
    for (int i=0; i < num_links; i++) {
        fprintf(pf, "  <link id=\"Link-%d\" bandwidth=\"%.2lfMBps\" latency=\"100us\" />\n", i, double_randfrom(min_link_bandwidth, max_link_bandwidth));
    }

    // Create routes
    fprintf(pf, "\n");
    int link_ids[route_length];
    for (int i=0; i < num_hosts; i++) {
        fprintf(pf, "  <route src=\"MasterHost\" dst=\"WorkerHost-%d\">\n", i);
        for (int j=0; j < route_length; j++) {
            int id = -1;
            while(id == -1) {
                id = int_randfrom(0, num_links-1);
                for (int k=0; k < j; k++) {
                    if (link_ids[k] == id) {
                        id = -1;
                        break;
                    }
                }
                if (id != -1) {
                    link_ids[j] = id;
                    break;
                }
            }
        }
        for (int j=0; j < route_length; j++) {
            fprintf(pf, "    <link_ctn id=\"Link-%d\"/>\n", link_ids[j]);
        }
        fprintf(pf, "  </route>\n");
    }

    // XML footer
    fprintf(pf, "</zone>\n");
    fprintf(pf, "</platform>\n");

    fclose(pf);
}

void create_deployment_file(std::string filepath,
                            int num_hosts,
                            int num_workers,
                            int num_tasks,
                            double min_computation,
                            double max_computation,
                            double min_data_size,
                            double max_data_size) {

    FILE *df = fopen(filepath.c_str(), "w");
    // XML Header
    fprintf(df, "<?xml version='1.0'?>\n");
    fprintf(df, "<!DOCTYPE platform SYSTEM \"https://simgrid.org/simgrid.dtd\">\n");
    fprintf(df, "<platform version=\"4.1\">\n");

    // Create master process
    fprintf(df, "  <actor host=\"MasterHost\" function=\"master\">\n");
    fprintf(df, "    <argument value=\"%d\" />\n", num_tasks);
    fprintf(df, "    <argument value=\"%.2lf\" />\n", min_computation * 1000000.0);
    fprintf(df, "    <argument value=\"%.2lf\" />\n", max_computation * 1000000.0);
    fprintf(df, "    <argument value=\"%.2lf\" />\n", min_data_size * 1000000.0);
    fprintf(df, "    <argument value=\"%.2lf\" />\n", max_data_size * 1000000.0);
    fprintf(df, "    <argument value=\"%d\" />\n", num_workers);
    fprintf(df, "  </actor>\n");

    // Create worker processes
    int current_worker_host_index = 0;
    for (int i=0; i < num_workers; i++) {
        fprintf(df, "  <actor host=\"WorkerHost-%d\" function=\"worker\" />\n", current_worker_host_index);
        current_worker_host_index  = (current_worker_host_index + 1) % num_hosts;
    }

    // XML footer
    fprintf(df, "</platform>\n");

    fclose(df);
}


// main-begin
int main(int argc, char* argv[])
{
    sg4::Engine e(&argc, argv);
    xbt_assert(argc == 16, "Usage: %s <#hosts> <#cores per host> <min core speed (Mf)> <max core speed (Mf)> <#links> <bandwidth min (MBps)> <bandwidth max (MBps)> <route length> <#workers> <#tasks> <min computation (Mf)> <max computation (Mf)> <min data size (MB)> <max data size (MB)> <seed>\n", argv[0]);

    // Parse commandline arguments
    int num_hosts;
    int num_cores_per_host;
    double min_core_speed;
    double max_core_speed;
    int num_links;
    double min_link_bandwidth;
    double max_link_bandwidth;
    int route_length;

    int num_workers;
    int num_tasks;
    double min_computation;
    double max_computation;
    double min_data_size;
    double max_data_size;

    int seed;

    xbt_assert(sscanf(argv[1], "%d", &num_hosts) == 1, "Invalid <#hosts> argument");
    xbt_assert(sscanf(argv[2], "%d", &num_cores_per_host) == 1, "Invalid <#cores per host> argument");
    xbt_assert(sscanf(argv[3], "%lf", &min_core_speed) == 1, "Invalid <min core speed (Mf)> argument");
    xbt_assert(sscanf(argv[4], "%lf", &max_core_speed) == 1, "Invalid <max core speed (Mf)> argument");
    xbt_assert(sscanf(argv[5], "%d", &num_links) == 1, "Invalid <#links> argument");
    xbt_assert(sscanf(argv[6], "%lf", &min_link_bandwidth) == 1, "Invalid <min link bandwidth (MB)> argument");
    xbt_assert(sscanf(argv[7], "%lf", &max_link_bandwidth) == 1, "Invalid <max link bandwidth (MB)> argument");
    xbt_assert(sscanf(argv[8], "%d", &route_length) == 1, "Invalid <route length> argument");
    xbt_assert(sscanf(argv[9], "%d", &num_workers) == 1, "Invalid <#workers> argument");
    xbt_assert(sscanf(argv[10], "%d", &num_tasks) == 1, "Invalid <#tasks> argument");
    xbt_assert(sscanf(argv[11], "%lf", &min_computation) == 1, "Invalid <min computation (Mf)> argument");
    xbt_assert(sscanf(argv[12], "%lf", &max_computation) == 1, "Invalid <max computation (Mf)> argument");
    xbt_assert(sscanf(argv[13], "%lf", &min_data_size) == 1, "Invalid <min data size (MB)> argument");
    xbt_assert(sscanf(argv[14], "%lf", &max_data_size) == 1, "Invalid <max data size (MB)> argument");
    xbt_assert(sscanf(argv[15], "%d", &seed) == 1, "Invalid <seed> argument");


    xbt_assert(route_length <= num_links, "The <route length> argument cannot be larger than the <#links> argument");

    // Seed the RNG
    srand(seed);

    // Create platform and deployment file
    std::string platform_file="/tmp/platform_master_worker.xml";
    std::string deployment_file="/tmp/platform_master_worker_d.xml";
    create_platform_file(platform_file, num_hosts, num_cores_per_host, min_core_speed, max_core_speed, num_links, min_link_bandwidth, max_link_bandwidth, route_length);
    create_deployment_file(deployment_file, num_hosts, num_workers, num_tasks, min_computation, max_computation, min_data_size, max_data_size);

    /* Register the functions representing the actors */
    e.register_function("master", &master);
    e.register_function("worker", &worker);

    /* Load the platform description and then deploy the application */
    e.load_platform(platform_file);
    e.load_deployment(deployment_file);

    /* Run the simulation */
    e.run();

    XBT_INFO("Simulation is over");

    return 0;
}
// main-end
