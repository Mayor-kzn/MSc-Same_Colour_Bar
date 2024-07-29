# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 14:10:11 2023

@author: Siyanda Hlathi
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
from datetime import datetime
import pytz
from scipy.stats import pearsonr

# Set font size for the plot
plt.rcParams.update({'font.size': 19})

# Read the CSV file containing meteor occurrence data
df2 = pd.read_csv('Rothera_Hourly_Counts_2011_2012.csv') 

# Convert 'datetime' column to datetime-like values
df2['local_datetime'] = pd.to_datetime(df2['datetime'])


# Convert UTC time to local time (Antarctica/Rothera)
#local_time_zone = pytz.timezone('Antarctica/Rothera')
#df2['local_datetime'] = df2['datetime'].dt.tz_localize('UTC').dt.tz_convert(local_time_zone)

# Define the months you want to analyze
months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL' 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'] 
#months = ['DEC']

# Initialize lists to store data for all months
all_hours = []
all_gates = []
all_powers = []
all_dates = []
all_beams = []

# Loop through the specified months
for month in months:
    # Initialize lists to store data for each month
    hours = []
    gates = []
    powers = []
    dates = []
    beams = []

    # Define the file pattern for the data files
    file_pattern = fr"C:\Users\shlathi\OneDrive - SANSA\Documents\My Masters Work\siyanda\{month}\*.txt"
    file_paths = glob.glob(file_pattern)

    # Loop through the data files
    for file_path in file_paths:
        with open(file_path) as f:
            date_str = None
            lines = f.readlines()
            for line in lines:
                values = line.strip().split(",")
                if len(values) == 5:
                    hour_val = float(values[0])
                    hours.append(hour_val)

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
                    if values[2]:
                        beam_val = float(values[2])
                        beams.append(beam_val)
                        dates.append(date_str)

    # Extend the lists for all months
    all_hours.extend(hours)
    all_gates.extend(gates)
    all_powers.extend(powers)
    all_dates.extend(dates)
    all_beams.extend(beams)

# Create a DataFrame for all months
data = {
    'Hour': all_hours,
    'Power': all_powers,
    'rgate': all_gates,
    'date': all_dates,
    'beam': all_beams
}
df = pd.DataFrame(data)

# Filter the DataFrame
df = df[df['beam'] != 7]
df = df[df['rgate'].isin([0, 1, 2, 3, 4])]

# Define a tolerance value for filtering near-zero values
tolerance = 1e-6

# Convert 'Power' column to a floating-point type
df['Power'] = df['Power'].astype(float)

# Filter out rows where 'Power' is close to zero
df = df[df['Power'].abs() > tolerance]

# Calculate the count of non-zero Power values for each group
df['NonZeroPowerCount'] = df.groupby(['Hour', 'rgate'])['Power'].transform(lambda x: (x != 0).sum())

# Pivot the DataFrame to prepare it for plotting
pivot_df = (df.pivot_table(index='Hour', columns='rgate', values='NonZeroPowerCount', aggfunc='sum'))/10000000000

# Create a figure and axis for plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot the data from the first DataFrame (df) on the primary y-axis
pivot_df.plot(ax=ax1, kind='line', label='NRE Occurrence')

# Set labels and title for the primary y-axis
ax1.set_xlabel("Universal Time ")
ax1.set_ylabel("NRE Occurrence (1e10)")
ax1.set_title("Occurrence vs. Time and Range Gate")

# Create a secondary y-axis for the CSV data
ax2 = ax1.twinx()

# Group by hour and sum the counts for the CSV data
df_grouped = df2.groupby(df2['local_datetime'].dt.hour)['count'].sum().reset_index()
df_grouped['count'] /= 100000            

# Plot the line graph for the CSV data on the secondary y-axis
ax2.plot(df_grouped['local_datetime'], df_grouped['count'], label='Meteor Occurrence Count', linestyle='--')

# Set labels and title for the secondary y-axis
ax2.set_ylabel('Meteor Occurrence (1e5)')

# Calculate the cross-correlation between the two time series
cross_corr = np.correlate(pivot_df.sum(axis=1), df_grouped['count'], mode='full')

# Display the lag values for the cross-correlation
lags = np.arange(-len(pivot_df) + 1, len(df_grouped))
lag_with_max_corr = lags[np.argmax(cross_corr)]
print("Lag with maximum correlation:", lag_with_max_corr)

# Calculate the correlation coefficient between the two time series
corr_coefficient, _ = pearsonr(pivot_df.sum(axis=1), df_grouped['count'])
print("Correlation Coefficient:", corr_coefficient)

# Show legends for both axes
# Adjusting the legend to show integer labels for the range gates
handles, labels = ax1.get_legend_handles_labels()
labels = [str(int(float(label))) for label in labels]
ax1.legend(handles, labels, loc='upper left')


# Show the plot
plt.show()


