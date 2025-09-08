import time
import pickle
import sqlite3
import uuid

import pandas as pd
from espn_api.football import League

from python import constants

# Function to pull all historical records 2019-2024
def fetch_api_data(version: int, league_id=constants.LEAGUE_ID, espn_s2=constants.ESPN_S2, swid=constants.SWID):
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
    
    data = {}

    for year in range(2018,2025):
        league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
        players = league.espn_request.get_pro_players()

        season_length = 17
        if year in [2019,2020]:
            season_length = 16
        elif year == 2018:
            season_length = 15

        matchups = {}
        for week in range(1, season_length + 1):
            if year == 2018:
                box_scores = league.scoreboard(week)
            else:
                box_scores = league.box_scores(week)

            matchups[week] = box_scores

            if (week == 1) or (week == season_length):
                print(f'Year: {year}, Week: {week}')
            time.sleep(3)

        data[year] = {
            'League':league,
            'Players':players,
            'Box Scores':matchups
        }

    write_pickle_file(data=data, version=version)

# Function to pull new records and append or overwrite pickle file
# Could be used to rerun any given season
def fetch_new_data(
        year: int,
        version: int,
        league_id=constants.LEAGUE_ID,
        espn_s2=constants.ESPN_S2,
        swid=constants.SWID
):
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    players = league.espn_request.get_pro_players()

    matchups = {}
    for week in range(1, league.current_week + 1):
        box_scores = league.box_scores(week)
        matchups[week] = box_scores

        time.sleep(3)

    new_data = {
        'League':league,
        'Players':players,
        'Box Scores':matchups
    }

    data = read_pickle_file(version=version)
    data[year] = new_data
    write_pickle_file(data=data, version=version)

# Write to pickle file
def write_pickle_file(data, version: int):
    with open(f'database/espn-data-{version}.pkl', 'wb') as file:
        pickle.dump(data, file)

    print('Pickle file written')

# Read in pickle file
def read_pickle_file(version: int) -> dict[str, list]:
    with open(f'database/espn-data-{version}.pkl', 'rb') as file:
        data = pickle.load(file)
    
    return data

