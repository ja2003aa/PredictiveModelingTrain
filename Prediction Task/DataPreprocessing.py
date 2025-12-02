import pandas as pd
import glob


# Load the CSV file
combined_df = pd.read_csv('Data/LIVST_NRCH_OD_a51_2017/LIVST_NRCH_OD_a51_2017_09_09.csv')



# Assuming 'data' is your main directory and it contains subdirectories named by year
# Adjust the path according to where your 'data' directory is located in your system
base_path = './Data'  # Replace with the correct path to the 'data' directory

# Generate a list of all CSV file paths from 2017 to 2022
csv_files = glob.glob(f'{base_path}/*/*.csv')

# Read each CSV file into a DataFrame
dataframes_list = [pd.read_csv(file) for file in csv_files]

# Concatenate all the DataFrames into one single DataFrame
combined_combined_df = pd.concat(dataframes_list, ignore_index=True)

df_filtered = combined_combined_df[combined_combined_df['is_passing_station'] != True]






print(df_filtered)
# Ensure 'rid' is a string
combined_combined_df['rid'] = combined_combined_df['rid'].astype(str)

# Extract the date from 'rid' (first 8 characters) and convert it to datetime format
combined_combined_df['date'] = pd.to_datetime(combined_combined_df['rid'].str[:8], format='%Y%m%d')

# Determine the day of the week (Monday=0, Sunday=6)
combined_combined_df['day_of_week'] = combined_combined_df['date'].dt.dayofweek

