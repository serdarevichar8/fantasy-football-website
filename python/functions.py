import pandas as pd
import numpy as np
import dominate
from dominate.tags import *

def df_to_table(data: pd.DataFrame, index_to_id: bool = False, table_id: str = None) -> table:
    t = table()
    head = thead()
    body = tbody()

    column_row = tr()
    for column in data.columns:
        column_row.add(th(column))
    head.add(column_row)
    
    for label, row in zip(data.index, data.values):
        r = tr(__pretty=False)
        if index_to_id:
            r['id'] = label
        for value in row:
            r.add(td(value))
        body.add(r)

    t.add(head)
    t.add(body)
    if table_id:
        t['id'] = table_id

    if len(data) > 20:
        scroll_div = div(_class='scroll-table')
        scroll_div.add(t)
        return scroll_div

    return t

def content_container(title: str, content: div | table | img, _id: str = None):
    container = div(_class='content-container')
    container_title = h2(title)
    container_content = content
    if _id:
        container_content['id'] = _id

    container.add(container_title, container_content)

    return container

def opp_luck_score(opp_score, mean=None, std=None) -> int:
    return int(((mean - opp_score) / np.absolute(mean - opp_score)) * np.floor(np.absolute(mean - opp_score) / std))

def your_luck_score(your_score, opp_score, mean=None, std=None) -> int:
    xi = lambda x: np.floor((mean + x) / (2*mean))
    result = int(your_score > opp_score)
    return int(np.floor(np.absolute(mean - your_score) / std) * (result * xi(2*mean - your_score) - (1-result) * xi(your_score)))
    
def close_luck_score(your_score, opp_score) -> int:
    close_game_flag = int(abs(your_score - opp_score) < 3)
    win_flag = int(your_score > opp_score)
    loss_flag = -int(your_score < opp_score)

    return (close_game_flag * win_flag) + (close_game_flag * loss_flag)

def summary_table(data: pd.DataFrame, year: int, week: int = None) -> pd.DataFrame:
    temp = data.loc[(data['Year'] == year) & (data['Playoff Flag'] == False)].copy()

    if week != None:
        temp = temp.loc[(data['Week'] <= week)]

    mean = temp['Score'].mean()
    std = temp['Score'].std() * 0.5

    opp_luck = []
    your_luck = []
    close_luck = []

    for your_score, opp_score in temp[['Score','Opp Score']].values:
        opp_luck.append(opp_luck_score(opp_score=opp_score, mean=mean, std=std))
        your_luck.append(your_luck_score(your_score=your_score, opp_score=opp_score, mean=mean, std=std))
        close_luck.append(close_luck_score(your_score=your_score, opp_score=opp_score))

    temp['Opp Luck Score'] = opp_luck
    temp['Your Luck Score'] = your_luck
    temp['Close Luck Score'] = close_luck

    temp['Luck Score'] = temp[['Opp Luck Score','Your Luck Score','Close Luck Score']].sum(axis=1)

    temp_teams = temp['Team'].unique()
    weekly_standings = []

    for team in temp_teams:
        temp_team = temp.loc[temp['Team'] == team]
        wins = temp_team['Win'].sum()
        losses = temp_team['Win'].eq(0).sum()
        record = f'{wins}-{losses}'

        pf = round(temp_team['Score'].sum(), 2)
        avg_pf = round(pf / len(temp_team), 2)
        pa = round(temp_team['Opp Score'].sum(), 2)
        avg_margin = round((pf - pa) / len(temp_team), 2)
        luck_score = temp_team['Luck Score'].sum()

        weekly_standings.append([team, wins, record, pf, pa, avg_pf, avg_margin, luck_score])

    weekly_standings = pd.DataFrame(weekly_standings, columns=['Team','Wins','Record', 'Points For','Points Against','Avg Points For','Avg Margin','Luck Score'])
    weekly_standings.sort_values(['Wins','Points For'], ascending=False, ignore_index=True, inplace=True)
    weekly_standings['Ranking'] = [i + 1 for i in weekly_standings.index]
    weekly_standings['Year'] = year
    weekly_standings = weekly_standings[['Year','Team','Record','Ranking','Points For','Points Against','Avg Points For','Avg Margin','Luck Score']]

    return weekly_standings