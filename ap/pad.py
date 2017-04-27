# -*- coding: utf-8 -*-

""" Wrapper around ROOT TPad, handling plotting, labeling, text, and legend. 

@file:   pad.py
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
from ..tools import *
from ..style import *

# Enum class, for easy handling different plotting cases
def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

PlotType = Enum('plot', 'hist', 'hist2d', 'stack', 'graph')


# Class definition
class pad (object):
    """ 
    docstring for pad 
    @TODO: Elaborate! 
    """

    def __init__(self, base, coords):
        super(pad, self).__init__()
        
        # Check(s)
        #assert type(base) in [ap.canvas, ap.pad], "..."
        assert type(coords) in [list, tuple], "Pad coordinates must be of type list or tuple."
        assert len(coords) == 4, "Number of coordinates provided {} is not equal to 4.".format(len(coords))
        assert coords[0] < coords[2], "X-axis coordinates must be increasing ({:%.3f}, :%.3f})".format(coords[0], coords[2])
        assert coords[1] < coords[3], "X-axis coordinates must be increasing ({:%.3f}, :%.3f})".format(coords[1], coords[3])

        # Member variables
        # -- TPad-type
        self._base = base
        self._base._bare().cd()
        self._pad = ROOT.TPad('pad_{}_{}'.format(self._base._bare().GetName(), id(self)), "", *coords)
        self._coords = coords
        self._scale  = (1./float(coords[2] - coords[0]), 1./float(coords[3] - coords[1]))

        # -- Book-keeping
        self._primitives = list()
        self._entries = list()
        self._stack = None
        self._legend = None
        self._children = list()

        # -- Plotting cosmetics
        self._padding = 0.4
        self._log  = False
        self._ylim = None
        self._line = None
        
        # Draw pad
        self._base._bare().cd()
        self._pad.Draw()
        self._base._bare().Update()
        return



    # Decorators
    # ----------------------------------------------------------------

    # Make sure that we're always on the current pad
    def cd (func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self._pad, 'cd'):
                self._pad.cd()
                pass
            return func(self, *args, **kwargs)
        return wrapper

    # Update pad upon completion of methdd
    def update (func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if hasattr(self._pad, 'Modified'):
                self._pad.Modified()
                self._pad.Update()
                pass
            return result
        return wrapper



    # Public plotting methods
    # ----------------------------------------------------------------

    def plot (self, data, **kwargs):
        """ ... """
        return self._plot(PlotType.plot, data, **kwargs)


    def hist (self, data, **kwargs):
        """ ... """
        return self._plot(PlotType.hist, data, **kwargs)


    def hist2d (self, data, **kwargs):
        """ ... """
        return self._plot(PlotType.hist2d, data, **kwargs)


    def stack (self, data, **kwargs):
        """ ... """
        return self._plot(PlotType.stack, data, **kwargs)


    def graph (self, data, **kwargs):
        """ ... """
        return self._plot(PlotType.graph, data, **kwargs)


    def ratio_plot (self, data, **kwargs):
        """ ... """
        return self._ratio_plot(PlotType.plot, data, **kwargs)



    # Public accessor/mutator methods
    # ----------------------------------------------------------------

    def getStackSum (self):
        """ ... """

        # Check(s)
        if self._stack is None: return None
        return get_stack_sum(self._stack)


    def log (self, log=True):
        """ ... """

        # Check(s)
        assert type(log) == bool, "Log parameter must be a boolean"

        # Set log
        self._log = log
        self._update()
        return


    def ylim (self, *args):
        """ ... """

        # Check(s)
        if type(args) == list and len(args) == 1:
            self.ylim(*args)
            return

        assert len(args) == 2, "Y-axis limits have size {}, which is different from two as required.".format(len(ylim))

        # Store axis limits
        self._ylim = args
        return


    def padding (self, padding):
        """ ... """

        # Check(s)
        assert padding > 0, "Padding must be greater than zero; %.2f requested." % padding
        assert padding < 1, "Padding must be smaller than one; %.2f requested." % padding

        # Set padding
        self._padding = padding
        self._update()
        return



    # Public line-drawing methods
    # ----------------------------------------------------------------

    @cd
    def line (self, x1, y1, x2, y2):
        """ ... """

        # Check(s)
        if self._line is None:
            self._line = ROOT.TLine()
            self._line.SetLineStyle(2)
            self._line.SetLineColor(ROOT.kGray + 3)
            pass

        # Draw line
        self._line.DrawLine(x1, y1, x2, y2)
        return


    def lines (self, coords):
        """ ... """

        for coord in coords:
            self.line(*coord)
            pass
        return


    def ylines (self, ys):
        """ ... """

        for y in ys: 
            self.yline(y)
            pass
        return


    def xlines (self, xs):
        """ ... """

        for x in xs: 
            self.xline(x)
            pass
        return


    def yline (self, y):
        """ ... """
        
        xaxis = self._xaxis()
        xmin, xmax = xaxis.GetXmin(), xaxis.GetXmax()
        self.line(xmin, y, xmax, y)
        return


    def xline (self, x):
        """ ... """
        
        ymin, ymax = self._pad.GetUymin(), self._pad.GetUymax()
        self.line(x, ymin, x, ymin)
        return



    # Public text/decoration methods
    # ----------------------------------------------------------------

    def xlabel (self, title):
        """ ... """

        try:
            self._xaxis().SetTitle(title)
        except AttributeError:
            # No axis was found
            pass
        return


    def ylabel (self, title):
        """ ... """

        try:
            self._yaxis().SetTitle(title)        
        except AttributeError:
            # No axis was found
            pass
        return


    @cd
    @update
    def text (self, lines=[], qualifier='', ATLAS=True):
        """ ... """ 

        # Check(s)
        # ...

        # Create text instance
        t = ROOT.TLatex()
        
        # Compute drawing coordinates
        h = self._pad.GetWh() / self._scale[1] #* (1. - self._fraction) # @TODO: Improve
        w = self._pad.GetWw() / self._scale[0]

        offset = 0.05
        ystep = t.GetTextSize() / float(h) * 1.30
        scale = 1.#(w/float(h) if w > h else h/float(w))

        x =       self._pad.GetLeftMargin() + offset * scale
        y = 1.0 - self._pad.GetTopMargin()  - offset - t.GetTextSize() / float(h) * 1.0

        # Draw ATLAS line
        if ATLAS or qualifier:
            t.DrawLatexNDC(x, y, "{ATLAS}{qualifier}".format(ATLAS="#scale[1.15]{#font[72]{ATLAS}}#scale[1.05]{  }" if ATLAS else "", qualifier= "#scale[1.05]{%s}" % qualifier))
            y -= ystep * 1.30
            pass

        # Draw lines.
        for line in lines:
            t.DrawLatexNDC(x, y, line)
            y -= ystep;
            pass

        return


    @cd
    @update
    def legend (self, header=None, categories=None,
                xmin=None,
                xmax=None,
                ymin=None,
                ymax=None,
                width=0.30,
                horisontal='R',
                vertical='T'):
        """ Draw legend on TPad. """

        # Check(s)
        N = len(self._get_all_entries())
        if N == 0:
            return

        if self._legend:
            warning('A legend has already been constructed.')
            return
        
        # Compute drawing coordinates
        h = self._pad.GetWh() / self._scale[1]
        w = self._pad.GetWw() / self._scale[0]

        fontsize = ROOT.gStyle.GetLegendTextSize()

        offset = 0.05
        height = (N + (1 if header else 0) + (len(categories) if categories else 0)) * fontsize / float(h) * 1.30

        # Setting x coordinates.
        if not (xmin or xmax):
            if   horisontal.upper() == 'R':
                xmax = 1. - self._pad.GetRightMargin() - offset
            elif horisontal.upper() == 'L':
                xmin = self._pad.GetLeftMargin() + offset
            else:
                warning("legend: Horisontal option '%s' not recognised." % horisontal)
                return
            pass
        if xmax and (not xmin):
            xmin = xmax - width
            pass
        if xmin and (not xmax):
            xmax = xmin + width
            pass

        # Setting y coordinates.
        if not (ymin or ymax):
            if   vertical.upper() == 'T':
                ymax = 1.0 - self._pad.GetTopMargin() - offset - fontsize / float(h) * 1.8
            elif vertical.upper() == 'B':
                ymin = self._pad.GetBottomMargin() + offset
            else:
                warning("legend: Vertical option '%s' not recognised." % vertical)
                return
            pass
        if ymax and (not ymin):
            ymin = ymax - height
            pass
        if ymin and (not ymax):
            ymax = ymin + height
            pass

        # Create legend
        self._legend = ROOT.TLegend(xmin, ymin, xmax, ymax)

        if header:
            self._legend.AddEntry(None, header, '')
            pass

        # @TODO: Defer to parent pad, if 'overlay'
        for (h,n,t) in self._get_all_entries(): 
            if type(h) == ROOT.THStack: continue
            self._legend.AddEntry(h, n, t)
            pass

        # @TODO: Improve
        if categories:
            for icat, (name, hist, opt) in enumerate(categories):
                self._legend.AddEntry(hist, name, opt)
                pass
            pass

        self._legend.Draw()
        return
    


    # Private accessor methods
    # ----------------------------------------------------------------

    def _bare (self):
        """ ... """

        self._pad
        return


    def _xaxis (self):
        """ ... """

        # Return axis
        primitive = self._get_first_primitive()

        if primitive is None:
            warning("Cannot access x-axis")
            return None

        if not hasattr(primitive, 'GetXaxis'): 
            return None

        return primitive.GetXaxis()


    def _yaxis (self):
        """ ... """

        # Return axis
        primitive = self._get_first_primitive()

        if primitive is None:
            warning("Cannot access y-axis")
            return None

        if not hasattr(primitive, 'GetYaxis'): 
            return None

        return primitive.GetYaxis()


    def _get_first_primitive (self):
        """ ... """

        # Check(s)
        if len(self._pad.GetListOfPrimitives()) < 2:
            warning("Nothing was drawn; cannot access first primitive.")
            return None

        # Return first primitive
        return self._pad.GetListOfPrimitives()[1]



    # Private plotting methods
    # ----------------------------------------------------------------

    def _plot (self, plottype, data, display=True, **kwargs):
        """ ... """
        
        # Get plot option
        if 'option' not in kwargs:
            kwargs['option'] = self._get_plot_option(plottype)
            pass

        if type(data).__module__.startswith(np.__name__):
            # Numpy-type
            if plottype == PlotType.stack:
                hist = self._plot1D_numpy(data, display=False,   **kwargs)
                return self._plot1D_stack(hist, display=display, **kwargs)
            else:
                return self._plot1D_numpy(data, display=display, **kwargs)

        elif type(data).__name__.startswith('TH1'):
            # ROOT TH1-type
            if plottype == PlotType.stack:
                hist = self._plot1D      (data, display=False,   **kwargs)
                return self._plot1D_stack(hist, display=display, **kwargs)
            else:
                return self._plot1D      (data, display=display, **kwargs)

        else:
            warning("Input data type not recognised:")
            print type(data[0])
            pass
        
        return None


    def _ratio_plot (self, plottype, data, **kwargs):
        """ ... """

        # Check(s)
        assert type(data) == type(data), "Input data types must match"

        # Get plot option
        if 'option' not in kwargs:
            kwargs['option'] = self._get_plot_option(plottype)
            pass
            
        if type(data[0]).__module__.startswith(np.__name__):
            # Numpy-type
            return self._ratio_plot1D_numpy(data, **kwargs)

        elif type(data[0]).__name__.startswith('TH1'):
            # ROOT TH1-type
            return self._ratio_plot1D      (data, **kwargs)

        else:
            warning("Input data type not recognised:")
            print type(data[0])
            pass
        return None


    def _plot1D_numpy (self, data, bins, weights=None, option='', **kwargs):
        """ ... """

        # Check(s)
        if bins is None:
            warning("You need to specify 'bins' when plotting a numpy-type input.")
            return

        if len(bins) < 2:
            warning("Number of bins {} is not accepted".format(len(bins)))
            return

        # Fill histogram
        if len(data) == len(bins):
            # Assuming 'data' and 'bins' are sets of (x,y)-points
            h = ROOT.TGraph(len(bins), bins, data)
        else:
            h = ROOT.TH1F('h_{}'.format(id(data)), "", len(bins) - 1, bins)
            if len(data) == len(bins) - 1:
                # Assuming 'data' are bin values
                array2hist(data, h)
            else:
                # Assuming 'data' are values to be filled
                fill_hist(h, data, weights=weights)
                pass
            pass
        
        # Plot histogram
        return self._plot1D(h, option, **kwargs)


    def _ratio_plot1D_numpy (self, data, bins, weights=None, option='', **kwargs):
        """ ... """

        # Check(s)
        if bins is None:
            warning("You need to specify 'bins' when plotting a numpy-type input.")
            return

        if len(bins) < 2:
            warning("Number of bins {} is not accepted".format(len(bins)))
            return

        # Fill histogram
        h1 = ROOT.TH1F('h_num_{}'.format(id(data)), "", len(bins) - 1, bins)
        h2 = ROOT.TH1F('h_den_{}'.format(id(data)), "", len(bins) - 1, bins)
        fill_hist(h1, data[0], weights=weights[0])
        fill_hist(h2, data[1], weights=weights[1])
        
        return _ratio_plot1D((h1,h2), option, **kwargs)


    @cd
    @update
    def _plot1D (self, hist, option='', display=True, scale=None, **kwargs):
        """ ... """

        # Check(s)
        # ...
            
        # Scale
        if scale and type(hist) != ROOT.THStack:
            hist.Scale(scale)
            pass

        # Style
        self._reset_style(hist, option)
        self._style(hist, **kwargs)
        
        # Append draw option (opt.)
        if is_overlay(self):
            option += " ][ SAME"
        elif len(self._primitives) > 0:
            option += " SAME"
            pass

        # Only plot if requested
        if display is None or not display: 
            return hist

        # Draw histograms
        if type(hist) in [ROOT.THStack, ROOT.TGraph]:
            hist.Draw(option)
        else:
            hist.DrawCopy(option)
            pass
        
        # Store reference to primitive
        self._primitives.append(hist)

        # Check whether several filled histograms have been added
        if (type(hist) == ROOT.THStack or hist.GetFillColor() != 0) and len(filter(lambda h: type(h) == ROOT.THStack or (type(h).__name__.startswith('TH') and h.GetFillColor() != 0 and not option.startswith('E')), self._primitives)) == 2:
            warning("Several filled, non-stacked histograms have been added. This may be misleading.")
            pass

        if type(hist) != ROOT.THStack:

            # Store legend entry
            if 'label' in kwargs and kwargs['label'] is not None:
                
                opt = self._get_label_option(option, hist)
                
                if kwargs['label'].strip().lower() == 'data':
                    self._entries.insert(0, (hist, kwargs['label'], opt))
                else:
                    self._entries.append((hist, kwargs['label'], opt))
                    pass
                pass

            pass
        
        return hist


    def _ratio_plot1D (self, hists, option='', **kwargs):
        """ ... """

        h = hists[0].Clone(hists[0].GetName() + '_ratio')
        for bin in range(1, h.GetXaxis().GetNbins() + 1):
            denom = hists[1].GetBinContent(bin)
            h.SetBinContent(bin, h.GetBinContent(bin) / denom if denom > 0 else 1)
            h.SetBinError  (bin, h.GetBinError  (bin) / denom if denom > 0 else 9999.)
            pass

        # Plot histogram
        return self._plot1D(h, option, **kwargs)


    @update
    def _plot1D_stack (self, hist, option='', **kwargs):
        """ ... """

        # Manually add to legend entries
        if 'label' in kwargs:
            # Add in the correct (inverse) order for stacked histograms
            idx = 1 if (len(self._entries) > 0 and self._entries[0][1].strip().lower() == 'data') else 0
            self._entries.insert(idx, (hist, kwargs['label'], self._get_label_option(option, hist)))
            pass

        first = self._add_to_stack(hist)
        if first:
            self._plot1D(self._stack, option=option, **kwargs)
            pass

        return hist


    def _add_to_stack (self, hist, option='HIST'):
        """ ... """

        first = False
        if self._stack is None:
            self._stack = ROOT.THStack('stack', "")
            ROOT.SetOwnership(self._stack, False)
            first = True
            pass
        
        self._stack.Add(hist, option)
        return first



    # Private cosmetics methods
    # ----------------------------------------------------------------

    def _bare (self):
        """ ... """
        return self._pad


    def _get_all_entries (self):
        """ ... """
        return self._entries + [entry for child in self._children for entry in child._entries]


    @update
    def _update (self, only_this=True):
        """ ... 
        @TODO: - This is some reaaaally shitty naming convention
        """

        # Check(s)
        if len(self._primitives) == 0 or not hasattr(self._pad, 'SetLogy'): return
        
        # Set y-axis log./lin. scale
        self._pad.SetLogy(self._log)
        
        # Set axis limits with padding
        axisrange = (None,None)
        if self._ylim:
            axisrange = self._ylim
        else:
            ymin, ymax = inf, -inf
            
            try:
                ymin          = min([v for v in map(get_minimum,          self._primitives) if v is not None])
            except ValueError: # only stacked histogram
                ymin = 0.
                pass
            ymin_positive = 2. # min([v for v in map(get_minimum_positive, self._primitives[idx_pad]) if v is not None]) # @TODO: Improve
            for hist in self._primitives:
                ymax = max(get_maximum(hist), ymax)
                pass

            if self._log:
                axisrange = (ymin_positive, np.exp((np.log(ymax) - np.log(ymin_positive)) / (1. - self._padding) + np.log(ymin_positive)))
            else:
                axisrange = (0, ymax / (1. - self._padding) )
                pass

            # Set overlay axis limits
            if is_overlay(self):
                #self.lim(ymin, ymax)
                self.lim(0, ymax, force=False) # @TODO: Fix. Getting ymin == ymax
                pass
            pass

        # Check if anything has been drawn
        if self._get_first_primitive() and self._yaxis():
            self._get_first_primitive().SetMinimum(axisrange[0]) # For THStack. @TODO: Improve?
            self._get_first_primitive().SetMaximum(axisrange[1])

            # Style
            # @TODO: Move into a 'style' method
            if is_canvas(self._base): # if 'pad' on 'canvas'
                self._yaxis().SetTitleOffset(ROOT.gStyle.GetTitleOffset('y') * self._base._size[1]       / float(self._base._size[0]))
                pass
            self._yaxis().SetRangeUser(*axisrange)
            
            self._xaxis().SetTickLength(ROOT.gStyle.GetTickLength('x') * self._scale[1])
            self._yaxis().SetTickLength(ROOT.gStyle.GetTickLength('y') * self._scale[0])
            pass

        # Perform overlay pad-specific update
        if is_overlay(self):
            self._update_overlay()
            pass

        return


    def _style (self, h, **kwargs): # @TODO: Should these be utility functions?
        """ ..."""

        # Check(s)
        if type(h) == ROOT.THStack: return

        # Dispatch style methods
        dispatch = {
            'fillstyle': h.SetFillStyle,
            'fillcolor': h.SetFillColor,
            
            'linestyle': h.SetLineStyle,
            'linecolor': h.SetLineColor,
            'linewidth': h.SetLineWidth,
            
            'markerstyle': h.SetMarkerStyle,
            'markercolor': h.SetMarkerColor,
            'markersize':  h.SetMarkerSize,
        }

        for var, setter in dispatch.items():
            if var in kwargs:
                setter(kwargs[var])
                pass
            pass
        
        return


    def _reset_style (self, h, option): # @TODO: Should these be utility functions?
        """ ... """

        # Check(s)
        if type(h) == ROOT.THStack: return

        option = option.strip().split()[0].upper()
        if 'P' not in option:
            h.SetMarkerSize (0)
            h.SetMarkerStyle(0)
            h.SetMarkerColor(0)
            pass

        # ...
        return


    def _get_plot_option (self, plottype):
        """ ... """

        option = ''
        if   plottype == PlotType.plot:  option = 'PE0'
        elif plottype == PlotType.hist:  option = 'HIST'
        elif plottype == PlotType.stack: option = 'HIST'
        elif plottype == PlotType.graph: option = 'PL' # APL
        else:
            warning("Plot type '{}' not recognised".format(plottype.name))
            pass

        return option


    def _get_label_option (self, plot_option, hist):
        """ ... """

        label_option = ''

        plot_option = plot_option.split()[0].upper() # Discard possible 'SAME'

        if 'L' in plot_option:
            label_option += 'L'
        elif 'HIST' in plot_option:
            if hist.GetFillColor() == 0:
                label_option += 'L'
            else:
                label_option += 'F'
                pass
            pass

        if 'P' in plot_option:
            label_option += 'P'
            pass

        if 'E2' in plot_option or 'E3' in plot_option:
            label_option += 'F'
        elif 'E' in plot_option:
            label_option += 'EL'
            pass

        return label_option

    pass
    
