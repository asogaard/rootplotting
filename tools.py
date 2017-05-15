# -*- coding: utf-8 -*-

""" Collection of utility tools. 

@file:   tools.py
@date:   25 April 2017
@author: Andreas Søgaard 
@email:  andreas.sogaard@cern.ch
"""

# Basic import(s)
import os

# Scientific import(s)
import ROOT
try:
    from root_numpy import tree2array

    import numpy as np
    from numpy.lib.recfunctions import append_fields
except:
    print "ERROR: Scientific python packages were not set up properly."
    print " $ source snippets/pythonenv.sh"
    print "or see e.g. [http://rootpy.github.io/root_numpy/start.html]."
    raise

# Global definitions
inf = np.finfo(float).max
eps = np.finfo(float).eps


def loadXsec (path, delimiter=',', comment='#'):
    """ Load cross section weights from file. """
    # @TODO: Use lambda's as accessors, to make to completely general?

    xsec = dict()
    with open(path, 'r') as f:
        for l in f:
            line = l.strip()
            if line == '' or line.startswith(comment):
                continue
            fields = [f.strip() for f in line.split(delimiter)]

            if fields[2] == 'Data': 
                continue

            # @TEMP: Assuming sum-of-weights normalisation included in per-event MC weights
            xsec[int(fields[0])] = float(fields[1]) * float(fields[3]) 

            pass
        pass

    return xsec


def loadData (paths, tree, branches=None, start=None, stop=None, step=None, prefix=None):
    """ Load data from ROOT TTree. """
    
    # Initialise output
    output = None

    # Loop file paths
    for ipath, path in enumerate(paths):
        
        # Open ROOT file
        if not os.path.isfile(path):
            warning("File '{:s}' does not exist.".format(path))
            continue
        
        if not path.endswith('.root'):
            warning("File '{:s}' is not a ROOT file.".format(path))
            continue

        f = ROOT.TFile(path, 'READ')
        
        # Get TTree
        t = f.Get(tree)

        if type(t) is not ROOT.TTree:
            warning("TTree '{:s}' was not found in file '{:s}'.".format(tree, path))
            continue

        # Read TTree into numpy array
        data = tree2array(t, branches=branches, start=start, stop=stop, step=step)

        # Append id field
        data = append_fields(data, 'id', np.ones((data.size,)) * ipath, dtypes=int)
        
        # Concatenate
        # Note: Force to be of tyoe numpy.ndarray, to avoid errors with mask when renaming
        if output is None:
            output = np.array(data, dtype=data.dtype)
        else:
            output = np.array(np.concatenate((output,data)), dtype=output.dtype)
            pass

        pass

    # Check(s)
    if output is None:
        warning("No data was loaded")
    else:
        # Remove prefix (opt.)
        if prefix:
            output.dtype.names = [name.replace(prefix, '') for name in output.dtype.names] 
            pass
        pass
    

    return output



def get_maximum (hist):
    """ Return the maximum bin content for a histogram. Assumes ... . Throws error if ... .  """

    # Check(s)
    if type(hist) == ROOT.THStack:
        return get_maximum(get_stack_sum(hist))
    elif type(hist) == ROOT.TGraph:
        N = hist.GetN()
        output, x, y = ROOT.Double(-inf), ROOT.Double(0), ROOT.Double(-inf)
        for i in range(N):
            hist.GetPoint(i, x, y)
            output = max(output,y)
            pass
        return output

    try:
        return max(map(hist.GetBinContent, range(1, hist.GetXaxis().GetNbins() + 1)))
    except ValueError:
        warning("get_maximum: No bins were found.")
    except:
        warning("get_maximum: Something didn't work here, for intput:")
        print hist
        pass
    return None


def get_minimum (hist):
    """ Return the minimum bin content for a histogram. Assumes ... . Throws error if ... .  """

    # Check(s)
    if type(hist) == ROOT.THStack:
        return get_minimum(get_stack_sum(hist))
    elif type(hist) == ROOT.TGraph:
        N = hist.GetN()
        output, x, y = ROOT.Double(inf), ROOT.Double(0), ROOT.Double(inf)
        for i in range(N):
            hist.GetPoint(i, x, y)
            output = min(output,y)
            pass
        return output

    try:
        return min(map(hist.GetBinContent, range(1, hist.GetXaxis().GetNbins() + 1)))
    except ValueError:
        warning("get_minimum: No bins were found.")
    except:
        warning("get_maximum: Something didn't work here, for intput:")
        print hist
        pass
    return None

def get_minimum_positive (hist):
    """ Return the minimum positive bin content for a histogram. Assumes ... . Throws error if ... .  """

    # Check(s)
    if type(hist) == ROOT.THStack:
        return get_minimum_positive(get_stack_sum(hist))
    elif type(hist) == ROOT.TGraph:
        N = hist.GetN()
        output, x, y = ROOT.Double(inf), ROOT.Double(0), ROOT.Double(inf)
        for i in range(N):
            hist.GetPoint(i, x, y)
            if x <= 0: continue
            output = min(output,y)
            pass
        return output

    try:
        return min([m for m in map(hist.GetBinContent, range(1, hist.GetXaxis().GetNbins() + 1)) if m > 0])
    except ValueError:
        warning("get_minimum_positive: No bins were found.")
    except:
        warning("get_minimum_positive: Something didn't work here, for intput:")
        print hist
        pass
    return None


def get_stack_sum (stack):
    """ ... """

    sumHisto = None
    for hist in stack.GetHists():
        if sumHisto is None:
            sumHisto = hist.Clone('sumHisto')
        else:
            sumHisto.Add(hist)
            pass
        pass
    return sumHisto


def is_overlay (pad):
    """ Determine whether input pad is of type 'overlay' """
    return type(pad).__name__.endswith('overlay')


def is_canvas (pad):
    """ Determine whether input pad is of type 'canvas' """
    return type(pad).__name__.endswith('canvas')


def warning (string):
    """ ... """
    print '\033[91m\033[1mWARNING\033[0m ' + string
    return


def wait ():
    """ Generic wait function.

    Halts the execution of the script until the user presses ``Enter``.
    """
    raw_input("\033[1mPress 'Enter' to continue...\033[0m")
    return
