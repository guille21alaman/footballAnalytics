import pandas as pd
import logging
import sys
from client import *
from helpers import *

#setup logger
logger = logging.getLogger()
logging_level = "INFO"
set_logging_level(logger, logging_level)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                              '%m-%d-%Y %H:%M:%S')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

fotmobLeagues = FotmobLeagues(logger)

# fotmobLeagues.get_league_fixtures(87, "2023/2024")
# fotmobLeagues.extract_details()
# fotmobLeagues.extract_matches()
# df = fotmobLeagues.process_dataframe()

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
amount_seasons = 10 
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
    logger.info("Processing... League: %s. Seasons: %s." %(league["name"],seasons))
    for season in seasons:
        fotmobLeagues.get_league_fixtures(league["id"], season)
        fotmobLeagues.extract_details()
        fotmobLeagues.extract_matches()
        df = fotmobLeagues.process_dataframe()
        all_matches_df = pd.concat([all_matches_df, df], ignore_index=True)

#debugging info
logger.debug(type(all_matches_df))
logger.debug(all_matches_df.shape)
logger.debug(all_matches_df.isna().sum())

#save data
csv_file = "test.csv"
logger.info("Saving csv file... to %s" %csv_file)
try:
    logger.info("Succesfully saved file")
    all_matches_df.to_csv(csv_file ,sep=";", decimal=",", index=False)
except Exception as e:
    logger.error("Failed to save file into: %s. Error: %s" %(csv_file, e))



