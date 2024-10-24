.NOTPARALLEL:

NUM_TRIALS=10

VERSIONS=v3_10 v3_36
# VERSIONS=v3_10 v3_14 v3_16 v3_24 v3_35 v3_12 v3_15 v3_20 v3_34 v3_36

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

run: run_workunit_experiment run_host_experiment run_core_experiment


XP1_MIN_NUM_HOSTS=1000
XP1_MAX_NUM_HOSTS=10000
XP1_STEP_NUM_HOSTS=1000
XP1_NUM_CORES_PER_HOST=4
XP1_NUM_WORKUNITS=40000

run_host_experiment:
	@echo "Running experiments for different numbers of hosts"
	python3 ./run_experiments.py /tmp/results.pickled ${XP1_NUM_CORES_PER_HOST} ${XP1_NUM_CORES_PER_HOST} 1 ${XP1_MIN_NUM_HOSTS} ${XP1_MAX_NUM_HOSTS} ${XP1_STEP_NUM_HOSTS} ${XP1_NUM_WORKUNITS} ${XP1_NUM_WORKUNITS} 1 ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_hosts_${XP1_MIN_NUM_HOSTS}_${XP1_MAX_NUM_HOSTS}_cores_${XP1_NUM_CORES_PER_HOST}_${XP1_NUM_CORES_PER_HOST}_workunits_${XP1_NUM_WORKUNITS}_${XP1_NUM_WORKUNITS}.pickled
	python3 ./plot_results.py  ./results_master_worker_hosts_${XP1_MIN_NUM_HOSTS}_${XP1_MAX_NUM_HOSTS}_cores_${XP1_NUM_CORES_PER_HOST}_${XP1_NUM_CORES_PER_HOST}_workunits_${XP1_NUM_WORKUNITS}_${XP1_NUM_WORKUNITS}.pickled ./results_master_worker_hosts_${XP1_MIN_NUM_HOSTS}_${XP1_MAX_NUM_HOSTS}_cores_${XP1_NUM_CORES_PER_HOST}_${XP1_NUM_CORES_PER_HOST}_workunits_${XP1_NUM_WORKUNITS}_${XP1_NUM_WORKUNITS}.pdf 1> ./results_master_worker_hosts_${XP1_MIN_NUM_HOSTS}_${XP1_MAX_NUM_HOSTS}_cores_${XP1_NUM_CORES_PER_HOST}_${XP1_NUM_CORES_PER_HOST}_workunits_${XP1_MIN_NUM_WORKUNITS}_${XP1_MAX_NUM_WORKUNITS}.txt

XP2_NUM_HOSTS=1000
XP2_NUM_CORES_PER_HOST=4
XP2_MIN_NUM_WORKUNITS=4000
XP2_MAX_NUM_WORKUNITS=40000
XP2_STEP_NUM_WORKUNITS=1000

run_workunit_experiment:
	@echo "Running experiments for different numbers of workunits"
	python3 ./run_experiments.py /tmp/results.pickled ${XP2_NUM_CORES_PER_HOST} ${XP2_NUM_CORES_PER_HOST} 1 ${XP2_NUM_HOSTS} ${XP2_NUM_HOSTS} 1 ${XP2_MIN_NUM_WORKUNITS} ${XP2_MAX_NUM_WORKUNITS} ${XP2_STEP_NUM_WORKUNITS} ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_hosts_${XP2_NUM_HOSTS}_${XP2_NUM_HOSTS}_cores_${XP2_NUM_CORES_PER_HOST}_${XP2_NUM_CORES_PER_HOST}_workunits_${XP2_MIN_NUM_WORKUNITS}_${XP2_MAX_NUM_WORKUNITS}.pickled
	python3 ./plot_results.py ./results_master_worker_hosts_${XP2_NUM_HOSTS}_${XP2_NUM_HOSTS}_cores_${XP2_NUM_CORES_PER_HOST}_${XP2_NUM_CORES_PER_HOST}_workunits_${XP2_MIN_NUM_WORKUNITS}_${XP2_MAX_NUM_WORKUNITS}.pickled ./results_master_worker_hosts_${XP2_NUM_HOSTS}_${XP2_NUM_HOSTS}_cores_${XP2_NUM_CORES_PER_HOST}_${XP2_NUM_CORES_PER_HOST}_workunits_${XP2_MIN_NUM_WORKUNITS}_${XP2_MAX_NUM_WORKUNITS}.pdf 1> ./results_master_worker_hosts_${XP2_NUM_HOSTS}_${XP2_NUM_HOSTS}_cores_${XP2_NUM_CORES_PER_HOST}_${XP2_NUM_CORES_PER_HOST}_workunits_${XP2_MIN_NUM_WORKUNITS}_${XP2_MAX_NUM_WORKUNITS}.txt

XP3_NUM_HOSTS=1000
XP3_NUM_WORKUNITS=40000
XP3_MIN_NUM_CORES_PER_HOST=4
XP3_MAX_NUM_CORES_PER_HOST=40
XP3_STEP_NUM_CORES_PER_HOST=4

run_core_experiment:
	@echo "Running experiments for different numbers of cores per host"
	python3 ./run_experiments.py /tmp/results.pickled ${XP3_MIN_NUM_CORES_PER_HOST} ${XP3_MAX_NUM_CORES_PER_HOST} ${XP3_STEP_NUM_CORES_PER_HOST} ${XP3_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS} ${XP3_NUM_HOSTS_FOR_NUM_CORES_EXPERIMENTS} 1 ${XP3_NUM_WORKUNITS} ${XP3_NUM_WORKUNITS} 1 ${NUM_TRIALS} ${VERSIONS}
	cp /tmp/results.pickled ./results_master_worker_hosts_${XP3_NUM_HOSTS}_${XP3_NUM_HOSTS}_cores_${XP3_MIN_NUM_CORES_PER_HOST}_${XP3_MAX_NUM_CORES_PER_HOST}_workunits_${XP3_NUM_WORKUNITS}_${XP3_NUM_WORKUNITS}.pickled
	python3 ./plot_results.py ./results_master_worker_hosts_${XP3_NUM_HOSTS}_${XP3_NUM_HOSTS}_cores_${XP3_MIN_NUM_CORES_PER_HOST}_${XP3_MAX_NUM_CORES_PER_HOST}_workunits_${XP3_NUM_WORKUNITS}_${XP3_NUM_WORKUNITS}.pickled ./results_master_worker_hosts_${XP3_NUM_HOSTS}_${XP3_NUM_HOSTS}_cores_${XP3_MIN_NUM_CORES_PER_HOST}_${XP3_MAX_NUM_CORES_PER_HOST}_workunits_${XP3_NUM_WORKUNITS}_${XP3_NUM_WORKUNITS}.pdf 1> ./results_master_worker_hosts_${XP3_NUM_HOSTS}_${XP3_NUM_HOSTS}_cores_${XP3_MIN_NUM_CORES_PER_HOST}_${XP3_MAX_NUM_CORES_PER_HOST}_workunits_${XP3_NUM_WORKUNITS}_${XP3_NUM_WORKUNITS}.txt

clean:
	/bin/rm -rf build_* results_*.pdf results_*.pickled results_*.txt

