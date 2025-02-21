# -*- coding: utf-8 -*-
"""
NetCDF Processing Toolbox

Contains functions for:
- Sorting river nodes
- Creating subsets of NetCDF files
"""

import netCDF4 as nc
import numpy as np
import pandas as pd
import os
import glob
from geopy.distance import geodesic


def sort_river_nodes(file_XY_river, sort_LonLat):
    """
    Function to sort river nodes based on longitude or latitude.

    Parameters:
    file_XY_river (str): Path to the CSV file with river coordinates.
    sort_LonLat (int): Sorting direction for river nodes. 0 for west-east, 1 for north-south.

    Returns:
    pd.DataFrame: Sorted river nodes with columns Node, Lat, Lon, Distance.
    """
    river_001 = pd.read_csv(file_XY_river)
    if sort_LonLat == 0:
        river_001 = river_001.sort_values(by='Lon')
    elif sort_LonLat == 1:
        river_001 = river_001.sort_values(by='Lat')
    else:
        raise ValueError('sort_LonLat must be 0 (west-east) or 1 (north-south)')
    
    river_001_x = river_001['Lat'].values
    river_001_y = river_001['Lon'].values
    river_001_n = river_001['Node'].values
    
    d1 = [0] * len(river_001_n)
    for rr in range(len(river_001_n) - 1, 0, -1):
        c_x1, c_y1 = river_001_x[rr], river_001_y[rr]
        c_x2, c_y2 = river_001_x[rr - 1], river_001_y[rr - 1]
        d1[rr - 1] = geodesic((c_x1, c_y1), (c_x2, c_y2)).meters
    
    nxyd = pd.DataFrame({
        'Node': river_001_n,
        'Lat': river_001_x,
        'Lon': river_001_y,
        'Distance': d1
    })
    
    return nxyd


def create_subset_nc(nc_file, river_file, sort_LonLat, output_file, time_steps=None, save_frequency=1):
    """
    Create a subset of the NetCDF file with specific nodes and time steps.

    Parameters:
    nc_file (str): Path to the original NetCDF file.
    river_file (str): Path to the CSV file with river coordinates.
    sort_LonLat (int): Sorting direction for river nodes. 0 for west-east, 1 for north-south.
    output_file (str): Path to the output NetCDF file.
    time_steps (list or None): List of time steps to save. If None, all time steps are considered.
    save_frequency (int): Frequency of saving time steps (e.g., every nth time step).
    """
    dataset = nc.Dataset(nc_file, 'r')
    longitude = dataset.variables['longitude'][:]
    latitude = dataset.variables['latitude'][:]
    level = dataset.variables['level'][:]
    total_depth = dataset.variables['total_depth'][:]
    time = dataset.variables['time'][:]
    
    river_nodes = sort_river_nodes(river_file, sort_LonLat)
    river_lons = river_nodes['Lon'].values
    river_lats = river_nodes['Lat'].values
    
    river_nodes_idx = []
    for lon, lat in zip(river_lons, river_lats):
        distances = np.sqrt((longitude - lon)**2 + (latitude - lat)**2)
        node_idx = np.unravel_index(np.argmin(distances, axis=None), distances.shape)
        river_nodes_idx.append(node_idx[0])
    
    if time_steps is None:
        time_steps = np.arange(0, len(time), save_frequency)
    else:
        time_steps = np.array(time_steps)[::save_frequency]
    
    with nc.Dataset(output_file, 'w', format='NETCDF4') as new_dataset:
        new_dataset.createDimension('node', len(river_nodes_idx))
        new_dataset.createDimension('level', len(level))
        new_dataset.createDimension('time', len(time_steps))
        
        new_longitude = new_dataset.createVariable('longitude', np.float64, ('node',))
        new_latitude = new_dataset.createVariable('latitude', np.float64, ('node',))
        new_level = new_dataset.createVariable('level', np.float32, ('level',))
        new_total_depth = new_dataset.createVariable('total_depth', np.float32, ('node',))
        new_time = new_dataset.createVariable('time', np.float64, ('time',))
        new_salinity = new_dataset.createVariable('salinity', np.float32, ('time', 'node', 'level'), fill_value=None)
        new_temperature = new_dataset.createVariable('temperature', np.float32, ('time', 'node', 'level'), fill_value=None)
        
        new_time.units = dataset.variables['time'].units
        new_latitude.units = 'degrees_north'
        new_longitude.units = 'degrees_east'
        new_level.units = 'meters'
        new_total_depth.units = 'meters'
        
        new_longitude[:] = longitude[river_nodes_idx]
        new_latitude[:] = latitude[river_nodes_idx]
        new_level[:] = level.astype(np.float32)
        new_total_depth[:] = total_depth[river_nodes_idx]
        new_time[:] = time[time_steps]
        
        for i, t in enumerate(time_steps):
            new_salinity[i, :, :] = dataset.variables['salinity'][t, river_nodes_idx, :]
            new_temperature[i, :, :] = dataset.variables['temperature'][t, river_nodes_idx, :]
        
    print(f"Subset NetCDF file created: {output_file}")


def process_folder(nc_folder, river_file, sort_LonLat, output_folder, save_frequency=1):
    """
    Automatically processes all NetCDF files in a folder.

    Parameters:
    nc_folder (str): Folder containing NetCDF files.
    river_file (str): Path to river nodes CSV file.
    sort_LonLat (int): Sorting direction for river nodes.
    output_folder (str): Folder where processed files will be saved.
    save_frequency (int): Frequency of saving time steps.
    """
    os.makedirs(output_folder, exist_ok=True)
    
    nc_files = glob.glob(os.path.join(nc_folder, "*.nc"))
    
    for nc_file in nc_files:
        output_file = os.path.join(output_folder, f"subset_{os.path.basename(nc_file)}")
        create_subset_nc(nc_file, river_file, sort_LonLat, output_file, save_frequency=save_frequency)


# Command-line usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process NetCDF files for river nodes.")
    parser.add_argument("nc_folder", type=str, help="Folder containing NetCDF files.")
    parser.add_argument("river_file", type=str, help="Path to river nodes CSV file.")
    parser.add_argument("sort_LonLat", type=int, choices=[0, 1], help="Sort by 0 (west-east) or 1 (north-south).")
    parser.add_argument("output_folder", type=str, help="Folder where subset NetCDF files will be saved.")
    parser.add_argument("--save_frequency", type=int, default=1, help="Save every nth time step.")

    args = parser.parse_args()

    process_folder(args.nc_folder, args.river_file, args.sort_LonLat, args.output_folder, args.save_frequency)
