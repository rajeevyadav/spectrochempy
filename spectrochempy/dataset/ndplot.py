# -*- coding: utf-8 -*-
#
# =============================================================================
# Copyright (©) 2015-2018 LCS
# Laboratoire Catalyse et Spectrochimie, Caen, France.
# CeCILL-B FREE SOFTWARE LICENSE AGREEMENT
# See full LICENSE agreement in the root directory
# =============================================================================

"""
This module defines the class |NDPlot| in which generic plot
methods for a |NDDataset| are defined.

"""

__all__ = ['NDPlot',
           'plot',

           # styles and colors
           '_set_figure_style'
           ]


# Python and third parties imports
# ----------------------------------

import warnings

from cycler import cycler
import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from traitlets import Dict, HasTraits, Instance

# local import
# ------------
from ..utils import (is_sequence, SpectroChemPyDeprecationWarning,
                                 docstrings, NBlack, NBlue, NGreen, NRed,
                                 get_figure)
from ..application import app

project_preferences = app.project_preferences
log = app.log
do_not_block = app.do_not_block


from ..core.plotters.plot1d import plot_1D
from ..core.plotters.plot3d import plot_3D
from ..core.plotters.plot2d import plot_2D

from ..utils import deprecated

# =============================================================================
# Class NDPlot to handle plotting of datasets
# =============================================================================

