# -*- coding: utf-8 -*-
#
# =============================================================================
# Copyright (©) 2015-2017 LCS
# Laboratoire Catalyse et Spectrochimie, Caen, France.
# CeCILL-B FREE SOFTWARE LICENSE AGREEMENT
# See full LICENSE agreement in the root directory
# =============================================================================

__all__ = ['read_zip', 'read_csv']

__dataset_methods__ = __all__

# ----------------------------------------------------------------------------
# standard imports
# ----------------------------------------------------------------------------

import os
import shutil
import warnings
from io import StringIO
from datetime import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US')  # to avoid problems with date format

# ----------------------------------------------------------------------------
# third party imports
# ----------------------------------------------------------------------------

import numpy as np

# -----------------------------------------------------------------------------
# Local imports
# -----------------------------------------------------------------------------
from spectrochempy.dataset.ndcoords import Coord
from spectrochempy.dataset.nddataset import NDDataset
from spectrochempy.core.processors.concatenate import stack
from spectrochempy.application import log, preferences
from spectrochempy.utils import (readfilename, unzip, is_sequence,
                                 SpectroChemPyWarning)

# =============================================================================
# read_zip
# =============================================================================

def read_zip(dataset, filename='', **kwargs):
    """Open a zipped list of .csv files  and set data/metadata in the
    current dataset

    Parameters
    ----------
    dataset : |NDDataset|
        The dataset to store the data and the metadata read from the spg file
    filename: str
        filename of the file to load
    directory: str, optional, default="".
        From where to read the specified filename. If not sperfied, read in
        the current directory.

    Returns
    -------
    |NDDataset|

    Examples
    --------
    >>> from spectrochempy.scp import NDDataset # doctest: +ELLIPSIS,
    +NORMALIZE_WHITESPACE
    SpectroChemPy's API ...
    >>> A = NDDataset.read_zip('agirdata/A350/FTIR/FTIR.zip')
    >>> print(A) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    <BLANKLINE>
    --------------------------------------------------------------------------------
      name/id: FTIR ...

    """

    return _read(dataset, filename,
                 filter='zip file (*.zip);', **kwargs)


# =============================================================================
# read_csv
# =============================================================================

def read_csv(dataset, filename='', **kwargs):
    """Open a .csv file and set data/metadata in the current dataset

    Parameters
    ----------
    dataset : NDDataset
        The dataset to store the data and the metadata read from the spg file
    filename: str
        filename of the file to load
    directory: str [optional, default=""].
        From where to read the specified filename. If not sperfied, read i 
        the current directory.

    Returns
    -------
    |NDDataset|

    Examples
    --------
    >>> from spectrochempy.scp import NDDataset # doctest: +ELLIPSIS,
    +NORMALIZE_WHITESPACE
    <BLANKLINE>
        SpectroChemPy's API ...
    >>> A = NDDataset.read_csv('agirdata/A350/TGA/tg.csv', directory=data)
    >>> print(A) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    <BLANKLINE>
    --------------------------------------------------------------------------------
      name/id: tg ...

    Notes
    -----
    This is limited to 1D array - csv file must have two columns [index, data]
    without header

    """

    return _read(dataset, filename,
                 filter='csv file (*.csv);', **kwargs)


# =============================================================================
# private functions
# =============================================================================

def _read(dataset, filename='',
          filter='zip file (*.zip);', **kwargs):

    # check if the first parameter is a dataset
    # because we allow not to pass it
    if not isinstance(dataset, NDDataset):
        # probably did not specify a dataset
        # so the first parameters must be the filename
        if isinstance(dataset, str) and dataset!= '':
            filename = dataset

        dataset = NDDataset()  # create a NDDataset

    directory = kwargs.get("directory", preferences.datadir)
    if not os.path.exists(directory):
        raise IOError("directory doesn't exists!")

    if os.path.isdir(directory):
        filename = os.path.expanduser(os.path.join(directory, filename))
    else:
        warnings.warn('Provided directory is a file, '
                      'so we use its parent directory', SpectroChemPyWarning)
        filename = os.path.join(os.path.dirname(directory), filename)


    # open file dialog box if necessary
    files = readfilename(filename,
                         directory = directory,
                         filter=filter)

    if not files:
        return None

    datasets = []

    for extension in files.keys():

        for filename in files[extension]:
            if extension == '.zip':
                # zip returns a list, so we extend the list of datasets
                datasets.extend(_read_zip(dataset, filename, **kwargs))

            elif extension == '.csv':
                csv = _read_csv(dataset, filename, **kwargs)
                # check is it is a list of datasets or a single
                if isinstance(csv, NDDataset):
                    datasets.append(csv)
                elif is_sequence(csv):
                    datasets.extend(csv)
            else:
                # try another format!
                dat = dataset.read(filename, protocol=extension[1:], **kwargs)
                if isinstance(dat, NDDataset):
                    datasets.append(dat)
                elif is_sequence(dat):
                    datasets.extend(dat)

    # and stack them into a single file - this assume they are compatibles
    new = stack(datasets)

    # now we return the results
    return new


