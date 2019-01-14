# coding=utf-8

import sys
import os

import pytest
import numpy as np
import pandas as pd

#############################################################
# initialize a ipython session before calling spectrochempy
#############################################################

@pytest.fixture(scope="module")
def ip():
    from IPython.testing.globalipapp import get_ipython as getipy
    ip = getipy()
    ip.run_cell("from spectrochempy import *")
    return ip

try:
    ip()
    # we need to go into this before anything else in the test
    # to have the IPython session available.
except:
    pass

from spectrochempy.dataset.ndarray import NDArray
from spectrochempy.dataset.nddataset import NDDataset
from spectrochempy.dataset.ndcoords import CoordSet, Coord
from spectrochempy.utils.testing import RandomSeedContext
from spectrochempy.application import general_preferences as prefs

###########################
# FIXTURES: some NDArray's
###########################

@pytest.fixture(scope="module")
def ndarray():
    # return a simple ndarray with some data
    with RandomSeedContext(12345):
        dx = 10.*np.random.random((10, 10))-5.
    _nd = NDArray()
    _nd.data = dx
    return _nd.copy()

@pytest.fixture(scope="module")
def ndarrayunit(ndarray):
    # return a simple ndarray with some data
    _nd = ndarray.copy()
    _nd.units = 'm/s'
    return _nd.copy()

@pytest.fixture(scope="module")
def ndarraycplx(ndarray):
    # return a complex ndarray
    # with some complex data
    _nd = ndarray.copy()
    _nd.set_complex(inplace=True)  # this means that the data are complex
    return _nd.copy()

@pytest.fixture(scope="module")
def ndarrayquaternion(ndarray):
    # return a complex ndarray
    # with hypercomplex data
    _nd = ndarray.copy()
    _nd.set_complex(inplace=True)
    _nd.set_quaternion(inplace=True)  # this means that the data are hypercomplex
    return _nd.copy()

#########################
# FIXTURES: some datasets
#########################
@pytest.fixture()
def ndcplx():
    # return a complex ndarray
    _nd = NDDataset()
    with RandomSeedContext(1234):
        _nd._data = np.random.random((10, 10))
    _nd.set_complex(axis=-1)  # this means that the data are complex in
    # the last dimension
    return _nd


@pytest.fixture()
def nd1d():
    # a simple ndarray with negative elements
    _nd = NDDataset()
    _nd._data = np.array([1., 2., 3., -0.4])
    return _nd

@pytest.fixture()
def nd2d():
    # a simple 2D ndarray with negative elements
    _nd = NDDataset()
    _nd._data = np.array([[1., 2., 3., -0.4], [-1., -.1, 1., 2.]])
    return _nd


@pytest.fixture()
def nd():
    # return a simple (positive) ndarray
    _nd = NDDataset()
    with RandomSeedContext(145):
        _nd._data = np.random.random((10, 10))
    return _nd.copy()

@pytest.fixture()
def ds1():

    with RandomSeedContext(12345):
        dx = np.random.random((10, 100, 3))
        # make complex along first dimension
        iscomplex = [False, False, False]  # TODO: check with complex

    coord0 = Coord(data=np.linspace(4000., 1000., 10),
                 labels='a b c d e f g h i j'.split(),
                 units="cm^-1",
                 title='wavenumber')

    coord1 = Coord(data=np.linspace(0., 60., 100),
                 units="s",
                 title='time-on-stream')

    coord2 = Coord(data=np.linspace(200., 300., 3),
                 labels=['cold', 'normal', 'hot'],
                 units="K",
                 title='temperature')

    da = NDDataset(dx,
                   iscomplex=iscomplex,
                   coordset=[coord0, coord1, coord2],
                   title='Absorbance',
                   units='absorbance',
                   uncertainty=dx * 0.1,
                   )
    return da.copy()


@pytest.fixture()
def ds2():
    with RandomSeedContext(12345):
        dx = np.random.random((9, 50, 4))
        # make complex along first dimension
        iscomplex = [False, False, False]  # TODO: check with complex

    coord0 = Coord(data=np.linspace(4000., 1000., 9),
                 labels='a b c d e f g h i'.split(),
                 units="cm^-1",
                 title='wavenumber')

    coord1 = Coord(data=np.linspace(0., 60., 50),
                 units="s",
                 title='time-on-stream')

    coord2 = Coord(data=np.linspace(200., 1000., 4),
                 labels=['cold', 'normal', 'hot', 'veryhot'],
                 units="K",
                 title='temperature')

    da = NDDataset(dx,
                   iscomplex=iscomplex,
                   coordset=[coord0, coord1, coord2],
                   title='Absorbance',
                   units='absorbance',
                   uncertainty=dx * 0.1,
                   )
    return da.copy()


@pytest.fixture()
def dsm():  # dataset with coords containing several axis

    with RandomSeedContext(12345):
        dx = np.random.random((9, 50))
        # make complex along first dimension
        iscomplex = [False, False]  # TODO: check with complex

    coord0 = Coord(data=np.linspace(4000., 1000., 9),
                 labels='a b c d e f g h i'.split(),
                 units="cm^-1",
                 title='wavenumber')

    coord11 = Coord(data=np.linspace(0., 60., 50),
                  units="s",
                  title='time-on-stream')

    coord12 = Coord(data=np.logspace(1., 4., 50),
                  units="K",
                  title='temperature')

    coordmultiple = CoordSet(coord11, coord12)
    da = NDDataset(dx,
                   iscomplex=iscomplex,
                   coordset=[coord0, coordmultiple],
                   title='Absorbance',
                   units='absorbance',
                   uncertainty=dx * 0.1,
                   )
    return da.copy()


