.NOTPARALLEL:


default: 
	docker build -t simgrid_v3_14 -f Dockerfile_simgrid_v3_14  .
	/bin/rm -rf build_simgrid_v3_14
	mkdir -rf build_simgrid_v3_14
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_14/ simgrid_v3_14 cmake ..
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_14/ simgrid_v3_14 make master_worker_v3_14
	docker build -t simgrid_v3_34 -f Dockerfile_simgrid_v3_34  .
	/bin/rm -rf build_simgrid_v3_34
	mkdir -rf build_simgrid_v3_34
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_34/ simgrid_v3_34 cmake ..
	docker run -it --rm -v `pwd`:/home/simgrid -w /home/simgrid/build_simgrid_v3_34/ simgrid_v3_34 make master_worker_v3_34
	./run_experiments.py

