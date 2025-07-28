FROM ubuntu:22.04

LABEL maintainer="raven@rubicon.aleeas.com"
LABEL version="0.1"
LABEL description="Docker image for Daybook usage and development."

# Update Ubuntu
RUN apt update
RUN apt upgrade -y

# Configure locale and user
RUN apt install -y locales sudo
RUN groupadd -r user && useradd -m -g user user && \
    echo 'user ALL=NOPASSWD: ALL' > /etc/sudoers.d/user

# Reconfigure locale
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales

# Install daybook required packages
RUN apt install -y python3-venv python3-pip docutils-common bash-completion man-db

# Required to read man pages
RUN yes | unminimize

# Change user and configure environment variables
USER user
WORKDIR /home/user
ENV HOME=/home/user
ENV PATH="$PATH:$HOME/.local/bin"
ENV MANPATH="$HOME/.local/usr/share/man"

RUN pip install --user 'build<0.10.0'
RUN echo source $HOME/.local/etc/bash_completion.d/daybook_completion.sh >> $HOME/.bashrc
