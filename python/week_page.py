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
    scoreboard_div = functions.content_container(
        title='Weekly Scoreboard',
        content=functions.df_to_table(
            data=scoreboard,
            table_id='scoreboard-table'
        )
    )

    lineup_data = constants.PLAYER_MATCHUP_DATA.loc[(constants.PLAYER_MATCHUP_DATA['Year'] == year) & (constants.PLAYER_MATCHUP_DATA['Week'] == week)].copy()
    lineup_data['Matchup Lookup'] = lineup_data['Home Team'].astype(str) + ' vs ' + lineup_data['Away Team'].astype(str)
    lineup_table = functions.df_to_table(
        data=lineup_data,
        custom_columns=['Home Team','Home Player','Home Player Points','Position','Away Player Points','Away Player','Away Team'],
        row_id_columns=['Matchup Lookup','Position'],
        table_id='lineup-table'
    )
    lineup_div = functions.content_container(
        title='Lineups',
        content=lineup_table,
        filter_id='lineup-filter',
        filter_column=lineup_data['Matchup Lookup']
    )

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
    standings_table = functions.df_to_table(
        data=standings,
        custom_columns=['Team','Record','Ranking','Points For','Points Against','Avg Points For','Avg Margin','Luck Score'],
        table_id='standings-table'
    )
    standings_div = functions.content_container(
        title='Updated Standings',
        content=standings_table,
    )

    container.add(title)
    container.add(scoreboard_div)
    container.add(lineup_div)
    container.add(stats_div)
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
            doc.add(script(src=f'{constants.ROOT}script.js'))

            with open(f'seasons/{year}/week-{week}.html','w') as file:
                file.write(doc.render())