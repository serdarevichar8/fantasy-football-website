import uuid

import pandas as pd

NAMESPACE = uuid.UUID('05859822-9e6e-4612-91ff-c714fa7e40f6')

ROOT = '/fantasy-football-website/'

MATCHUP_DATA = pd.read_csv('database/fantasy-football-matchup-data.csv')
GAME_DATA = pd.read_csv('database/fantasy-football-game-data.csv')
DRAFT_DATA = pd.read_csv('database/fantasy-football-draft-data.csv')
PLAYER_MATCHUP_DATA = pd.read_csv('database/fantasy-football-player-matchup-data.csv')
TEAMS = pd.read_csv('database/fantasy-football-team-data.csv')['team_name'].values
YEARS = GAME_DATA['Year'].unique()
YEARS_WEEKS = [(year, GAME_DATA.loc[(GAME_DATA['Year'] == year) & (GAME_DATA['Playoff Flag'] == False), 'Week'].max()) for year in YEARS]

LEAGUE_ID = 565994
ESPN_S2 = None
SWID = None

COLOR_DICT = {'andrew':'cornflowerblue',
              'mcgwire':'darkblue',
              'tyler':'lightgreen',
              'noah':'#33a02c',
              'michael':'#fb9a99',
              'haris':'#e31a1c',
              'dante':'sandybrown',
              'nathan':'#ff7f00',
              'kevin':'violet',
              'ethan':'#6a3d9a',
              'zach':'gold',
              'carter':'#b15928',
              'justin':"#DA5CB4",
              'klapp':"#cec962",
              'jackson':"#9968cdff"}