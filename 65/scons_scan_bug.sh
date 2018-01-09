#! /usr/bin/env bash

set -ex

scons=$1

if [ "$scons" = "" ]; then
  scons=scons
fi

mkdir -p scons_test
cd scons_test

mkdir -p src
echo '#include "inc1"' > src/foo.c

mkdir -p src/inc/inc1
mkdir -p src/inc/inc2
echo > src/inc/inc2/inc1

echo 'SConscript("src/SConscript", build_dir = "build", duplicate = 0)' > SConstruct

echo 'StaticObject("foo.c", CPPPATH = ["#build/inc", "#src/inc/inc2"])' > src/SConscript

$scons .
