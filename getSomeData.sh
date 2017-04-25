#!/usr/bin/env bash

UNAME=

if [ ! $UNAME ]; then
    echo "No username provided"
else
    mkdir -p data
    cd data/
    scp -r ${UNAME}@lxplus.cern.ch:/afs/cern.ch/work/a/asogaard/public/Analysis/2016/BoostedJetISR/outputObjdef/objdef_MC_3610*.root .
    scp -r ${UNAME}@lxplus.cern.ch:/afs/cern.ch/work/a/asogaard/public/Analysis/2016/BoostedJetISR/outputObjdef/objdef_MC_30543*.root .
    scp -r ${UNAME}@lxplus.cern.ch:/afs/cern.ch/work/a/asogaard/public/Analysis/2016/BoostedJetISR/outputObjdef/objdef_MC_30544*.root .
    cd -
fi