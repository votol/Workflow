cmake_minimum_required(VERSION 3.0)

get_filename_component(PARENT_DIR ${CMAKE_CURRENT_SOURCE_DIR} DIRECTORY)

add_custom_command(
    OUTPUT  schema.h
    COMMAND ${PARENT_DIR}/Workflow/scripts/generateSchema.py -d ${PARENT_DIR}/description.yaml -f ${CMAKE_CURRENT_BINARY_DIR}/schema.h
    DEPENDS ${PARENT_DIR}/description.yaml
)

get_filename_component(PARENT_DIR ${CMAKE_CURRENT_SOURCE_DIR} DIRECTORY)
include_directories (${CMAKE_CURRENT_BINARY_DIR})

add_executable(${PROJECT_NAME}
    main.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/schema.h
)



