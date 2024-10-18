## Coordinator-Worker Flashback

### Objective

Compare the simulation time and memory footprint of the classical coordinator-worker example provided in the [SimGrid](https://simgrid.org) distribution between different versions (currently 3.10 and 3.34)

### Requirements

  - Docker
  - Python3 and matplotlib

### Usage

Typing

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
  - run a set of experiments to produce a result figure in PDF, using the simulators.


These experiments are for some default sets of numbers of workers and numbers of trials (as encoded in the Makefile). These can be changed by typing, for instance:

```
make MIN_WORKERS=1000 MAX_WORKERS=50000 STEP_WORKERS=1000 MIN_TASKS=1000 MAX_TASKS=50000 STEP_TASKS=250 NUM_TRIALS=5 run
```


