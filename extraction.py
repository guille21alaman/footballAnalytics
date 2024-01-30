import pandas as pd
import datetime
from client import *
from logger import *
import os

#setup logger
logging_level = os.getenv("LOG_LEVEL", "INFO")
logger = set_up_logger(logging_level=logging_level)

#class initialization
fotmobLeagues = FotmobLeagues(logger)

# Define leagues and target seasons
leagues = [
    {"id": 87, "name": "laliga"},
    {"id": 47, "name": "premier-league"},
    {"id": 54, "name": "bundesliga"},
    {"id": 55, "name": "serie-a"},
    {"id": 53, "name": "ligue-1"},
    {"id": 57, "name": "eredivisie"},
]

#define how many seasons starting from last one we want to extract
amount_seasons = 5
last_season = "2023/2024"
last_year = int(last_season.split("/")[1])
first_year = last_year - amount_seasons
seasons = []
for year in range(first_year, last_year):
    seasons.append("%s/%s" %(year, year+1))

#or define list of seasons
# seasons = ["2020/2021", "2021/2022"]
    
#define final df
all_matches_df = pd.DataFrame()

for league in leagues:
    for season in seasons:
        start_time = datetime.datetime.now()
        logger.info("Processing... League: %s. Season: %s." %(league["name"],season))
        fotmobLeagues.get_league_fixtures(league["id"], season)
        fotmobLeagues.extract_details()
        fotmobLeagues.extract_matches()
        df = fotmobLeagues.process_dataframe()
        all_matches_df = pd.concat([all_matches_df, df], ignore_index=True)
        end_time = datetime.datetime.now()
        logger.info("League %s. Season %s. Processed. Total time: %s" %(league["name"], season, end_time-start_time))

#debugging info
logger.debug(type(all_matches_df))
logger.debug(all_matches_df.shape)
logger.debug(all_matches_df.isna().sum())

#save data
csv_folder = "data/"
csv_file = csv_folder + "AllMatches.csv"
logger.info("Saving csv file... to %s" %csv_file)
try:
    logger.info("Succesfully saved file")
    all_matches_df.to_csv(csv_file ,sep=";", decimal=",", index=False)
except Exception as e:
    logger.error("Failed to save file into: %s. Error: %s" %(csv_file, e))



