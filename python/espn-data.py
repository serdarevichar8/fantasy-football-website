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

    with open('database/espn-data.pkl', 'wb') as file:
        pickle.dump(data, file)

# Read in pickle file
def read_pickle_file() -> dict[str, list]:
    with open('database/espn-data.pkl', 'rb') as file:
        data = pickle.load(file)
    
    return data

# Use pickle file data to build a dataframe for each eventual database table
def construct_dataframes() -> dict[str, pd.DataFrame]:
    '''
    Takes in espn-data.pkl file data and produces the following dataframes:
     - teams
     - drafts
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
    data_drafts = []
    data_players = []

    leagues = data['Leagues']
    for record in leagues:
        league = record['League']
        year = record['Year']

        for player in league.player_map.keys():
            if type(player) == int:
                continue
            data_players.append(player)

        for pick in league.draft:
            team_name = pick.team.owners[0]['firstName']
            if team_name == 'The':
                team_name = 'Klapp'
            elif team_name == 'Noah ':
                team_name = 'Noah'

            data_drafts.append(
                {
                    'draft_pick_id':str(uuid.uuid4()),
                    'player_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=pick.playerName)),
                    'team_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=team_name)),
                    'year':year,
                    'round':pick.round_num,
                    'pick':pick.round_pick
                }
            )

        for team in league.teams:
            team_name = team.owners[0]['firstName']
            if team_name == 'The':
                team_name = 'Klapp'
            elif team_name == 'Noah ':
                team_name = 'Noah'

            data_teams.append(
                    team_name
                )

    data_teams = [{'team_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=team)), 'team_name':team} for team in list(set(data_teams))]
    df_teams = pd.DataFrame(data_teams)
    data_players = [{'player_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=player)), 'player_name':player} for player in list(set(data_players))]
    df_players = pd.DataFrame(data_players)
    df_drafts = pd.DataFrame(data_drafts)

    data_matchups = []
    data_games = []
    data_player_games = []

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

    df_matchups = pd.DataFrame(data_matchups)
    df_games = pd.DataFrame(data_games)
    df_player_games = pd.DataFrame(data_player_games)

    return {'teams':df_teams, 'drafts':df_drafts, 'matchups':df_matchups, 'games':df_games, 'player_games':df_player_games, 'players':df_players}

# Create the database and fill it with the tables from dataframes
def create_database() -> None:
    data_dict = construct_dataframes()

    conn = sqlite3.connect('database/fantasy-football.db')

    # teams_table = '''
    #     CREATE TABLE IF NOT EXISTS teams (
    #         team_id TEXT PRIMARY KEY,
    #         team_name TEXT
    #     )
    # '''
    # drafts_table = '''
    #     CREATE TABLE IF NOT EXISTS drafts (
    #         draft_pick_id TEXT PRIMARY KEY,
    #         player_id TEXT,
    #         team_id TEXT,
    #         year INTEGER,
    #         pick INTEGER,
    #         FOREIGN KEY (player_id) REFERENCES players(player_id),
    #         FOREIGN KEY (team_id) REFERENCES teams(team_id)
    #     )
    # '''
    # matchups_table = '''
    #     CREATE TABLE IF NOT EXISTS matchups (
    #         matchup_id TEXT PRIMARY KEY,
    #         year INTEGER,
    #         week INTEGER,
    #         matchup_type TEXT,
    #         playoff_flag INTEGER,
    #         home_team_id TEXT,
    #         home_score REAL,
    #         away_team_id TEXT,
    #         away_score REAL,
    #         FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    #         FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
    #     )
    # '''
    # games_table = '''
    #     CREATE TABLE IF NOT EXISTS games (
    #         game_id TEXT PRIMARY KEY,
    #         matchup_id TEXT,
    #         team_id TEXT,
    #         score REAL,
    #         opp_score REAL,
    #         win_flag INTEGER,
    #         margin REAL,
    #         FOREIGN KEY (matchup_id) REFERENCES matchups(matchup_id),
    #         FOREIGN KEY (team_id) REFERENCES teams(team_id)
    #     )
    # '''
    # player_games_table = '''
    #     CREATE TABLE IF NOT EXISTS player_games (
    #         player_game_id TEXT PRIMARY KEY,
    #         matchup_id TEXT,
    #         game_id TEXT,
    #         team_id TEXT,
    #         player_id TEXT,
    #         points REAL,
    #         slot_position TEXT,
    #         active_status TEXT,
    #         bye_week_flag INTEGER,
    #         FOREIGN KEY (matchup_id) REFERENCES matchups(matchup_id),
    #         FOREIGN KEY (game_id) REFERENCES games(game_id),
    #         FOREIGN KEY (team_id) REFERENCES teams(team_id),
    #         FOREIGN KEY (player_id) REFERENCES players(player_id)
    #     )
    # '''
    # players_table = '''
    #     CREATE TABLE IF NOT EXISTS players (
    #         player_id TEXT PRIMARY KEY,
    #         player_name TEXT
    #     )
    # '''

    # conn.execute(teams_table)
    # conn.execute(players_table)
    # conn.execute(matchups_table)
    # conn.execute(drafts_table)
    # conn.execute(games_table)
    # conn.execute(player_games_table)
    

    data_dict['teams'].to_sql('teams', con=conn, if_exists='replace', index=False)
    data_dict['drafts'].to_sql('drafts', con=conn, if_exists='replace', index=False)
    data_dict['matchups'].to_sql('matchups', con=conn, if_exists='replace', index=False)
    data_dict['games'].to_sql('games', con=conn, if_exists='replace', index=False)
    data_dict['player_games'].to_sql('player_games', con=conn, if_exists='replace', index=False)
    data_dict['players'].to_sql('players', con=conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

# Connects to database and creates/updates the views which are converted into CSV files
def database_views() -> None:
    conn = sqlite3.connect('database/fantasy-football.db')
    c = conn.cursor()

    c.execute('DROP VIEW IF EXISTS game_data')
    game_view = '''
        CREATE VIEW game_data AS
            SELECT
                m.year AS "Year",
                m.week AS "Week",
                m.playoff_flag AS "Playoff Flag",
                t.team_name AS "Team",
                g.score AS "Score",
                g.opp_score AS "Opp Score",
                g.win_flag AS "Win",
                g.margin AS "Margin"
                    
            FROM games AS g

            LEFT JOIN matchups AS m
            ON m.matchup_id = g.matchup_id

            LEFT JOIN teams AS t
            ON t.team_id = g.team_id

            WHERE
                m.matchup_type IN ('NONE','WINNERS_BRACKET')
    '''
    c.execute(game_view)

    c.execute('DROP VIEW IF EXISTS matchup_data')
    matchup_view = '''
        CREATE VIEW matchup_data AS
            SELECT
                m.year AS "Year",
                m.week AS "Week",
                m.playoff_flag AS "Playoff Flag",
                t.team_name AS "Home Team",
                m.home_score AS "Home Score",
                COALESCE(t2.team_name,'Bye') AS "Away Team",
                m.away_score AS "Away Score"
                    
            FROM matchups AS m
            
            LEFT JOIN teams AS t
            ON t.team_id = m.home_team_id
            
            LEFT JOIN teams AS t2
            ON t2.team_id = m.away_team_id
            
            WHERE
                m.matchup_type IN ('NONE','WINNERS_BRACKET')
    '''
    c.execute(matchup_view)

    c.execute('DROP VIEW IF EXISTS draft_data')
    draft_view = '''
        CREATE VIEW draft_data AS
            SELECT
                d.year AS "Year",
                d.round AS "Round",
                d.pick AS "Pick",
                p.player_name AS "Player",
                t.team_name AS "Team",
                ROW_NUMBER() OVER (PARTITION BY d.year ORDER BY d.round, d.pick) AS "Overall Pick"

            FROM drafts AS d

            LEFT JOIN players AS p
            ON p.player_id = d.player_id

            LEFT JOIN teams AS t
            ON t.team_id = d.team_id
    '''
    c.execute(draft_view)

    conn.commit()
    conn.close()

# Write views to csv files
def write_csvs() -> None:
    conn = sqlite3.connect('database/fantasy-football.db')

    pd.read_sql('SELECT * FROM game_data', con=conn).to_csv('database/fantasy-football-game-data.csv', index=False)
    pd.read_sql('SELECT * FROM matchup_data', con=conn).to_csv('database/fantasy-football-matchup-data.csv', index=False)
    pd.read_sql('SELECT * FROM teams', con=conn).to_csv('database/fantasy-football-team-data.csv', index=False)
    pd.read_sql('SELECT * FROM draft_data', con=conn).to_csv('database/fantasy-football-draft-data.csv', index=False)

    conn.commit()
    conn.close()

# create_database()
# database_views()
write_csvs()