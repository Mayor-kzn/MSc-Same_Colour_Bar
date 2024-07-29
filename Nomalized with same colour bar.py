# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 22:40:51 2023

@author: Siyanda Hlathi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import seaborn as sns

plt.rcParams.update({'font.size': 60})

#months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',"JUL",'AUG','SEP', 'OCT', 'NOV', 'DEC']
#months = ['JAN', 'FEB']
#months = ['January', 'February', 'March', 'April', 'May', 'June','September', 'October', 'November', 'December']
months = ['2012Jan', '2012Feb', '2012Mar', '2012April', '2012May', '2012Jun','2012Jul', '2015Aug' '2012Sep', '2012Oct', '2012Nov', '2012Dec']

fig, axes = plt.subplots(nrows=len(months), figsize=(36, 8 * len(months)), gridspec_kw={'hspace': 0.0})

global_max = 1

for idx, month in enumerate(months):
    hours = []
    minutes = []
    seconds = []
    beams = []
    gates = []
    powers = []
    velocities = []
    spec_widths = []
    dates = []

    file_pattern = fr"C:\Users\shlathi\OneDrive - SANSA\Documents\My Masters Work\siyanda\{month}\*.txt"
    file_paths = glob.glob(file_pattern)

    for file_path in file_paths:
        with open(file_path) as f:
            date_str = None
            lines = f.readlines()
            for line in lines:
                values = line.strip().split(",")
                if len(values) == 5:
                    hour_val = float(values[0])
                    hours.append(hour_val)
                
                    minute_val = float(values[1])
                    minutes.append(minute_val)

                    second_val = float(values[2])
                    seconds.append(second_val)

                    beam_val = float(values[3])
                    beams.append(beam_val)

                    gate_val = float(values[4])
                    gates.append(gate_val)

                if line.startswith('2011') or line.startswith('2012'):
                    year = line[0:4]
                    month = line[4:6]
                    day = line[6:8]
                    date_str = year + "-" + month + "-" + day  # Extract the date once per file

                if len(values) == 3:
                    if values[0]:
                        power_val = float(values[0])
                        powers.append(power_val)
                    if values[1]:
                        velocity_val = float(values[1])
                        velocities.append(velocity_val)
                    if values[2]:
                        spec_width_val = float(values[2])
                        spec_widths.append(spec_width_val)
                        dates.append(date_str)

    # Convert the lists to arrays for further processing
    hour = np.array(hours)
    minute = np.array(minutes)
    second = np.array(seconds)
    gate = np.array(gates)
    power = np.array(powers)
    velocity = np.array(velocities)
    spec_width = np.array(spec_widths)
    date_ary = np.array(dates)
    beam = np.array(beams)

    # Create a data dictionary to construct the DataFrame
    data = {
        'Hour': hour,
        'Power': power,
        'Velocity': velocity,
        'Spectral_width': spec_width,
        'rgate': gate,
        'date': date_ary,
        'beam': beam
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Filter data
    df = df[df['beam'] != 7]
    #df = df[df['beam'] == 15 ]
    df = df[df['rgate'].isin([0, 1, 2, 3, 4])]

    # Define a tolerance value for filtering near-zero values
    tolerance = 1e-6

    # Convert 'Power' column to a floating-point type
    df['Power'] = df['Power'].astype(float)

    # Filter out rows where 'Power' is close to zero
    df = df[df['Power'].abs() > tolerance]

    # Count the number of unique dates
    unique_dates = np.unique(date_ary)
    num_unique_dates = len(unique_dates)
    
    # Group the DataFrame by 'Hour' and 'rgate' columns, count non-zero occurrences
    hdf = df.groupby(['Hour', 'rgate'])['Power'].transform(lambda x: (x != 0).sum().mean())

    # Normalize the 'Power' values based on the number of unique dates
    df['Normalized_Occurrence'] = hdf / num_unique_dates
    rg = df['rgate']
    rgin = rg.astype(int)
    df['rgate'] = rgin

    # Pivot the normalized data for the heatmap
    pivot_df = df.pivot_table(index='rgate', columns='Hour', values='Normalized_Occurrence', aggfunc='mean')
    pivot_df = pivot_df.iloc[::-1]

    # Update the global maximum if the current month's maximum is greater
    month_max = pivot_df.max().max()
    if month_max > global_max:
        global_max = month_max

    ax = sns.heatmap(pivot_df, cmap='YlGnBu', cbar=False, ax=axes[idx], vmax=global_max)

    if idx == len(months) - 1:
        ax.set_xlabel("Time (UT)", fontsize=60)
        ax.set_xticks(np.arange(0, 24, 3))  # Adjust the ticks on x-axis
        ax.set_xticklabels(np.arange(0, 24, 3), fontsize=60, rotation=0)  # Rotate x-tick labels
    else:
        ax.set_xticks([])
        ax.set_xlabel('')

    ax.set_ylabel("Range Gates", fontsize=60)
    ax.text(1.01, 0.5, f'{num_unique_dates} days', transform=ax.transAxes,
            fontsize=60, verticalalignment='center', rotation=90)
    
    # Set y-axis labels to integers
    y_ticks = pivot_df.index.astype(int)
    ax.set_yticks(np.arange(len(y_ticks)))
    ax.set_yticklabels(y_ticks, fontsize=60)

# Create a single vertical color bar for all subplots on the right
cbar_ax = fig.add_axes([0.92, 0.12, 0.01, 0.20])
cbar = plt.colorbar(ax.collections[0], cax=cbar_ax)
cbar.set_label("Normalized Occurrence", fontsize=60)
cbar.ax.tick_params(labelsize=60)

plt.subplots_adjust(left=0.2, bottom=0.12, right=0.85, top=0.95, wspace=0.0, hspace=0.3)
plt.savefig('magnet2975981.png', dpi=600)
plt.show()
