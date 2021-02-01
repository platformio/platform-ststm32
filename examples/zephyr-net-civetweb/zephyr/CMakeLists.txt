# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.13.1)

set (CONF_FILE "prj.conf")

include($ENV{ZEPHYR_BASE}/cmake/app/boilerplate.cmake NO_POLICY_SCOPE)
project(civetweb-server)

FILE(GLOB app_sources ../src/*.c)
target_sources(app PRIVATE ${app_sources})

zephyr_include_directories(../include)

set(gen_dir ${ZEPHYR_BINARY_DIR}/include/generated/)
