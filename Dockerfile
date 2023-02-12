# Copyright (c) 2020 Bystronic Laser AG, author Jonas Grossenbacher
######################################################################
# This Dockerfile contains all necessary packages and SW and libraries
# to build Bystronic Kerf Control Service
######################################################################

# base image
FROM debian:bullseye 

# environment variables

# set proxy inside container
# Uncoment following lines for local tests if You're working in Bystronic Network
#ENV http_proxy  "http://ch10proxy.bystronic.com:8080"
#ENV https_proxy "http://ch10proxy.bystronic.com:8080"
#RUN sh -c 'echo "Acquire::http::Proxy \"http://ch10proxy.bystronic.com:8080\";" > /etc/apt/apt.conf.d/proxy.conf' && \
#    sh -c 'echo "Acquire::https::Proxy \"http://ch10proxy.bystronic.com:8080\";" >> /etc/apt/apt.conf.d/proxy.conf'

# got list with apt-mark showmanual
RUN apt update && apt install -y \
    build-essential \
    cli-common-dev \
    cmake \ 
    debhelper \
    # devscripts \
    dh-autoreconf \
    dh-virtualenv \
    dh-python\ 
    equivs \
    # git-all \
    libbz2-dev \
    libffi-dev \
    libgdbm-dev \
    libncurses5-dev \
    libnss3-dev \
    libprotobuf-dev \
    libreadline-dev \
    libssl-dev \
    openssl \
    protobuf-compiler \
    python-setuptools \
    # python-wheel \
    python3 \
    python3-all \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-systemd \
    python3-venv \
    python3-wheel \
    # pyvenv-foobar-build-deps \
    wget \
    zlib1g-dev \
