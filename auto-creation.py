import dominate
from dominate.tags import *
import pandas as pd

root = '/fantasy-football-website'


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





def header(active_year: int = None):
    container = div(_class='header')
    logo = img(src=f'{root}/Assets/Fantasy-Football-App-LOGO.png', height=85, style='float: left;')
    heading = h1('Fantasy Football Luck Scores')

    navbar = topnav(active_year=active_year)
    
    container.add(logo)
    container.add(heading)
    container.add(br())
    container.add(navbar)

    return container


def topnav(active_year: int = None):
    container = div(_class='topnav')

    if active_year == 'Home':
        home = div(a('Home', href=f'{root}/'), _class='dropdown active')
    else:
        home = div(a('Home', href=f'{root}/'), _class='dropdown')
    container.add(home)

    years_weeks = [(2019,13), (2020,13), (2021,14), (2022,14), (2023,14), (2024,14)]

    for year, week in years_weeks:
        if active_year == year:
            dropdown = div(_class='dropdown active')
        else:
            dropdown = div(_class='dropdown')
        dropdown_button = a(year, href=f'{root}/{year}/', _class='dropdown-button')
        dropdown.add(dropdown_button)

        dropdown_content = div(_class='dropdown-content')
        for i in range(week):
            _a = a(f'Week {i+1}', href=f'{root}/{year}/week-{i+1}.html')

            dropdown_content.add(_a)

        dropdown.add(dropdown_content)
        container.add(dropdown)

    champions = div(a('Champions', href=f'{root}/champion.html'), _class='dropdown')
    container.add(champions)

    return container


def content(title: str, scoreboard: pd.DataFrame = None, standings: pd.DataFrame = None):
    container = div(_class='content')

    title = h1(title)

    scoreboard_div = div(_class='scoreboard')
    scoreboard_title = h2('Weekly Scoreboard')
    scoreboard_table = df_to_table(data=scoreboard)
    scoreboard_table['id'] = 'scoreboard-table'
    scoreboard_div.add([scoreboard_title, scoreboard_table])

    standings_div = div(_class='standings')
    standings_title = h2('Updated Standings')
    standings_table = df_to_table(data=standings)
    standings_table['id'] = 'standings-table'
    standings_div.add([standings_title, standings_table])

    container.add(title)
    container.add(scoreboard_div)
    container.add(br())
    container.add(standings_div)

    return container



df = pd.read_csv('/Users/serdarevichar/Library/CloudStorage/GoogleDrive-serdarevichar@gmail.com/My Drive/fantasy-football-database.csv', index_col = 'Unnamed: 0')

#print(header(active_year=2019))


def week_pages():
    years = [2019,2020,2021,2022,2023,2024]

    for year in years:
        if year < 2021:
            weeks = 13
        else:
            weeks = 14

        for i in range(weeks):
            # Construct the body of the HTML
            doc = dominate.document(title='Fantasy Football')
            doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))


            # Add in the pieces which make up the general template
            doc.add(header(active_year=year))
            scoreboard = df.loc[(df['Year'] == year) & (df['Week'] == i+1), ['Home Team','Home Score','Away Score','Away Team']].copy()
            standings = df.loc[(df['Year'] == year) & (df['Week'] <= i+1)].copy()

            temp1 = standings[['Home Team','Home Score','Away Score']].copy()
            temp2 = standings[['Away Team','Away Score','Home Score']].copy()

            temp1.rename(columns={'Home Team':'Team', 'Home Score':'Score', 'Away Score':'Opp Score'}, inplace=True)
            temp2.rename(columns={'Away Team':'Team', 'Away Score':'Score', 'Home Score':'Opp Score'}, inplace=True)

            standings_data = pd.concat([temp1,temp2], axis=0, ignore_index=True)
            standings_data['Win'] = standings_data['Score'] > standings_data['Opp Score']
            standings_data['Win'] = standings_data['Win'].map(int)

            teams = standings_data['Team'].unique()
            records = []

            for team in teams:
                wins = standings_data.loc[(standings_data['Team'] == team) & (standings_data['Win'] == 1), 'Win'].sum()
                losses = i + 1 - wins
                points_for = round(standings_data.loc[(standings_data['Team'] == team), 'Score'].sum(), 2)
                points_against = round(standings_data.loc[(standings_data['Team'] == team), 'Opp Score'].sum(), 2)
                records.append([team, wins, losses, points_for, points_against])
            standings = pd.DataFrame(records, columns=['Team','Wins','Losses','Points For','Points Against']).sort_values(['Wins','Points For'], ascending=False)


            doc.add(content(title=f'{year} Week {i+1}', scoreboard=scoreboard, standings=standings))
            doc_string = str(doc)

            with open(f'fantasy-football-website/{year}/week-{i+1}.html','w') as file:
                file.write(doc_string)



def home_page():
    doc = dominate.document(title='Fantasy Football')
    doc.head.add(link(rel='stylesheet', href=f'{root}/style.css'))
    doc.add(header(active_year='Home'))

    content = div(_class='content')
    content.add(h1('Documentation'))

    documentation = object_('Documentation', data='/fantasy-football-website/Assets/Fantasy-Football.pdf', height='1000px', width='90%')
    content.add(documentation)

    doc.add(content)

    with open(f'fantasy-football-website/index.html','w') as file:
        file.write(doc.render())

home_page()