class NDPlot(HasTraits):
    """
    Plotting interface for |NDDataset|

    This class is used as basic plotting interface of the |NDDataset|.

    """

    # The figure on which this dataset can be plotted
    _fig = Instance(plt.Figure, allow_none=True)

    # The axes on which this dataset and other elements such as projections 
    # and colorbar can be plotted
    _ndaxes = Dict(Instance(plt.Axes))

    # -------------------------------------------------------------------------
    # generic plotter and plot related methods or properties
    # -------------------------------------------------------------------------

    # .........................................................................
    @docstrings.get_sectionsf('plot')
    @docstrings.dedent
    def plot(self, **kwargs):
        """
        Generic plot function for
        a |NDDataset| which
        actually delegate the work to a plotter defined by the parameter ``method``.

        Parameters
        ----------
        method : str, optional
            The method of plot of the dataset, which will determine the
            plotter to use. For instance, for 2D data, it can be `map`,
            `stack` or `image` among other method.
        ax : |Axes| instance. Optional, default:current or new one
            The axe where to plot
        figsize : tuple, optional, default is mpl.rcParams['figure.figsize']
            The figure size
        fontsize : int, optional
            The font size in pixels, default is 10 (or read from preferences)
        hold : `bool`, optional, default = `False`.
            Should we plot on the ax previously used or create a new figure?
        style : str
        autolayout : `bool`, optional, default=True
            if True, layout will be set automatically
        output: str
            A string containing a path to a filename. The output format is deduced
            from the extension of the filename. If the filename has no extension,
            the value of the rc parameter savefig.format is used.
        dpi : [ None | scalar > 0]
            The resolution in dots per inch. If None it will default to the
            value savefig.dpi in the matplotlibrc file.

        """

        # color cycle
        # prop_cycle = options.prop_cycle
        # mpl.rcParams['axes.prop_cycle']= r" cycler('color', %s) " % prop_cycle

        # --------------------------------------------------------------------
        # select plotter depending on the dimension of the data
        # --------------------------------------------------------------------

        method = 'generic'

        # check the deprecated use of `kind`
        kind = kwargs.pop('kind', None)
        if kind is not None:
            method=kind
            warnings.warn('`kind`is deprecated, use `method` instead',
                          SpectroChemPyDeprecationWarning)

        method = kwargs.pop('method', method)
        log.debug('Call to plot_{}'.format(method))

        # Find or guess the adequate plotter
        # -----------------------------------

        _plotter = getattr(self, 'plot_{}'.format(method), None)
        if _plotter is None:
            # no plotter found
            log.error('The specified plotter for method '
                      '`{}` was not found!'.format(method))
            raise IOError

        # Execute the plotter
        # --------------------

        return _plotter(**kwargs)

    # -------------------------------------------------------------------------
    # plotter: plot_generic
    # -------------------------------------------------------------------------

    # .........................................................................
    def plot_generic(self, **kwargs):
        """
        The generic plotter. It try to guess an adequate basic plot for the data.
        Other method of plotters are defined explicitely in the `viewer` package.

        Parameters
        ----------

        ax : :class:`matplotlib.axe`

            the viewplot where to plot.

        kwargs : optional additional arguments

        Returns
        -------

        ax : return the handler to ax where the main plot was done

        """

        if self.ndim == 1:

            ax = plot_1D(self, **kwargs)

        elif self.ndim == 2:

            ax = plot_2D(self, **kwargs)

        elif self.ndim == 3:

            ax = plot_3D(self, **kwargs)

        else:
            log.error('Cannot guess an adequate plotter, nothing done!')
            return False

        return ax

    # -------------------------------------------------------------------------
    # setup figure properties
    # -------------------------------------------------------------------------

    # .........................................................................
    def _figure_setup(self, ndim=1, **kwargs):

        _set_figure_style(**kwargs)

        self._figsize = mpl.rcParams['figure.figsize'] = \
            kwargs.get('figsize', mpl.rcParams['figure.figsize'])

        mpl.rcParams[
            'figure.autolayout'] = kwargs.pop('autolayout', True)

        # Get current figure information
        # ------------------------------
        log.debug('update plot')

        # should we use the previous figure?
        #TODO: change this keword to newfig which willl be clearer!
        hold = kwargs.get('hold', False)

        # is ax in the keywords ?
        ax = kwargs.pop('ax', None)

        # is it a twin figure? In such case if ax and hold are also provided,
        # they will be ignored
        tax = kwargs.get('twinx', None)
        if tax is not None:
            if isinstance(tax, plt.Axes):
                hold = True
                ax = tax.twinx()
                ax.name = 'main'
                tax.name = 'twin' # the previous main is renamed!
                self.ndaxes['main'] = ax
                self.ndaxes['twin'] = tax
            else:
                raise ValueError(
                        '{} is not recognized as a valid Axe'.format(tax))


        # get the current figure (or the last used)
        self._fig = get_figure(hold)
        self._fig.rcParams = plt.rcParams.copy()

        if not hold:
            self._ndaxes = {}  # reset ndaxes
            self._divider = None

        if ax is not None:
            # ax given in the plot parameters,
            # in this case we will plot on this ax
            if isinstance(ax, plt.Axes):
                ax.name = 'main'
                self.ndaxes['main'] = ax
            else:
                raise ValueError(
                        '{} is not recognized as a valid Axe'.format(ax))

        elif self._fig.get_axes():
            # no ax parameters in keywords, so we need to get those existing
            # We assume that the existing axes have a name
            self.ndaxes = self._fig.get_axes()
        else:
            # or create a new subplot
            ax = self._fig.gca()
            ax.name = 'main'
            self.ndaxes['main'] = ax

        if ax is not None and kwargs.get('method') in ['scatter']:
            ax.set_prop_cycle(
                    cycler('color',
                           [NBlack, NBlue, NRed, NGreen] * 3) +
                    cycler('linestyle',
                           ['-', '--', ':', '-.'] * 3) +
                    cycler('marker',
                           ['o', 's', '^'] * 4))
        elif ax is not None and kwargs.get('method') in ['lines']:
            ax.set_prop_cycle(
                    cycler('color',
                           [NBlack, NBlue, NRed, NGreen]) +
                    cycler('linestyle',
                           ['-', '--', ':', '-.']))

        # Get the number of the present figure
        self._fignum = self._fig.number

        # for generic plot, we assume only a single axe
        # with possible projections
        # and an optional colobar.
        # other plot class may take care of other needs

        ax = self.ndaxes['main']

        if ndim == 2:
            # TODO: also the case of 3D

            method = kwargs.get('method', project_preferences.method_2D)

            # show projections (only useful for map or image)
            # ------------------------------------------------

            colorbar = kwargs.get('colorbar', True)

            proj = kwargs.get('proj', project_preferences.show_projections)
            # TODO: tell the axis by title.

            xproj = kwargs.get('xproj', project_preferences.show_projection_x)

            yproj = kwargs.get('yproj', project_preferences.show_projection_y)

            SHOWXPROJ = (proj or xproj) and method in ['map', 'image']
            SHOWYPROJ = (proj or yproj) and method in ['map', 'image']

            # Create the various axes
            # -------------------------
            # create new axes on the right and on the top of the current axes
            # The first argument of the new_vertical(new_horizontal) method is
            # the height (width) of the axes to be created in inches.
            #
            # This is necessary for projections and colorbar

            if (SHOWXPROJ or SHOWYPROJ or colorbar) \
                    and self._divider is None:
                self._divider = make_axes_locatable(ax)

            divider = self._divider

            if SHOWXPROJ:
                axex = divider.append_axes("top", 1.01, pad=0.01, sharex=ax,
                                           frameon=0, yticks=[])
                axex.tick_params(bottom='off', top='off')
                plt.setp(axex.get_xticklabels() + axex.get_yticklabels(),
                         visible=False)
                axex.name = 'xproj'
                self.ndaxes['xproj'] = axex

            if SHOWYPROJ:
                axey = divider.append_axes("right", 1.01, pad=0.01, sharey=ax,
                                           frameon=0, xticks=[])
                axey.tick_params(right='off', left='off')
                plt.setp(axey.get_xticklabels() + axey.get_yticklabels(),
                         visible=False)
                axey.name = 'yproj'
                self.ndaxes['yproj'] = axey

            if colorbar:
                axec = divider.append_axes("right", .15, pad=0.1, frameon=0,
                                           xticks=[], yticks=[])
                axec.tick_params(right='off', left='off')
                # plt.setp(axec.get_xticklabels(), visible=False)
                axec.name = 'colorbar'
                self.ndaxes['colorbar'] = axec

    # -------------------------------------------------------------------------
    # resume a figure plot
    # -------------------------------------------------------------------------

    # .........................................................................
    def _plot_resume(self, origin, **kwargs):

        log.debug('resume plot')

        # put back the axes in the original dataset
        # (we have worked on a copy in plot)
        if not kwargs.get('data_transposed', False):
            origin.ndaxes = self.ndaxes
            origin._ax_lines = self._ax_lines
            if hasattr(self, "_axcb"):
                origin._axcb = origin._axcb
        else:
            nda = {}
            for k, v in self.ndaxes.items():
                nda[k + 'T'] = v
            origin.ndaxes = nda
            origin._axT_lines = self._ax_lines
            if hasattr(self, "_axcb"):
                origin._axcbT = origin._axcb

        origin._fig = self._fig

        # Additional matplotlib commands on the current plot
        # ---------------------------------------------------------------------

        commands = kwargs.get('commands', [])
        if commands:
            for command in commands:
                com, val = command.split('(')
                val = val.split(')')[0].split(',')
                ags = []
                kws = {}
                for item in val:
                    if '=' in item:
                        k, v = item.split('=')
                        kws[k.strip()] = eval(v)
                    else:
                        ags.append(eval(item))
                getattr(self.ndaxes['main'], com)(*ags,
                                                  **kws)  # TODO:improve this

        # output command should be after all plot commands

        savename = kwargs.get('output', None)
        if savename is not None:
            # we save the figure with options found in kwargs
            # starting with `save`
            log.debug('save plot to {}'.format(savename))
            kw = {}
            for key, value in kwargs.items():
                if key.startswith('save'):
                    key = key[4:]
                    kw[key] = value
            self._fig.savefig(savename, **kw)

    # -------------------------------------------------------------------------
    # Special attributes
    # -------------------------------------------------------------------------

    # .........................................................................
    def __dir__(self):
        return ['fignum', 'ndaxes', 'divider']

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    # .........................................................................
    @property
    def fig(self):
        """
        Matplotlib figure associated to this dataset

        """
        return self._fig

    # .........................................................................
    @property
    def fignum(self):
        """
        Matplotlib figure associated to this dataset

        """
        return self._fignum

    # .........................................................................
    @property
    def ndaxes(self):
        """
        A dictionary containing all the axes of the current figures
        """
        return self._ndaxes

    # .........................................................................
    @ndaxes.setter
    def ndaxes(self, axes):
        # we assume that the axes have a name
        if isinstance(axes, list):
            # a list a axes have been passed
            for ax in axes:
                log.debug('add axe: {}'.format(ax.name))
                self._ndaxes[ax.name] = ax
        elif isinstance(axes, dict):
            self._ndaxes.update(axes)
        elif isinstance(axes, plt.Axes):
            # it's an axe! add it to our list
            self._ndaxes[axes.name] = axes

    # .........................................................................
    @property
    def ax(self):
        """
        the main matplotlib axe associated to this dataset

        """
        return self._ndaxes['main']

    # .........................................................................
    @property
    def axT(self):
        """
        the matplotlib axe associated to the transposed dataset

        """
        return self._ndaxes['mainT']

    # .........................................................................
    @property
    def axec(self):
        """
        Matplotlib colorbar axe associated to this dataset

        """
        return self._ndaxes['colorbar']

    # .........................................................................
    @property
    def axecT(self):
        """
        Matplotlib colorbar axe associated to the transposed dataset

        """
        return self._ndaxes['colorbarT']

    # .........................................................................
    @property
    def axex(self):
        """
        Matplotlib projection x axe associated to this dataset

        """
        return self._ndaxes['xproj']

    # .........................................................................
    @property
    def axey(self):
        """
        Matplotlib projection y axe associated to this dataset

        """
        return self._ndaxes['yproj']

    # .........................................................................
    @property
    def divider(self):
        """
        Matplotlib plot divider

        """
        return self._divider

