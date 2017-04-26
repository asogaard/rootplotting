# -*- coding: utf-8 -*-

""" Class(es) for easy ROOT plotting. 

@file:   ap.py
@date:   25 April 2017
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

# Enum(s)
def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

PlotType = Enum('plot', 'hist', 'hist2d', 'stack', 'graph')

"""
@TODO: - Make 'pad' class, such that 'overlay' in inherits from 'pad' and 'canvas' is a wrapper than can hold one or more pads.
       - 'pad' should implement the core plotting functionality
"""


# Overlay class
# --------------------------------------------------------------------

class overlay (object):
    """ docstring for overlay """

    def __init__(self, canvas, idx_pad=0, color=ROOT.kRed):
        super(overlay, self).__init__()

        # Check(s)
        # ...

        # Get refernce to base pad
        canvas._update()
        other = canvas._pads[idx_pad]
        
        # Member variables
        self._pad     = None
        self._axis    = None
        self._padding = canvas._padding
        self._xmin = 0
        self._xmax = 0
        self._base = other
        self._base_yaxis = canvas._yaxis(idx_pad)
        self._log   = False #canvas._log
        self._color = color

        # Resize canvas and pad(S)
        canvas._canvas.SetCanvasSize(int(canvas._canvas.GetWw() * 0.80 / 0.75), canvas._canvas.GetWh())
        for pad in canvas._pads:
            pad.SetRightMargin(0.10)
            pass

        other.SetTicks(1,0)
        other.Update()
        other.cd()

        # Store coordinates
        self._xmin = self._base.GetUxmin()
        self._xmax = self._base.GetUxmax()
        
        # Create overlay pad
        self._pad = ROOT.TPad(self._base.GetName() + '_overlay', "", 0, 0, 1, 1)
        
        # Set proper ranges
        ymin, ymax = 0, 1 # @TODO: Improve
        if self._log:
            ymax = np.exp((np.log(ymax) - np.log(ymin)) / (1. - self._padding) + np.log(ymin))
        else:
            ymax = ymax / (1. - self._padding)
            pass
        dy   = (ymax       - ymin)       / (1. - self._base.GetTopMargin()  - self._base.GetBottomMargin())
        dx   = (self._xmax - self._xmin) / (1. - self._base.GetLeftMargin() - self._base.GetRightMargin())
      
        self._pad.Range(self._xmin - self._base.GetLeftMargin()   * dx,
                        ymin       - self._base.GetBottomMargin() * dy,
                        self._xmax + self._base.GetRightMargin()  * dx,
                        ymax       + self._base.GetTopMargin()    * dy)

        # Axis
        self._axis = ROOT.TGaxis(self._xmax, ymin,
                                 self._xmax, ymax, 
                                 ymin, ymax, 510, "+L")

        # Style
        self._style()

        # Draw overlay pad and axis
        self._pad.Draw()
        self._pad.cd()
        self._axis.Draw()
        return


    def _style (self):
        """ ... """

        # Pad
        if self._pad:
            self._pad.SetFillStyle(4000)
            self._pad.SetFrameFillStyle(4000)
            self._pad.SetFrameFillColor(0)
            pass

        # Axis
        if self._axis:
            self._axis.SetLabelFont(ROOT.gStyle.GetTextFont())
            self._axis.SetLabelSize(ROOT.gStyle.GetTextSize())
            self._axis.SetTitleFont(ROOT.gStyle.GetTextFont())
            self._axis.SetTitleSize(ROOT.gStyle.GetTextSize())
            self._axis.SetLineColor (self._color)
            self._axis.SetLabelColor(self._color)
            self._axis.SetTitleColor(self._color)
            self._axis.SetLabelOffset(ROOT.gStyle.GetLabelOffset('y'))
            pass

        return


# Canvas class
# --------------------------------------------------------------------

class canvas (object):
    """ docstring for canvas """

    def __init__(self, num_pads=1, size=None, fraction=0.3, batch=False):
        super(canvas, self).__init__()

        ROOT.gROOT.SetBatch(batch)
        
        # Check(s)
        assert type(num_pads) == int, "Number of pads must be an integer"
        assert num_pads < 3, "Requested number of pads {} is too large".format(num_pads)
        assert num_pads > 0, "Requested number of pads {} is too small".format(num_pads)

        # Member variables
        self._num_pads = num_pads
        self._fraction = fraction if num_pads == 2 else 0.
        self._size = size or ((600,600) if num_pads == 1 else (600,int(521.79/float(1-fraction))))
        self._canvas = ROOT.TCanvas('c_{}'.format(id(self)), "", self._size[0], self._size[1])
        self._primitives = [list() for _ in range(self._num_pads)]
        self._entries = list()
        self._padding = 0.4
        self._log = False
        self._ylims = [None for _ in range(self._num_pads)]
        self._stack = None
        
        # Create pads
        self._pads = list()
        if   self._num_pads == 1:
            self._pads.append(ROOT.TPad(self._canvas.GetName() + '_pad0', "", 0, 0, 1, 1))
        elif self._num_pads == 2:
            self._pads.append(ROOT.TPad(self._canvas.GetName() + '_pad0', "", 0, fraction, 1, 1))
            self._pads.append(ROOT.TPad(self._canvas.GetName() + '_pad1', "", 0, 0, 1, fraction))
            pass

        # Draw pads
        for pad in self._pads: 
            self._canvas.cd()
            pad.Draw()
            self._canvas.Update()
            pass

        return


    def lines (self, lines=[], qualifier='', ATLAS=True, idx_pad=0):
        """ ... """ 

        # Check(s)
        # ...

        # Get pad on which to draw
        pad = self._pads[idx_pad]
        pad.cd()

        # Create text instance
        t = ROOT.TLatex()
        
        # Compute drawing coordinates
        h = pad.GetWh() * (1. - self._fraction)
        w = pad.GetWw()

        offset = 0.05
        ystep = t.GetTextSize() / float(h) * 1.30
        scale = 1.#(w/float(h) if w > h else h/float(w))

        x =       pad.GetLeftMargin() + offset * scale
        y = 1.0 - pad.GetTopMargin()  - offset - t.GetTextSize() / float(h) * 1.0

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

        # Update pad
        pad.Update()

        return


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
        N = len(self._entries)
        if N == 0:
            return
        
        # Get pad on which to draw legend
        pad = self._pads[0]
        pad.cd()

        # Compute drawing coordinates
        h = pad.GetWh() * (1. - self._fraction)
        w = pad.GetWw()

        fontsize = gStyle.GetLegendTextSize()

        offset = 0.05
        height = (N + (1 if header else 0) + (len(categories) if categories else 0) + (0 if self._stack else 0)) * fontsize / float(h) * 1.30

        # Setting x coordinates.
        if not (xmin or xmax):
            if   horisontal.upper() == 'R':
                xmax = 1. - pad.GetRightMargin() - offset
            elif horisontal.upper() == 'L':
                xmin = pad.GetLeftMargin() + offset
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
                ymax = 1.0 - pad.GetTopMargin() - offset - fontsize / float(h) * 1.8
            elif vertical.upper() == 'B':
                ymin = pad.GetBottomMargin() + offset
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
        legend = ROOT.TLegend(xmin, ymin, xmax, ymax)

        if header:
            legend.AddEntry(None, header, '')
            pass

        for (h,n,t) in self._entries:
            if type(h) == ROOT.THStack: continue
            legend.AddEntry(h, n, t)
            pass

        # @TODO: Improve
        if categories:
            for icat, (name, hist, opt) in enumerate(categories):
                legend.AddEntry(hist, name, opt)
                pass
            pass

        legend.Draw()

        # Make global (i.e. don't delete when going out of scope). @TODO: Necessary?
        ROOT.SetOwnership(legend, 0) 

        # Update pad
        pad.Update()

        return legend


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


    def _plot1D_numpy (self, data, bins, weights=None, idx_pad=0, option='', **kwargs):
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
        return self._plot1D(h, idx_pad, option, **kwargs)


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


    def _plot1D (self, hist, idx_pad=0, option='', display=True, scale=None, **kwargs):
        """ ... """

        # Check(s)
        assert idx_pad < len(self._pads), "Requested pad number {} is too large".format(idx_pad)
        assert idx_pad >= 0,              "Requested pad number {} is too small".format(idx_pad)

        # Scale
        if scale and type(hist) != ROOT.THStack:
            hist.Scale(scale)
            pass

        # Style
        self._reset_style(hist, option)
        self._style(hist, **kwargs)
        
        # Append draw option (opt.)
        if len(self._primitives[idx_pad]) > 0:
            option += " SAME"
            pass

        # Only plot if requested
        if not display: 
            return hist

        # Draw histograms
        self._pads[idx_pad].cd()
        if type(hist) == ROOT.THStack:
            hist.Draw(option)
            self._pads[idx_pad].Modified()
            self._pads[idx_pad].Update()
        else:
            hist.DrawCopy(option)
            pass
        self._pads[idx_pad].Update()

        # Store reference to primitive
        self._primitives[idx_pad].append(hist)

        if type(hist) != ROOT.THStack:

            # Check whether several filled histograms have been added
            if hist.GetFillColor() != 0 and len(filter(lambda h: type(h).__name__.startswith('TH1') and h.GetFillColor() != 0, self._primitives[0])) > 1:
                warning("Several filled, non-stacked histograms have been added. This may be misleading.")
                pass

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


    def _ratio_plot1D (self, hists, idx_pad=0, option='', **kwargs):
        """ ... """

        h = hists[0].Clone(hists[0].GetName() + '_ratio')
        for bin in range(1, h.GetXaxis().GetNbins() + 1):
            denom = hists[1].GetBinContent(bin)
            h.SetBinContent(bin, h.GetBinContent(bin) / denom if denom > 0 else 1)
            h.SetBinError  (bin, h.GetBinError  (bin) / denom if denom > 0 else 9999.)
            pass

        # Plot histogram
        return self._plot1D(h, 1, option, **kwargs)


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

        for pad in self._pads + [self._canvas]:
            pad.Modified()
            pad.Update()
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


    def ylim (self, ylim, idx_pad=0):
        """ ... """

        # Check(s)
        if type(ylim) not in [list, tuple]:
            warning("Axis limits must be provided as a tuple or lost. Recieved:")
            print type(ylim)
            return

        assert idx_pad < self._num_pads, "Pad index requested ({}) is too large.".format(idx_pad)
        assert idx_pad >= 0,             "Pad index requested ({}) is too small.".format(idx_pad)
        assert len(ylim) == 2,           "Y-axis limits have size {}, which is different from two as required.".format(len(ylim))

        # Store axis limits
        self._ylims[idx_pad] = ylim
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


    def xlabel (self, title, idx_pad=-1):
        """ ... """

        try:
            self._xaxis(idx_pad).SetTitle(title)
        except AttributeError:
            # No axis was found
            pass
        return


    def ylabel (self, title, idx_pad=0):
        """ ... """

        try:
            self._yaxis(idx_pad).SetTitle(title)        
        except AttributeError:
            # No axis was found
            pass
        return


    def ylines (self, ys, idx_pad=0):
        """ ... """

        for y in ys: 
            self.yline(y, idx_pad)
            pass
        return


    def yline (self, y, idx_pad=0):
        """ ... """

        pad = self._pads[idx_pad]

        pad.cd()
        line = ROOT.TLine()
        line.SetLineStyle(2)
        line.SetLineColor(ROOT.kGray + 3)
        xaxis = self._xaxis(idx_pad)
        xmin, xmax = xaxis.GetXmin(), xaxis.GetXmax()
        line.DrawLine(xmin, y, xmax, y)
        pad.Modified()
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


    def _update (self):
        """ ... """

        # Main pad
        idx_pad = 0

        # Update y-axis padding
        pad = self._pads[idx_pad]
        
        # Set y-axis log./lin. scale
        pad.SetLogy(self._log)

        # Set axis limits with padding
        axisrange = (None,None)
        if self._ylims[idx_pad] is not None:
            axisrange = self._ylims[idx_pad]
        else:
            ymin, ymax = inf, -inf
            
            ymin          = min([v for v in map(get_minimum,          self._primitives[idx_pad]) if v is not None])
            ymin_positive = 2. # min([v for v in map(get_minimum_positive, self._primitives[idx_pad]) if v is not None]) # @TODO: Improve
            for hist in self._primitives[idx_pad]:
                ymax = max(get_maximum(hist), ymax)
                pass

            if self._log:
                axisrange = (ymin_positive, np.exp((np.log(ymax) - np.log(ymin_positive)) / (1. - self._padding) + np.log(ymin_positive)))
            else:
                axisrange = (0, ymax / (1. - self._padding) )
                pass
            pass

        self._yaxis(pad).SetTitleOffset(ROOT.gStyle.GetTitleOffset('y') * self._size[1] / float(self._size[0]))
        self._yaxis(pad).SetRangeUser(*axisrange)
        self._get_first_primitive(pad).SetMinimum(axisrange[0])
        self._get_first_primitive(pad).SetMaximum(axisrange[1])

        # Update current pad
        pad.Modified()
        pad.Update()
            
        # Ratio pad
        if self._num_pads == 2:
            
            self._xaxis(pad).SetLabelOffset(9999.)
            self._xaxis(pad).SetTitleOffset(9999.)
            pad.SetBottomMargin(0.030)

            idx_pad = 1
            pad = self._pads[idx_pad]
            pad.cd()

            pad.SetBottomMargin(0.30)
            pad.SetTopMargin   (0.040)

            self._yaxis(pad).SetTitleOffset(ROOT.gStyle.GetTitleOffset('y') * self._size[1] / float(self._size[0]))
            self._yaxis(pad).SetNdivisions(505)
            self._xaxis(pad).SetTickLength(ROOT.gStyle.GetTickLength('x') * (1. - self._fraction) / self._fraction)
            self._xaxis(pad).SetTitleOffset(4)
            if self._ylims[idx_pad] is not None:
                axisrange = self._ylims[idx_pad]
                self._yaxis(pad).SetRangeUser(*axisrange)
                self._get_first_primitive(pad).SetMinimum(axisrange[0])
                self._get_first_primitive(pad).SetMaximum(axisrange[1])
                pass
            
            # Update current pad
            pad.Modified()
            pad.Update()
            pass

        # Update canvas
        self._canvas.Update()

        return



    # Private methods
    # ----------------------------------------------------------------

    def _xaxis (self, pad):
        """ ... """

        # Return axis
        primitive = self._get_first_primitive(pad)

        if primitive is None:
            warning("Cannot access x-axis")
            return None

        return primitive.GetXaxis()


    def _yaxis (self, pad):
        """ ... """

        # Return axis
        primitive = self._get_first_primitive(pad)

        if primitive is None:
            warning("Cannot access y-axis")
            return None

        return primitive.GetYaxis()


    def _get_first_primitive (self, pad):
        """ ... """

        # Get pad
        if type(pad) == int: 
            pad = self._pads[pad]
            pass

        # Check(s)
        if len(pad.GetListOfPrimitives()) < 2:
            warning("Nothing was drawn; cannot access first primitive.")
            return None

        # Return first primitive
        return pad.GetListOfPrimitives()[1]


    def _style (self, h, **kwargs):
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


    def _reset_style (self, h, option):
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
        elif plottype == PlotType.graph: option = 'APL'
        else:
            warning("Plot type '{}' not recognised".format(plottype.name))
            pass

        return option


    def _get_label_option (self, plot_option, hist):
        """ ... """

        label_option = ''

        plot_option = plot_option.split()[0].upper() # Discard possible 'SAME'

        if 'HIST' in plot_option:
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