def _read_zip(dataset, filename, **kwargs):

    if not os.path.exists(filename):
        print('Sorry but this filename (%s) does not exists!'%filename)
        return None

    temp = os.path.join(os.path.dirname(filename), '~temp')
    basename = os.path.splitext(os.path.basename(filename))[0]
    unzip(filename, temp)
    unzipfilename = os.path.join(temp, basename, basename)

    # get all .csv in directory
    filelist = os.listdir(unzipfilename)
    filelist.sort()

    # read all .csv files?
    only = kwargs.pop('only',None)
    if only is not None:
        filelist = filelist[:only+1]
    datasets = []

    for i, f in enumerate(filelist):
        f = os.path.basename(f)

        if os.path.splitext(f)[-1] != '.csv':
            continue # bypass non-csv files

        pth = os.path.join(unzipfilename,f)
        log.debug('reading %s: %s' % (f,pth) )

        datasets.append(_read_csv(dataset, pth, **kwargs))

    try:
        shutil.rmtree(temp)
    except:
        pass

    return datasets

def _read_csv(dataset, filename='', **kwargs):

    # this is limited to 1D array (two columns reading!)
    # TODO: improve this for 2D with header

    if not os.path.exists(filename):
        raise IOError("{} file doesn't exists!".format(filename))

    new = dataset.copy() # important
    delimiter = kwargs.get("csv_delimiter", preferences.csv_delimiter)
    try:
        d = np.loadtxt(filename, delimiter=delimiter)
    except ValueError:
        # it might be that the delimiter is not correct (default is ','), but
        # french excel export for instance, use ";".
        delimiter =';'
        # in this case, in french, very often the decimal '.' is replaced by a
        # comma:  Let's try to correct this
        with open(filename, "r") as f:
            txt = f.read()
            txt = txt.replace(',','.')
            fil = StringIO(txt)
            try:
                d = np.loadtxt(fil, delimiter=delimiter)
            except:
                raise IOError(
                  '{} is not a .csv file or its structure cannot be recognized')

    # transpose d so the the rows becomes the last dimensions
    d = d.T

    # First row should now be the coordinates, and data the rest of the array
    coord1 = d[0]
    data = d[1]

    # create the dataset
    new.data = data
    name = os.path.splitext(os.path.basename(filename))[0]
    new.name = kwargs.get('name', name)
    new.title = kwargs.get('title', None)
    new.units = kwargs.get('units', None)
    new.description = kwargs.get('description',
                                    '"name" '+ 'read from .csv file')
    coord0 = Coord(labels=[new.name])
    new.coordset = [coord0, coord1] #[coord0, coord1]
    new.history = str(datetime.now()) + ':read from .csv file \n'
    new._date = datetime.now()
    new._modified = new.date

    # here we can check some particular format
    origin = kwargs.get('origin', '')
    if 'omnic' in origin:
        # this will be treated as csv export from omnic (IR data)
        new = _add_omnic_info(new, **kwargs)

    return new

def _add_omnic_info(dataset, **kwargs):

    # get the time and name
    name = desc = dataset.name
    name, dat =  name.split('_')

    # if needed convert weekday name to English
    dat = dat.replace('Lun', 'Mon')
    dat = dat[:3].replace('Mar', 'Tue') + dat[3:]
    dat = dat.replace('Mer', 'Wed')
    dat = dat.replace('Jeu', 'Thu')
    dat = dat.replace('Ven', 'Fri')
    dat = dat.replace('Sam', 'Sat')
    dat = dat.replace('Dim', 'Sun')
    # convert month name to English
    dat = dat.replace('Aout', 'Aug')

    # get the dates
    acqdate = datetime.strptime(dat, "%a %b %d %H-%M-%S %Y")

    # Transform back to timestamp for storage in the Coord object
    # use datetime.fromtimestamp(d, timezone.utc))
    # to transform back to datetime obkct
    timestamp = acqdate.timestamp()

    # modify the dataset metadata
    dataset.units = 'absorbance'
    dataset.title = 'Absorbance'
    dataset.name = name
    xaxis = dataset.coordset[-1]
    dataset.coordset = [np.array([timestamp]), xaxis]
    dataset.coordset.titles = ('Acquisition timestamp (GMT)', 'Wavenumbers')
    dataset.coordset[1].units = 'cm^-1'
    dataset.coordset[0].labels = np.array([[acqdate], [name]])
    dataset.coordset[0].units = 's'

    # Set description and history
    dataset.description = (
        'Dataset from .csv file : {}\n'.format(desc))

    dataset.history = str(datetime.now()) + ':read from spg file \n'

    # Set the NDDataset date
    dataset._date = datetime.now()
    dataset._modified = dataset.date

    return dataset

#===============================================================================
# tests
#===============================================================================
if __name__ == '__main__':

    from spectrochempy import (NDDataset, preferences, ERROR, show)


    preferences.log_level = ERROR

    # A = NDDataset.read_zip('agirdata/A350/FTIR/FTIR.zip',
    #                        directory=data,
    #                        origin='omnic_export')
    # print(A)
    # A.plot_stack()


    B = NDDataset.read_csv('agirdata/A350/TGA/tg.csv')
    print(B)

    B = B[-0.5:60.0]

    B.x.units = 'hour'
    B.x.title = 'time on stream'
    B.units = 'weight_percent'
    B.title = 'loss of mass'

    B.plot()
    show()

    # to open the file dialog editor
    #C = NDDataset.read_csv(directory=data)
    #print(C)