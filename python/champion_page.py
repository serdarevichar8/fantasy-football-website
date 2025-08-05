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
    
    champions = constants.GAME_DATA.loc[(constants.GAME_DATA['Week'] == 17) & (constants.GAME_DATA['Win'] == 1), ['Year','Team']].values
    data = []
    for year, team in champions:
        temp = constants.GAME_DATA.loc[(constants.GAME_DATA['Year'] == year) & (constants.GAME_DATA['Team'] == team) & (constants.GAME_DATA['Playoff Flag'] == False)]
        wins = temp['Win'].sum()
        losses = len(temp) - wins
        record = f'{wins}-{losses}'

        pf = round(temp['Score'].sum(), 2)
        avg_pf = round(pf / len(temp), 2)
        pa = round(temp['Opp Score'].sum(), 2)
        avg_margin = round((pf - pa) / len(temp), 2)

        data.append([year, team, record, pf, avg_pf, avg_margin])

    t = pd.DataFrame(data, columns=['Year','Team','Record','Points For','Avg Points For','Avg Margin'])

    summary_div = functions.content_container(title='Champions Summary', content=functions.df_to_table(data=t, table_id='champion-summary-table'))

    # summary_div = div(_class='content-container')
    # summary_title = h2('Champions Summary')
    # summary_table = functions.df_to_table(data=t)
    # summary_table['id'] = 'champion-summary-table'
    # summary_div.add([summary_title, summary_table])

    years_div = div(_class='champion-years')
    for year, team in champions:
        years_div.add(h3(f'{year} Season'))
        years_div.add(p(team))

    container.add(summary_div)
    container.add(years_div)

    return container

def champion_page():
    doc = document.document()
    doc.add(page_header.page_header(active_year='champion'))

    doc.add(champion_content())

    with open('champion.html','w') as file:
        file.write(doc.render())