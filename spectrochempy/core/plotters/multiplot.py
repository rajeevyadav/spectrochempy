# -*- coding: utf-8 -*-
#
# =============================================================================
# Copyright (©) 2015-2017 LCS
# Laboratoire Catalyse et Spectrochimie, Caen, France.
#
# This software is a computer program whose purpose is to [describe
# functionalities and technical features of your software].
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software. You can use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading, using, modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean that it is complicated to manipulate, and that also
# therefore means that it is reserved for developers and experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and, more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
# =============================================================================


"""
Module containing multiplot function(s)

"""
import  numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.tight_layout import (get_renderer, get_tight_layout_figure,
                                     get_subplotspec_list)
from spectrochempy.core.dataset.ndplot import _set_figure_style
from spectrochempy.utils import is_sequence
from spectrochempy.application import app
plotoptions = app.plotoptions
log = app.log
options = app


__all__ = ['multiplot', 'multiplot_map', 'multiplot_stack',
           'multiplot_image', 'multiplot_lines', 'multiplot_scatter',
           'multiplot_with_transposed', 'plot_with_transposed']

_methods = __all__[:]

# .............................................................................
def multiplot_scatter(sources, **kwargs):
    """
    Plot a multiplot with 1D scatter type plots.

    Alias of multiplot (with `method` argument set to ``scatter``.

    """
    kwargs['method'] = 'scatter'
    return multiplot(sources, **kwargs)

# .............................................................................
def multiplot_lines(sources, **kwargs):
    """
    Plot a multiplot with 1D linetype plots.

    Alias of multiplot (with `method` argument set to ``lines``.

    """
    kwargs['method'] = 'lines'
    return multiplot(sources, **kwargs)

# .............................................................................
def multiplot_stack(sources, **kwargs):
    """
    Plot a multiplot with 2D stack type plots.

    Alias of multiplot (with `method` argument set to ``stack``.

    """
    kwargs['method'] = 'stack'
    return multiplot(sources, **kwargs)

# .............................................................................
def multiplot_map(sources, **kwargs):
    """
    Plot a multiplot with 2D map type plots.

    Alias of multiplot (with `method` argument set to ``map``.

    """
    kwargs['method'] = 'map'
    return multiplot(sources, **kwargs)


# .............................................................................
def multiplot_image(sources, **kwargs):
    """
    Plot a multiplot with 2D image type plots.

    Alias of multiplot (with `method` argument set to ``image``.

    """
    kwargs['method'] = 'image'
    return multiplot(sources, **kwargs)


# with transpose plot  -----------------------------------------------------------------

def plot_with_transposed(source, **kwargs):
    """
    Plot a 2D dataset as a stacked plot with its transposition in a second
    axe.

    Alias of plot_2D (with `method` argument set to ``with_transposed``).

    """
    kwargs['method'] = 'with_transposed'
    axes = multiplot(source, **kwargs)
    return axes

multiplot_with_transposed = plot_with_transposed

