import dominate
from dominate.tags import *
import pandas as pd
import numpy as np
import sqlite3

from python import functions

ROOT = '/fantasy-football-website/'

MATCHUP_DATA = pd.read_csv('fantasy-football-website/database/fantasy-football-matchup-data.csv')
GAME_DATA = pd.read_csv('fantasy-football-website/database/fantasy-football-game-data.csv')
TEAMS = GAME_DATA['Team'].unique()
YEARS = GAME_DATA['Year'].unique()
YEARS_WEEKS = [(year, GAME_DATA.loc[(GAME_DATA['Year'] == year) & (GAME_DATA['Playoff Flag'] == False), 'Week'].max()) for year in YEARS]




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
    logo = img(src=f'{ROOT}Assets/Fantasy-Football-App-LOGO.png', height=85, style='float: left;padding: 0px 20px')
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
        home = div(a('Home', href=f'{ROOT}'), _class='dropdown active')
    else:
        home = div(a('Home', href=f'{ROOT}'), _class='dropdown')
    container.add(home)

    for year, week in YEARS_WEEKS:
        if active_year == year:
            dropdown = div(_class='dropdown active')
        else:
            dropdown = div(_class='dropdown')
        dropdown_button = a(year, href=f'{ROOT}seasons/{year}/', _class='dropdown-button')
        dropdown.add(dropdown_button)

        dropdown_content = div(_class='dropdown-content')
        for i in range(week):
            _a = a(f'Week {i+1}', href=f'{ROOT}seasons/{year}/week-{i+1}.html')

            dropdown_content.add(_a)

        dropdown.add(dropdown_content)
        container.add(dropdown)

    if active_year == 'team':
        team_dropdown = div(_class='dropdown active')
    else:
        team_dropdown = div(_class='dropdown')
    team_dropdown_button = a('Teams', href=f'{ROOT}teams/', _class='dropdown-button')
    team_dropdown.add(team_dropdown_button)

    team_dropdown_content = div(_class='dropdown-content')
    for team in TEAMS:
        _a = a(f'{team}', href=f'{ROOT}teams/{team}.html')

        team_dropdown_content.add(_a)

    team_dropdown.add(team_dropdown_content)
    container.add(team_dropdown)

    if active_year == 'champion':
        champions = div(a('Champions', href=f'{ROOT}champion.html'), _class='dropdown active')
    else:
        champions = div(a('Champions', href=f'{ROOT}champion.html'), _class='dropdown')
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

    # Create scoreboard table of the matchups that week
    scoreboard = MATCHUP_DATA.loc[(MATCHUP_DATA['Year'] == year) & (MATCHUP_DATA['Week'] == week), ['Home Team','Home Score','Away Score','Away Team']].copy()    
    scoreboard_div = div(_class='content-container')
    scoreboard_title = h2('Weekly Scoreboard')
    scoreboard_table = functions.df_to_table(data=scoreboard)
    scoreboard_table['id'] = 'scoreboard-table'
    scoreboard_div.add([scoreboard_title, scoreboard_table])

    # Create the weekly recap stats section
    # This temp df needs to look at only the current week
    temp = GAME_DATA.loc[(GAME_DATA['Year'] == year) & (GAME_DATA['Week'] == week)].copy()


    highest_scorer = temp.sort_values('Score', ascending=False, ignore_index=True).loc[0,['Team','Score']].values
    lowest_scorer = temp.sort_values('Score', ascending=True, ignore_index=True).loc[0,['Team','Score']].values
    largest_win = temp.sort_values('Margin', ascending=False, ignore_index=True).loc[0,['Team','Score','Opp Score']].values
    closest_win = temp.loc[temp['Margin'] >= 0].sort_values('Margin', ascending=True, ignore_index=True).loc[0,['Team','Score','Opp Score']].values

    stats_div = div(_class='content-container stats')
    stats_title = h2('Weekly Recap:')
    stat1 = li(f'Highest Scorer: {highest_scorer[0]} -- {highest_scorer[1]}')
    stat2 = li(f'Lowest Scorer: {lowest_scorer[0]} -- {lowest_scorer[1]}')
    stat3 = li(f'Largest Blowout: {largest_win[0]} -- {largest_win[1]}-{largest_win[2]}')
    stat4 = li(f'Closest Game: {closest_win[0]} -- {closest_win[1]}-{closest_win[2]}')
    stats_list = ul([stat1, stat2, stat3, stat4])
    stats_div.add([stats_title, stats_list])

    # Create the live standings table
    standings = functions.summary_table(GAME_DATA, year = year, week = week)

    standings_div = div(_class='content-container')
    standings_title = h2('Updated Standings')
    standings_table = functions.df_to_table(data=standings)
    standings_table['id'] = 'standings-table'
    standings_div.add([standings_title, standings_table])

    container.add(title)
    container.add(scoreboard_div)
    container.add(br())
    container.add(stats_div)
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

    champions = GAME_DATA.loc[(GAME_DATA['Week'] == 17) & (GAME_DATA['Win'] == 1), ['Year','Team']].values
    data = []
    for year, team in champions:
        temp = GAME_DATA.loc[(GAME_DATA['Year'] == year) & (GAME_DATA['Team'] == team) & (GAME_DATA['Playoff Flag'] == False)]
        wins = temp['Win'].sum()
        losses = len(temp) - wins
        record = f'{wins}-{losses}'

        pf = round(temp['Score'].sum(), 2)
        avg_pf = round(pf / len(temp), 2)
        pa = round(temp['Opp Score'].sum(), 2)
        avg_margin = round((pf - pa) / len(temp), 2)

        data.append([year, team, record, pf, avg_pf, avg_margin])

    t = pd.DataFrame(data, columns=['Year','Team','Record','Points For','Avg Points For','Avg Margin'])

    summary_div = div(_class='content-container')
    summary_title = h2('Champions Summary')
    summary_table = functions.df_to_table(data=t)
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

    summary_div = div(_class='content-container')
    summary_title = h2('Team Summary')
    summary_table = functions.df_to_table(data=data)
    summary_table['id'] = 'team-summary-table'
    summary_div.add([summary_title, summary_table])
    
    container.add(summary_div)

    return container


