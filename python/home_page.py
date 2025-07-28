from dominate.tags import *

from python import document, page_header

def home_content() -> div:
    '''
    Function which creates the home page content

    Includes:
    ---------
    * Documentation PDF
    '''
    container = div(_class='content')
    container.add(h1('Documentation'))

    documentation = object_('Documentation', data='/fantasy-football-website/Assets/Fantasy-Football.pdf', height='1000px', width='90%')
    container.add(documentation)

    return container

def home_page():
    doc = document.document()
    doc.add(page_header.page_header(active_year='home'))

    doc.add(home_content())

    with open('index.html','w') as file:
        file.write(doc.render())