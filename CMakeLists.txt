cmake_minimum_required(VERSION 2.8.12)
project(SimGridMasterWorker)

set(CMAKE_C_FLAGS --std=c99)

find_library(SIMGRID_LIBRARY NAMES simgrid)

add_executable(master_worker_v3_10 ./msg-app-masterworker-3.10.c)
add_executable(master_worker_v3_12 ./msg-app-masterworker-3.10.c)
add_executable(master_worker_v3_34 ./s4u-app-masterworkers.cpp)

target_link_libraries(master_worker_v3_10 ${SIMGRID_LIBRARY})
target_link_libraries(master_worker_v3_12 ${SIMGRID_LIBRARY})
target_link_libraries(master_worker_v3_34 ${SIMGRID_LIBRARY})

install(TARGETS master_worker_v3_10 DESTINATION bin)
install(TARGETS master_worker_v3_12 DESTINATION bin)
install(TARGETS master_worker_v3_34 DESTINATION bin)