# .............................................................................
def multiplot( sources=[], labels=[], nrow=1, ncol=1,
               method='stack',
               sharex=False, sharey=False, sharez=False,
               colorbar=False,
               suptitle=None, suptitle_color=None,
               **kwargs):

    """
    Generate a figure with multiple axes arranged in array (n rows, n columns)

    Parameters
    ----------

    sources : nddataset or list of nddataset

    labels : list of str.

        The labels that will be used as title of each axes.

    method : str, default to `map` for 2D and `lines` for 1D data

        Type of plot to draw in all axes (`lines` , `scatter` , `stack` , `map`
        ,`image` or `with_transposed`).

    nrows, ncols : int, default: 1

        Number of rows/cols of the subplot grid. ncol*nrow must be equal
        to the number of sources to plot

    sharex, sharey : bool or {'none', 'all', 'row', 'col'}, default: False

        Controls sharing of properties among x (`sharex`) or y (`sharey`)
        axes::

        - True or 'all': x- or y-axis will be shared among all subplots.
        - False or 'none': each subplot x- or y-axis will be independent.
        - 'row': each subplot row will share an x- or y-axis.
        - 'col': each subplot column will share an x- or y-axis.

        When subplots have a shared x-axis along a column, only the x tick
        labels of the bottom subplot are visible.  Similarly, when
        subplots have a shared y-axis along a row, only the y tick labels
        of the first column subplot are visible.

    sharez: bool or {'none', 'all', 'row', 'col'}, default: False
        equivalent to sharey for 1D plot.
        for 2D plot, z is the intensity axis (i.e., contour levels for maps or
        the vertical axis for stack plot), y is the third axis.

    figsize : 2-tuple of floats

        ``(width, height)`` tuple in inches

    dpi : float

        Dots per inch

    facecolor : color

        The figure patch facecolor; defaults to rc ``figure.facecolor``

    edgecolor : color

        The figure patch edge color; defaults to rc ``figure.edgecolor``

    linewidth : float

        The figure patch edge linewidth; the default linewidth of the frame

    frameon : bool

        If ``False`` , suppress drawing the figure frame

    left : float in the [0-1] interval

        The left side of the subplots of the figure

    right : float in the [0-1] interval

        The right side of the subplots of the figure

    bottom : float in the [0-1] interval

        The bottom of the subplots of the figure

    top : float in the [0-1] interval

        The top of the subplots of the figure

    wspace : float in the [0-1] interval

        The amount of width reserved for blank space between subplots,
        expressed as a fraction of the average axis width

    hspace : float in the [0-1] interval

        The amount of height reserved for white space between subplots,
        expressed as a fraction of the average axis height

    suptitle : str

        title of the figure to display on top

    suptitle_color : color

    """

    # some basic checking
    # -------------------

    show_transposed = False
    if method in 'with_transposed':
        show_transposed = True
        method = 'stack'
        nrow = 2
        ncol = 1
        sources = [sources, sources]   # we need to sources
        sharez = True

    single=False
    if not is_sequence(sources):
        single=True
        sources = list([sources])  # make a list

    if len(sources) < nrow * ncol and not show_transposed:
        # not enough sources given in this list.
        raise ValueError('Not enough sources given in this list')

    # if labels and len(labels) != len(sources):
    #     # not enough labels given in this list.
    #     raise ValueError('Not enough labels given in this list')

    if nrow == ncol and nrow == 1 and not show_transposed and single:
        # obviously a single plot, return it
        return sources[0].plot(**kwargs)
    elif nrow*ncol <len(sources):
        nrow = ncol = len(sources)//2
        if nrow*ncol<len(sources):
            ncol+=1

    ndims = set([source.ndim for source in sources])
    if len(ndims) > 1:
        raise NotImplementedError('mixed source shape.')
    ndim = list(ndims)[0]

    # create the subplots and plot the ndarrays
    # ------------------------------------------

    # first make style
    _set_figure_style(**kwargs)

    mpl.rcParams['figure.autolayout'] = False

    figsize = kwargs.pop('figsize', None)
    dpi = kwargs.pop('dpi', 150)

    fig = kwargs.pop('fig', plt.figure(figsize=figsize, dpi=dpi))

    fig.rcParams = plt.rcParams.copy()  # save params used for this figure

    if suptitle is not None:
        fig.suptitle(suptitle, color=suptitle_color)

    # axes is dictionary with keys such as 'axe12', where  the fist number
    # is the row and the second the column
    axes = {}

    # limits
    xlims = []
    ylims = []
    zlims = []

    if sharex not in [None, True, False, 'all','col']:
        raise ValueError("invalid option for sharex. Should be"
                     " among (None, False, True, 'all' or 'col')")

    if sharex: sharex='all'

    if ndim == 1:
        sharez = False

    textsharey = "sharey"
    textsharez = "sharez"
    if method in ['stack']:
        sharez, sharey = sharey, sharez  # we echange them
        zlims, ylims = ylims, zlims
        # for our internal needs as only sharex and sharey are recognized by
        # matplotlib subplots
        textsharey = "sharez"
        textsharez = "sharey"

    if sharey not in [None, False, True, 'all','col']:
        raise ValueError("invalid option for {}. Should be"
                         " among (None, False, True, 'all' or 'row')".format(
                textsharey))

    if sharez not in [None, False, True, 'all', 'col', 'row']:
        raise ValueError("invalid option for {}. Should be"
                         " among (None, False, True, "
                         "'all', 'row' or 'col')".format(textsharez))

    if sharey: sharey='all'
    if sharez: sharez='all'

    for irow in range(nrow):
        for icol in range(ncol):

            idx = irow*ncol + icol
            source = sources[idx]
            try:
                label = labels[idx]
            except:
                label = ''

            _sharex = None
            _sharey = None
            _sharez = None
            # on the type of the plot and
            if ((irow == icol and irow == 0) or # axe11
               (sharex == 'col' and irow == 0) or # axe1*
               (sharey == 'row' and icol == 0)) :  # axe*1

                ax = fig.add_subplot(nrow, ncol, irow * ncol + icol + 1)

            else:
                if sharex == 'all':
                    _sharex = axes['axe11']
                elif sharex == 'col':
                    _sharex = axes['axe1{}'.format(icol+1)]

                if sharey == 'all':
                    _sharey = axes['axe11']
                elif sharey == 'row':
                    _sharey = axes['axe{}1'.format(irow + 1)]

                # in the last dimension
                if sharez == 'all':
                    _sharez = axes['axe11']
                elif sharez == 'row':
                    _sharez = axes['axe{}1'.format(irow + 1)]
                elif sharez == 'col':
                    _sharez = axes['axe1{}'.format(icol + 1)]


                ax = fig.add_subplot(nrow, ncol, idx+1,
                                     sharex=_sharex, sharey=_sharey)


            ax._sharez = _sharez  # we add a new share info to the ax.
            # wich will be useful for the interactive masks

            ax.name = 'axe{}{}'.format(irow + 1, icol + 1)
            axes[ax.name] = ax
            if icol > 0 and sharey:
                # hide the redondant ticklabels on left side of interior figures
                plt.setp(axes[ax.name].get_yticklabels(), visible=False)
                axes[ax.name].yaxis.set_tick_params(which='both',
                                         labelleft=False, labelright=False)
                axes[ax.name].yaxis.offsetText.set_visible(False)
            if irow < nrow - 1 and sharex:
                # hide the bottom ticklabels of interior rows
                plt.setp(axes[ax.name].get_xticklabels(), visible=False)
                axes[ax.name].xaxis.set_tick_params(which='both',
                                                    labelbottom=False,
                                                    labeltop=False)
                axes[ax.name].xaxis.offsetText.set_visible(False)

            if show_transposed and irow==1:
                transposed = True
            else:
                transposed = False

            source.plot(method=method,
                        ax=ax, hold=True, autolayout=False,
                        colorbar=colorbar,
                        data_transposed = transposed,
                        **kwargs)

            ax.set_title(label, fontsize=12)
            if sharex and irow<nrow-1:
                ax.xaxis.label.set_visible(False)
            if sharey and icol>0:
                ax.yaxis.label.set_visible(False)

            xlims.append(ax.get_xlim())
            ylims.append(ax.get_ylim())
            xrev = (ax.get_xlim()[1] - ax.get_xlim()[0]) < 0
            yrev = (ax.get_ylim()[1] - ax.get_ylim()[0]) < 0

    # TODO: add a common color bar (set vmin and vmax using zlims)

    amp = np.ptp(np.array(ylims))
    ylim = [np.min(np.array(ylims)-amp*0.01), np.max(np.array(ylims))+amp*0.01]
    for ax in axes.values():
        ax.set_ylim(ylim)
    if yrev:
        ylim = ylim[::-1]
    amp = np.ptp(np.array(xlims))

    if not show_transposed:
        xlim = [np.min(np.array(xlims)), np.max(np.array(xlims))]
        if xrev:
            xlim = xlim[::-1]
        for ax in axes.values():
            ax.set_xlim(xlim)

    def do_tight_layout(fig, axes, suptitle, **kwargs):

        # tight_layout
        renderer = get_renderer(fig)
        axeslist = list(axes.values())
        subplots_list = list(get_subplotspec_list(axeslist))
        kw = get_tight_layout_figure(fig, axeslist, subplots_list, renderer,
                                     pad=1.08, h_pad=0, w_pad=0, rect=None)

        left = kwargs.get('left',kw['left'])
        bottom = kwargs.get('bottom',kw['bottom'])
        right = kwargs.get('right',kw['right'])
        top = kw['top']
        if suptitle:
            top = top*.95
        top = kwargs.get('top',top)
        ws = kwargs.get('wspace',kw.get('wspace',0)*1.1)
        hs = kwargs.get('hspace',kw.get('hspace',0)*1.1)

        plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top,
                            wspace=ws, hspace=hs)

    do_tight_layout(fig, axes, suptitle, **kwargs)

    # make an event that will trigger subplot adjust each time the mouse leave
    # or enter the axes or figure
    def _onenter(event):
        do_tight_layout(fig, axes, suptitle, **kwargs)
        fig.canvas.draw()

    fig.canvas.mpl_connect('axes_enter_event', _onenter)
    fig.canvas.mpl_connect('axes_leave_event', _onenter)
    fig.canvas.mpl_connect('figure_enter_event', _onenter)
    fig.canvas.mpl_connect('figure_leave_event', _onenter)

    return axes