# Use pickle file data to build a dataframe for each eventual database table
def construct_dataframes(version: int) -> dict[str, pd.DataFrame]:
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
    data = read_pickle_file(version=version)

    data_teams = []
    data_drafts = []
    data_players = []
    data_matchups = []
    data_games = []
    data_player_games = []

    for year in data.keys():
        league = data[year]['League']
        players = data[year]['Players']
        box_scores = data[year]['Box Scores']

        for pick in league.draft:
            team_name = pick.team.owners[0]['firstName']
            if team_name == 'The':
                team_name = 'Klapp'
            elif team_name == 'Noah ':
                team_name = 'Noah'

            data_drafts.append(
                {
                    'draft_pick_id':str(uuid.uuid4()),
                    'player_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=str(pick.playerId))),
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
                    {
                        'team_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=team_name)),
                        'team_name':team_name
                    }
                )
            
        for player in players:
            if player['defaultPositionId'] not in [1, 2, 3, 4, 5, 16]:
                continue

            data_players.append(
                {
                    'player_id':str(uuid.uuid5(namespace=constants.NAMESPACE, name=str(player['id']))),
                    'player_name':player['fullName'],
                    'position':constants.DEFAULT_POSITION_MAP[player['defaultPositionId']]
                }
            )

        for week in box_scores.keys():
            matchups = box_scores[week]

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

                if year > 2018:
                    for player in matchup.home_lineup:
                        data_player_games.append(
                            {
                                'player_game_id':str(uuid.uuid4()),
                                'matchup_id':matchup_id,
                                'game_id':home_game_id,
                                'team_id':str(uuid.uuid5(constants.NAMESPACE, name=home_team)),
                                'player_id':str(uuid.uuid5(constants.NAMESPACE, name=str(player.playerId))),
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
                                'player_id':str(uuid.uuid5(constants.NAMESPACE, name=str(player.playerId))),
                                'points':player.points,
                                'slot_position':player.slot_position,
                                'active_status':player.active_status,
                                'bye_week_flag':player.on_bye_week
                            }
                        )
    df_teams = pd.DataFrame(data_teams).drop_duplicates().reset_index(drop=True)
    df_drafts = pd.DataFrame(data_drafts)
    df_players = pd.DataFrame(data_players).drop_duplicates('player_id', keep='last').reset_index(drop=True)
    df_matchups = pd.DataFrame(data_matchups)
    df_games = pd.DataFrame(data_games)
    df_player_games = pd.DataFrame(data_player_games)


    return {'teams':df_teams, 'drafts':df_drafts, 'matchups':df_matchups, 'games':df_games, 'player_games':df_player_games, 'players':df_players}

# Create the database and fill it with the tables from dataframes
def create_database(version: int) -> None:
    data_dict = construct_dataframes(version=version)

    conn = sqlite3.connect('database/fantasy-football.db')
    
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
                t.team_name AS "Team",
                p.player_name AS "Player",
                p.position AS "Position",
                d.round AS "Round",
                d.pick AS "Pick",
                ROW_NUMBER() OVER (PARTITION BY d.year ORDER BY d.round, d.pick) AS "Overall Pick"

            FROM drafts AS d

            LEFT JOIN players AS p
            ON p.player_id = d.player_id

            LEFT JOIN teams AS t
            ON t.team_id = d.team_id
    '''
    c.execute(draft_view)

    c.execute('DROP VIEW IF EXISTS player_matchup_data')
    player_matchup_view = '''
        CREATE VIEW player_matchup_data AS
            WITH
                pg AS (
                    SELECT
                        pg.matchup_id,
                        pg.team_id,
                        t.team_name,
                        p.player_name,
                        pg.points,
                        CASE    WHEN pg.slot_position IN ('RB','WR') THEN pg.slot_position || ROW_NUMBER() OVER (PARTITION BY pg.game_id, pg.slot_position ORDER BY pg.points DESC)
                                WHEN pg.slot_position = 'RB/WR/TE' THEN 'FLEX'
                                ELSE pg.slot_position
                        END AS slot_position,
                        CASE    WHEN pg.slot_position = 'QB' THEN 1
                                WHEN pg.slot_position = 'RB' THEN 2
                                WHEN pg.slot_position = 'WR' THEN 4
                                WHEN pg.slot_position = 'TE' THEN 6
                                WHEN pg.slot_position = 'RB/WR/TE' THEN 7
                                WHEN pg.slot_position = 'D/ST' THEN 8
                                WHEN pg.slot_position = 'K' THEN 9
                        END AS position_sort
                            
                    FROM player_games AS pg
                    
                    LEFT JOIN players AS p
                    ON p.player_id = pg.player_id
                    
                    LEFT JOIN teams AS t
                    ON t.team_id = pg.team_id
                    
                    WHERE
                        pg.slot_position <> 'BE'
                )

            SELECT
                m.year AS "Year",
                m.week AS "Week",
                pg.team_name AS "Home Team",
                pg.player_name AS "Home Player",
                pg.points AS "Home Player Points",
                pg.slot_position AS "Position",
                pg2.points AS "Away Player Points",
                pg2.player_name AS "Away Player",
                pg2.team_name AS "Away Team"
                    
            FROM matchups AS m

            LEFT JOIN pg
            ON pg.matchup_id = m.matchup_id AND pg.team_id = m.home_team_id

            LEFT JOIN pg AS pg2
            ON pg2.matchup_id = m.matchup_id AND pg2.team_id = m.away_team_id AND pg2.slot_position = pg.slot_position

            WHERE
                m.matchup_type IN ('NONE','WINNERS_BRACKET')
                AND pg.slot_position <> 'BE'
                    
            ORDER BY
                m.year,
                m.week,
                pg.team_name,
                pg.position_sort,
                pg.points DESC
    '''
    c.execute(player_matchup_view)

    conn.commit()
    conn.close()

# Write views to csv files
def write_csvs() -> None:
    conn = sqlite3.connect('database/fantasy-football.db')

    pd.read_sql('SELECT * FROM game_data', con=conn).to_csv('database/fantasy-football-game-data.csv', index=False)
    pd.read_sql('SELECT * FROM matchup_data', con=conn).to_csv('database/fantasy-football-matchup-data.csv', index=False)
    pd.read_sql('SELECT * FROM teams', con=conn).to_csv('database/fantasy-football-team-data.csv', index=False)
    pd.read_sql('SELECT * FROM draft_data', con=conn).to_csv('database/fantasy-football-draft-data.csv', index=False)
    pd.read_sql('SELECT * FROM player_matchup_data', con=conn).to_csv('database/fantasy-football-player-matchup-data.csv', index=False)

    conn.commit()
    conn.close()