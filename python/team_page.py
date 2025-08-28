from dominate.tags import *
import pandas as pd
from matplotlib import pyplot as plt

from python import functions, constants, document, page_header

def team_content(team: str) -> div:
    container = div(_class='content')
    container.add(h1(f'{team} Data'))

    seasons = [functions.summary_table(constants.GAME_DATA, year=year) for year in constants.YEARS]
    seasons_df = pd.concat(seasons)
    seasons_df = seasons_df.loc[seasons_df['Team'] == team]
    seasons_table = functions.df_to_table(
        data=seasons_df,
        custom_columns=['Year','Record','Ranking','Points For','Points Against','PF/G+','Avg Margin','Luck Score'],
        table_id='team-summary-table',
        champ_class=True
    )
    summary_div = functions.content_container(
        title='Team Summary',
        content=seasons_table
    )

    line_chart_svg = functions.df_to_svg(
        data=seasons_df,
        x_col='Year',
        y_col='Luck Score',
        chart_type='bar',
        x_tick_spacing=1,
        y_tick_spacing=2
    )
    line_chart_div = functions.content_container(
        title='Luck Score by Season',
        content=line_chart_svg
    )
    
    draft_data = constants.DRAFT_DATA.loc[constants.DRAFT_DATA['Team'] == team].copy()
    draft_table = functions.df_to_table(
        data=draft_data,
        row_id_columns=['Year','Round','Pick'],
        table_id='league-draft-table'
    )
    draft_div = functions.content_container(
        title='League Draft',
        content=draft_table,
        filter_id='draft-filter',
        filter_column=draft_data['Year']
    )

    container.add(summary_div)
    container.add(line_chart_div)
    container.add(draft_div)

    return container

def team_pages():
    for team in constants.TEAMS:
        doc = document.document()
        doc.add(page_header.page_header(active_year='team'))

        doc.add(team_content(team=team))
        doc.add(script(src=f'{constants.ROOT}script.js'))

        with open(f'teams/{team}.html','w') as file:
            file.write(doc.render())