# .............................................................................
def _set_figure_style(**kwargs):
    # set temporarily a new style if any

    log.debug('set style')

    style = kwargs.get('style', None)

    if style:
        if not is_sequence(style):
            style = [style]
        if isinstance(style, dict):
            style = [style]
        style = ['classic', project_preferences.style] + list(style)
        plt.style.use(style)
    else:
        style = ['classic', project_preferences.style]
        plt.style.use(style)
        plt.style.use(project_preferences.style)

        fontsize = mpl.rcParams['font.size'] = \
            kwargs.get('fontsize', mpl.rcParams['font.size'])
        mpl.rcParams['legend.fontsize'] = int(fontsize * .8)
        mpl.rcParams['xtick.labelsize'] = int(fontsize)
        mpl.rcParams['ytick.labelsize'] = int(fontsize)
        mpl.rcParams['axes.prop_cycle'] = (
            cycler('color', [NBlack, NBlue, NRed, NGreen]))

        return mpl.rcParams

@deprecated('use `available styles` from application instead')
# .............................................................................
def available_styles():
    """
    Styles availables in SpectroChemPy

    Todo
    -----
    Make this list extensible programmatically

    Returns
    -------
    l : a list of style

    """
    return app.available_styles()


# .............................................................................
plot = NDPlot.plot  # make plot accessible directly from the scp API

# =============================================================================
if __name__ == '__main__':
    pass


