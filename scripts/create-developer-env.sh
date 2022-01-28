#!/bin/bash -l

#Script that shows an example of creating a developer environment from a shared snapshot for Exawind software

cmd() {
  echo "+ $@"
  eval "$@"
}

set -e

printf "Starting at $(date).\n"

if [[ -z ${SPACK_MANAGER} ]]; then
    printf "\nSPACK_MANAGER not set so setting it to ${PWD}\n"
    cmd "export SPACK_MANAGER=${PWD}"
else
    printf "\nSPACK_MANAGER set to ${SPACK_MANAGER}\n"
fi

printf "\nActivating Spack-Manager...\n"
cmd "source ${SPACK_MANAGER}/start.sh"

printf "\nCreating developer environment...\n"
if [ "${SPACK_MANAGER_MACHINE}" == 'eagle' ]; then
  SNAPSHOT_DIR='/projects/exawind/exawind-snapshots/environment-latest'
  COMPILER='gcc'
  SPEC="nalu-wind@master+hypre+cuda cuda_arch=70 %${COMPILER}"
  BLACKLIST='nalu-wind hypre'
  DEV_COMMAND='spack manager develop nalu-wind@master; spack manager develop hypre@develop'
  VIEW="${COMPILER}-cuda"
elif [ "${SPACK_MANAGER_MACHINE}" == 'rhodes' ]; then
  SNAPSHOT_DIR='/projects/ecp/exawind/exawind-snapshots/environment-latest'
  COMPILER='gcc'
  SPEC="nalu-wind@master+hypre %${COMPILER}"
  BLACKLIST='nalu-wind hypre'
  DEV_COMMAND='spack manager develop nalu-wind@master; spack manager develop hypre@develop'
  VIEW="${COMPILER}"
fi
cmd "spack manager create-env --directory ${SPACK_MANAGER}/environments/exawind --spec "${SPEC}""
cmd "spack env activate -d ${SPACK_MANAGER}/environments/exawind"
cmd "spack config add config:concretizer:original"
cmd "spack manager external ${SNAPSHOT_DIR} -v ${VIEW} --blacklist ${BLACKLIST}"
cmd "${DEV_COMMAND}"
cmd "spack concretize -f"
cmd "spack install"

printf "\nDone at $(date)\n"