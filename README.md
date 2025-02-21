# Shyfem Toolbox

## Overview
**Shyfem Toolbox** is a Python package designed to work with NetCDF files that were generated with SHYFEM and shyelab, to use it is necesary to have river node data and also is recommended to have measured data. It provides functions for:
- Sorting river nodes (`sort_river_nodes`)
- Creating subsets of NetCDF files (`create_subset_nc`)
- Processing multiple NetCDF files automatically (`process_folder`)
- Reading and plotting data (`reader.py`, `plotter.py`, `utils.py`)

This toolbox is useful for hydrodynamic and environmental modeling, especially for working with **Shyfem model outputs**.

## Installation

### **1. Install from Source**
Clone the repository and install it:
```sh
git clone https://github.com/yourusername/shyfem_toolbox.git
cd shyfem_toolbox
pip install -e .

```

## Steps to generate plots from NC
- For runs of 1 year or more, usually there will be a big file containing all information (hydro and ts), 
- There is an SH file (`gen_2month_ncFiles.sh`) that uses shyelab to separate the big file into smaller 2-month chunks of information, file is used in main runeed folder 
- The 
