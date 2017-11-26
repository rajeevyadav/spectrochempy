# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-
#
# =============================================================================
# Copyright (©) 2015-2018 LCS
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

"""This module provides Coord related classes

"""

import copy
import uuid
import warnings
from datetime import datetime

import numpy as np
from pandas import Index
from traitlets import (HasTraits, List, Bool, Unicode, default, Instance)

from spectrochempy.application import app
log = app.log

from spectrochempy.core.dataset.ndarray import (NDArray)
from spectrochempy.core.dataset.ndmath import NDMath
from spectrochempy.utils import set_operators
from spectrochempy.core.units import Quantity
# from ...utils import create_traitsdoc

from spectrochempy.utils import (is_number,
                                 numpyprintoptions,
                                 docstrings,
                                 SpectroChemPyWarning)
from spectrochempy.utils.traittypes import Range

__all__ = ['Coord',
           'CoordRange']
_classes = __all__[:]

# =============================================================================
# set numpy print options
# =============================================================================

numpyprintoptions()

# =============================================================================
# Coord
# =============================================================================

class Coord(NDMath, NDArray):
    """A class describing the coords of the data along a given axis.

    """

    _copy = Bool

    # -------------------------------------------------------------------------
    # initialization
    # -------------------------------------------------------------------------
    docstrings.delete_params('NDArray.parameters', 'data', 'masks',
                             'uncertainty')

    @docstrings.dedent
    def __init__(self, data=None, **kwargs):
        """
        Parameters
        -----------
        data : array of floats
            The actual data array contained in the Coord object.
            The given array (with a single dimension) can be a `list`, a `tuple`,
            a :class:`~numpy.ndarray`, a :class:`~numpy.ndarray`-like,
            a `NDArray` or any subclass of `NDArray`.
            If a subclass of NDArray is passed that contains
            already mask, labels, or units these elements will be
            used to accordingly set those of the created object.
            If possible, the provided data  will not be copied for `data` input,
            but will be passed by reference, so you should make a copy the
            :attr:`data` before passing it in if that's the desired behavior or
            set the `copy` argument to True.
        %(NDArray.parameters.no_masks|uncertainty)s

        Notes
        -----
        If only labels are provided during initialisation of a Coord object,
        a numerical axis is automatically created with the labels indices.

        Examples
        ---------
        >>> from spectrochempy.api import Coord # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        SpectroChemPy's API  ...

        >>> x = Coord([1,2,3], title='time on stream', units='hours')
        >>> print(x) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
                  title: Time on stream
               data: [       1        2        3] hr

        >>> print(x.data) # doctest: +NORMALIZE_WHITESPACE
        [       1        2        3]


        """
        super(Coord, self).__init__(data, **kwargs)

        # some checking
        if self.ndim >1:
            raise ValueError("Number of dimension for coordinate's array "
                              "should be 1!")

    # -------------------------------------------------------------------------
    # properties
    # -------------------------------------------------------------------------
    @default('_name')
    def _get_name_default(self):
        return "Coord_" + str(uuid.uuid1()).split('-')[0]  # a unique id

    @property
    def is_reversed(self):
        """`bool`, read-only property - Whether the axis is ascending or reversed.

        return a correct result only if the data are sorted

        """
        if "wavenumber" in self.title.lower() or "ppm" in self.title.lower():
            return True
        return False

        return bool(self.data[0] > self.data[-1])

    ########
    # hidden properties (for the documentation, only - we remove the docs)
    # some of the property of NDArray has to be hidden because they are not
    # usefull for this Coord class

    @property
    def is_complex(self):
        return [False, False]  # always real (the first dimension is of size 1)

    @property
    def ndim(self):
        return 1

    @property
    def uncertainty(self):
        return np.zeros_like(self._data, dtype=float)

    @uncertainty.setter
    def uncertainty(self, uncertainty):
        pass

    @property
    def T(self):  # no transpose
        return self

    @property
    def shape(self):
        return self._data.shape

    # -------------------------------------------------------------------------
    # private methods
    # -------------------------------------------------------------------------

    def _loc2index(self, loc, axis=None):
        # Return the index of a location (label or coordinates) along the axis
        # axis is not use here as wa are already ib a coord axis.

        # underlying axis array and labels
        data = self._data
        labels = self._labels

        if isinstance(loc, str) and labels is not None:
            # it's probably a label
            indexes = np.argwhere(labels == loc).flatten()
            if indexes.size > 0:
                return indexes[0]
            else:
                raise IndexError(
                        'Could not find this label: {}'.format(loc))

        elif isinstance(loc, datetime):
            # not implemented yet
            return None  # TODO: date!

        elif is_number(loc):
            # get the index of this coordinate
            if loc > data.max() or loc < data.min():
                warnings.warn('This coordinate ({}) is outside the axis limits '
                              '({}-{}).\nThe closest limit index is '
                              'returned'.format(loc, data.min(), data.max()),
                     SpectroChemPyWarning)
            index = (np.abs(data - loc)).argmin()
            return index

        else:
            raise IndexError('Could not find this location: {}'.format(loc))

    def _repr_html_(self):

        tr = "<tr style='border: 1px solid lightgray;'>" \
              "<td style='padding-right:5px; width:100px'><strong>{}</strong></td>" \
              "<td style='text-align:left'>{}</td><tr>\n"

        out = "<table style='width:100%'>\n"
        out += tr.format("Title", self.title.capitalize())
        if self.data is not None:
            data_str = super(Coord, self)._repr_html_()
            out += tr.format("Data", data_str )

        if self.is_labeled:
            out += tr.format("Labels", self.labels)

        out += '</table>\n'
        return out

    # TODO: _repr_latex

    # -------------------------------------------------------------------------
    # special methods
    # -------------------------------------------------------------------------

    def __dir__(self):
        # with remove some methods with respect to the full NDArray
        # as they are not usefull for Coord.
        return ['data', 'mask', 'labels', 'units', 'meta', 'name', 'title']

    def __str__(self):
        out = '      title: %s\n' % (self.title.capitalize())
        if self.data is not None:
            data_str = super(Coord, self).__str__()
            out += '       data: %s\n' % data_str
        if self.is_labeled:
            out += '     labels: %s\n' % str(self.labels)
        if out[-1]=='\n':
            out = out[:-1]
        return out


