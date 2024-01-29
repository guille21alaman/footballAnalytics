import pandas as pd
import urllib.request
from logger import *

#################
# LOGGER SET-UP #
#################

logging_level = "INFO"
logger = set_up_logger(logging_level=logging_level)

#############
# INGESTION #
#############

#read data
csv_folder = "data/"
csv_file = csv_folder + "AllMatches.csv"
df = pd.read_csv(csv_file, sep=";", decimal=",")
missing_raw = df.isna().sum()

########################
# MISSING, DTYPES, ETC #
########################

#relevant info
logger.debug(f"Raw shape: {df.shape}")
logger.debug(f"Dtypes raw:{df.dtypes}")
logger.debug(f"Missing raw:{missing_raw[missing_raw>0]}")

#transform date to datetime
df["date"] = pd.to_datetime(df["date"])
logger.info(f"Matches from {df['date'].min()} to {df['date'].max()}")

#rename "name" column to league_name
df = df.rename(columns={"name":"league_name"})

#transform objects to float
to_transform = ["expected_goals", "score"]
for t in to_transform:
    for p in ["home","away"]:
        df[f"{p}_{t}"] = df[f"{p}_{t}"].astype(float)

#transform percentage 
for p in ["home", "away"]:
    df[f"{p}_accurate_passes_percentage"] = df[f"{p}_accurate_passes"].str.replace("%","").astype(float)
    df = df.drop([f"{p}_accurate_passes"],axis=1)

logger.debug(f"Dtypes transformed:{df.dtypes}")

#remove irrelevant missing values
df = df.dropna(subset=["home_expected_goals"], axis=0) #identified entry with some missing info (not relevant)
df = df.dropna(subset=["home_score","away_score"], axis=0) #remove rows if result not available
if "home_ShotsOffTarget" in df.columns:
    df = df.drop(["home_ShotsOffTarget","away_ShotsOffTarget","home_Offsides","away_Offsides"], axis=1) #some columns only exist for that problematic entry, remove them

logger.debug(f"Shape after dealing with missing values: {df.shape}")

###################
# PROCESSING DATA #
###################

#save logo of each team
for team_id in df["home_team_id"].unique():
    image_url = f'https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}_small.png' #the image on the web
    save_name = 'fotmob-dashboard/logo/' + f"{team_id}_small.png" #local name to be saved
    urllib.request.urlretrieve(image_url, save_name)

#one row per game per team (i.e., 2 rows per game)
#each row contains info about the match of that specific team (did it win? did it play home?)

#teams in the database
teams = df["away_team"].unique()
df_game_per_team = pd.DataFrame()


for team in teams:
    logger.info(f"Team being processed: {team}" )
    games_team_raw = df[
                (df["away_team"] == team)
                | (df["home_team"] == team)
            ]

    #list of columns with stats to be unfolded
    cols = [col for col in games_team_raw.columns if "home" in col or "away" in col]

    #loop over rows of a team
    for index, row in games_team_raw.iterrows():
        if row["home_team"] == team:
            home_or_away = "home"
            rival_home_or_away = "away"
        else: 
            home_or_away = "away"
            rival_home_or_away = "home"

        #add where they played
        row["played"] = home_or_away

        #collect stats
        for s in cols:
            if home_or_away in s:
                row[s.replace("%s_" %home_or_away, "")] = row[s]
            else:
                row[s.replace("%s_" %rival_home_or_away, "rival_")] = row[s]

        #set won, lost or tied (outcome)
        if row["%s_score" %home_or_away] > row["%s_score" %rival_home_or_away]:
            row["outcome"] = "W"
        elif row["%s_score" %home_or_away] < row["%s_score" %rival_home_or_away]:
            row["outcome"] = "L"
        else: 
            row["outcome"] = "Tie"
        
        #drop not needed columns
        row  = row.drop(cols)

        #append row to generic dataframe with all teams
        df_game_per_team = df_game_per_team._append(row, ignore_index=True)

logger.debug(f"Clean shape: {df_game_per_team.shape}")
logger.debug(f"Dtypes clean:{df_game_per_team.dtypes}")


csv_folder = "data/"
csv_file = csv_folder + "AllMatches.csv"
df_game_per_team.to_csv(csv_file, sep=";", decimal=",", index=False)