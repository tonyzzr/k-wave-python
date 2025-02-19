"""
    Using An Ultrasound Transducer As A Sensor Example

    This example shows how an ultrasound transducer can be used as a detector
    by substituting a transducer object for the normal sensor input
    structure. It builds on the Defining An Ultrasound Transducer and
    Simulating Ultrasound Beam Patterns examples.
"""
import os
from copy import deepcopy
from tempfile import gettempdir

import numpy as np

# noinspection PyUnresolvedReferences
import setup_test
from kwave.kgrid import kWaveGrid
from kwave.kmedium import kWaveMedium
from kwave.ksource import kSource
from kwave.kspaceFirstOrder3D import kspaceFirstOrder3DC
from kwave.ktransducer import kSensor
from kwave.utils.filters import filter_time_series
from tests.diff_utils import compare_against_ref


def test_tvsp_3D_simulation():
    # create the computational grid
    Nx = 64  # number of grid points in the x direction
    Ny = 64  # number of grid points in the y direction
    Nz = 64  # number of grid points in the z direction
    dx = 0.1e-3  # grid point spacing in the x direction [m]
    dy = 0.1e-3        # grid point spacing in the y direction [m]
    dz = 0.1e-3        # grid point spacing in the z direction [m]
    kgrid = kWaveGrid([Nx, Ny, Nz], [dx, dy, dz])

    # define the properties of the propagation medium
    medium = kWaveMedium(
        sound_speed=1500 * np.ones((Nx, Ny, Nz)),
        density=1000 * np.ones((Nx, Ny, Nz))
    )
    medium.sound_speed[0:Nx//2, :, :] = 1800            # [m/s]
    medium.density[:, Ny//4-1:, :] = 1200               # [kg/m^3]

    # create the time array
    kgrid.makeTime(medium.sound_speed)

    # define a square source element
    source = kSource()
    source_radius = 5  # [grid points]
    source.p_mask = np.zeros((Nx, Ny, Nz))
    source.p_mask[Nx//4 - 1, Ny//2 - source_radius - 1:Ny//2 + source_radius, Nz//2 - source_radius - 1:Nz//2 + source_radius] = 1

    # define a time varying sinusoidal source
    source_freq = 2e6  # [Hz]
    source_mag = 1     # [Pa]
    source.p = source_mag * np.sin(2 * np.pi * source_freq * kgrid.t_array)

    # filter the source to remove high frequencies not supported by the grid
    source.p = filter_time_series(kgrid, medium, source.p)

    # define a series of Cartesian points to collect the data
    y = np.arange(-20, 21, 2) * dy            # [m]
    z = np.arange(-20, 21, 2) * dz            # [m]
    x = 20 * dx * np.ones(z.shape)    # [m]
    sensor_mask = np.array([x, y, z])
    sensor = kSensor(sensor_mask)

    # define the field parameters to record
    sensor.record = ['p', 'p_final']
    input_filename = f'example_tvsp_3d_input.h5'
    pathname = gettempdir()
    input_file_full_path = os.path.join(pathname, input_filename)
    # input arguments
    input_args = {
        'data_cast': 'single',
        'cart_interp': 'nearest',
        'save_to_disk': True,
        'input_filename': input_filename,
        'data_path': pathname,
        'save_to_disk_exit': True
    }

    # run the simulation
    kspaceFirstOrder3DC(**{
        'medium': medium,
        'kgrid': kgrid,
        'source': deepcopy(source),
        'sensor': sensor,
        **input_args
    })
    assert compare_against_ref(f'out_tvsp_3D_simulation', input_file_full_path), \
        'Files do not match!'
