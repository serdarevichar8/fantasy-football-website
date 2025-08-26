from dominate.tags import *
import pandas as pd

from python import functions, constants, document, page_header

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

    champions = []
    for year in constants.YEARS:
        data = functions.summary_table(data=constants.GAME_DATA, year=year)
        champions.append(data.loc[data['Champ Flag'] == 1])

    champions_df = pd.concat(champions)

    summary_div = functions.content_container(
        title='Champions Summary',
        content=functions.df_to_table(
            data=champions_df,
            custom_columns=['Year','Team','Record','Points For','PF/G','PF/G+','Avg Margin','Luck Score'],
            table_id='champion-summary-table')
    )

    container.add(summary_div)

    return container

def champion_page():
    doc = document.document()
    doc.add(page_header.page_header(active_year='champion'))

    doc.add(champion_content())

    with open('champion.html','w') as file:
        file.write(doc.render())