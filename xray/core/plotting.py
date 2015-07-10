"""
Plotting functions are implemented here and also monkeypatched into
the DataArray class
"""

import numpy as np

from .utils import is_uniform_spaced

# TODO - Is there a better way to import matplotlib in the function?
# Other piece of duplicated logic is the checking for axes.
# Decorators don't preserve the argument names
# But if all the plotting methods have same signature...


# TODO - implement this
class FacetGrid():
    pass


def plot(darray, ax=None, rtol=0.01, **kwargs):
    """
    Default plot of DataArray using matplotlib / pylab.

    Calls xray plotting function based on the dimensions of
    the array:

    =============== =========== ===========================
    Dimensions      Coordinates Plotting function
    --------------- ----------- ---------------------------
    1                           :py:meth:`xray.DataArray.plot_line`
    2               Uniform     :py:meth:`xray.DataArray.plot_imshow`
    2               Irregular   :py:meth:`xray.DataArray.plot_contourf`
    Anything else               :py:meth:`xray.DataArray.plot_hist`
    =============== =========== ===========================

    Parameters
    ----------
    darray : DataArray
    ax : matplotlib axes object
        If None, uses the current axis
    rtol : relative tolerance
        Relative tolerance used to determine if the indexes
        are uniformly spaced
    kwargs
        Additional keyword arguments to matplotlib

    """
    ndims = len(darray.dims)

    if ndims == 1:
        plotfunc = plot_line
    elif ndims == 2:
        indexes = darray.indexes.values()
        if all(is_uniform_spaced(i, rtol=rtol) for i in indexes):
            plotfunc = plot_imshow
        else:
            plotfunc = plot_contourf
    else:
        plotfunc = plot_hist

    kwargs['ax'] = ax
    return plotfunc(darray, **kwargs)


# This function signature should not change so that it can use
# matplotlib format strings
def plot_line(darray, *args, **kwargs):
    """
    Line plot of 1 dimensional DataArray index against values

    Wraps matplotlib.pyplot.plot

    Parameters
    ----------
    darray : DataArray
        Must be 1 dimensional
    ax : matplotlib axes object
        If not passed, uses the current axis
    args, kwargs
        Additional arguments to matplotlib.pyplot.plot

    """
    import matplotlib.pyplot as plt

    ndims = len(darray.dims)
    if ndims != 1:
        raise ValueError('Line plots are for 1 dimensional DataArrays. '
                         'Passed DataArray has {} dimensions'.format(ndims))

    # Ensures consistency with .plot method
    try:
        ax = kwargs.pop('ax')
    except KeyError:
        ax = None

    if ax is None:
        ax = plt.gca()

    xlabel, x = list(darray.indexes.items())[0]

    ax.plot(x, darray, *args, **kwargs)

    ax.set_xlabel(xlabel)

    if darray.name is not None:
        ax.set_ylabel(darray.name)

    return ax


def plot_imshow(darray, ax=None, add_colorbar=True, **kwargs):
    """
    Image plot of 2d DataArray using matplotlib / pylab

    Wraps matplotlib.pyplot.imshow

    WARNING: This function needs uniformly spaced coordinates to
    properly label the axes. Call DataArray.plot() to check.

    Parameters
    ----------
    darray : DataArray
        Must be 2 dimensional
    ax : matplotlib axes object
        If None, uses the current axis
    add_colorbar : Boolean
        Adds colorbar to axis
    kwargs :
        Additional arguments to matplotlib.pyplot.imshow

    Details
    -------
    The pixels are centered on the coordinates values. Ie, if the coordinate
    value is 3.2 then the pixels for those coordinates will be centered on 3.2.

    """
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    try:
        ylab, xlab = darray.dims
    except ValueError:
        raise ValueError('Image plots are for 2 dimensional DataArrays. '
                         'Passed DataArray has {} dimensions'
                         .format(len(darray.dims)))

    x = darray[xlab]
    y = darray[ylab]

    # Centering the pixels- Assumes uniform spacing
    xstep = (x[1] - x[0]) / 2.0
    ystep = (y[1] - y[0]) / 2.0
    left, right = x[0] - xstep, x[-1] + xstep
    bottom, top = y[-1] + ystep, y[0] - ystep

    defaults = {'extent': [left, right, bottom, top],
                'aspect': 'auto',
                'interpolation': 'nearest',
                }

    # Allow user to override these defaults
    defaults.update(kwargs)

    image = ax.imshow(darray, **defaults)

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    if add_colorbar:
        plt.colorbar(image, ax=ax)

    return ax


# TODO - Could refactor this to avoid duplicating plot_imshow logic.
# There's also some similar tests for the two.
def plot_contourf(darray, ax=None, add_colorbar=True, **kwargs):
    """
    Filled contour plot of 2d DataArray

    Wraps matplotlib.pyplot.contourf

    Parameters
    ----------
    darray : DataArray
        Must be 2 dimensional
    ax : matplotlib axes object
        If None, uses the current axis
    add_colorbar : Boolean
        Adds colorbar to axis
    kwargs :
        Additional arguments to matplotlib.pyplot.imshow

    """
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    try:
        ylab, xlab = darray.dims
    except ValueError:
        raise ValueError('Contour plots are for 2 dimensional DataArrays. '
                         'Passed DataArray has {} dimensions'
                         .format(len(darray.dims)))

    contours = ax.contourf(darray[xlab], darray[ylab], darray, **kwargs)

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    if add_colorbar:
        plt.colorbar(contours, ax=ax)

    return ax


def plot_hist(darray, ax=None, **kwargs):
    """
    Histogram of DataArray

    Wraps matplotlib.pyplot.hist

    Plots N dimensional arrays by first flattening the array.

    Parameters
    ----------
    darray : DataArray
        Can be any dimension
    ax : matplotlib axes object
        If not passed, uses the current axis
    kwargs :
        Additional keyword arguments to matplotlib.pyplot.hist

    """
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    ax.hist(np.ravel(darray), **kwargs)

    ax.set_ylabel('Count')

    if darray.name is not None:
        ax.set_title('Histogram of {}'.format(darray.name))

    return ax