# Classify as 'Weekday' or 'Weekend' based on the day of the week
combined_combined_df['weekday_or_weekend'] = combined_combined_df['day_of_week'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')

import numpy as np
combined_combined_df.drop(['cr_code', 'lr_code', 'pta', 'ptd'], axis=1, inplace=True)
print(combined_combined_df.columns)
combined_df.replace({"": np.nan, " ": np.nan, "some_placeholder": np.nan}, inplace=True)

# Assuming combined_combined_df is your dataframe

# Departure and Arrival Classification based on station name
combined_combined_df['is_departure_station'] = (combined_combined_df['tpl'] == 'LIVST')
combined_combined_df['is_arrival_station'] = (combined_combined_df['tpl'] == 'NRCH')

# Adjusting logic for Passing Station to avoid misclassification
# A station is classified as passing only if it is not a departure or an arrival station and has passing info
combined_combined_df['is_passing_station'] = (
    ~combined_combined_df['is_departure_station'] &
    ~combined_combined_df['is_arrival_station'] &
    (~combined_combined_df['wtp'].isna() | ~combined_combined_df['pass_at'].isna() | ~combined_combined_df['pass_et'].isna())
)

# Stopping Station Classification
# A station is a stopping station if it is not a departure, arrival, or passing station and has departure information (wtd, dep_at, dep_et)
combined_combined_df['is_stopping_station'] = (
    ~combined_combined_df['is_departure_station'] &
    ~combined_combined_df['is_arrival_station'] &
    ~combined_combined_df['is_passing_station'] &
    (~combined_combined_df['wtd'].isna() | ~combined_combined_df['dep_at'].isna() | ~combined_combined_df['dep_et'].isna())

)
print(combined_combined_df['wtp'].head())


#print(combined_combined_df[['tpl','is_departure_station','is_arrival_station','is_passing_station','is_stopping_station']].head())
"""
# The departure delay is the difference between the actual or estimated departure time
combined_combined_df['date'] = pd.to_datetime(combined_combined_df['date'], errors='coerce')
combined_combined_df['dep_at'] = pd.to_datetime(combined_combined_df['date'].dt.strftime('%Y-%m-%d') + ' ' + combined_combined_df['dep_at'], errors='coerce', format='%Y-%m-%d %H:%M')
combined_combined_df['dep_et'] = pd.to_datetime(combined_combined_df['date'].dt.strftime('%Y-%m-%d') + ' ' + combined_combined_df['dep_et'], errors='coerce', format='%Y-%m-%d %H:%M')
combined_combined_df['wtd'] = pd.to_datetime(combined_combined_df['date'].dt.strftime('%Y-%m-%d') + ' ' + combined_combined_df['wtd'], errors='coerce', format='%Y-%m-%d %H:%M')
"""
"""
def normalize_time_format(time_str):
    if pd.isnull(time_str):
        return np.nan
    parts = time_str.split(':')
    if len(parts) == 2:  # Format is HH:MM
        return f"{parts[0]}:{parts[1]}:00"  # Append seconds
    return time_str  # Return HH:MM:SS as is


# Normalize time format and convert to datetime objects
combined_combined_df['normalized_wtp'] = combined_combined_df['wtp'].apply(normalize_time_format)
combined_combined_df['normalized_pass_at'] = combined_combined_df['pass_at'].apply(normalize_time_format)
combined_combined_df['normalized_pass_et'] = combined_combined_df['pass_et'].apply(normalize_time_format)
combined_combined_df['normalized_wtd'] = combined_combined_df['wtd'].apply(normalize_time_format)
combined_combined_df['normalized_dep_at'] = combined_combined_df['dep_at'].apply(normalize_time_format)
combined_combined_df['normalized_dep_et'] = combined_combined_df['dep_et'].apply(normalize_time_format)
combined_combined_df['normalized_wta'] = combined_combined_df['wta'].apply(normalize_time_format)
combined_combined_df['normalized_arr_at'] = combined_combined_df['arr_at'].apply(normalize_time_format)
combined_combined_df['normalized_arr_et'] = combined_combined_df['arr_et'].apply(normalize_time_format)


# Assuming you've correctly normalized the times, now convert them to datetime objects
combined_combined_df['normalized_wtp'] = pd.to_datetime(combined_combined_df['normalized_wtp'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_pass_at'] = pd.to_datetime(combined_combined_df['normalized_pass_at'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_pass_et'] = pd.to_datetime(combined_combined_df['normalized_pass_et'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_wtd'] = pd.to_datetime(combined_combined_df['normalized_wtd'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_dep_at'] = pd.to_datetime(combined_combined_df['normalized_dep_at'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_dep_et'] = pd.to_datetime(combined_combined_df['normalized_dep_et'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_wta'] = pd.to_datetime(combined_combined_df['normalized_wta'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_arr_at'] = pd.to_datetime(combined_combined_df['normalized_arr_at'], format='%H:%M:%S', errors='coerce')
combined_combined_df['normalized_arr_et'] = pd.to_datetime(combined_combined_df['normalized_arr_et'], format='%H:%M:%S', errors='coerce')
"""
def normalize_time_format_without_seconds(time_str):
    """
    Normalize time string to HH:MM format, removing seconds if present.
    """
    if pd.isnull(time_str):
        return np.nan
    parts = time_str.split(':')
    # Return HH:MM format whether original was HH:MM or HH:MM:SS
    return f"{parts[0]}:{parts[1]}"

# Apply normalization function to each column
columns_to_normalize = ['wtp', 'pass_at', 'pass_et', 'wtd', 'dep_at', 'dep_et', 'wta', 'arr_at', 'arr_et']
for col in columns_to_normalize:
    combined_combined_df[col] = combined_combined_df[col].apply(normalize_time_format_without_seconds)

# Convert normalized time strings to datetime objects, specifying only hour and minute in the format
for col in columns_to_normalize:
    combined_combined_df[col] = pd.to_datetime(combined_combined_df[col], format='%H:%M', errors='coerce')


# Use 'dep_at' if available; otherwise, use 'dep_et' for departure time
combined_combined_df['used_dep_time'] = combined_combined_df['dep_at'].combine_first(combined_combined_df['dep_et'])
combined_combined_df['departure_delay'] = (combined_combined_df['used_dep_time'] - combined_combined_df['wtd']).dt.total_seconds() / 60

combined_combined_df['used_arr_time'] = combined_combined_df['arr_at'].combine_first(combined_combined_df['arr_et'])
combined_combined_df['arrival_delay'] = (combined_combined_df['used_arr_time'] - combined_combined_df['wta']).dt.total_seconds() / 60

combined_combined_df['used_pass_time'] = combined_combined_df['pass_at'].combine_first(combined_combined_df['pass_et'])
combined_combined_df['passing_delay'] = (combined_combined_df['used_pass_time'] - combined_combined_df['wtp']).dt.total_seconds() / 60

print(combined_combined_df[['departure_delay','arrival_delay','passing_delay']])

from datetime import datetime, time


def classify_peak_offpeak(row):
    # Check if time information is missing or NaT
    if pd.isnull(row['wtd']):
        return None

    # Ensure the time comparison is only done if wtd is not NaT
    time_to_check = row['wtd'].time()

    # Check for weekdays
    if row['weekday_or_weekend'] == 'Weekday':
        if ((time_to_check >= time(6, 30)) and (time_to_check <= time(9, 30))) or \
                ((time_to_check >= time(16, 30)) and (time_to_check <= time(19, 0))):
            return 'Peak'
        else:
            return 'Off-Peak'
    else:  # For weekends or any other case not explicitly defined as 'Weekday'
        return 'Off-Peak'
combined_combined_df['peak_offpeak'] = combined_combined_df.apply(classify_peak_offpeak, axis=1)

combined_combined_df.loc[(combined_combined_df['is_arrival_station'] == True) & (combined_combined_df['arr_at'].isna()), 'arr_at'] = combined_combined_df['arr_et']

# Impute missing 'dep_at' with 'dep_et' if 'is_departure_station' is True
combined_combined_df.loc[(combined_combined_df['is_departure_station'] == True) & (combined_combined_df['dep_at'].isna()), 'dep_at'] = combined_combined_df['dep_et']

# Impute missing 'pass_at' with 'pass_et' if 'is_passing_station' is True
combined_combined_df.loc[(combined_combined_df['is_passing_station'] == True) & (combined_combined_df['pass_at'].isna()), 'pass_at'] = combined_combined_df['pass_et']
combined_combined_df.loc[(combined_combined_df['is_stopping_station'] == True) & (combined_combined_df['arr_at'].isna()), 'arr_at'] = combined_combined_df['arr_et']
combined_combined_df.loc[(combined_combined_df['is_stopping_station'] == True) & (combined_combined_df['dep_at'].isna()), 'dep_at'] = combined_combined_df['dep_et']
df_backup = combined_combined_df.copy()


# Check for rows where 'arr_at' is not null but 'wta' is null
missing_wta = combined_combined_df[(combined_combined_df['arr_at'].notna()) & (combined_combined_df['wta'].isna())]

print("Number of instances where 'arr_at' is present but 'wta' is missing:", len(missing_wta))


# Example to check for missing values in the necessary columns for stopping stations
print("HERE ARE THE MISSING VALUES FOR STOPPIN STATIONS")
missing_info_df = combined_combined_df[
    (combined_combined_df['is_stopping_station'] == True) &
    ((combined_combined_df['arr_at'].isna()) | (combined_combined_df['dep_at'].isna()))
]
print(missing_info_df[['rid','tpl', 'wta', 'wtd', 'arr_at', 'dep_at']])

combined_combined_df.drop(['arr_at','arr_et', 'dep_et', 'pass_et',  'arr_wet', 'arr_atRemoved', 'pass_wet', 'pass_atRemoved', 'dep_wet', 'dep_atRemoved', 'used_dep_time','used_arr_time','used_pass_time'], axis=1, inplace=True)






