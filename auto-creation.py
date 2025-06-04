import dominate
from dominate.tags import *
import pandas as pd
import numpy as np
import sqlite3

root = '/fantasy-football-website'

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

teams = df_converted['Team'].unique()
years = df_converted['Year'].unique()
years_weeks = [(year, df_converted.loc[(df_converted['Year'] == year) & (df_converted['Playoff Flag'] == False), 'Week'].max()) for year in years]

def df_to_table(data: pd.DataFrame):
    t = table()
    head = thead()
    body = tbody()

    for column in data.columns:
        head.add(th(column))
    
    for row in data.values:
        r = tr()
        for value in row:
            r.add(td(value))
        body.add(r)

    t.add(head)
    t.add(body)

    return t



def header(active_year: int = None) -> div:
    '''
    Creates the blue header div, adds in the logo and heading at the top

    Takes an input for the active page in the navbar. This is passed directly to topnav()
    
    Parameters
    ----------
    active_year : int
        The active page to be highlighted in navbar (deprecated naming)
    
    Returns
    -------
    div
        div container for the entire header
    '''
    container = div(_class='header')
    logo = img(src=f'{root}/Assets/Fantasy-Football-App-LOGO.png', height=85, style='float: left;padding: 0px 20px')
    heading = h1('Fantasy Football Luck Scores')

    navbar = topnav(active_year=active_year)
    
    container.add(logo)
    container.add(heading)
    container.add(br())
    container.add(navbar)

    return container


def topnav(active_year: int = None) -> div:
    '''
    Creates the navbar with dropdowns. Called by the header() function

    Parameters
    ----------
    active_year : int
        Active page to be highlighted by the navbar (deprecated naming convention)

    Returns
    -------
    div
        div container for navbar
    '''
    container = div(_class='topnav')

    if active_year == 'home':
        home = div(a('Home', href=f'{root}/'), _class='dropdown active')
    else:
        home = div(a('Home', href=f'{root}/'), _class='dropdown')
    container.add(home)

    for year, week in years_weeks:
        if active_year == year:
            dropdown = div(_class='dropdown active')
        else:
            dropdown = div(_class='dropdown')
        dropdown_button = a(year, href=f'{root}/{year}/', _class='dropdown-button')
        dropdown.add(dropdown_button)

        dropdown_content = div(_class='dropdown-content')
        for i in range(week):
            _a = a(f'Week {i+1}', href=f'{root}/{year}/week-{i+1}.html')

            dropdown_content.add(_a)

        dropdown.add(dropdown_content)
        container.add(dropdown)

    if active_year == 'team':
        team_dropdown = div(_class='dropdown active')
    else:
        team_dropdown = div(_class='dropdown')
    team_dropdown_button = a('Teams', href=f'{root}/teams/', _class='dropdown-button')
    team_dropdown.add(team_dropdown_button)

    team_dropdown_content = div(_class='dropdown-content')
    for team in teams:
        _a = a(f'{team}', href=f'{root}/teams/{team}.html')

        team_dropdown_content.add(_a)

    team_dropdown.add(team_dropdown_content)
    container.add(team_dropdown)

    if active_year == 'champion':
        champions = div(a('Champions', href=f'{root}/champion.html'), _class='dropdown active')
    else:
        champions = div(a('Champions', href=f'{root}/champion.html'), _class='dropdown')
    container.add(champions)

    return container


# Function which creates the content for each of the individual week pages
# Editing this will change the structure of all the individual week pages
def week_content(year: int, week: int) -> div:
    '''
    Function which creates the content for each of the individual week pages

    Includes
    --------
    * Weekly scoreboard
        Simply shows each of the matchups in the week
    * Updated Standings
        Table which shows the standings as of that week

    Parameters
    ----------
    year : int
        which season to pull matchups from
    week : int
        which week in the season

    Returns
    -------
    div
    '''
    container = div(_class='content')

    title = h1(f'{year} Week {week}')

    scoreboard = df.loc[(df['Year'] == year) & (df['Week'] == week), ['Home Team','Home Score','Away Score','Away Team']].copy()    
    scoreboard_div = div(_class='scoreboard')
    scoreboard_title = h2('Weekly Scoreboard')
    scoreboard_table = df_to_table(data=scoreboard)
    scoreboard_table['id'] = 'scoreboard-table'
    scoreboard_div.add([scoreboard_title, scoreboard_table])

    temp = df_converted.loc[(df_converted['Year'] == year) & (df_converted['Week'] <= week)]

    teams = temp['Team'].unique()
    records = []

    for team in teams:
        temp_team = temp.loc[temp['Team'] == team]
        wins = temp_team['Win'].sum()
        losses = week - wins
        record = f'{wins}-{losses}'

        pf = round(temp_team['Score'].sum(), 2)
        avg_pf = round(pf / week, 2)
        pa = round(temp_team['Opp Score'].sum(), 2)
        avg_margin = round((pf - pa) / week, 2)

        records.append([team, wins, record, pf, pa, avg_pf, avg_margin])

    standings = pd.DataFrame(records, columns=['Team','Wins','Record','Points For','Points Against','Avg Points For','Avg Margin']).sort_values(['Wins','Points For'], ascending=False)
    standings = standings[['Team','Record','Points For','Points Against','Avg Points For','Avg Margin']]

    standings_div = div(_class='standings')
    standings_title = h2('Updated Standings')
    standings_table = df_to_table(data=standings)
    standings_table['id'] = 'standings-table'
    standings_div.add([standings_title, standings_table])

    container.add(title)
    container.add(scoreboard_div)
    container.add(br())
    container.add(standings_div)

    return container

