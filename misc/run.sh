#!/usr/bin/env bash
cd $BOLASDIR
source $BOLASDIR/bin/activate
pgrep -f run.py || python $BOLASDIR/run.py
