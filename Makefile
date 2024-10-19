.NOTPARALLEL:

MIN_WORKERS=1000
MAX_WORKERS=30000
STEP_WORKERS=1000
FIXED_TASKS=30000
MIN_TASKS=1000
MAX_TASKS=30000
STEP_TASKS=1000
FIXED_WORKERS=1000
NUM_TRIALS=5

VERSIONS=v3_10 v3_36

default:
	@echo "make build  : will build the Docker containers and the simulators (do this first)"
	@echo "make check  : will run one experiment with all containers to check that makespans are the same"
	@echo "make run    : will run the experiment with whatever has been built last"

build: clean
	@for version in ${VERSIONS} ; do \
    		echo "** Building for SimGrid $${version} **" ; \
		echo docker build -t simgrid_$${version} -f Dockerfile_simgrid_$${version} . ; \
		docker build -t simgrid_$${version} -f Dockerfile_simgrid_$${version} . ; \
		mkdir build_simgrid_$${version} ; \
		docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_$${version}/ simgrid_$${version} cmake .. ; \
		docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_$${version}/ simgrid_$${version} make master_worker_$${version} ; \
	done	

check:
	python3 ./check_makespans.py ${VERSIONS}

run: 
	@echo "Running experiments for different numbers of workers"
	python3 ./run_experiments.py ${MIN_WORKERS} ${MAX_WORKERS} ${STEP_WORKERS} ${FIXED_TASKS} ${FIXED_TASKS} 1 ${NUM_TRIALS} ${VERSIONS}
	@echo "Running experiments for different numbers of tasks"
	python3 ./run_experiments.py ${FIXED_WORKERS} ${FIXED_WORKERS} 1 ${MIN_TASKS} ${MAX_TASKS} ${STEP_TASKS} ${NUM_TRIALS} ${VERSIONS}

clean:
	/bin/rm -rf build_* *.pdf

