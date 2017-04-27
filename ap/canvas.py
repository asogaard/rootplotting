# -*- coding: utf-8 -*-

""" Wrapper around ROOT TCanvas, handling pads, showing, and saving. 

@file:   canvas.py
@date:   26 April 2017
@author: Andreas Søgaard 
@email:  andreas.sogaard@cern.ch
"""

# Scientific import(s)
import ROOT
try:
    import numpy as np
    from root_numpy import fill_hist, array2hist
except:
    print "ERROR: Scientific python packages were not set up properly."
    print " $ source snippets/pythonenv.sh"
    print "or see e.g. [http://rootpy.github.io/root_numpy/start.html]."
    raise

# Local import(s)
from tools import *
from style import *
from pad import *


# Class definition
class canvas (object):
    """ 
    docstring for canvas 
    @TODO: Elaborate! 
    """

    def __init__(self, num_pads=1, size=None, fraction=0.3, batch=False, ratio=True):
        super(canvas, self).__init__()
        
        ROOT.gROOT.SetBatch(batch)
        
        # Check(s)
        assert type(num_pads) == int, "Number of pads must be an integer"
        assert num_pads < 3, "Requested number of pads {} is too large".format(num_pads)
        assert num_pads > 0, "Requested number of pads {} is too small".format(num_pads)

        # Member variables
        self._num_pads = num_pads
        self._fraction = fraction if num_pads == 2 else 0.
        self._size = size or ((600, int(521.79/float(1. - fraction))) if (num_pads == 2 and ratio) else (600,600))
        self._canvas = ROOT.TCanvas('c_{}'.format(id(self)), "", self._size[0], self._size[1])
        self._ratio = ratio and self._num_pads == 2
        self._setup = False
        
        # -- Pads
        self._pads = list()
        if   self._num_pads == 1:
            self._pads.append(pad(self, (0, 0, 1, 1)))
        elif self._num_pads == 2:
            self._pads.append(pad(self, (0, fraction, 1, 1)))
            self._pads.append(pad(self, (0, 0, 1, fraction)))
            pass

        # Draw pads
        for p in self._pads: 
            self._canvas.cd()
            p._pad.Draw()
            self._canvas.Update()
            pass

        return



    # Public accessor methods
    # ----------------------------------------------------------------

    def pad (self):
        """ ... """
        assert len(self._pads) == 1, "More than one pad exists; call is ambiguous"
        return self._pads[0]


    def pads (self):
        """ ... """
        return self._pads



    # Public deferral methods
    # ----------------------------------------------------------------

    def defer (idx_default): # Decorators taking arguments need an additional level of nesting.
        def inner(func):
            def wrapper (self, *args, **kwargs):
                idx_pad = kwargs.pop('idx_pad', idx_default)
                assert idx_pad == -1 or (idx_pad >= 0 and idx_pad < self._num_pads), "Requested pad index {} is no good.".format(idx_pad)
                # Find non-overlay pad
                if is_overlay(self._pads[idx_pad]):
                    idx_pad = len(self._pads) - 1
                    while idx_pad >= 0:
                        idx_pad -= 1
                        if not is_overlay(self._pads[idx_pad]): break
                        pass
                    pass
                assert idx_pad == -1 or (idx_pad >= 0 and idx_pad < self._num_pads), "Requested pad index {} is no good.".format(idx_pad)
                method = getattr(self._pads[idx_pad], func.__name__)
                # Note: func(self, ...) is never called
                return method(*args, **kwargs)
            return wrapper
        return inner


    @defer(0) 
    def text (self, *args, **kwargs): return
    """ Defer method to _first_ pad, by default """

    @defer(0)
    def legend (self, *args,**kwargs): return
    
    @defer(-1) 
    def xlabel (self, *args, **kwargs): return
    """ Defer method to _last_ non-overlay pad, by default """

    @defer(0)
    def ylabel (self, *args, **kwargs): return
    
    @defer(0)
    def plot (self, *args, **kwargs): return

    @defer(0)
    def hist (self, *args, **kwargs): return

    @defer(0)
    def hist2d (self, *args, **kwargs): return
    
    @defer(0)
    def stack (self, *args, **kwargs): return
    
    @defer(0)
    def graph (self, *args, **kwargs): return

    @defer(-1)
    def ratio_plot (self, *args, **kwargs): return

    @defer(0)
    def getStackSum (self, *args, **kwargs): return

    @defer(0)
    def ylim (self, *args, **kwargs): return

    @defer(0)
    def padding (self, *args, **kwargs): return

    @defer(0)
    def log (self, *args, **kwargs): return

    @defer(0)
    def line (self, *args, **kwargs): return
    
    @defer(0)
    def lines (self, *args, **kwargs): return

    @defer(0)
    def xline (self, *args, **kwargs): return
    
    @defer(0)
    def yline (self, *args, **kwargs): return
        
    @defer(0)
    def xlines (self, *args, **kwargs): return
    
    @defer(0)
    def ylines (self, *args, **kwargs): return



    # Public high-level/management methods
    # ----------------------------------------------------------------
    
    def _update (self):
        """ ... """

        self._canvas.Update()

        # Set up main- and ratio pads, in the most common case
        if self._ratio:# and not self._setup:
            self._setup_ratio_pads()
            pass

        # Update children pads
        for p in self._pads:
            p._update()
            pass

        return

    def show (self):
        """ ... """
        self._update()
        wait()
        return


    def save (self, path):
        """ ... """

        self._update()
        self._canvas.SaveAs(path)
        return
    


    # Private accessor methods
    # ----------------------------------------------------------------
    
    def _bare (self):
        """ ... """
        return self._canvas


    def _setup_ratio_pads (self):
        """ ... """

        # Main pad(s) -- incl. overlay
        for main_pad in self._pads[:-1]:

            if main_pad._xaxis() is None: continue

            main_pad._xaxis().SetLabelOffset(9999.)
            main_pad._xaxis().SetTitleOffset(9999.)
            main_pad._bare().SetBottomMargin(0.030)
            main_pad._bare().Modified()
            main_pad._bare().Update()

            if is_overlay(main_pad):
                main_pad._yaxis().SetLabelOffset(9999.)
                main_pad._yaxis().SetTitleOffset(9999.)
                main_pad._xaxis().SetTickLength(0)
                main_pad._yaxis().SetTickLength(0)
                pass
            pass

        # Ratio pad
        ratio_pad = self._pads[-1]

        ratio_pad._bare().SetBottomMargin(0.30)
        ratio_pad._bare().SetTopMargin   (0.040)

        ratio_pad._xaxis().SetTitleOffset(ROOT.gStyle.GetTitleOffset('x') * ratio_pad._scale[1])
        ratio_pad._yaxis().SetTitleOffset(ROOT.gStyle.GetTitleOffset('y') * ratio_pad._scale[0])
        ratio_pad._yaxis().SetNdivisions(505)
        ratio_pad._xaxis().SetTickLength (ROOT.gStyle.GetTickLength ('x') * ratio_pad._scale[1])
        #ratio_pad._xaxis().SetTitleOffset(4)
        if ratio_pad._ylim is not None:
            axisrange = ratio_pad._ylim
            ratio_pad._yaxis().SetRangeUser(*axisrange)
            ratio_pad._get_first_primitive().SetMinimum(axisrange[0])
            ratio_pad._get_first_primitive().SetMaximum(axisrange[1])
            pass
        ratio_pad._bare().Modified()
        ratio_pad._bare().Update()

        self._setup = True

        return

    pass
    