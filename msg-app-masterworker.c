/* Copyright (c) 2010-2016. The SimGrid Team. All rights reserved.          */

/* This program is free software; you can redistribute it and/or modify it
 * under the terms of the license (GNU LGPL) which comes with this package. */

#include "simgrid/msg.h"
#include <stdlib.h>

XBT_LOG_NEW_DEFAULT_CATEGORY(msg_app_masterworker, "Messages specific for this msg example");

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


/* Main function of the master process */
static int master(int argc, char *argv[])
{
  xbt_assert(argc==7, "The master function expects 7 arguments from the XML deployment file");
  long number_of_tasks = xbt_str_parse_int(argv[1], "Invalid number of tasks: %s");    /* - Number of tasks      */
  double min_comp_size = xbt_str_parse_double(argv[2], "Invalid min computational size: %s");  /* - Min task compute cost    */
  double max_comp_size = xbt_str_parse_double(argv[3], "Invalid max computational size: %s");  /* - Max task compute cost    */
  double min_comm_size = xbt_str_parse_double(argv[4], "Invalid min communication size: %s");  /* - Task communication size */
  double max_comm_size = xbt_str_parse_double(argv[5], "Invalid max communication size: %s");  /* - Task communication size */
  long workers_count = xbt_str_parse_int(argv[6], "Invalid amount of workers: %s");    /* - Number of workers    */

  XBT_INFO("Got %ld workers and %ld tasks to process", workers_count, number_of_tasks);

  for (int i = 0; i < number_of_tasks; i++) {  /* For each task to be executed: */
    char mailbox[80];
    char task_name[80];

    snprintf(mailbox,79, "worker-%ld", i % workers_count); /* - Select a @ref worker in a round-robin way */
    snprintf(task_name,79, "Task_%d", i);
    msg_task_t task = MSG_task_create(task_name, double_randfrom(min_comp_size, max_comp_size), double_randfrom(min_comm_size, max_comm_size), NULL);   /* - Create a task */
    if (number_of_tasks < 10000 || i % 10000 == 0)
      XBT_INFO("Sending \"%s\" (of %ld) to mailbox \"%s\"", task->name, number_of_tasks, mailbox);

    MSG_task_send(task, mailbox); /* - Send the task to the @ref worker */
  }

  XBT_INFO("All tasks have been dispatched. Let's tell everybody the computation is over.");
  for (int i = 0; i < workers_count; i++) { /* - Eventually tell all the workers to stop by sending a "finalize" task */
    char mailbox[80];

    snprintf(mailbox,79, "worker-%ld", i % workers_count);
    msg_task_t finalize = MSG_task_create("finalize", 0, 0, 0);
    MSG_task_send(finalize, mailbox);
  }

  return 0;
}

/* Main functions of the Worker processes */
static int worker(int argc, char *argv[])
{
  xbt_assert(argc==2, "The worker expects a single argument from the XML deployment file: its worker ID (its numerical rank)");
  char mailbox[80];

  long id= xbt_str_parse_int(argv[1], "Invalid argument %s");

  snprintf(mailbox,79, "worker-%ld", id);

  while (1) {  /* The worker wait in an infinite loop for tasks sent by the \ref master */
    msg_task_t task = NULL;
    int res = MSG_task_receive(&task, mailbox);
    xbt_assert(res == MSG_OK, "MSG_task_get failed");

    if (strcmp(MSG_task_get_name(task), "finalize") == 0) {
      MSG_task_destroy(task);  /* - Exit if 'finalize' is received */
      break;
    }
    XBT_INFO("I am doing a task");
    MSG_task_execute(task);    /*  - Otherwise, process the task */
    XBT_INFO("I've done a task");
    MSG_task_destroy(task);
  }
  XBT_INFO("I'm done. See you!");
  return 0;
}


