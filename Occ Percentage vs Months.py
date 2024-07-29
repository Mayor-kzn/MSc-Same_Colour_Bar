# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 11:24:00 2024

@author: shlathi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import seaborn as sns

# List of months
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# DataFrame to store the percentage of occurrences for each month and range gate
percentage_df = pd.DataFrame()

# Iterate through each month and calculate the percentage of occurrences for each range gate
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
                    month_str = line[4:6]
                    day = line[6:8]
                    date_str = year + "-" + month_str + "-" + day

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

    # Calculate the percentage of occurrences for each range gate
    gate_counts = df['rgate'].value_counts(normalize=True) * 100
    gate_counts = gate_counts.sort_index()
    percentage_df[month] = gate_counts

# Plotting the line graph
plt.figure(figsize=(18, 10))
for rgate in percentage_df.index:
    plt.plot(months, percentage_df.loc[rgate], marker='o', label=f'Range Gate {rgate}')

plt.xlabel('Months', fontsize=20)
plt.ylabel('Percentage of Occurrences', fontsize=20)
plt.title('Percentage of Occurrences in Each Range Gate for Different Months', fontsize=24)
plt.legend(fontsize= 20, loc='upper right')
plt.grid(True)
plt.xticks(rotation=45, fontsize=20)
plt.yticks(fontsize=20)
plt.tight_layout()
plt.savefig('range_gates_percentage.png', dpi=300)
plt.show()