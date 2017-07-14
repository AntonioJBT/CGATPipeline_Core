##################################################
# Dockerfile for CGATPipeline_core 
# https://github.com/
##################################################


############
# Base image
############

# FROM continuumio/miniconda # probably OK but needs dependencies sorting out
# and maybe conflicts with Requirements.py
# FROM continuumio/anaconda # works
# FROM continuumio/anaconda3

# FROM jfloff/alpine-python:2.7
# FROM jfloff/alpine-python
# https://github.com/jfloff/alpine-python
# This is a minimal Python 3 image that can start from python or bash

FROM continuumio/miniconda3

# Or simply run:
# docker run --rm -ti jfloff/alpine-python bash
# docker run --rm -ti jfloff/alpine-python python hello.py

#########
# Contact
#########
MAINTAINER Antonio Berlanga-Taylor <a.berlanga@imperial.ac.uk>


#########################
# Update/install packages
#########################

# Install system dependencies

# For anaconda/miniconda:
#RUN apt-get update && apt-get install -y \
#    wget
#    bzip2 \
#    fixincludes \
#    unzip \
#    vim

# For Alpine:
# https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management
#RUN apk update && apk upgrade \
#     && apk add \
#     sudo

#############################
# Install additional packages
#############################

RUN pip install --upgrade pip
#                          setuptools \
#                          future \
#                          ruffus \
#                          numpy \
#                          pandas \
#                          pyyaml \
#    && pip list

# If running with anaconda:
#RUN conda update conda

# Install R:
RUN conda install -c r r-essentials \
    && conda update -c r r-essentials \
    && conda install rpy2

# conda create -n py35 python=3.5

# rpy2 is not in r-essentials, Dockerfile installation with pip errors, use
# conda install

#########################
# Install package to test 
#########################
# Install CGAT core utilities:

RUN cd home \
    && git clone https://github.com/AntonioJBT/CGATPipeline_core.git \
    && cd CGATPipeline_core \
    && python setup.py install \
    && cd ..

RUN pip install -r requirements.txt

###############################
# Install external dependencies
###############################



############################
# Default action to start in
############################
# Only one CMD is read (if several only the last one is executed)

# Set environment variables
# ENV PATH=/shared/conda-install/envs/cgat-devel/bin:$PATH

# Add an entry point to the cgat command
#ENTRYPOINT ["/shared/conda-install/envs/cgat-devel/bin/cgat"]

#CMD echo "Hello world"
CMD ["/bin/bash"]

# Create a shared folder between docker container and host
#VOLUME ["/shared/data"]
