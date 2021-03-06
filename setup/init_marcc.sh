#!/usr/bin/env bash

# =====================
# START A MARCC SESSION

# load modules
#module load python/2.7.9

module load gcc slurm sed git tmux byobu cmake autoconf/gcc automake/gcc boost cuda/8.0 cudnn/5.1 python/2.7.12 tensorflow/cuda-8.0/r1.3 parallel_studio_xe_2015 intel-mpi readline ruby piplib/1.3.1

# Helpful image tool
module load feh

# Setup paths for costar models
export PATH=$HOME/.local/lib/python3.6/site-packages/:$PATH
export PYTHONPATH=$HOME/.local/lib/python3.6/site-packages/:$PYTHONPATH


