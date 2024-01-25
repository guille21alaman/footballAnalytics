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
        self.matches_url = f"{self.BASE_URL}/matchDetails"

    def get_match_fixtures(self, match_id: int):
        """
            Fetch match details from FOTMOB API

            Input: match_id; identifier of a match
            Output: json data with match details

        """
        try:
            params = {"matchId": match_id}
            response = self.SESSION.get(self.matches_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except RequestException as e:
            self.LOGGER.error(
                f"An error occurred while fetching data for match {match_id}: {e}"
            )
            return None, None

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
        self.matches_list = []
        # Loop through every match and get this data
        for match in self.matches:
            match_dict = {}
            
        
           #append generic data
            match_dict["match_id"] =  match.get("id") 
            match_dict["page_url"] =  match.get("pageUrl")
            match_dict["round"] =  match.get("round")
            match_dict["date"] =  match.get("status", {}).get("utcTime")
            match_dict["home_team"] =  match.get("home", {}).get("name")
            match_dict["away_team"] =  match.get("away", {}).get("name")
            match_dict["cancelled"] =  match.get("status", {}).get("cancelled")
            match_dict["finished"] =  match.get("status", {}).get("finished")
            match_dict["result"] =  match.get("status", {}).get("scoreStr")
            
            #additional stats if match finished
            if match_dict["finished"] == True:
                match_details = self.get_match_fixtures(match.get("id"))
                #red cards
                match_dict["home_red_cards"] =  len(match_details.get("header", {}).get("status", {}).get("homeRedCards"))
                match_dict["away_red_cards"] =  len(match_details.get("header", {}).get("status", {}).get("awayRedCards"))
                #top stats
                match_stats = match_details.get("content", {}).get("stats", {}).get("Periods", {}).get("All", {}).get("stats")[0].get("stats")
                #loop over available stats and append (if match is finished)
                for stat in match_stats:
                    #if accurate passes keep only percentage
                    if "accurate_passes" in stat["key"]:
                        stat["stats"][0] = stat["stats"][0].split(" ")[1].replace("(","").replace("%)", "%")
                        stat["stats"][1] = stat["stats"][1].split(" ")[1].replace("(","").replace("%)", "%")
                    match_dict["home_%s" %stat["key"]] = stat["stats"][0]
                    match_dict["away_%s" %stat["key"]] = stat["stats"][1]
            else:
                continue
            
            #append dict to list that will be used to create de data frame later on
            self.matches_list.append(match_dict)
        
        #debug logs
        self.LOGGER.debug("Type of self.matches_list", type(self.matches_list))
        self.LOGGER.debug("Length of self.matches_list", len(self.matches_list))

        self.matches_df = pd.DataFrame(self.matches_list)
        return self.LOGGER.debug("Successfully extracted matches information and transformed self.matches list intoself.matches_list")

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
        # self.matches_df.drop(columns=["result"], inplace=True)

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