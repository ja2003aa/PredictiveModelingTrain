import pandas as pd
import glob


# Load the CSV file
combined_Data = pd.read_csv('Data/LIVST_NRCH_OD_a51_2017/LIVST_NRCH_OD_a51_2017_09_09.csv')



# Assuming 'data' is your main directory and it contains subdirectories named by year
# Adjust the path according to where your 'data' directory is located in your system
base_path = './Data'  # Replace with the correct path to the 'data' directory

# Generate a list of all CSV file paths from 2017 to 2022
csv_files = glob.glob(f'{base_path}/*/*.csv')

# Read each CSV file into a DataFrame
dataframes_list = [pd.read_csv(file) for file in csv_files]

# Concatenate all the DataFrames into one single DataFrame
Data = pd.concat(dataframes_list, ignore_index=True)


Data = Data.drop(['pta', 'ptd', 'arr_atRemoved','pass_atRemoved','dep_atRemoved','cr_code','lr_code'], axis=1)

Data['is_departure_station'] = (Data['tpl'] == 'LIVST')
Data['is_arrival_station'] = (Data['tpl'] == 'NRCH')

# Adjusting logic for Passing Station to avoid misclassification
# A station is classified as passing only if it is not a departure or an arrival station and has passing info
Data['is_passing_station'] = (
    ~Data['is_departure_station'] &
    ~Data['is_arrival_station'] &
    (~Data['wtp'].isna() | ~Data['pass_at'].isna() | ~Data['pass_et'].isna())
)

Data['is_stopping_station'] = (
    ~Data['is_departure_station'] &
    ~Data['is_arrival_station'] &
    ~Data['is_passing_station'] &
    (~Data['wtd'].isna() | ~Data['dep_at'].isna() | ~Data['dep_et'].isna()))

Data = Data[Data['is_passing_station'] == False]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Adding neccessary data :
# - Day of the week
# - hour of the data
# - time of the year i.e month
# - peak/off_peak
# - arrival delay
# - depaure dealy

Data['rid'] = Data['rid'].astype(str)


Data['date'] = pd.to_datetime(Data['rid'].str[:8], format='%Y%m%d')


Data['day_of_week'] = Data['date'].dt.dayofweek


Data['month'] = Data['date'].dt.month
Data['arr_at'] = Data['arr_at'].fillna(Data['arr_et']).fillna(Data['arr_wet'])


Data['dep_at'] = Data['dep_at'].fillna(Data['dep_et']).fillna(Data['dep_wet'])


Data['arrival_time_of_day'] = pd.to_datetime(Data['arr_at'], format='%H:%M').dt.hour
Data['departure_time_of_day'] = pd.to_datetime(Data['dep_at'], format='%H:%M').dt.hour


def parse_time(t):
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return pd.to_datetime(t, format=fmt)
        except ValueError:
            pass
    return pd.NaT


Data['wta'] = Data['wta'].apply(parse_time)
Data['arr_at'] = Data['arr_at'].apply(parse_time)
Data['arr_et'] = Data['arr_et'].apply(parse_time)
Data['wtd'] = Data['wtd'].apply(parse_time)
Data['dep_at'] = Data['dep_at'].apply(parse_time)
Data['dep_et'] = Data['dep_et'].apply(parse_time)


Data['arrival_delay'] = (Data['wta'] - Data['arr_at']).dt.total_seconds() / 60
Data['departure_delay'] = (Data['wtd'] - Data['dep_at']).dt.total_seconds() / 60

station_pairs = []
time_of_day = []
day_of_week = []
month = []
dep_delay = []
arrival_delay = []
arrival_time = []
route_ids = []  # List to store the route IDs

for rid, group in Data.groupby('rid'):
    stations = group['tpl'].tolist()
    pairs = [(stations[i], stations[i + 1]) for i in range(len(stations) - 1)]

    # Extend the list of pairs and other attributes
    station_pairs.extend(pairs)
    time_of_day.extend(group['departure_time_of_day'].iloc[:-1])
    day_of_week.extend(group['day_of_week'].iloc[:-1])
    month.extend(group['month'].iloc[:-1])
    dep_delay.extend(group['departure_delay'].iloc[:-1])
    arrival_delay.extend(group['arrival_delay'].iloc[1:])
    arrival_time.extend(group['arr_at'].iloc[1:])
    route_ids.extend([rid] * (len(stations) - 1))  # Add the route ID for each pair

# Create a DataFrame from the lists
pair_data = pd.DataFrame(station_pairs, columns=['Station_A', 'Station_B'])
pair_data['rid'] = route_ids  # Add the route IDs to the DataFrame
pair_data['departure_time_of_day'] = time_of_day
pair_data['day_of_week'] = day_of_week
pair_data['month'] = month
pair_data['departure_delay'] = dep_delay
pair_data['arrival_delay'] = arrival_delay
pair_data['arr_at'] = arrival_time

print(pair_data)





pair_data.to_csv('pair_data.csv', index=False)