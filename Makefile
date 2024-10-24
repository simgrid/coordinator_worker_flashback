.NOTPARALLEL:

MIN_NUM_CORES_PER_HOST=8
MAX_NUM_CORES_PER_HOST=60
STEP_NUM_CORES_PER_HOST=4
FIXED_NUM_CORES_PER_HOST=8
FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS=500

MIN=1000
MAX=30000
STEP=1000

MIN_NUM_HOSTS=${MIN}
MAX_NUM_HOSTS=${MAX}
STEP_NUM_HOSTS=${STEP}
FIXED_WORKUNITS=${MAX}
MIN_NUM_WORKUNITS=${MIN}
MAX_NUM_WORKUNITS=${MAX}
STEP_WORKUNITS=${STEP}
FIXED_NUM_HOSTS=${MAX}

NUM_TRIALS=1

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
	@echo "Running experiments for different numbers of hosts"
	python3 ./run_experiments.py /tmp/results.pickled ${FIXED_NUM_CORES_PER_HOST} ${FIXED_NUM_CORES_PER_HOST} 1 ${MIN_NUM_HOSTS} ${MAX_NUM_HOSTS} ${STEP_NUM_HOSTS} ${FIXED_WORKUNITS} ${FIXED_WORKUNITS} 1 ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_hosts_${MIN_NUM_HOSTS}_${MAX_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.pickled
	python3 ./plot_results.py  ./results_master_worker_hosts_${MIN_NUM_HOSTS}_${MAX_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.pickled ./results_master_worker_hosts_${MIN_NUM_HOSTS}_${MAX_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.pdf 1> ./results_master_worker_hosts_${MIN_NUM_HOSTS}_${MAX_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_NUM_WORKUNITS}_${MAX_NUM_WORKUNITS}.txt
	@echo "Running experiments for different numbers of workunits"
	python3 ./run_experiments.py /tmp/results.pickled ${FIXED_NUM_CORES_PER_HOST} ${FIXED_NUM_CORES_PER_HOST} 1 ${FIXED_NUM_HOSTS} ${FIXED_NUM_HOSTS} 1 ${MIN_NUM_WORKUNITS} ${MAX_NUM_WORKUNITS} ${STEP_WORKUNITS} ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_hosts_${FIXED_NUM_HOSTS}_${FIXED_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_NUM_WORKUNITS}_${MAX_NUM_WORKUNITS}.pickled
	python3 ./plot_results.py ./results_master_worker_hosts_${FIXED_NUM_HOSTS}_${FIXED_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_NUM_WORKUNITS}_${MAX_NUM_WORKUNITS}.pickled ./results_master_worker_hosts_${FIXED_NUM_HOSTS}_${FIXED_WORKUNITS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_NUM_WORKUNITS}_${MAX_NUM_WORKUNITS}.pdf 1> ./results_master_worker_hosts_${FIXED_NUM_HOSTS}_${FIXED_NUM_HOSTS}_cores_${FIXED_NUM_CORES_PER_HOST}_${FIXED_NUM_CORES_PER_HOST}_workunits_${MIN_NUM_WORKUNITS}_${MAX_NUM_WORKUNITS}.txt
	@echo "Running experiments for different numbers of cores per host"
	python3 ./run_experiments.py /tmp/results.pickled ${MIN_NUM_CORES_PER_HOST} ${MAX_NUM_CORES_PER_HOST} ${STEP_NUM_CORES_PER_HOST} ${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS} ${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS} 1 ${FIXED_WORKUNITS} ${FIXED_WORKUNITS} 1 ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_hosts_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.pickled
	python3 ./plot_results.py ./results_master_worker_hosts_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.pickled ./results_master_worker_hosts_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_${FIXED_NUM_HOSTS}_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.pdf 1> ./results_master_worker_hosts_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_${FIXED_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS}_cores_${MIN_NUM_CORES_PER_HOST}_${MAX_NUM_CORES_PER_HOST}_workunits_${FIXED_WORKUNITS}_${FIXED_WORKUNITS}.txt

clean:
	/bin/rm -rf build_* results_*.pdf results_*.pickled results_*.txt

