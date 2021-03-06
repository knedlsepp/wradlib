#!/usr/bin/env python
# Copyright (c) 2016, wradlib developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

"""
Data Quality
^^^^^^^^^^^^

This module will serve two purposes:

#. provide routines to create simple radar data quality related fields.
#. provide routines to decide which radar pixel to choose based on the
   competing information in different quality fields.

Data is supposed to be stored in 'aligned' arrays. Aligned here means that
all fields are structured such that in each field the data for a certain index
is representative for the same physical target.

Therefore no assumptions are made on the dimensions or shape of the input
fields except that they exhibit the numpy ndarray interface.

.. autosummary::
   :nosignatures:
   :toctree: generated/

    beam_height_ft
    beam_height_ft_doviak
    pulse_volume
    beam_block_frac

"""

import numpy as np


def beam_height_ft(ranges, elevations, degrees=True, re=6371000):
    """Calculates the height of a radar beam above the antenna according to
    the 4/3 (four-thirds -> ft) effective Earth radius model.
    The formula was taken from :cite:`Collier1996`.

    Parameters
    ----------
    ranges : array
        the distances of each bin from the radar [m]
    elevations : array
        the elevation angles of each bin from the radar [degrees or radians]
    degrees : bool
        if True (the default) elevation angles are given in degrees and will
        be converted to radians before calculation. If False no transformation
        will be done and elevations has to be given in radians.
    re : float
        earth radius [m]

    Returns
    -------
    output : array
        height of the beam [m]

    Note
    ----
    The shape of `elevations` and `ranges` may differ in which case numpy's
    broadcasting rules will apply and the shape of `output` will be that of
    the broadcast arrays. See the numpy documentation on how broadcasting
    works.

    """
    if degrees:
        elev = np.deg2rad(elevations)
    else:
        elev = elevations

    return ((ranges ** 2 * np.cos(elev) ** 2) /
            (2 * (4. / 3.) * re)) + ranges * np.sin(elev)


def beam_height_ft_doviak(ranges, elevations, degrees=True, re=6371000):
    """Calculates the height of a radar beam above the antenna according to
    the 4/3 (four-thirds -> ft) effective Earth radius model.
    The formula was taken from :cite:`Doviak1993`.

    Parameters
    ----------
    ranges : array
        the distances of each bin from the radar [m]
    elevations : array
        the elevation angles of each bin from the radar [degrees or radians]
    degrees : bool
        if True (the default) elevation angles are assumed to be given in
        degrees and will
        be converted to radians before calculation. If False no transformation
        will be done and `elevations` has to be given in radians.
    re : float
        earth radius [m]

    Returns
    -------
    output : array
        height of the beam [m]

    Note
    ----
    The shape of `elevations` and `ranges` may differ in which case numpy's
    broadcasting rules will apply and the shape of `output` will be that of
    the broadcast arrays. See the numpy documentation on how broadcasting
    works.

    """
    if degrees:
        elev = np.deg2rad(elevations)
    else:
        elev = elevations

    reft = (4. / 3.) * re

    return np.sqrt(ranges ** 2 + reft ** 2 +
                   2 * ranges * reft * np.sin(elev)) - reft


def pulse_volume(ranges, h, theta):
    r"""Calculates the sampling volume of the radar beam per bin depending on
    range and aperture.

    We assume a cone frustum which has the volume
    :math:`V=(\pi/3) \cdot h \cdot (R^2 + R \cdot r + r^2)`.
    R and r are the radii of the two frustum surface circles. Assuming that the
    pulse width is small compared to the range, we get
    :math:`R=r= \tan ( \theta \cdot \pi/180 ) \cdot range`.
    Thus, the pulse volume simply becomes the volume of a cylinder with
    :math:`V=\pi \cdot h \cdot range^2 \cdot \tan(\theta \cdot \pi/180)^2`

    Parameters
    ----------
    ranges : array
        the distances of each bin from the radar [m]
    h : float
        pulse width (which corresponds to the range resolution [m])
    theta : float
        the aperture angle (beam width) of the radar beam [degree]

    Returns
    -------
    output : array
        volume of radar bins at each range in `ranges` [:math:`m^3`]

    Examples
    --------

    See :ref:`notebooks/workflow/recipe1.ipynb`.

    """
    return np.pi * h * (ranges ** 2) * (np.tan(np.radians(theta))) ** 2


def beam_block_frac(Th, Bh, a):
    """Partial beam blockage fraction.

    .. versionadded:: 0.6.0

    Note
    ----
    Code was migrated from https://github.com/nguy/PyRadarMet.

    From Bech et al. (2003), Eqn 2 and Appendix

    Parameters
    ----------
    Th : float
        array of floats
        Terrain height [m]
    Bh : float
        array of floats
        Beam height [m]
    a : float
        array of floats
        Half power beam radius [m]

    Returns
    -------
    PBB : float
        Partial beam blockage fraction [unitless]

    Examples
    --------
    >>> PBB = beam_block_frac(Th,Bh,a) #doctest: +SKIP

    See :ref:`notebooks/beamblockage/wradlib_beamblock.ipynb`.

    Note
    ----
    This procedure uses a simplified interception function where no vertical
    gradient of refractivity is considered.  Other algorithms treat this
    more thoroughly.  However, this is accurate in most cases other than
    the super-refractive case.

    See the the half_power_radius function to calculate variable `a`.

    The heights must be the same units!
    """

    # First find the difference between the terrain and height of
    # radar beam (Bech et al. (2003), Fig.3)
    y = Th - Bh

    Numer = (y * np.sqrt(a ** 2 - y ** 2)) + \
            (a ** 2 * np.arcsin(y / a)) + (np.pi * a ** 2 / 2.)

    Denom = np.pi * a ** 2

    PBB = Numer / Denom

    return PBB


if __name__ == '__main__':
    print('wradlib: Calling module <qual> as main...')
