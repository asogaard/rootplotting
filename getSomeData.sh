#!/usr/bin/env bash

# Target directory for files
DIR=data

if [[ `echo $HOSTNAME | cut -c1-6` == "lxplus" ]]; then
    # Running on lxplus; simply create symbolic link
    rm -f ./$DIR
    ln -s /eos/atlas/user/a/asogaard/Analysis/2016/BoostedJetISR/outputObjdef/2017-04-27 $DIR

else
    # Running elsewhere; copy files
    UNAME=
    
    if [ ! $UNAME ]; then
	echo "Not running on lxplus; please provide a username (UNAME)"
    else
	mkdir -p $DIR
	scp -r ${UNAME}@lxplus.cern.ch:/afs/cern.ch/work/a/asogaard/public/Analysis/2016/BoostedJetISR/outputObjdef/objdef_MC_3610*.root ./$DIR/
	scp -r ${UNAME}@lxplus.cern.ch:/afs/cern.ch/work/a/asogaard/public/Analysis/2016/BoostedJetISR/outputObjdef/objdef_MC_30543*.root ./$DIR/
	scp -r ${UNAME}@lxplus.cern.ch:/afs/cern.ch/work/a/asogaard/public/Analysis/2016/BoostedJetISR/outputObjdef/objdef_MC_30544*.root ./$DIR/
    fi
    
fi