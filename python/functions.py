import pandas as pd
import numpy as np
import dominate
from dominate.tags import *
from dominate.svg import *

from python import constants

def df_to_table(
        data: pd.DataFrame,
        custom_columns: list[str] = None,
        row_id_columns: list[str] = None,
        table_id: str = None,
        champ_class: bool = False
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

    table_id : str, default None
        ID to be assigned to the main table tag. If set to None, no ID will be given.

    champ_class : bool, default False

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
        if champ_class:
            if record['Champ Flag'] == 1:
                data_row['class'] = 'champ'
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

    champ_week = data.loc[data['Year'] == year, 'Week'].max()
    if champ_week > 14:
        champ = data.loc[(data['Year'] == year) & (data['Week'] == champ_week) & (data['Win'] == 1), 'Team'].item()
    else:
        champ = None

    league_pfpg = round(temp['Score'].mean(), 2)

    temp_teams = temp['Team'].unique()
    weekly_standings = []

    for team in temp_teams:
        temp_team = temp.loc[temp['Team'] == team]
        wins = temp_team['Win'].sum()
        losses = temp_team['Win'].eq(0).sum()
        record = f'{wins}-{losses}'

        pf = round(temp_team['Score'].sum(), 2)
        pfpg = round(temp_team['Score'].mean(), 2)
        pfpg_plus = int(pfpg / league_pfpg * 100)
        pa = round(temp_team['Opp Score'].sum(), 2)
        papg = round(temp_team['Opp Score'].mean(), 2)
        papg_plus = int(papg / league_pfpg * 100)
        avg_margin = round((pf - pa) / len(temp_team), 2)
        luck_score = temp_team['Luck Score'].sum()

        champ_flag = int(champ == team)

        weekly_standings.append(
            {
                'Week':week,
                'Year':year,
                'Team':team,
                'Wins':wins,
                'Losses':losses,
                'Record':record,
                'Points For':pf,
                'Points Against':pa,
                'PF/G':pfpg,
                'PF/G+':pfpg_plus,
                'PA/G':papg,
                'PA/G+':papg_plus,
                'Avg Margin':avg_margin,
                'Luck Score':luck_score,
                'Champ Flag':champ_flag
            }
        )

    weekly_standings = pd.DataFrame(weekly_standings)
    weekly_standings.sort_values(['Wins','Points For'], ascending=False, ignore_index=True, inplace=True)
    weekly_standings['Ranking'] = [i + 1 for i in weekly_standings.index]

    return weekly_standings

def round_min(value, rounding, min_distance=0.1):
    rounded = np.floor(value / rounding) * rounding

    if value - rounded < rounding * min_distance:
        rounded -= rounding

    return int(rounded)

def round_max(value, rounding, min_distance=0.1):
    rounded = np.ceil(value / rounding) * rounding

    if rounded - value < rounding * min_distance:
        rounded += rounding

    return int(rounded)

def write_path(x_values, y_values, close=False):
    '''
    Writes the d argument for an SVG <path/> element using lists of x and y values
    '''
    if len(x_values) != len(y_values):
        raise ValueError('x_values and y_values must be of the same length')
    
    length = len(x_values)

    d = []

    for i in range(length):
        prefix = 'M' if i == 0 else 'L'
        d.append(f'{prefix}{x_values[i]},{y_values[i]}')

    if close:
        d.append('Z')

    return ' '.join(d)

def calculate_limits(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        x_tick_spacing: int,
        y_tick_spacing: int,
        include_zero: bool = False
):
    # Find the actual min and max of x and y values
    x_min, x_max = data[x_col].min(), data[x_col].max()
    y_min, y_max = data[y_col].min(), data[y_col].max()

    # Round the min/max values down/up to the nearest round number according to the tick spacing
    # If actual min/max is equal to (or within 10% of) rounded value, then will go one step further
    x_limit_min, x_limit_max = round_min(x_min, rounding=x_tick_spacing), round_max(x_max, rounding=x_tick_spacing)
    y_limit_min, y_limit_max = round_min(y_min, rounding=y_tick_spacing), round_max(y_max, rounding=y_tick_spacing)

    if include_zero:
        y_limit_min = 0 if y_limit_min >= 0 else y_limit_min
        y_limit_max = 0 if y_limit_max <= 0 else y_limit_max

    xlim = (x_limit_min, x_limit_max)
    ylim = (y_limit_min, y_limit_max)

    return xlim, ylim

def calculate_ticks(
        xlim: tuple,
        ylim: tuple,
        x_tick_spacing: int,
        y_tick_spacing: int
):
    x_limit_min, x_limit_max = xlim
    y_limit_min, y_limit_max = ylim

    x_ticks = [(i * x_tick_spacing) + x_limit_min for i in range(int((x_limit_max - x_limit_min) / x_tick_spacing) + 1)]
    y_ticks = [(i * y_tick_spacing) + y_limit_min for i in range(int((y_limit_max - y_limit_min) / y_tick_spacing) + 1)]

    return x_ticks, y_ticks

def df_to_svg(
        data: pd.DataFrame, 
        x_col: str, 
        y_col: str,
        chart_type: str = 'scatter',
        width: int = 500, 
        height: int = 300,
        x_tick_spacing: int = 50,
        y_tick_spacing: int = 50
):

    # margin x and y from edges of visual
    m_top, m_bottom, m_left, m_right = 10, 50, 60, 10
    # plot width and height
    P_x, P_y = width - m_left - m_right, height - m_top - m_bottom
    # tick margin (distance between axes and tick label)
    m_tick = 5

    # Bring in x and y ticks from calculate_ticks function
    include_zero = True if chart_type == 'bar' else False
    xlim, ylim = calculate_limits(data=data, x_col=x_col, y_col=y_col, x_tick_spacing=x_tick_spacing, y_tick_spacing=y_tick_spacing, include_zero=include_zero)
    # if 'ylim' in kwargs:
    #     ylim = kwargs.pop('ylim')

    x_limit_min, x_limit_max = xlim
    y_limit_min, y_limit_max = ylim

    x_ticks, y_ticks = calculate_ticks(xlim=xlim, ylim=ylim, x_tick_spacing=x_tick_spacing, y_tick_spacing=y_tick_spacing)

    d_svg = svg(
        xmlns='http://www.w3.org/2000/svg',
        width=width,
        height=height,
        viewBox=f'0 0 {width} {height}'
    )

    outer_group = g(
        font_family='Arial',
        font_size=10,
        text_anchor='middle',
        dominant_baseline='hanging'
    )
    d_svg.add(outer_group)

    border = write_path([0, width, width, 0], [0, 0, height, height], close=True)
    border_path = path(d=border, fill='white', _id='border')
    outer_group.add(border_path)

    

    xlabel_group = g()

    grid_path_d = []
    for i, xtick in enumerate(x_ticks):
        if i == 0 or i == (len(x_ticks) - 1):
            continue
        x = round(m_left + (xtick - x_limit_min) / (x_limit_max - x_limit_min) * P_x, 3)

        gridline = write_path([x, x], [m_top, height - m_bottom])
        grid_path_d.append(gridline)

        xtick_label = text(
            xtick,
            x=x,
            y=height - m_bottom + m_tick
        )
        xlabel_group.add(xtick_label)

    outer_group.add(xlabel_group)

    ylabel_group = g(
        text_anchor='end',
        dominant_baseline='middle'
    )
    zero_grid_path = False
    zero_ytick = False
    for ytick in y_ticks:
        y = round((height - m_bottom) - (ytick - y_limit_min) / (y_limit_max - y_limit_min) * P_y, 3)

        gridline = write_path([m_left, width - m_right], [y, y])
        grid_path_d.append(gridline)

        ytick_label = text(
            ytick,
            x=m_left - m_tick,
            y=y
        )
        ylabel_group.add(ytick_label)


        if ytick == 0:
            zero_grid_path = path(d=gridline, stroke='black')
            zero_ytick = y

    outer_group.add(ylabel_group)

    grid_path = path(
        d=' '.join(grid_path_d),
        stroke='lightgrey'
    )
    outer_group.add(grid_path)
    if zero_grid_path:
        outer_group.add(zero_grid_path)

    axis_title_group = g(font_size=16)
    outer_group.add(axis_title_group)
    xlabel = text(
        x_col,
        x=(P_x / 2 + m_left),
        y=(height - (m_bottom / 2))
    )
    ylabel = text(
        y_col,
        x=10,
        y=(P_y / 2 + m_top),
        transform=f'rotate(-90, {10}, {P_y / 2 + m_top})'
    )

    axis_title_group.add([xlabel, ylabel])
    axes = write_path([m_left, width - m_right, width - m_right, m_left], [m_top, m_top, height - m_bottom, height - m_bottom], close=True)
    axes_path = path(d=axes, fill='none', stroke='black', _id='axes')
    outer_group.add(axes_path)

    x_points = []
    y_points = []
    circles_group = g(
        stroke='black',
        stroke_width=1.5
    )
    bars_group = g(stroke='black')
    for index, row in data.iterrows():
        v_x = round(m_left + ((row[x_col] - x_limit_min) / (x_limit_max - x_limit_min) * (P_x)), 3)
        v_y = round((height - m_bottom) - ((row[y_col] - y_limit_min) / (y_limit_max - y_limit_min) * (P_y)), 3)

        bar_y = v_y if row[y_col] > 0 else zero_ytick
        bar_height = zero_ytick - v_y if row[y_col] > 0 else v_y - zero_ytick
        bar_width = 25

        bars_group.add(
            rect(
                x=v_x - bar_width / 2,
                y=bar_y,
                width=bar_width,
                height=bar_height,
                fill=constants.COLOR_DICT[row['Team'].lower()]
            )
        )
        circles_group.add(circle(cx=v_x, cy=v_y, r=4, fill=constants.COLOR_DICT[row['Team'].lower()]))
        
        x_points.append(v_x)
        y_points.append(v_y)


    if chart_type == 'line':
        line = write_path(x_points, y_points)
        line_path = path(d=line, fill='none', stroke='black')
        outer_group.add(line_path)

    if chart_type in ['scatter','line']:
        outer_group.add(circles_group)

    if chart_type == 'bar':
        outer_group.add(bars_group)

    return d_svg