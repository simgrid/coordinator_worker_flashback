cmake_minimum_required(VERSION 2.8)
project(SimGridMasterWorker)

set(CMAKE_C_FLAGS --std=c99)

find_library(SIMGRID_LIBRARY NAMES simgrid)

add_executable(master_worker_v3_14 ./msg-app-masterworker.c)
add_executable(master_worker_v3_34 ./s4u-app-masterworkers.cpp)

target_link_libraries(master_worker_v3_14 ${SIMGRID_LIBRARY})
target_link_libraries(master_worker_v3_34 ${SIMGRID_LIBRARY})

install(TARGETS master_worker_v3_14 DESTINATION bin)
install(TARGETS master_worker_v3_34 DESTINATION bin)
