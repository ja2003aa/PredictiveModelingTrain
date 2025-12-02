import csv
import os
from dotenv import load_dotenv

# get env variables
load_dotenv()
stations_csv = os.getenv("STATIONS_CSV_PATH")


# convert station name to crs
def crs_converter(start_loc, end_loc):
    with open(stations_csv, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if start_loc.upper() == row[0]:
                start_loc_crs = row[3]
            if end_loc.upper() == row[0]:
                end_loc_crs = row[3]

    return (start_loc_crs, end_loc_crs)