void create_platform_file(char *filepath, 
  			  int num_hosts, 
			  int num_cores_per_host, 
			  double min_core_speed, 
			  double max_core_speed, 
			  int num_links, 
			  double min_link_bandwidth, 
			  double max_link_bandwidth, 
			  int route_length) {

  FILE *pf = fopen(filepath, "w");

  // XML Header 
  fprintf(pf, "<?xml version='1.0'?>\n");
  fprintf(pf, "<!DOCTYPE platform SYSTEM \"http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd\">\n");
  fprintf(pf, "<platform version=\"4\">\n");
  fprintf(pf, "<AS id=\"AS0\" routing=\"Full\">\n\n");
  
  // Create master hosts
  fprintf(pf, "  <host id=\"MasterHost\" speed=\"1Mf\" core=\"1\" />\n\n");

  // Create worker hosts
  for (int i=0; i < num_hosts; i++) {
    fprintf(pf, "  <host id=\"WorkerHost-%d\" speed=\"%.2lfMf\" core=\"%d\" />\n", i, double_randfrom(min_core_speed, max_core_speed), num_cores_per_host);
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
  fprintf(pf, "</AS>\n");
  fprintf(pf, "</platform>\n");

  fclose(pf);
}

void create_deployment_file(char *filepath, 
  			  int num_hosts, 
			  int num_workers, 
			  int num_tasks, 
			  double min_computation, 
			  double max_computation, 
			  double min_data_size, 
			  double max_data_size) { 

  FILE *df = fopen(filepath, "w");
  // XML Header 
  fprintf(df, "<?xml version='1.0'?>\n");
  fprintf(df, "<!DOCTYPE platform SYSTEM \"http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd\">\n");
  fprintf(df, "<platform version=\"4\">\n");
  
  // Create master process 
  fprintf(df, "  <process host=\"MasterHost\" function=\"master\">\n");
  fprintf(df, "    <argument value=\"%d\" />\n", num_tasks);
  fprintf(df, "    <argument value=\"%.2lf\" />\n", min_computation * 1000000.0);
  fprintf(df, "    <argument value=\"%.2lf\" />\n", max_computation * 1000000.0);
  fprintf(df, "    <argument value=\"%.2lf\" />\n", min_data_size * 1000000.0);
  fprintf(df, "    <argument value=\"%.2lf\" />\n", max_data_size * 1000000.0);
  fprintf(df, "    <argument value=\"%d\" />\n", num_workers);
  fprintf(df, "  </process>\n");

  // Create worker processes
  int current_worker_host_index = 0;
  for (int i=0; i < num_workers; i++) {
    fprintf(df, "  <process host=\"WorkerHost-%d\" function=\"worker\">\n", current_worker_host_index);
    fprintf(df, "    <argument value=\"%d\" />\n", i);
    fprintf(df, "  </process>\n");
    current_worker_host_index  = (current_worker_host_index + 1) % num_hosts;
  }

  // XML footer
  fprintf(df, "</platform>\n");
 
  fclose(df);
}


int main(int argc, char *argv[])
{


  MSG_init(&argc, argv);
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
  char *platform_file="/tmp/platform_master_worker.xml";
  char *deployment_file="/tmp/platform_master_worker_d.xml";
  create_platform_file(platform_file, num_hosts, num_cores_per_host, min_core_speed, max_core_speed, num_links, min_link_bandwidth, max_link_bandwidth, route_length);
  create_deployment_file(deployment_file, num_hosts, num_workers, num_tasks, min_computation, max_computation, min_data_size, max_data_size);
  

  MSG_create_environment(platform_file);          /* - Load the platform description */

  MSG_function_register("master", master);  /* - Register the function to be executed by the processes */
  MSG_function_register("worker", worker);
  MSG_launch_application(deployment_file);          /* - Deploy the application */

  msg_error_t res = MSG_main();             /* - Run the simulation */

  XBT_INFO("Simulation time %g", MSG_get_clock());

  return res != MSG_OK;
}
