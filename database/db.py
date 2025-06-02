import sqlite3
import pandas as pd

conn = sqlite3.connect('fantasy-football.db')


df = pd.read_csv('/Users/serdarevichar/Library/CloudStorage/GoogleDrive-serdarevichar@gmail.com/My Drive/fantasy-football-database.csv', index_col = 'Unnamed: 0')
df['Home Team'] = df['Home Team'].replace({'The':'Klapp'})
df['Away Team'] = df['Away Team'].replace({'The':'Klapp'})

temp1 = df[['Year','Week','Playoff Flag','Home Team','Home Score','Away Score']].copy()
temp2 = df[['Year','Week','Playoff Flag','Away Team','Away Score','Home Score']].copy()

temp1.rename(columns={'Home Team':'Team', 'Home Score':'Score', 'Away Score':'Opp Score'}, inplace=True)
temp2.rename(columns={'Away Team':'Team', 'Away Score':'Score', 'Home Score':'Opp Score'}, inplace=True)

df_converted = pd.concat([temp1,temp2], axis=0, ignore_index=True)
df_converted['Win'] = df_converted['Score'] > df_converted['Opp Score']
df_converted['Win'] = df_converted['Win'].map(int)
df_converted

df_converted.sort_values(['Year','Week'], inplace = True)

# Create a table in DB
# df_converted.to_sql('results', con=conn)


query = '''
    SELECT
        year,
        team,
        SUM(score) AS pf,
        SUM("opp score") AS pa,
        SUM(win) AS Wins
        
    FROM results
        
    WHERE
        "playoff flag" = 0
        AND year = 2023

    GROUP BY
        year,
        team
'''

view = '''
    CREATE VIEW IF NOT EXISTS season_totals AS

    WITH
        aggregate AS (
            SELECT
                Year,
                Team,
                SUM(score) AS PF,
                SUM("opp score") AS PA,
                SUM(win) AS Wins,
                MAX(week) AS season_length

            FROM results

            WHERE
                "playoff flag" = 0

            GROUP BY
                year,
                team    
        )

    SELECT
        Year,
        Team,
        PF,
        PA,
        Wins,
        season_length - Wins AS Losses,
        Wins || '-' || (season_length - Wins) AS Record,
        ROW_NUMBER() OVER (PARTITION BY Year ORDER BY WINS DESC, PF DESC) AS Ranking

    FROM aggregate

'''


c = conn.cursor()
# Drop season_totals view (necessary to update it since UPDATE not valid in SQLite)
c.execute('DROP VIEW IF EXISTS season_totals')

# Create season_totals view
c.execute(view)


#print(pd.read_sql('SELECT * FROM season_totals', con=conn))


season_totals = pd.read_sql('SELECT * FROM season_totals WHERE year IN (2020,2021,2022,2023)', con=conn)
print(season_totals.sort_values(['Year','Ranking'], ascending=[True, True]))



conn.commit()

conn.close()