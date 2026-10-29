cmake_minimum_required(VERSION 3.8)
project(seeker_sim)

find_package(ament_cmake REQUIRED)

# No code to compile yet: just copy these folders into the install space
install(DIRECTORY urdf worlds config launch rviz DESTINATION share/${PROJECT_NAME})

ament_package()
