import time
import pickle
import sqlite3
import uuid

import pandas as pd
from espn_api.football import League

import constants

# Function to pull all historical records 2019-2024
def fetch_api_data(league_id=constants.LEAGUE_ID, espn_s2=constants.ESPN_S2, swid=constants.SWID):
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

# Use pickle file data to build a dataframe for each eventual database table
def construct_dataframes():
    '''
    Takes in espn-data.pkl file data and produces the following dataframes:
     - teams
     - matchups
     - games
     - player_games
     - players
    All of which will be converted into tables in the database

    Returns
    -------
    Dict : [Str, DataFrame]
    '''
    data = read_pickle_file()

    data_teams = []

    leagues = data['Leagues']
    for record in leagues:
        league = record['League']
        for team in league.teams:
            data_teams.append(
                    team.owners[0]['firstName']
                )

    data_teams = [{'team_name':team} for team in list(set(data_teams))]
    df_teams = pd.DataFrame(data_teams)
    df_teams['team_name'] = df_teams['team_name'].replace({'The':'Klapp', 'Noah ':'Noah'})
    df_teams['team_id'] = df_teams['team_name'].apply(lambda team_name: str(uuid.uuid5(constants.NAMESPACE, name=team_name)))

    data_matchups = []
    data_games = []
    data_player_games = []
    data_players = []

    box_scores = data['Box Scores']
    for box_score in box_scores:
        year = box_score['Year']
        week = box_score['Week']
        matchups = box_score['Box Scores']

        for matchup in matchups:
            matchup_id = str(uuid.uuid4())

            home_team = matchup.home_team.owners[0]['firstName']
            if home_team == 'The':
                home_team = 'Klapp'
            elif home_team == 'Noah ':
                home_team = 'Noah'

            if matchup.away_team == 0:
                away_team = 'Bye'
            else:
                away_team = matchup.away_team.owners[0]['firstName']
            if away_team == 'The':
                away_team = 'Klapp'
            elif away_team == 'Noah ':
                away_team = 'Noah'

            data_matchups.append(
                {
                    'matchup_id':matchup_id,
                    'year':year,
                    'week':week,
                    'matchup_type':matchup.matchup_type,
                    'playoff_flag':matchup.is_playoff,
                    'home_team_id':str(uuid.uuid5(constants.NAMESPACE, name=home_team)),
                    'home_score':matchup.home_score,
                    'away_team_id':str(uuid.uuid5(constants.NAMESPACE, name=away_team)),
                    'away_score':matchup.away_score
                }
            )

            home_game_id = str(uuid.uuid4())
            data_games.append(
                {
                    'game_id':home_game_id,
                    'matchup_id':matchup_id,
                    'team_id':str(uuid.uuid5(constants.NAMESPACE, name=home_team)),
                    'score':matchup.home_score,
                    'opp_score':matchup.away_score,
                    'win_flag':int(matchup.home_score > matchup.away_score),
                    'margin':round(matchup.home_score - matchup.away_score, 2)
                }
            )

            away_game_id = str(uuid.uuid4())
            data_games.append(
                {
                    'game_id':away_game_id,
                    'matchup_id':matchup_id,
                    'team_id':str(uuid.uuid5(constants.NAMESPACE, name=away_team)),
                    'score':matchup.away_score,
                    'opp_score':matchup.home_score,
                    'win_flag':int(matchup.away_score > matchup.home_score),
                    'margin':round(matchup.away_score - matchup.home_score, 2)
                }
            )

            for player in matchup.home_lineup:
                data_player_games.append(
                    {
                        'player_game_id':str(uuid.uuid4()),
                        'matchup_id':matchup_id,
                        'game_id':home_game_id,
                        'team_id':str(uuid.uuid5(constants.NAMESPACE, name=home_team)),
                        'player_id':str(uuid.uuid5(constants.NAMESPACE, name=player.name)),
                        'points':player.points,
                        'slot_position':player.slot_position,
                        'active_status':player.active_status,
                        'bye_week_flag':player.on_bye_week
                    }
                )

            for player in matchup.away_lineup:
                data_player_games.append(
                    {
                        'player_game_id':str(uuid.uuid4()),
                        'matchup_id':matchup_id,
                        'game_id':away_game_id,
                        'team_id':str(uuid.uuid5(constants.NAMESPACE, name=away_team)),
                        'player_id':str(uuid.uuid5(constants.NAMESPACE, name=player.name)),
                        'points':player.points,
                        'slot_position':player.slot_position,
                        'active_status':player.active_status,
                        'bye_week_flag':player.on_bye_week
                    }
                )

            for player in (matchup.home_lineup + matchup.away_lineup):
                data_players.append(player.name)


    df_matchups = pd.DataFrame(data_matchups)
    df_games = pd.DataFrame(data_games)
    df_player_games = pd.DataFrame(data_player_games)

    data_players = [{'player_id':str(uuid.uuid5(constants.NAMESPACE, name=player)), 'player_name':player} for player in list(set(data_players))]
    df_players = pd.DataFrame(data_players)

    return {'teams':df_teams, 'matchups':df_matchups, 'games':df_games, 'player_games':df_player_games, 'players':df_players}

# Create the database and fill it with the tables from dataframes
def create_database() -> None:
    data_dict = construct_dataframes()

    conn = sqlite3.connect('fantasy-football-website/database/fantasy-football.db')

    data_dict['teams'].to_sql('teams', con=conn, if_exists='replace', index=False)
    data_dict['matchups'].to_sql('matchups', con=conn, if_exists='replace', index=False)
    data_dict['games'].to_sql('games', con=conn, if_exists='replace', index=False)
    data_dict['player_games'].to_sql('player_games', con=conn, if_exists='replace', index=False)
    data_dict['players'].to_sql('players', con=conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

create_database()