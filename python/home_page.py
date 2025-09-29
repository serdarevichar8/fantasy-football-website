from dominate.tags import *
import pandas as pd

from python import document, page_header, functions, constants

def home_content(week: int) -> div:
    '''
    Function which creates the home page content

    Includes:
    ---------
    * Documentation PDF
    '''
    container = div(_class='content')
    container.add(h1('Home'))

    payout_df = pd.DataFrame(
        {
            'Position':['1st','2nd','3rd','Reg Szn Champ'],
            'Payout':['$400','$150','$50','$60']
        }
    )
    payout_table = functions.df_to_table(payout_df)
    payout_div = functions.content_container(
        title='2025 Payout Rules',
        content=payout_table
    )

    container.add(payout_div)


    container.add(h2('Weekly Summary'))

    year = 2025

    data = constants.PLAYER_GAME_DATA.loc[(constants.PLAYER_GAME_DATA['Year'] == year) & (constants.PLAYER_GAME_DATA['Week'] == week)].copy()
    data['Proj Diff'] = round(data['Points'] - data['Projected Points'], 2)

    bench_df = data.loc[data['Slot Position'] == 'BE', ['Team','Player','Position','Points']].copy().sort_values('Points', ascending=False).head(5)
    bench_table = functions.df_to_table(data=bench_df, table_id='topScoringBench')
    bench_div = functions.content_container(title='Highest Scoring Bench Players', content=bench_table)

    under_df = data.loc[data['Slot Position'] != 'BE', ['Team','Player','Slot Position','Proj Diff']].copy().sort_values('Proj Diff', ascending=True).reset_index(drop=True).head(5)
    under_table = functions.df_to_table(data=under_df, table_id='topUnderPerformers')
    under_div = functions.content_container(title='Top Under Performers', content=under_table)

    over_df = data.loc[data['Slot Position'] != 'BE', ['Team','Player','Slot Position','Proj Diff']].copy().sort_values('Proj Diff', ascending=False).reset_index(drop=True).head(5)
    over_table = functions.df_to_table(data=over_df, table_id='topOverPerformers')
    over_div = functions.content_container(title='Top Over Performers', content=over_table)
    
    container.add(bench_div)
    container.add(under_div)
    container.add(over_div)

    return container

def home_page(week: int):
    doc = document.document()
    doc.add(page_header.page_header(active_year='home'))

    doc.add(home_content(week=week))
    doc.add(script(src=f'{constants.ROOT}script.js'))

    with open('index.html','w') as file:
        file.write(doc.render())