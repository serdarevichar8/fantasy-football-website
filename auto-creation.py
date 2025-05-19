import dominate
from dominate.tags import *
import pandas as pd

def header():
    container = div(_class='header')
    logo = img(src='/Assets/Fantasy-Football-App-LOGO.png', height=85, style='float: left;')
    heading = h1('Fantasy Football Luck Scores')
    
    container.add(logo)
    container.add(heading)

    return container



def topnav(years: list):
    container = div(_class='topnav')

    home = a('Home', href='/')
    container.add(home)


    for year in years:
        dropdown = div(_class='dropdown')
        _a = a(year, href=f'/{year}/', _class='dropdown-button')
        dropdown.add(_a)

        for i in range(5):
            _a = a(f'Week {i+1}', href=f'/{year}/week-{i+1}.html')

            dropdown.add(_a)

        container.add(dropdown)


    

    return container


#print(header())

doc = body(header())
doc.add(topnav(years=[2023]))

df = pd.DataFrame({'A':[1,2,3], 'B':[4,3,2]})

result = df.to_html()


print(doc, result)