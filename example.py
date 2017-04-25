#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Example script, showing the rootplotting interface. 

@file:   style.py
@date:   25 April 2017
@author: Andreas Søgaard 
@email:  andreas.sogaard@cern.ch
"""

# Basic
import sys

# Scientific import(s)
import ROOT
import numpy as np

# Local import(s)
from tools import *
import ap


# Main function
def main ():
    
    # Check(s)
    if len(sys.argv) == 1:
        warning("No inputs were provided")
        return


    # Setup.
    # – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – 

    # Load data
    files  = sys.argv[1:]
    tree   = 'BoostedJet+ISRgamma/EventSelection/Pass/NumFatjetsAfterDphi/Postcut'
    prefix = 'leadingfatjet_'

    data = loadData(files, tree)
    info = loadData(files, 'BoostedJet+ISRgamma/outputTree', stop=1)

    # Rename variables
    data.dtype.names = [name.replace(prefix, '') for name in data.dtype.names]

    # Scaling by cross section
    xsec = loadXsec('sampleInfo.csv')

    # Append new DSID field
    data = append_fields(data, 'DSID', np.zeros((data.size,)), dtypes=int)
    for idx in info['id']:    
        msk = (data['id'] == idx) # Get mask of all 'data' entries with same id, i.e. from same file
        DSID = info['DSID'][idx]  # Get DSID for this file
        data['weight'][msk] *= xsec[DSID] # Scale by cross section x filter eff. for this DSID
        data['DSID']  [msk] = DSID # Store DSID
        pass
    
    msk_incl = (data['DSID'] >= 361039) & (data['DSID'] <= 361062)
    msk_WZ   = (data['DSID'] >= 305435) & (data['DSID'] <= 305439)

    
    # Plotting
    # – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – – 

    bins = np.linspace(0, 300, 31, endpoint=True)
    
    # Setup canvas
    c = ap.canvas(num_pads=2)

    # Add stacked backgrounds
    h_WZ   = c.stack(data['m'][msk_WZ],   bins=bins, weights=data['weight'][msk_WZ],   fillcolor=ROOT.kRed + 1,   label='W/Z + #gamma', scale=1)
    h_bkg  = c.stack(data['m'][msk_incl], bins=bins, weights=data['weight'][msk_incl], fillcolor=ROOT.kAzure + 7, label='Background')
    
    # Draw stats. error of stacked sum
    h_sum  = c.getStackSum()
    c.hist(h_sum, fillstyle=3245, fillcolor=ROOT.kGray+2, linecolor=ROOT.kGray + 3, label='Stats. uncert.', option='E2')
    
    # Add (pseudo-) data
    np.random.seed(21)
    h_data = c.plot (data['m'][msk_incl], bins=bins, weights=data['weight'][msk_incl] * (1. + np.random.randn(np.sum(msk_incl)) * 2.), markersize=0.8, label='Data')

    # Draw error- and ratio plots
    h_err   = c.ratio_plot((h_sum,  h_sum), option='E2')
    h_ratio = c.ratio_plot((h_data, h_sum), markersize=0.8)
    
    # Add labels and text
    c.xlabel('Signal jet mass [GeV]')
    c.ylabel('Events')
    c.ylabel('Data / Bkg.', idx_pad=1)
    c.lines(["#sqrt{s} = 13 TeV,  L = 36.1 fb^{-1}",
             "Trimmed anti-k_{t}^{R=1.0} jets"], 
            qualifier='Simulation Internal')

    # Add line(s) and limit(s)
    c.yline(1, idx_pad=1)
    c.ylim((0.5, 1.5), idx_pad=1)

    # Configure axis padding and -scale
    c.padding(0.35)
    c.log(True)

    # Draw legend
    c.legend()

    # Save and show plot
    c.save('test.pdf')
    c.show()

    return


# Main function call.
if __name__ == '__main__':
    main()
    pass
