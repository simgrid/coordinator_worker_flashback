## Master Worker Flashback

### Objective

Compare the simulation time and memory footprint of the classical master-worker example provided in SimGrid distribution between different versions (currently 3.14 vs. 3.34)

### Requirements

  - Docker
  - Python3 and matplotlib

### Instructions**

Typing

```
make
```

will:
  - build Docker images locally;
  - build the two versions of the simulators using these images; and
  - run a set of experiments that produce a result figure in pdf.

These experiments are, by default for scales betwen 5 and 10 (as encoded in theMakefile). This can be changed by typing: 

```
make MIN_SCALE=2 MAX_SCALE=15
```