# Datasets and CoordSet
@pytest.fixture()
def dataset1d():

    # create a simple 1D
    length = 10.
    x_axis = Coord(np.arange(length) * 1000.,
                  title='wavelengths',
                  units='cm^-1')
    with RandomSeedContext(125):
        ds = NDDataset(np.random.randn(length),
                       coordset=[x_axis],
                       title='absorbance',
                       units='dimensionless')
    return ds.copy()


@pytest.fixture()
def dataset3d():

    with RandomSeedContext(12345):
        dx = np.random.random((10, 100, 3))

    coord0 = Coord(np.linspace(4000., 1000., 10),
                labels='a b c d e f g h i j'.split(),
                mask=None,
                units="cm^-1",
                title='wavelength')

    coord1 = Coord(np.linspace(0., 60., 100),
                labels=None,
                mask=None,
                units="s",
                title='time-on-stream')

    coord2 = Coord(np.linspace(200., 300., 3),
                labels=['cold', 'normal', 'hot'],
                mask=None,
                units="K",
                title='temperature')

    da = NDDataset(dx,
                coordset=[coord0, coord1, coord2],
                title='absorbance',
                units='dimensionless',
                uncertainty=dx * 0.1,
                mask=np.zeros_like(dx)  # no mask
                )
    return da.copy()


# ------------------------------
# Fixture:  IR spectra (SPG)
# -----------------------------

@pytest.fixture(scope="function")
def IR_dataset_1D():
    directory = prefs.datadir
    dataset = NDDataset.load(
            os.path.join(directory, 'irdata', 'nh4y-activation.spg'))
    return dataset[0]

@pytest.fixture(scope="function")
def IR_dataset_2D():
    directory = prefs.datadir
    dataset = NDDataset.read_omnic(
            os.path.join(directory, 'irdata', 'nh4y-activation.spg'))
    return dataset

# Fixture:  IR spectra
@pytest.fixture(scope="function")
def IR_scp_1():
    directory = prefs.datadir
    dataset = NDDataset.load(
            os.path.join(directory, 'irdata', 'nh4.scp'))
    return dataset


# ------------------------
# Fixture : NMR spectra
# ------------------------

@pytest.fixture(scope="function")
def NMR_dataset_1D():
    directory = prefs.datadir
    path = os.path.join(directory, 'nmrdata', 'bruker', 'tests', 'nmr',
                        'bruker_1d')
    dataset = NDDataset.read_bruker_nmr(
            path, expno=1, remove_digital_filter=True)
    return dataset


@pytest.fixture(scope="function")
def NMR_dataset_1D_1H():
    directory =  prefs.datadir
    path = os.path.join(directory, 'nmrdata', 'bruker', 'tests', 'nmr',
                        'tpa')
    dataset = NDDataset.read_bruker_nmr(
            path, expno=10, remove_digital_filter=True)
    return dataset


@pytest.fixture(scope="function")
def NMR_dataset_2D():
    directory = prefs.datadir
    path = os.path.join(directory, 'nmrdata', 'bruker', 'tests', 'nmr',
                        'bruker_2d')
    dataset = NDDataset.read_bruker_nmr(
            path, expno=1, remove_digital_filter=True)
    return dataset

# -------------------------------------------------
# init with panda structure
# Some panda structure for dataset initialization
# -------------------------------------------------
@pytest.fixture()
def series():
    with RandomSeedContext(2345):
        arr = pd.Series(np.random.randn(4), index=np.arange(4) * 10.)
    arr.index.name = 'un nom'
    return arr


@pytest.fixture()
def dataframe():
    with RandomSeedContext(23451):
        arr = pd.DataFrame(np.random.randn(6, 4), index=np.arange(6) * 10.,
                           columns=np.arange(4) * 10.)
    for ax, name in zip(arr.axes, ['y', 'x']):
        ax.name = name
    return arr


@pytest.fixture()
def panel():
    shape = (7, 6, 5)
    with RandomSeedContext(23452):
        # TODO: WARNING: pd.Panel is deprecated in pandas
        arr = pd.Panel(np.random.randn(*shape), items=np.arange(shape[0]) * 10.,
                       major_axis=np.arange(shape[1]) * 10.,
                       minor_axis=np.arange(shape[2]) * 10.)

    for ax, name in zip(arr.axes, ['z', 'y', 'x']):
        ax.name = name
    return arr


@pytest.fixture()
def panelnocoordname():
    shape = (7, 6, 5)
    with RandomSeedContext(2452):
        arr = pd.Panel(np.random.randn(*shape), items=np.arange(shape[0]) * 10.,
                       major_axis=np.arange(shape[1]) * 10.,
                       minor_axis=np.arange(shape[2]) * 10.)
    return arr




# ----------------------------------------------------------------------------
# GUI Fixtures
# ----------------------------------------------------------------------------

#from spectrochempy.extern.pyqtgraph import mkQApp

#@pytest.fixture(scope="module")
#def app():
#    return mkQApp()