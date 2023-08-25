.NOTPARALLEL:

MIN_HOSTS=1000
MAX_HOSTS=10000
STEP_HOSTS=1000
NUM_TRIALS=5

default:
	@echo "make build  : will build the Docker containers and the simulators"
	@echo "make run    : will run the experiment with whatever has been built last"

build: clean
	docker build -t simgrid_v3_14 -f Dockerfile_simgrid_v3_14  .
	mkdir build_simgrid_v3_14
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_14/ simgrid_v3_14 cmake ..
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_14/ simgrid_v3_14 make master_worker_v3_14
	docker build -t simgrid_v3_34 -f Dockerfile_simgrid_v3_34  .
	mkdir build_simgrid_v3_34
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_34/ simgrid_v3_34 cmake ..
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_34/ simgrid_v3_34 make master_worker_v3_34

run:
	python3 ./run_experiments.py ${MIN_HOSTS} ${MAX_HOSTS} ${STEP_HOSTS} ${NUM_TRIALS}


clean:
	/bin/rm -rf build_*

