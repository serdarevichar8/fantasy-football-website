import dominate
from dominate.tags import *
import pandas as pd



def df_to_table(data: pd.DataFrame):
    t = table()
    head = thead()
    body = tbody()

    for column in data.columns:
        head.add(th(column))
    
    for row in data.values:
        r = tr()
        for value in row:
            r.add(td(value))
        body.add(r)

    t.add(head)
    t.add(body)

    return t


def header():
    container = div(_class='header')
    logo = img(src='/Assets/Fantasy-Football-App-LOGO.png', height=85, style='float: left;')
    heading = h1('Fantasy Football Luck Scores')
    
    container.add(logo)
    container.add(heading)

    return container



def topnav(years_weeks: list[(int,int)]):
    container = div(_class='topnav')

    home = a('Home', href='/')
    container.add(home)



    for year, week in years_weeks:
        dropdown = div(_class='dropdown')
        dropdown_button = a(year, href=f'/{year}/', _class='dropdown-button')
        dropdown.add(dropdown_button)

        dropdown_content = div(_class='dropdown-content')
        for i in range(week):
            _a = a(f'Week {i+1}', href=f'/{year}/week-{i+1}.html')

            dropdown_content.add(_a)

        dropdown.add(dropdown_content)
        container.add(dropdown)

    champions = a('Champions', href='champion.html')
    container.add(champions)

    return container

def content(title: str, scoreboard: pd.DataFrame):
    container = div(_class='content')

    title = h1(title)

    scoreboard_div = div(_class='scoreboard')
    scoreboard_title = h2('Weekly Scoreboard')
    scoreboard_table = df_to_table(data=scoreboard)
    scoreboard_table['id'] = 'scoreboard-table'
    scoreboard_div.add([scoreboard_title, scoreboard_table])

    container.add(title)
    container.add(scoreboard_div)

    return container


# Construct the body of the HTML
doc = dominate.document(title='Fantasy Football')
doc.head.add(link(rel='stylesheet', href='style.css'))


# Add in the pieces which make up the general template
doc.add(header())
doc.add(topnav(years_weeks=[(2019,13), (2020,13), (2021,14), (2022,14), (2023,14), (2024,14)]))
#doc.add(topnav(years_weeks=[(2024,4)]))

df = pd.read_csv('/Users/serdarevichar/Library/CloudStorage/GoogleDrive-serdarevichar@gmail.com/My Drive/fantasy-football-database.csv', index_col = 'Unnamed: 0')
scoreboard = df.loc[(df['Year'] == 2019) & (df['Week'] == 1), ['Home Team','Home Score','Away Score','Away Team']].copy()

doc.add(content(title='2019 Week 1', scoreboard=scoreboard))

doc_string = str(doc)


with open('test.html','w') as file:
    file.write(doc_string)