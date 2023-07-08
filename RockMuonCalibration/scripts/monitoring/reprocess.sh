#!/bin/bash
#
#
# script to reprocess rockmuon monitoring job.
#

year=2018
month=01

start_day=22
end_day=23

pushd ${ROCKMUONCALIBRATIONROOT}/scripts

for ((i=start_day; i <= end_day; i++))
do
    cd ./monitoring
    python remove_ntuples.py $year $month $i
    cd ..
done

for ((i=start_day; i <= end_day; i++))
do
        cd ./processing
	python submitGridJobs.py --year $year --month $month --day $i
	cd ..
done	
popd


