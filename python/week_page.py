from dominate.tags import *
import numpy as np

from python import functions, constants, document, page_header

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
    scoreboard = constants.MATCHUP_DATA.loc[(constants.MATCHUP_DATA['Year'] == year) & (constants.MATCHUP_DATA['Week'] == week), ['Home Team','Home Score','Away Score','Away Team']].copy()    
    scoreboard_div = functions.content_container(title='Weekly Scoreboard', content=functions.df_to_table(data=scoreboard), _id='scoreboard-table')
    
    # scoreboard_div = div(_class='content-container')
    # scoreboard_title = h2('Weekly Scoreboard')
    # scoreboard_table = functions.df_to_table(data=scoreboard)
    # scoreboard_table['id'] = 'scoreboard-table'
    # scoreboard_div.add([scoreboard_title, scoreboard_table])

    # Create the weekly recap stats section
    # This temp df needs to look at only the current week
    temp = constants.GAME_DATA.loc[(constants.GAME_DATA['Year'] == year) & (constants.GAME_DATA['Week'] == week)].copy()


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
    standings = functions.summary_table(constants.GAME_DATA, year = year, week = week)
    standings = standings.drop('Year', axis = 1)

    standings_div = functions.content_container(title='Updated Standings', content=functions.df_to_table(data=standings), _id='standings-table')

    # standings_div = div(_class='content-container')
    # standings_title = h2('Updated Standings')
    # standings_table = functions.df_to_table(data=standings)
    # standings_table['id'] = 'standings-table'
    # standings_div.add([standings_title, standings_table])

    container.add(title)
    container.add(scoreboard_div)
    container.add(br())
    container.add(stats_div)
    container.add(br())
    container.add(standings_div)

    return container

def week_pages():
    years = np.arange(2019, 2025)

    for year in years:
        if year < 2021:
            weeks = np.arange(1,14)
        else:
            weeks = np.arange(1,15)

        for week in weeks:
            doc = document.document()
            doc.add(page_header.page_header(active_year=year))

            doc.add(week_content(year=year, week=week))

            with open(f'seasons/{year}/week-{week}.html','w') as file:
                file.write(doc.render())