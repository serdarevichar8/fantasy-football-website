import dominate
from dominate.tags import *
from matplotlib import pyplot as plt

from python import functions, constants, document, page_header

def year_content(year: int) -> div:
    container = div(_class='content')
    container.add(h1(f'{year} Data'))

    data = functions.summary_table(constants.GAME_DATA, year = year)

    scatter_svg = functions.df_to_svg(
        data=data,
        x_col='Points For',
        y_col='Points Against',
        chart_type='scatter'
    )
    scatter_div = functions.content_container(
        title='PF vs PA',
        content=scatter_svg
    )

    summary_table = functions.df_to_table(
        data=data,
        custom_columns=['Team','Record','Ranking','Points For','Points Against','PF/G+','Avg Margin','Luck Score'],
        table_id='season-summary-table',
        champ_class=True
    )
    summary_div = functions.content_container(
        title='Regular Season Summary',
        content=summary_table
    )

    # playoff_matchups = constants.MATCHUP_DATA.loc[(constants.MATCHUP_DATA['Year'] == year) & (constants.MATCHUP_DATA['Playoff Flag'])].copy()
    # playoff_matchups['Playoff Round'] = (playoff_matchups['Week'] % playoff_matchups['Week'].min()) + 1

    # bracket = main(_id='playoff-bracket')

    # rounds = []

    # for round in playoff_matchups['Playoff Round'].unique():
    #     _ul = ul(_class=f'round round-{round}')
    #     _ul.add(li(dominate.util.raw('&nbsp;'), _class='spacer'))

    #     for team1, score1, team2, score2 in playoff_matchups.loc[playoff_matchups['Playoff Round'] == round, ['Home Team','Home Score','Away Team','Away Score']].values:

    #         top_team = li(team1, _class='game game-top')
    #         if team1 != 'Bye':
    #             top_team.add(span(score1))

    #         bot_team = li(team2, _class='game game-bottom')
    #         if team2 != 'Bye':
    #             bot_team.add(span(score2))

    #         _ul.add(top_team)
    #         _ul.add(li(dominate.util.raw('&nbsp;'), _class='game game-spacer'))
    #         _ul.add(bot_team)
    #         _ul.add(li(dominate.util.raw('&nbsp;'), _class='spacer'))

    #     rounds.append(_ul)

    # bracket.add(rounds)

    if year < 2025:
        bracket = functions.playoff_bracket_svg(constants.MATCHUP_DATA, year=year)
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
    if year < 2025:
        container.add(bracket_div)
    container.add(draft_div)

    return container


def year_pages():
    for year in constants.YEARS:
        doc = document.document()
        doc.add(page_header.page_header(active_year=year))

        doc.add(year_content(year))
        doc.add(script(src=f'{constants.ROOT}script.js'))

        with open(f'seasons/{year}/index.html','w') as file:
            file.write(doc.render())