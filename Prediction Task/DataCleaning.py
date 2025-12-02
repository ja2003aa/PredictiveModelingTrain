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



combined_combined_df['is_departure_station'] = (combined_combined_df['tpl'] == 'LIVST')
combined_combined_df['is_arrival_station'] = (combined_combined_df['tpl'] == 'NRCH')

# Adjusting logic for Passing Station to avoid misclassification
# A station is classified as passing only if it is not a departure or an arrival station and has passing info
combined_combined_df['is_passing_station'] = (
    ~combined_combined_df['is_departure_station'] &
    ~combined_combined_df['is_arrival_station'] &
    (~combined_combined_df['wtp'].isna() | ~combined_combined_df['pass_at'].isna() | ~combined_combined_df['pass_et'].isna())
)
combined_combined_df['is_stopping_station'] = (
    ~combined_combined_df['is_departure_station'] &
    ~combined_combined_df['is_arrival_station'] &
    ~combined_combined_df['is_passing_station'] &
    (~combined_combined_df['wtd'].isna() | ~combined_combined_df['dep_at'].isna() | ~combined_combined_df['dep_et'].isna())

)

data= combined_combined_df[combined_combined_df['is_passing_station'] != True]
print(data.head(20))

# Verify the DataFrame to see the remaining columns
column_names = combined_combined_df.columns.tolist()
print(column_names)
df_encoded = pd.get_dummies(combined_combined_df, columns=[
    'tpl', 'day_of_week', 'weekday_or_weekend', 'peak_offpeak'
], drop_first=True)  # drop_first=True to avoid dummy variable trap
print(df_encoded.columns)
print(df_encoded.head(3))
grouped =df_encoded.groupby('rid').apply(lambda x: x[['tpl', 'wta', 'wtp', 'wtd', 'pass_at', 'dep_at', 'date',
                                               'day_of_week', 'weekday_or_weekend', 'is_departure_station',
                                               'is_arrival_station', 'is_passing_station', 'is_stopping_station',
                                               'departure_delay', 'arrival_delay', 'passing_delay', 'peak_offpeak']].values.tolist()).tolist()




X = []
y = []

for sequence in grouped:
    # Separate features and labels for each sequence
    sequence_features = [event[:-1] for event in sequence]  # All elements except the last one (assuming last one is 'arrival_delay')
    sequence_labels = [event[-1] for event in sequence]  # The last element of each event (assuming it's 'arrival_delay')
    X.append(sequence_features)
    y.append(sequence_labels)

# At this point, X is a list of sequences with each sequence being a list of events without the arrival_delay
# And y is a list of sequences with each sequence being a list of arrival_delay values for each event

# Now, let's pad the sequences so that they all have the same length
# We'll pad X and y separately since they might have different lengths and you'll pad y only if it's sequential
import tensorflow as tf
X_padded = tf.keras.preprocessing.sequence.pad_sequences(X, padding='post', dtype='float32', value=-1.0)
# If your labels are sequential (e.g., a time series), pad them as well
y_padded = tf.keras.preprocessing.sequence.pad_sequences(y, padding='post', dtype='float32', value=-1.0)
print(X_padded)
"""
journey_
sequences = combined_combined_df.groupby('rid').apply(lambda x: x[
    ['wta', 'wtp', 'wtd', 'arr_et', 'arr_wet', 'arr_atRemoved',
     'pass_et', 'pass_wet', 'pass_atRemoved', 'dep_et', 'dep_wet',
     'dep_atRemoved', 'arr_at', 'pass_at', 'dep_at', 'date', 'day_of_week',
     'weekday_or_weekend', 'is_departure_station', 'is_arrival_station',
     'is_passing_station', 'is_stopping_station', 'used_dep_time', 'departure_delay',
     'used_arr_time', 'arrival_delay', 'used_pass_time', 'passing_delay',
     'peak_offpeak']
].values.tolist())

sequences = journey_sequences.tolist()
"""





