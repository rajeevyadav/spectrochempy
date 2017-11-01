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


""" Tests for the  module

"""
import sys
import functools
import pytest
from tests.utils import (assert_equal, assert_array_equal,
                         assert_array_almost_equal, assert_equal_units,
                         raises, show_do_not_block)

from spectrochempy.api import *
from spectrochempy.api import figure, show
from spectrochempy.utils import SpectroChemPyWarning


@show_do_not_block
def test_nmr_2D(NMR_source_2D):
    figure()
    source = NMR_source_2D
    source.plot(nlevels=20)  # , start=0.15)
    show()
    pass


@show_do_not_block
def test_nmr_2D_imag(NMR_source_2D):
    # plt.ion()
    figure()
    source = NMR_source_2D.copy()
    source.plot(imag=True)
    show()
    pass


@show_do_not_block
def test_nmr_2D_imag_compare(NMR_source_2D):
    # plt.ion()
    figure()
    source = NMR_source_2D.copy()
    source.plot()
    source.plot(imag=True, cmap='jet', data_only=True, alpha=.3)
    # better not to replot a second colorbar
    show()
    pass


@show_do_not_block
def test_nmr_2D_hold(NMR_source_2D):
    source = NMR_source_2D
    figure()
    source.plot()
    source.imag.plot(cmap='jet', data_only=True)
    show()
    pass


@show_do_not_block
def test_nmr_2D_em_(NMR_source_2D):
    figure()
    source = NMR_source_2D.copy()
    source.plot()
    assert source.shape == (96, 948)
    source.em(lb=100. * ur.Hz)
    assert source.shape == (96, 948)
    source.em(lb=50. * ur.Hz, axis=0)
    assert source.shape == (96, 948)
    source.plot(cmap='copper', data_only=True)
    show()
    pass