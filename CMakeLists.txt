
cmake_minimum_required(VERSION 2.6.4)
project(libqi-js)
find_package(qibuild)

qi_install_program(qimessaging-json)
install(DIRECTORY libs DESTINATION /var/www COMPONENT runtime)
