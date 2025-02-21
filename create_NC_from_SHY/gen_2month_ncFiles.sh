#!/bin/bash

# Command template
command_template="./shyelab_po-em -outformat nc -tmin {tmin} -tmax {tmax} {file}"
# Previous command generates the out.nc file

# Define the time ranges for every 2 months in 2022
declare -a time_ranges=(
    "2022-01-01 2022-03-01"
    "2022-03-01 2022-05-01"
    "2022-05-01 2022-07-01"
    "2022-07-01 2022-09-01"
    "2022-09-01 2022-11-01"
    "2022-11-01 2022-12-31"
)

# deltapo_ER_2022_025.hydro.shy
# Define the list of files and corresponding output directories
declare -A files=(
    ["deltapo_ER_2022.ts.shy"]="NC_output/z025_cf"
)

# Create the main output directory
mkdir -p NC_output

# Create subdirectories for each model
mkdir -p NC_output/zhyb_025

# Loop through each time range
for time_range in "${time_ranges[@]}"; do
    tmin=$(echo $time_range | cut -d ' ' -f 1)
    tmax=$(echo $time_range | cut -d ' ' -f 2)
    
    # Loop through each file and its output directory
    for file in "${!files[@]}"; do
        outdir=${files[$file]}
        
        # Extract the base name of the file (e.g., deltapo_ER_2022_zeta.ts.shy -> deltapo_ER_2022_zeta_ts)
        base_name=$(basename "$file" .shy | sed 's/\./_/')
        
        # Define the output file name
        output_file="${base_name}_${tmin//-/}_${tmax//-/}.nc"
        
        # Replace placeholders in the command template
        command=$(echo $command_template | sed "s/{tmin}/$tmin/" | sed "s/{tmax}/$tmax/" | sed "s/{file}/$file/")
        
        # Execute the command
        echo "Executing: $command"
        eval $command
        
        # Move the output file to the correct directory with the correct name
        mv out.nc "${outdir}/${output_file}"
    done
done