"""
print(combined_combined_df[['tpl','wtd','peak_offpeak']])
# Assuming 'combined_combined_df' has a 'date' column in datetime format
combined_combined_df['time_of_month'] = combined_combined_df['date'].dt.day

# Display the first few rows to verify the new column
print(combined_combined_df[['date', 'time_of_month']].head())
#
import matplotlib.pyplot as plt
import seaborn as sns

plt.scatter(combined_combined_df['peak_offpeak'], combined_combined_df['departure_delay'])
plt.title('Scatter Plot of Departure Delays Throughout the Day')
plt.xlabel('Time of Day')
plt.ylabel('Departure Delay (minutes)')
plt.show()
sns.boxplot(x=combined_combined_df['time_of_month'], y=combined_combined_df['departure_delay'])
plt.xlabel('Day of Month')
plt.ylabel('Departure Delay (minutes)')
plt.title('Departure Delays by Day of Month')
plt.xticks(rotation=45)
plt.show()
sns.boxplot(x=combined_combined_df['peak_offpeak'], y=combined_combined_df['departure_delay'])
plt.xlabel('Time of Day')
plt.ylabel('Departure Delay (minutes)')
plt.title('Departure Delays by Time of Day')
plt.show()
combined_combined_df['date'] = pd.to_datetime(combined_combined_df['date'])

# Now, extract the month from the date
combined_combined_df['month'] = combined_combined_df['date'].dt.month

# If you want to plot delays over the month, you'll also need numeric time for plotting
# Let's say you have a 'wtd' column for the planned departure time
# You can convert it to a float representing the hour of the day
combined_combined_df['time_as_float'] = combined_combined_df['wtd'].dt.hour + combined_combined_df['wtd'].dt.minute / 60

# Now, let's create a scatter plot
plt.figure(figsize=(10,6))

# Scatter plot by month
for month in sorted(combined_combined_df['month'].unique()):
    monthly_data = combined_combined_df[combined_combined_df['month'] == month]
    plt.scatter(monthly_data['time_as_float'], monthly_data['departure_delay'], alpha=0.5, label=f'Month {month}')

plt.title('Scatter Plot of Departure Delays over the Day by Month')
plt.xlabel('Time of Day (Hours)')
plt.ylabel('Departure Delay (minutes)')
plt.legend()
plt.show()
"""
"""

# Step 1: Create a representation of each route as a sorted list of stations for each 'rid'
combined_combined_df['station_sequence'] = combined_combined_df.groupby('rid')['tpl'].transform(lambda x: '->'.join(sorted(x.unique())))

# Step 2: Identify unique routes and assign a unique route ID
unique_routes = combined_combined_df['station_sequence'].drop_duplicates().reset_index(drop=True)
route_id_mapping = {route: i for i, route in enumerate(unique_routes, start=1)}

# Step 3: Map the route IDs back to the original DataFrame
combined_combined_df['route_id'] = combined_combined_df['station_sequence'].map(route_id_mapping)

# Display the DataFrame to verify the new 'route_id' column
print(combined_combined_df["route_id"].value_counts())
"""
"""
print(combined_combined_df['wtd'].head())
print(combined_combined_df['dep_at'].head())
print(combined_combined_df['dep_et'].head())

combined_combined_df['wtd'] = pd.to_datetime(combined_combined_df['wtd'])
combined_combined_df['dep_at'] = pd.to_datetime(combined_combined_df['dep_at'])
combined_combined_df['dep_et'] = pd.to_datetime(combined_combined_df['dep_et'])



# Calculating delay
# Use actual departure time if available; otherwise, use estimated departure time
combined_combined_df['used_dep_time'] = combined_combined_df['dep_at'].combine_first(combined_combined_df['dep_et'])

# Calculate delay as the difference between the used departure time and the planned time
# The result will be a timedelta object
combined_combined_df['delay'] = combined_combined_df['used_dep_time'] - combined_combined_df['wtd']

# Convert delay from timedelta to a more readable format (e.g., minutes)
# Negative values indicate the train departed or arrived earlier than planned
combined_combined_df['delay_minutes'] = combined_combined_df['delay'].dt.total_seconds() / 60

#print(combined_combined_df[['wtd', 'dep_at', 'dep_et', 'used_dep_time', 'delay', 'delay_minutes']])
"""
"""
# Use actual arrival time if available; otherwise, use estimated arrival time.
combined_combined_df['used_arr_time'] = combined_combined_df['arr_at'].combine_first(combined_combined_df['arr_et'])

# Calculate arrival delay as the difference between the used arrival time and the planned arrival time (wta).
combined_combined_df['arrival_delay'] = combined_combined_df['used_arr_time'] - combined_combined_df['wta']

# Convert arrival delay from timedelta to a more readable format (e.g., minutes).
# Negative values indicate the train arrived earlier than planned.
combined_combined_df['arrival_delay_minutes'] = combined_combined_df['arrival_delay'].dt.total_seconds() / 60

# Display the relevant columns to verify the calculation.
combined_combined_df[['wta', 'arr_at', 'arr_et', 'used_arr_time', 'arrival_delay', 'arrival_delay_minutes']].head()
"""

"""
# Now pd.isna() can be used to filter rows where 'pta' and 'wtp' are NaN (including originally empty strings or placeholders)
departure_stations_df = combined_combined_df[pd.notna(combined_combined_df['wtd']) &
                                    pd.isna(combined_combined_df['wta']) & pd.isna(combined_combined_df['wtp'])]

num_cases_both_empty = departure_stations_df[(departure_stations_df['dep_et'] == "") &
                                              (departure_stations_df['dep_atRemoved'] == "")].shape[0]

print(f'Number of departure cases where both dep_et and dep_at are null: {num_cases_both_empty}')

provided_dep_et = departure_stations_df[(departure_stations_df['dep_et'].notna()) & (departure_stations_df['dep_et'] != "")]

# Print the cases where 'dep_et' is provided
print(provided_dep_et)
"""


# Now, departure_stations_df contains only the rows for departure stations excluding passing stations
#print(departure_stations_df)


"""
import matplotlib.pyplot as plt

# Replace 'delay' with the name of your delay column
combined_combined_df['delay'].hist(bins=50)
plt.title('Distribution of Train Delays')
plt.xlabel('Delay (minutes)')
plt.ylabel('Frequency')
plt.show()

import seaborn as sns

correlation_matrix = combined_combined_df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix of Features')
plt.show()
"""

