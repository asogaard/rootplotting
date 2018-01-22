# rootplotting
Scripts for producing ROOT plots using a matplotlib-like interface.


## Setup

To setup, do:
```bash
$ git clone git@github.com:asogaard/rootplotting.git
$ pip install -e rootplotting/
```
Then, the tools in this package will be available by importing `import rootplotting as rp` anywhere in python.


## Contents

This repository contains several small python files that will hopefully make your ROOT-plotting life a bit easier. These are all stored in [rootplotting/](rootplotting/). This package contains several plotting classes — in particular the `pad`, `canvas`, and `overlay` — which allow you to create ROOT plots using an interface similar to that of the popular python library matplotlib:

```python
import ROOT
import rootplotting import rp

# ...

# data, bkg, WZ = structured numpy arrays
# bins = list of bin edges

# Create canvas
c = rp.canvas()

# Draw stacked backgrounds
h_WZ  = c.stack(WZ ['m'], bins=bins, weights=WZ ['weight'], \
               fillcolor=ROOT.kAzure + 2, label='W(qq) + #gamma', scale=1.0)
h_bkg = c.stack(bkg['m'], bins=bins, weights=bkg['weight'], \
                fillcolor=ROOT.kAzure + 7, label='Incl. #gamma')

# Draw stats. error of stacked sum
h_sum  = c.getStackSum()
c.hist(h_sum, fillstyle=3245, fillcolor=ROOT.kGray+2, \
       linecolor=ROOT.kGray + 3, label='Stats. uncert.', option='E2')

# Draw data
h_data = c.plot(data['m'], bins=bins, markersize=0.8, label='Data')

# Add labels and text
c.xlabel('Signal jet mass [GeV]')
c.ylabel('Events')
c.text(["#sqrt{s} = 13 TeV,  L = 36.1 fb^{-1}",
        "Trimmed anti-k_{t}^{R=1.0} jets"],
       qualifier='Simulation Internal')

# Configure y-axis scale
c.log(True)

# Draw legend
c.legend()

# Save and show plot
c.save('test.pdf')
c.show()
```

In addition, [rootplotting/tools.py](rootplotting/tools.py) contains some utility functions, e.g. to make the reading of ROOT TTrees into numpy arrays easier, and [rootplotting/style.py](rootplotting/style.py) is a style sheet for the ROOT plots, based on the ATLAS style recommendations.


## Dependencies

The only non-standard dependencies should be ROOT and numpy. If you're on lxplus, you can set up the latter as e.g.
```bash
$ source /cvmfs/sft.cern.ch/lcg/views/LCG_91/x86_64-slc6-gcc62-opt/setup.sh
```