if __name__ == '__main__':

    from spectrochempy.api import *

    source = NDDataset.read_omnic(
         os.path.join(scpdata, 'irdata', 'NH4Y-activation.SPG'))[0:20]

    sources=[source, source*1.1, source*1.2, source*1.3]
    labels = ['sample {}'.format(label) for label in
              ["1", "2", "3", "4"]]
    multiplot(sources=sources, method='stack', labels=labels, nrow=2, ncol=2,
              figsize=(9, 5), style='sans',
              sharex=True, sharey=True, sharez=True)

    multiplot(sources=sources, method='image', labels=labels, nrow=2, ncol=2,
                    figsize=(9, 5), sharex=True, sharey=True, sharez=True)

    sources = [source * 1.2, source * 1.3,
               source, source * 1.1, source * 1.2, source * 1.3]
    labels = ['sample {}'.format(label) for label in
                                 ["1", "2", "3", "4", "5", "6"]]
    multiplot_map(sources=sources, labels=labels, nrow=2, ncol=3,
              figsize=(9, 5), sharex=False, sharey=False, sharez=True)

    multiplot_map(sources=sources, labels=labels, nrow=2, ncol=3,
              figsize=(9, 5), sharex=True, sharey=True, sharez=True)

    sources = [source * 1.2, source * 1.3, source, ]
    labels = ['sample {}'.format(label) for label in
              ["1", "2", "3"]]
    multiplot_stack(sources=sources, labels=labels, nrow=1, ncol=3,
                    figsize=(9, 5), sharex=True,
                    sharey=True, sharez=True)

    multiplot_stack(sources=sources, labels=labels, nrow=3, ncol=1,
                    figsize=(9, 5), sharex=True,
                    sharey=True, sharez=True)

    multiplot(method='lines', sources=[source[0], source[10]*1.1,
                                     source[19]*1.2, source[15]*1.3],
              nrow=2, ncol=2, figsize=(9, 5),
              labels=labels, sharex=True)
    plt.show()