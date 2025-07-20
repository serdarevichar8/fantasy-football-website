import dominate
from dominate.tags import *

ROOT = '/fantasy-football-website/'

class Document(dominate.document):
    def __init__(self, title):
        super().__init__(title)

        self.head.add(link(rel='stylesheet', href=f'{ROOT}style.css'))
        self.head.add(link(rel='icon', type='image/png', href=f'{ROOT}Assets/Fantasy-Football-App-LOGO.png'))

    def print_html(self):
        print(self.render())

    def write_html(self):
        pass
    


d = Document('Fantasy Football')

d.add(div(p('test')))

d.print_html()