# Function which creates home page content
# Edit this for the content on the home page
def home_content() -> div:
    '''
    Function which creates the home page content

    Includes:
    ---------
    * Documentation PDF
    '''
    container = div(_class='content')
    container.add(h1('Documentation'))

    documentation = object_('Documentation', data='/fantasy-football-website/Assets/Fantasy-Football.pdf', height='1000px', width='90%')
    container.add(documentation)

    return container


# Function which creates champion page content
# Edit this for the content on the champion page
def champion_content() -> div:
    '''
    Function which creates the champion page content

    Includes:
    ---------
    * Summary Table for each season
    * List of all Champions
    '''
    container = div(_class='content')
    container.add(h1('League Champions'))

    champions = df_converted.loc[(df_converted['Week'] == 17) & (df_converted['Win'] == 1), ['Year','Team']].values
    data = []
    for year, team in champions:
        temp = df_converted.loc[(df_converted['Year'] == year) & (df_converted['Team'] == team) & (df_converted['Playoff Flag'] == False)]
        wins = temp['Win'].sum()
        losses = len(temp) - wins
        record = f'{wins}-{losses}'

        pf = round(temp['Score'].sum(), 2)
        avg_pf = round(pf / len(temp), 2)
        pa = round(temp['Opp Score'].sum(), 2)
        avg_margin = round((pf - pa) / len(temp), 2)

        data.append([year, team, record, pf, avg_pf, avg_margin])

    t = pd.DataFrame(data, columns=['Year','Team','Record','Points For','Avg Points For','Avg Margin'])

    summary_div = div(_class='champion-summary')
    summary_title = h2('Champions Summary')
    summary_table = df_to_table(data=t)
    summary_table['id'] = 'champion-summary-table'
    summary_div.add([summary_title, summary_table])

    years_div = div(_class='champion-years')
    for year, team in champions:
        years_div.add(h3(f'{year} Season'))
        years_div.add(p(team))

    container.add(summary_div)
    container.add(years_div)

    return container


def team_content(team: str, conn: sqlite3.Connection) -> div:
    container = div(_class='content')
    container.add(h1(f'{team} Data'))
    
    query = '''
        SELECT
            Year,
            Record,
            Ranking,
            ROUND("Points For", 2) AS "Points For",
            ROUND("Points Against", 2) AS "Points Against",
            "Avg Points For",
            "Avg Margin"
        FROM season_totals
    '''

    data = pd.read_sql(query + f"WHERE team = '{team}'", con=conn)

    summary_div = div(_class='team-summary')
    summary_title = h2('Team Summary')
    summary_table = df_to_table(data=data)
    summary_table['id'] = 'team-summary-table'
    summary_div.add([summary_title, summary_table])
    
    container.add(summary_div)

    return container


def year_content(year: int, conn: sqlite3.Connection) -> div:
    container = div(_class='content')
    container.add(h1(f'{year} Data'))
    
    query = '''
        SELECT
            Team,
            Record,
            Ranking,
            ROUND("Points For", 2) AS "Points For",
            ROUND("Points Against", 2) AS "Points Against",
            "Avg Points For",
            "Avg Margin"
        FROM season_totals
    '''

    data = pd.read_sql(query + f"WHERE year = '{year}'", con=conn)

    summary_div = div(_class='season-summary')
    summary_title = h2('Season Summary')
    summary_table = df_to_table(data=data)
    summary_table['id'] = 'season-summary-table'
    summary_div.add([summary_title, summary_table])
    
    container.add(summary_div)

    return container

# conn = sqlite3.connect('fantasy-football-website/database/fantasy-football.db')

# print(year_content(2023, conn=conn).render())

# conn.close()




# Construct and write every individual week html file
## Loops through the years and weeks to write one html file for each
## Applies week_content function with the specific year/week combo to generate tables dynamically
def week_pages():
    years = np.arange(2019, 2025)

    for year in years:
        if year < 2021:
            weeks = np.arange(1,14)
        else:
            weeks = np.arange(1,15)

        for week in weeks:
            doc = dominate.document(title='Fantasy Football')
            doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))
            doc.add(header(active_year=year))

            doc.add(week_content(year=year, week=week))

            with open(f'fantasy-football-website/{year}/week-{week}.html','w') as file:
                file.write(doc.render())

# Construct and write the home page
def home_page():
    doc = dominate.document(title='Fantasy Football')
    doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))
    doc.add(header(active_year='home'))

    doc.add(home_content())

    with open(f'fantasy-football-website/index.html','w') as file:
        file.write(doc.render())

# Construct and write the champion page
def champion_page():
    doc = dominate.document(title='Fantasy Football')
    doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))
    doc.add(header(active_year='champion'))

    doc.add(champion_content())

    with open(f'fantasy-football-website/champion.html','w') as file:
        file.write(doc.render())

def team_pages():
    conn = sqlite3.connect('fantasy-football-website/database/fantasy-football.db')

    for team in teams:
        doc = dominate.document(title='Fantasy Football')
        doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))
        doc.add(header(active_year='team'))

        doc.add(team_content(team=team, conn=conn))

        with open(f'fantasy-football-website/teams/{team}.html','w') as file:
            file.write(doc.render())

    conn.close()

def year_pages():
    conn = sqlite3.connect('fantasy-football-website/database/fantasy-football.db')

    for year in years:
        doc = dominate.document(title='Fantasy Football')
        doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))
        doc.add(header(active_year=year))

        doc.add(year_content(year, conn=conn))

        with open(f'fantasy-football-website/{year}/index.html','w') as file:
            file.write(doc.render())

    conn.close()

# Call the constructing functions
# home_page()
# champion_page()
# week_pages()
# team_pages()
year_pages()