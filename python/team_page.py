from dominate.tags import *
import pandas as pd
from matplotlib import pyplot as plt

from python import functions, constants, document, page_header

def team_content(team: str, build_figure: bool = False) -> div:
    container = div(_class='content')
    container.add(h1(f'{team} Data'))

    seasons = [functions.summary_table(constants.GAME_DATA, year=year) for year in constants.YEARS]
    seasons_df = pd.concat(seasons)
    seasons_df = seasons_df.loc[seasons_df['Team'] == team].drop('Team', axis = 1)

    summary_div = div(_class='content-container')
    summary_title = h2('Team Summary')
    summary_table = functions.df_to_table(data=seasons_df)
    summary_table['id'] = 'team-summary-table'
    summary_div.add([summary_title, summary_table])

    if build_figure:
        plt.figure(figsize = (5,3), dpi = 300)
        plt.grid(linewidth = 0.5, zorder = 0)
        plt.plot(seasons_df['Year'], seasons_df['Luck Score'], c = constants.COLOR_DICT[team.lower()], marker = 'o', zorder = 3)
        plt.xlabel('Season')
        plt.ylabel('Luck Score')
        plt.savefig(f'Assets/Luck-Score-Year-{team}.svg', format = 'svg', bbox_inches = 'tight')

    line_chart_div = div(_class = 'content-container')
    line_chart_title = h2('Luck Score by Season')
    line_chart_img = img(src = f'{constants.ROOT}Assets/Luck-Score-Year-{team}.svg')
    line_chart_div.add([line_chart_title, line_chart_img])
    
    container.add(summary_div)
    container.add(line_chart_div)

    return container

def team_pages(build_figure: bool = False):
    for team in constants.TEAMS:
        doc = document.document()
        doc.add(page_header.page_header(active_year='team'))

        doc.add(team_content(team=team, build_figure=build_figure))

        with open(f'teams/{team}.html','w') as file:
            file.write(doc.render())