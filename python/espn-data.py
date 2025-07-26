import time
import pickle
import sqlite3

import pandas as pd
from espn_api.football import League

import constants

# Function to pull all historical records 2019-2024
def fetch_api_data(league_id=constants.LEAGUE_ID, espn_s2=constants.ESPN_S2, swid=constants.SWID) -> dict[str, list]:
    '''
    THIS FUNCTION SHOULD ONLY BE RUN ONCE
    -------------------------------------

    Uses the espn-api package to fetch all historical data.
    Compiles every League class into a list.
    Runs .box_scores method for each week in each season.
    Compiles all box scores into a list of lists.

    Creates dict of list(Leagues) and list(box scores)

    Creates/writes pickle file into database folder.

    THIS FUNCTION SHOULD ONLY BE RUN ONCE
    -------------------------------------
    '''

    run = input('WARNING: This function should only be run once. Are you sure you want to run it? [NO]/yes: ')
    if run.lower() != 'yes':
        return

    leagues = []
    matchups = []

    for year in range(2019,2025):
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
        leagues.append(
            {
                'Year':year,
                'League':league
            }
        )

        season_length = 17
        if year in [2019,2020]:
            season_length = 16

        for week in range(1,season_length + 1):
            box_scores = league.box_scores(week)
            matchups.append(
                {
                    'Year':year,
                    'Week':week,
                    'Box Scores':box_scores
                }
            )

            time.sleep(3)
            
    data = {
        'Leagues':leagues,
        'Box Scores':matchups
    }

    with open('fantasy-football-website/database/espn-data.pkl', 'wb') as file:
        pickle.dump(data, file)

# Read in pickle file
def read_pickle_file() -> dict[str, list]:
    with open('fantasy-football-website/database/espn-data.pkl', 'rb') as file:
        data = pickle.load(file)
    
    return data

data = read_pickle_file()