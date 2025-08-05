from dominate.tags import *
import pandas as pd
from matplotlib import pyplot as plt

from python import functions, constants, document, page_header

def team_content(team: str, build_figure: bool = False) -> div:
    container = div(_class='content')
    container.add(h1(f'{team} Data'))

    seasons = [functions.summary_table(constants.GAME_DATA, year=year) for year in constants.YEARS]
    seasons_df = pd.concat(seasons)
    seasons_df = seasons_df.loc[seasons_df['Team'] == team]
    seasons_table = functions.df_to_table(
        data=seasons_df,
        custom_columns=['Year','Record','Ranking','Points For','Points Against','Avg Points For','Avg Margin','Luck Score'],
        table_id='team-summary-table'
    )
    summary_div = functions.content_container(
        title='Team Summary',
        content=seasons_table
    )

    if build_figure:
        plt.figure(figsize = (5,3), dpi = 300)
        plt.grid(linewidth = 0.5, zorder = 0)
        plt.plot(seasons_df['Year'], seasons_df['Luck Score'], c = constants.COLOR_DICT[team.lower()], marker = 'o', zorder = 3)
        plt.xlabel('Season')
        plt.ylabel('Luck Score')
        plt.savefig(f'Assets/Luck-Score-Year-{team}.svg', format = 'svg', bbox_inches = 'tight')

    line_chart_div = functions.content_container(title='Luck Score by Season', content=img(src = f'{constants.ROOT}Assets/Luck-Score-Year-{team}.svg'))
    
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

def team_pages(build_figure: bool = False):
    for team in constants.TEAMS:
        doc = document.document()
        doc.add(page_header.page_header(active_year='team'))

        doc.add(team_content(team=team, build_figure=build_figure))
        doc.add(script(src=f'{constants.ROOT}script.js'))

        with open(f'teams/{team}.html','w') as file:
            file.write(doc.render())