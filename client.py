import pandas as pd
from logging import getLevelName, getLogger
import requests
import re
from typing import Tuple, List, Dict, Union, Optional
from requests.exceptions import RequestException
from mobfot import MobFot


class FotmobLeagues: 
   
    def __init__(self, logger) -> None:

         # Where we are going to get the data from
        self.BASE_URL = "https://www.fotmob.com/api"
        self.SESSION = requests.Session()
        self.LOGGER = logger 
        self.leagues_url = f"{self.BASE_URL}/leagues"

    def get_league_fixtures(self, league_id: int, season: str):
        """
        Fetch league details and matches from the Fotmob API.

        Args:
            league_id: ID of the league to fetch.
            season: The target season in the format 'YYYY/YYYY'.

        Returns:
            League details and matches data if successful, (None, None) otherwise.
        """
        
        #check if season format is correct
        pattern = re.compile(r'^\d{4}/\d{4}$')
        if pattern.match(season):
            if (int(season.split("/")[0])+1 == int(season.split("/")[1])):
                params = {"id": league_id, "season": season}
            else: 
                raise ValueError("Seasons should be consecutive (i.e., 2019/2020). Not: %s" %season)
        else:
            raise ValueError("Season should be of format YYYY/YYYY. Not: %s" %season)
        try:
            response = self.SESSION.get(self.leagues_url, params=params)
            response.raise_for_status()
            data = response.json()
            self.details, self.matches = data["details"], data["matches"]["allMatches"]
            return self.LOGGER.debug("Successfully stored details and matches in self.matches, self.details")
        except RequestException as e:
            self.LOGGER.error(
                f"An error occurred while fetching data for league ID {league_id}: {e}"
            )
            return None, None
    
    def extract_details(self):
        """
            Extracts a dictionary with some relevant details from the league

            Input: details json extracted from the API (data["details"])
            Output: self.details_dict = dictionary with selected details (can be edited according to needs)
            
        """
        self.details_dict =  {
            "country": self.details["country"],
            "name": self.details["name"],
            "season": self.details["selectedSeason"],
            "type": self.details["type"],
        }
        return self.LOGGER.debug("Successfully extracted generic league details into self.details_dict")

    def extract_matches(self):
        """
            Extracts a dictionary with some relevant match data for every match provided in matches

            Input: matches list json extracted from the API (data["matches"]["AllMatches"]])
            Output: dataframe with relevant information about matches (can be edited acordding to needs)
            
        """

        self.matches_dict =  [
            {
                "match_id": match.get("id"), 
                "page_url": match.get("pageUrl"),
                "round": match.get("round"),
                "date": match.get("status", {}).get("utcTime"),
                "away_team": match.get("away", {}).get("name"),
                "home_team": match.get("home", {}).get("name"),
                "cancelled": match.get("status", {}).get("cancelled"),
                "finished": match.get("status", {}).get("finished"),
                "result": match.get("status", {}).get("scoreStr"),
            }
            for match in self.matches # Loop through every match and get this data
        ]
        self.matches_df = pd.DataFrame(self.matches_dict)
        return self.LOGGER.debug("Successfully extracted matches information and transformed self.matches list into self.matches_dict")

    def process_dataframe(self):

        """
        Adds league details to dataframe
        Maps country codes to full names, splits the result column,
        and removes other unnecessary columns (can be edited according to needs).

        Input: self.matches_df (pd.DataFrame): The DataFrame containing the fetched macthes data.
        Output: pd.DataFrame: The processed DataFrame.
        """

        # Splitting result column into home and away scores
        self.matches_df[["home_score", "away_score"]] = self.matches_df["result"].str.split(" - ", expand=True)
        self.matches_df.drop(columns=["result"], inplace=True)

        #add league details 
        self.matches_df = self.matches_df.assign(**self.details_dict)

        # Mapping country codes to full names
        country_map = {
            "ESP": "Spain",
            "ENG": "England",
            "GER": "Germany",
            "ITA": "Italy",
            "FRA": "France",
            "NED": "Netherlands",
        }
        self.matches_df["country"] = self.matches_df["country"].map(country_map)

        return self.matches_df