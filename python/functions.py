import pandas as pd
import numpy as np
import dominate
from dominate.tags import *

def df_to_table(
        data: pd.DataFrame,
        custom_columns: list[str] = None,
        row_id_columns: list[str] = None,
        table_id: str = None
) -> table:
    '''
    Converts a pandas DataFrame into an HTML table with optional styling.

    If dataframe is longer than 20 rows, table will be wrapped in a "scroll-table" div.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to be converted.

    custom_columns : list[str], default None
        Columns to be displayed in the HTML table. If set to None, all columns in DataFrame will be used.

    row_id_columns : list[str], default None
        ID to be assigned to each tr tag in the tbody.
        Accepts a list of columns, will concatenate them starting with 'row' and separating with '-'.
        If set to None, no IDs will be assigned.

    table_id : str[str], default None
        ID to be assigned to the main table tag. If set to None, no ID will be given.

    Returns
    -------
    dominate.table or dominate.div
        Return a dominate HTML object. Can be either a table or div
    '''
    t = table()
    head = thead()
    body = tbody()

    records = data.to_dict('records')

    columns = data.columns
    if custom_columns:
        columns = custom_columns

    column_row = tr()
    for column in columns:
        column_row.add(th(column, _class=str(column).lower().replace(' ','-')))
    head.add(column_row)
    
    for record in records:
        data_row = tr(__pretty=False)
        if row_id_columns:
            row_id = 'row'
            for column in row_id_columns:
                row_id += ('-' + str(record[column]).lower().replace(' ',''))
            data_row['id'] = row_id

        for column in columns:
            data_row.add(td(record[column], _class=str(column).lower().replace(' ','-')))
        body.add(data_row)

    t.add(head)
    t.add(body)
    if table_id:
        t['id'] = table_id

    if len(data) > 20:
        scroll_div = div(_class='scroll-table')
        scroll_div.add(t)
        return scroll_div

    return t

def content_container(
        title: str,
        content: div | table | img,

        filter_id: str = None,
        filter_column: pd.Series = None,
        filter_showall: bool = False
) -> div:
    '''
    Creates a div with class "content-container," including an h2 title tag and content. Optionally may include a dropdown filter if content is a table.

    Parameters
    ----------
    title : str
        Name to be set as the title for the content bubble.

    content : div | table | img
        General content that will be added to the body of the bubble. May be any of the following:
            * div
            * table
            * img

    filter_id : str, default None
        ID to be given to dropdown filter.

    filter_column : pd.Series, default None
        Series from the DataFrame used for content table. Should always be set to the first column in row_id_columns argument in df_to_table().
    
    filter_showall : bool, default False
        Choose whether filter dropdown features All as an option.

    Returns
    -------
    div
        Return a dominate div object. 
    '''
    container = div(_class='content-container')
    container_title = h2(title)

    if filter_id:
        container_select_options = [option(record, value=str(record).lower().replace(' ','')) for record in filter_column.unique()]
        if filter_showall:
            container_select_options.insert(0, option('All', value='all'))

        if type(content) == table:
            table_id = content['id']
        else:
            table_id = content.get(table)[0]['id']
        container_select = select(container_select_options,
                                  _id=filter_id,
                                  onchange=f"tableFilter('{filter_id}', '{table_id}')")
        container_title.add(container_select)

    container_content = content

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