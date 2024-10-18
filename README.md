## Coordinator-Worker Flashback

### Objective

Compare the simulation time and memory footprint of the classical coordinator-worker example provided in the [SimGrid](https://simgrid.org) distribution between different versions.

### Requirements

  - Docker
  - Python3 and matplotlib

### Usage

Edit the Makefile to select versions you want to compare. Then typing

```
make build
```

will:
  - build Docker images locally if needed; and
  - build the simulators using these images.

Typing

```
make run
```

will:
  - run a set of experiments to produce two PDF figures: one for different number of workers used for a fixed number of tasks, and one for different numbers of tasks executed using a fixed number of workers. 


You can edit the Makefile to define the parameters of the experiments, or do it on the command-line, 
for instance as:

```
make MIN_WORKERS=1000 MAX_WORKERS=50000 STEP_WORKERS=1000 MIN_TASKS=1000 MAX_TASKS=50000 STEP_TASKS=250 NUM_TRIALS=5 run
```


