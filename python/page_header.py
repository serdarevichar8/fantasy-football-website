import dominate
from dominate.tags import *

from python import constants

def page_header(active_year: int = None) -> div:
    '''
    Creates the blue header div, adds in the logo and heading at the top

    Takes an input for the active page in the navbar. This is passed directly to topnav()
    
    Parameters
    ----------
    active_year : int
        The active page to be highlighted in navbar (deprecated naming)
    
    Returns
    -------
    div
        div container for the entire header
    '''
    container = div(_class='header')
    logo = img(src=f'{constants.ROOT}Assets/Fantasy-Football-App-LOGO.png', height=85, style='float: left;padding: 0px 20px')
    heading = h1('Fantasy Football Luck Scores')

    navbar = topnav(active_year=active_year)
    
    container.add(logo)
    container.add(heading)
    container.add(br())
    container.add(navbar)

    return container


def topnav(active_year: int = None) -> div:
    '''
    Creates the navbar with dropdowns. Called by the header() function

    Parameters
    ----------
    active_year : int
        Active page to be highlighted by the navbar (deprecated naming convention)

    Returns
    -------
    div
        div container for navbar
    '''
    container = div(_class='topnav')

    if active_year == 'home':
        home = div(a('Home', href=f'{constants.ROOT}'), _class='dropdown active')
    else:
        home = div(a('Home', href=f'{constants.ROOT}'), _class='dropdown')
    container.add(home)

    for year, week in constants.YEARS_WEEKS:
        if active_year == year:
            dropdown = div(_class='dropdown active')
        else:
            dropdown = div(_class='dropdown')
        dropdown_button = a(year, href=f'{constants.ROOT}seasons/{year}/', _class='dropdown-button')
        dropdown.add(dropdown_button)

        dropdown_content = div(_class='dropdown-content')
        for i in range(week):
            _a = a(f'Week {i+1}', href=f'{constants.ROOT}seasons/{year}/week-{i+1}.html')

            dropdown_content.add(_a)

        dropdown.add(dropdown_content)
        container.add(dropdown)

    if active_year == 'team':
        team_dropdown = div(_class='dropdown active')
    else:
        team_dropdown = div(_class='dropdown')
    team_dropdown_button = a('Teams', href=f'{constants.ROOT}teams/', _class='dropdown-button')
    team_dropdown.add(team_dropdown_button)

    team_dropdown_content = div(_class='dropdown-content')
    for team in constants.TEAMS:
        _a = a(f'{team}', href=f'{constants.ROOT}teams/{team}.html')

        team_dropdown_content.add(_a)

    team_dropdown.add(team_dropdown_content)
    container.add(team_dropdown)

    if active_year == 'champion':
        champions = div(a('Champions', href=f'{constants.ROOT}champion.html'), _class='dropdown active')
    else:
        champions = div(a('Champions', href=f'{constants.ROOT}champion.html'), _class='dropdown')
    container.add(champions)

    return container