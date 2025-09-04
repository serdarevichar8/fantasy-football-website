from dominate.tags import *
import pandas as pd

from python import document, page_header, functions

def home_content() -> div:
    '''
    Function which creates the home page content

    Includes:
    ---------
    * Documentation PDF
    '''
    container = div(_class='content')
    container.add(h1('Home'))

    draft_order_df = pd.DataFrame(
        {
            'Team':['Andrew','Dante','Noah','Haris','Stolarz','McGwire','Nathan','Ethan','Michael','Kevin','Carter','Tyler'],
            'Pick':[1,2,3,4,5,6,7,8,9,10,11,12]
        }
    )
    draft_order_table = functions.df_to_table(draft_order_df)
    draft_order_div = functions.content_container(
        title='2025 Draft Order',
        content=draft_order_table
    )
    
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

    container.add(draft_order_div)
    container.add(payout_div)

    return container

def home_page():
    doc = document.document()
    doc.add(page_header.page_header(active_year='home'))

    doc.add(home_content())

    with open('index.html','w') as file:
        file.write(doc.render())