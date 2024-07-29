# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 21:37:43 2023

@author: Siyanda Hlathi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

plt.rcParams.update({'font.size': 70})

# Define the months you want to plot
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',"JUL",'AUG','SEP', 'OCT', 'NOV', 'DEC']

# Create subplots
fig, axes = plt.subplots(nrows=len(months), figsize=(36, 8 * len(months)), gridspec_kw={'hspace': 0.0})

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

    hour = np.array(hours)
    minute = np.array(minutes)
    second = np.array(seconds)
    gate = np.array(gates)
    power = np.array(powers)
    velocity = np.array(velocities)
    spec_width = np.array(spec_widths)
    date_ary = np.array(dates)
    beam = np.array(beams)

    data = {
        'Hour': hour,
        'Power': power,
        'Velocity': velocity,
        'Spectral_width': spec_width,
        'rgate': gate,
        'date': date_ary,
        'beam': beam
    }

    df = pd.DataFrame(data)

    df = df[df['beam'] != 7]
    df = df[df['rgate'].isin([0, 1, 2, 3, 4])]

    tolerance = 1e-6

    df['Power'] = df['Power'].astype(float)

    df = df[df['Power'].abs() > tolerance]

    unique_dates = np.unique(date_ary)
    num_unique_dates = len(unique_dates)

    hdf = df.groupby(['Hour', 'rgate'])['Power'].transform(lambda x: (x != 0).sum().mean())

    df['Normalized_Occurrence'] = hdf / num_unique_dates
    rg = df['rgate']
    rgin = rg.astype(int)
    df['range gate'] = rgin

    t = df['Hour']
    time = t.astype(int)
    df['time'] = time

    pivot_df = df.pivot_table(index='range gate', columns='time', values='Normalized_Occurrence', aggfunc='mean')

    pivot_df = pivot_df.iloc[::-1]

    month_max = pivot_df.max().max()

    ax = sns.heatmap(pivot_df, cmap='YlGnBu', cbar=False, ax=axes[idx], vmax=month_max)

    # Create a separate color bar for each subplot
    cbar = ax.figure.colorbar(ax.collections[0], ax=ax, pad=0.01)
    cbar.set_label("Normalized \n Occurrence", fontsize=60)

    if idx != len(months) - 1:
        ax.set_xticks([])
        ax.set_xlabel('')
    else:
        ax.set_xlabel('Time (UT)', fontsize=60)
        ax.set_xticks(np.arange(0, 24, 3))  # Adjust the ticks on x-axis
        ax.set_xticklabels(np.arange(0, 24, 3), fontsize=60, rotation=0)  # Rotate x-tick labels
        ax.set_ylabel('Range Gates', fontsize=60)
       # ax.text(1.01, 0.5, f'{num_unique_dates} days', transform=ax.transAxes,
        #        fontsize=60, verticalalignment='center', rotation=90)
"""
    ax.text(1.01, 0.5, f'{num_unique_dates} days', transform=ax.transAxes,
            fontsize=60, verticalalignment='center', rotation=90)

    # Draw a horizontal line to separate plots (except after the last one)
    if idx < len(months) - 1:
        divider = axes[idx].get_position().bounds[1] + axes[idx].get_position().bounds[3]
        fig.add_artist(plt.Line2D([0, 1], [divider, divider], color='black', linewidth=2, transform=fig.transFigure, clip_on=False))
"""
plt.tight_layout()
plt.savefig('normalized_occurrence.png', dpi=300)
plt.show()