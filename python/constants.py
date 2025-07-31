import uuid

import pandas as pd

NAMESPACE = uuid.UUID('05859822-9e6e-4612-91ff-c714fa7e40f6')

ROOT = '/fantasy-football-website/'

MATCHUP_DATA = pd.read_csv('database/fantasy-football-matchup-data.csv')
GAME_DATA = pd.read_csv('database/fantasy-football-game-data.csv')
DRAFT_DATA = pd.read_csv('database/fantasy-football-draft-data.csv')
TEAMS = pd.read_csv('database/fantasy-football-team-data.csv')['team_name'].values
YEARS = GAME_DATA['Year'].unique()
YEARS_WEEKS = [(year, GAME_DATA.loc[(GAME_DATA['Year'] == year) & (GAME_DATA['Playoff Flag'] == False), 'Week'].max()) for year in YEARS]

LEAGUE_ID = 565994
ESPN_S2 = 'AECM5wfhjIj%2FgFWK7gldFYleiro5zx5YQV0NKDgcd1glbVuvTot8VFFUNWhPjAOG46Ut0lFYEI5mo75eeL5VDdQMyLKmpms7TetGiz2dMsUSIfl2A7MNQMrSMFvmBHhg0wi1SQbHOFKI6FBVsJqtBlq5c%2B%2Bl5dGvpM8LmhrFp563Dv4eaZhclj9lfSPq3CC4u%2FsUk7iSzQq42W7AUMVbYJqAKKX11dazM5GmocQozc9GXNKiRIhuNDAe2en7%2FjyAbJqSZEwlWu%2BRyOIyOpmLgr6wnx47jWxeKJmTIYP24Hk13Q%3D%3D'
SWID = '{1B555C10-31F2-4EC7-A015-90782392E593}'

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
              'klapp':"#cec962"}