#!/usr/bin/env bash
# Run the daybook container in an interactive environment.
#
# The daybook installation is performed here so the container has
# the latest local version.

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPODIR=$SCRIPT_DIR/..

# Mount your own ledger files using -v
docker run --rm -it \
    -v $REPODIR:/home/user/daybook \
    daybook bash -c 'cd daybook/docs/man && make && cd - \
        && pip install --user ./daybook && daybook && bash'
