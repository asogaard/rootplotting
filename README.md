# rootplotting
Scripts for producing ROOT plots using a matplotlib-like interface. Requires `numpy` for running. If you're on lxplus, you can set it up as

```
$ source /cvmfs/sft.cern.ch/lcg/views/LCG_88/x86_64-slc6-gcc49-opt/setup.sh
```

## Contents

This repository contains several small `python` files that will hopyfully make your `ROOT`-plotting life a bit easier. In particular:

* [ap.py](ap.py): Contains plotting classes, most notably the `canvas` class that allows you to create `ROOT` plots using an interface similar to that of the popular python library `matplotlib`.
* [tools.py](tools.py): Contains some utility functions, e.g. to make the reading of `ROOT` TTrees into `numpy` arrays easier.
* [style.py](style.py): Style sheet for the `ROOT` plots, based on the ATLAS style recommendations.
* [examples.py](example.py): An python script showing how to make pretty plots in just a few lines. Run as 
```
$ python example.py
```
Requires that you have downloaded data of the correct format using...
* [getSomeData.sh](getSomeData.sh): Set your lxplus username in the script (`UNAME=...`) and run
```
$ source getSomeData.sh
```
to download some `ROOT` files that can be used along with the example above.
* [sampleInfo.csv](sampleInfo.csv): CSV-file containing cross-sections and generator filter efficiencies for the Monte Carlo samples downloaded using the [getSomeData.sh](getSomeData.sh) script.

