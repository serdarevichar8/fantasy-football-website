import dominate
from dominate.tags import *


from python import constants
# Only use the below import when debugging this file directly
# import constants

def document() -> dominate.document:
    doc = dominate.document(title='Fantasy Football')
    doc.head.add(link(rel='stylesheet', href=f'{constants.ROOT}style.css'))
    doc.head.add(link(rel='icon', type='image/png', href=f'{constants.ROOT}Assets/Fantasy-Football-App-LOGO.png'))

    return doc