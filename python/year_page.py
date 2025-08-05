import dominate
from dominate.tags import *
from matplotlib import pyplot as plt

from python import functions, constants, document, page_header

def year_content(year: int, build_figure: bool = False) -> div:
    container = div(_class='content')
    container.add(h1(f'{year} Data'))

    data = functions.summary_table(constants.GAME_DATA, year = year)
    data = data.drop('Year', axis = 1)

    s = [(team, pf, pa, constants.COLOR_DICT[team.lower()]) for team, pf, pa in zip(data['Team'], data['Points For'], data['Points Against'])]

    if build_figure:
        plt.figure(figsize = (5,3), dpi = 300)
        plt.grid(linewidth = 0.5, zorder = 0)
        for team, pf, pa, color in s:
            plt.scatter(pf, pa, c = color, label = team, zorder = 3, edgecolor = 'k')
        plt.xlim(int(data['Points For'].min() - 4) - (int(data['Points For'].min()-4) % 25),
                int(data['Points For'].max() + 4) + 25 - (int(data['Points For'].max() + 4) % 25)) # Automatically finds nearest 25 below/above for range
        plt.ylim(int(data['Points Against'].min() - 4) - (int(data['Points Against'].min() - 4) % 25),
                int(data['Points Against'].max() + 4) + 25 - (int(data['Points Against'].max() + 4) % 25))
        plt.xlabel('Points For')
        plt.ylabel('Points Against')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize = 9)
        plt.savefig(f'Assets/PF-vs-PA-{year}.svg', format = 'svg',bbox_inches = 'tight')

    scatter_div = functions.content_container(title='PF vs PA', content=img(src = f'{constants.ROOT}Assets/PF-vs-PA-{year}.svg'))

    summary_table = functions.df_to_table(
        data=data,
        table_id='season-summary-table'
    )
    summary_div = functions.content_container(
        title='Regular Season Summary',
        content=summary_table
    )

    playoff_matchups = constants.MATCHUP_DATA.loc[(constants.MATCHUP_DATA['Year'] == year) & (constants.MATCHUP_DATA['Playoff Flag'])].copy()
    playoff_matchups['Playoff Round'] = (playoff_matchups['Week'] % playoff_matchups['Week'].min()) + 1

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

    bracket_div = functions.content_container(title='Playoff Bracket', content=bracket)

    draft_data = constants.DRAFT_DATA.loc[constants.DRAFT_DATA['Year'] == year].copy()
    draft_table = functions.df_to_table(
        data=draft_data,
        row_id_columns=['Team','Round','Pick'],
        table_id='league-draft-table'
    )
    draft_div = functions.content_container(
        title='League Draft',
        content=draft_table,
        filter_id='draft-filter',
        filter_column=draft_data['Team'],
        filter_showall=True
    )

    container.add(summary_div)
    container.add(scatter_div)
    container.add(bracket_div)
    container.add(draft_div)

    return container


def year_pages(build_figure: bool = False):
    for year in constants.YEARS:
        doc = document.document()
        doc.add(page_header.page_header(active_year=year))

        doc.add(year_content(year, build_figure=build_figure))
        doc.add(script(src=f'{constants.ROOT}script.js'))

        with open(f'seasons/{year}/index.html','w') as file:
            file.write(doc.render())