# =============================================================================
# CoordRange
# =============================================================================

class CoordRange(HasTraits):
    """An axisrange is a set of ordered, non intersecting intervals,\
    e.g. [[a, b], [c, d]] with a < b < c < d or a > b > c > d.

    Parameters
    -----------

    ranges :  iterable,  an interval or a set of intervals.

        An interval or a set of intervals.
        set of  intervals. If none is given, the axisrange
        will be a set of an empty interval [[]]. The interval limits do not
        need to be ordered, and the intervals do not need to be distincts.

    reversed : `bool`, optional.

        The intervals are ranked by decreasing order if True
        or increasing order if False.

    nranges :  `int`

        Number of distinct ranges

    """
    # TODO: May use also units ???

    ranges = List(Range)
    reversed = Bool

    def __init__(self, *ranges, **kwargs):
        """ Constructs CoordRange with default values

        """
        super(CoordRange, self).__init__(**kwargs)

        self.reversed = kwargs.get('reversed', False)

        if len(ranges) == 0:
            # first case: no argument passed, returns an empty range

            self.ranges = []

        elif len(ranges) == 2 and all(
                isinstance(elt, (int, float)) for elt in ranges):
            # second case: a pair of scalars has been passed
            # using the Interval class, we have autochecking of the interval validity

            self.ranges = [list(map(float,ranges))]

        else:
            # third case: a set of pairs of scalars has been passed

            self.ranges = self._cleanranges(ranges)

        if self.reversed:
            self.reverse()

        if self.ranges:
            self.ranges = self._cleanranges(self.ranges)

    def __iter__(self):
        """
        return an iterator

        """
        for x in self.ranges:
            yield x

    # Properties

    @property
    def nranges(self):
        return len(self.ranges)

    # public methods

    def reverse(self):
        """ Reverse the order of the axis range

        """
        for range in self.ranges:
            range.reverse()
        self.ranges.reverse()

    # private methods

    @staticmethod
    def _cleanranges(ranges):
        """ sort and merge overlaping ranges

        works as follows::

        1. orders each interval
        2. sorts intervals
        3. merge overlapping intervals
        4. reverse the orders if required

        """

        # transforms each pairs into valid interval
        # should generate an error if a pair is not valid

        ranges = [list(range) for range in ranges]

        # order the ranges

        ranges = sorted(ranges, key=lambda r: min(r[0], r[1]))

        cleaned_ranges = [ranges[0]]

        for range in ranges[1:]:
            if range[0] <= cleaned_ranges[-1][1]:
                if range[1] >= cleaned_ranges[-1][1]:
                    cleaned_ranges[-1][1] = range[1]
            else:
                cleaned_ranges.append(range)

        return cleaned_ranges


# =============================================================================
# Set the operators
# =============================================================================

set_operators(Coord, priority=50)


if __name__ == '__main__':

    from spectrochempy.api import Coord
    print(Coord.__init__.__doc__)
