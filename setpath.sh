#!/usr/bin/env bash
PYTHONPATH=$PYTHONPATH:"$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ./examples/customcommands
PYTHONPATH=$PYTHONPATH:"$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ../..
