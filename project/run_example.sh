#!/usr/bin/env sh
TEST_PIDS=$(ps aux | grep python | grep -E "Test" | awk {'print $2'})
if [ "$TEST_PIDS" != "" ]
then
        kill -9 $TEST_PIDS
fi

sh $NETSIM/run/startAll.sh -nd "Alice Bob Eve"

python aliceTest.py &
python bobTest.py &
python eveTest.py &