def year_content(year: int, conn: sqlite3.Connection) -> div:
    container = div(_class='content')
    container.add(h1(f'{year} Data'))

    data = functions.summary_table(GAME_DATA, year = year)

    summary_div = div(_class='content-container')
    summary_title = h2('Season Summary')
    summary_table = functions.df_to_table(data=data)
    summary_table['id'] = 'season-summary-table'
    summary_div.add([summary_title, summary_table])

    playoff_matchups = MATCHUP_DATA.loc[(MATCHUP_DATA['Year'] == year) & (MATCHUP_DATA['Playoff Flag'])].copy()
    playoff_matchups['Playoff Round'] = (playoff_matchups['Week'] % playoff_matchups['Week'].min()) + 1

    bracket_div = div(_class='content-container')
    bracket_title = h2('Playoff Bracket')
    bracket_div.add(bracket_title)

    bracket = main(_id='playoff-bracket')

    rounds = []

    for round in playoff_matchups['Playoff Round'].unique():
        _ul = ul(_class=f'round round-{round}')
        _ul.add(li(dominate.util.raw('&nbsp;'), _class='spacer'))

        for team1, score1, team2, score2 in playoff_matchups.loc[playoff_matchups['Playoff Round'] == round, ['Home Team','Home Score','Away Team','Away Score']].values:

            top_team = li(team1, _class='game game-top')
            if team1 != 'Bye':
                top_team.add(span(score1))

            bot_team = li(team2, _class='game game-bottom')
            if team2 != 'Bye':
                bot_team.add(span(score2))

            _ul.add(top_team)
            _ul.add(li(dominate.util.raw('&nbsp;'), _class='game game-spacer'))
            _ul.add(bot_team)
            _ul.add(li(dominate.util.raw('&nbsp;'), _class='spacer'))

        rounds.append(_ul)

    bracket.add(rounds)
    bracket_div.add(bracket)
    
    container.add(summary_div)
    container.add(bracket_div)

    return container



def document() -> dominate.document:
    doc = dominate.document(title='Fantasy Football')
    doc.head.add(link(rel='stylesheet', href=f'{ROOT}style.css'))
    doc.head.add(link(rel='icon', type='image/png', href=f'{ROOT}Assets/Fantasy-Football-App-LOGO.png'))

    return doc



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
            doc = document()
            doc.add(header(active_year=year))

            doc.add(week_content(year=year, week=week))

            with open(f'fantasy-football-website/seasons/{year}/week-{week}.html','w') as file:
                file.write(doc.render())

# Construct and write the home page
def home_page():
    doc = document()
    doc.add(header(active_year='home'))

    doc.add(home_content())

    with open(f'fantasy-football-website/index.html','w') as file:
        file.write(doc.render())

# Construct and write the champion page
def champion_page():
    doc = document()
    doc.add(header(active_year='champion'))

    doc.add(champion_content())

    with open(f'fantasy-football-website/champion.html','w') as file:
        file.write(doc.render())

# Construct and write the team pages
def team_pages():
    conn = sqlite3.connect('fantasy-football-website/database/fantasy-football.db')

    for team in TEAMS:
        doc = document()
        doc.add(header(active_year='team'))

        doc.add(team_content(team=team, conn=conn))

        with open(f'fantasy-football-website/teams/{team}.html','w') as file:
            file.write(doc.render())

    conn.close()

# Construct and write the year pages
def year_pages():
    conn = sqlite3.connect('fantasy-football-website/database/fantasy-football.db')

    for year in YEARS:
        doc = document()
        doc.add(header(active_year=year))

        doc.add(year_content(year, conn=conn))

        with open(f'fantasy-football-website/seasons/{year}/index.html','w') as file:
            file.write(doc.render())

    conn.close()

# Call the constructing functions
# home_page()
# champion_page()
# week_pages()
# team_pages()
# year_pages()