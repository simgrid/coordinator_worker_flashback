.NOTPARALLEL:

MIN_NUM_CORES_PER_HOST=2
MAX_NUM_CORES_PER_HOST=64
STEP_NUM_CORES_PER_HOST=2
FIXED_NUM_CORES_PER_HOST=8

MIN=1000
MAX=30000
STEP=1000

MIN_WORKERS=${MIN}
MAX_WORKERS=${MAX}
STEP_WORKERS=${STEP}
FIXED_TASKS=${MAX}
MIN_TASKS=${MIN}
MAX_TASKS=${MAX}
STEP_TASKS=${STEP}
FIXED_WORKERS=${MAX}

NUM_TRIALS=10

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
	python3 ./run_experiments.py /tmp/results.pickled ${FIXED_NUM_CORES_PER_HOST} ${FIXED_NUM_CORES_PER_HOST} 1 ${MIN_WORKERS} ${MAX_WORKERS} ${STEP_WORKERS} ${FIXED_TASKS} ${FIXED_TASKS} 1 ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${MIN_WORKERS}_${MAX_WORKERS}.pickled
	python3 ./plot_results.py  ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${MIN_WORKERS}_${MAX_WORKERS}.pickled ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${MIN_WORKERS}_${MAX_WORKERS}.pdf 1> ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_TASKS}_${MAX_TASKS}_workers_${MIN_WORKERS}_${MAX_WORKERS}.txt
	@echo "Running experiments for different numbers of tasks"
	python3 ./run_experiments.py /tmp/results.pickled ${FIXED_NUM_CORES_PER_HOST} ${FIXED_NUM_CORES_PER_HOST} 1 ${FIXED_WORKERS} ${FIXED_WORKERS} 1 ${MIN_TASKS} ${MAX_TASKS} ${STEP_TASKS} ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_TASKS}_${MAX_TASKS}_workers_${FIXED_WORKERS}_${FIXED_WORKERS}.pickled
	python3 ./plot_results.py ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_TASKS}_${MAX_TASKS}_workers_${FIXED_WORKERS}_${FIXED_WORKERS}.pickled ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_TASKS}_${MAX_TASKS}_workers_${FIXED_WORKERS}_${FIXED_TASKS}.pdf 1> ./results_master_worker_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_TASKS}_${MAX_TASKS}_workers_${FIXED_WORKERS}_${FIXED_WORKERS}.txt
	@echo "Running experiments for different numbers of cores per host"
	python3 ./run_experiments.py /tmp/results.pickled ${MIN_NUM_CORES_PER_HOST} ${MAX_NUM_CORES_PER_HOST} ${STEP_NUM_CORES_PER_HOST} ${FIXED_WORKERS} ${FIXED_WORKERS} 1 ${FIXED_TASKS} ${FIXED_TASKS} 1 ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${FIXED_WORKERS}_${FIXED_WORKERS}.pickled
	python3 ./plot_results.py ./results_master_worker_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${FIXED_WORKERS}_${FIXED_WORKERS}.pickled ./results_master_worker_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${FIXED_WORKERS}_${FIXED_TASKS}.pdf 1> ./results_master_worker_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_TASKS}_${FIXED_TASKS}_workers_${FIXED_WORKERS}_${FIXED_WORKERS}.txt
clean:
	/bin/rm -rf build_* *.pdf *.pickled

