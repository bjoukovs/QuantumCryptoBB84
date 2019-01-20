#!/usr/bin/env sh
PIDS=$(ps aux | grep python | grep -i "Alice\|Bob\|Eve" | awk {'print $2'})
if [ "$PIDS" != "" ]
then
        kill -9 $PIDS
fi

sh "$NETSIM/run/startAll.sh" -nd "Alice Bob Eve"

python $NETSIM/project/alice.py &
python $NETSIM/project/bob.py &
python $NETSIM/project/eve.py &
