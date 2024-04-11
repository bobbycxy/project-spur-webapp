import boto3
import pandas as pd
import numpy as np
import creds
from dash import Dash, dcc, html, Input, Output
import plotly.express as px


db_client = boto3.resource('dynamodb',aws_access_key_id=creds.AWS_ACCESS_KEY,aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY)

def get_data(table_name, db_client):
    data = pd.DataFrame(db_client.Table(table_name).scan()['Items'])
    return data

attendance = get_data('attendance',db_client)
members = get_data('person',db_client)

df = attendance[['event_type','cell_group','date_attended']].drop_duplicates().merge(members[['cell_group','role','name']], on = ['cell_group'], how = 'outer')
df = df.merge(attendance, on = ['event_type','cell_group','date_attended','name'], how = 'left')
df['attendance_type'] = np.where(df['attendance_type'].isna(), 'Absent Invalid', df['attendance_type'])

colors = {
    'background': '#FFFFFF',
    'text': '#111111'
}

app = Dash(__name__)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children = [
    
    html.Div([

        html.H1('POD Youth Ministry Attendance Dashboard')

    ], style={
        'padding': '5px 10px'
    }),

    html.Div([

        html.Div([
            html.P('Select cell group:'),
            dcc.Dropdown(
                id = 'select_cell_group',
                options = ['ALL'] + list(df['cell_group'].unique()),
                value = 'ALL',
                clearable=False
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.P('Select event type:'),
            dcc.Dropdown(
                id = 'select_event_type',
                options = ['ALL'] + list(df['event_type'].unique()),
                value = 'ALL',
                clearable=False
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})

    ], style={
        'padding': '0px 10px'
    }),

    html.Div([

        html.Div([
            html.P('Select attendance type:'),
            dcc.Dropdown(
                id = 'select_attendance_type',
                options = ['ALL'] + list(df['attendance_type'].unique()),
                value = 'ALL',
                clearable=False
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.P('Select role:'),
            dcc.Dropdown(
                id = 'select_role',
                options = ['ALL'] + list(df['role'].unique()),
                value = 'ALL',
                clearable=False
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        
    ], style={
        'padding': '20px 10px'
    }),

    html.Hr(),
    
    html.Div([

        html.Div([
            dcc.Graph(id = 'table1')
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id = 'table2')
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        
    ], style={
        'padding': '5px 10px'
    }),
    dcc.Graph(id = 'heatmap1'),
    dcc.Graph(id = 'barplot1'),
    dcc.Graph(id = 'barplot2'),
])


@app.callback(
    Output('table1','figure'),
    Input('select_cell_group', 'value'),
    Input('select_event_type', 'value'),
    Input('select_attendance_type', 'value'),
    Input('select_role', 'value'),)
def display_cell_group(cell_group, event_type, attendance_type, role):
    if cell_group == 'ALL':
        cell_group = df['cell_group'].unique()
    else:
        cell_group = [cell_group]

    if event_type == 'ALL':
        event_type = df['event_type'].unique()
    else:
        event_type = [event_type]

    if attendance_type == 'ALL':
        attendance_type = df['attendance_type'].unique()
    else:
        attendance_type = [attendance_type]

    if role == 'ALL':
        role = df['role'].unique()
    else:
        role = [role]

    filtered_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['attendance_type'].isin(list(attendance_type)))&
        (df['role'].isin(list(role)))
    ]

    temp = filtered_df.groupby(['date_attended']).agg({'name':'count'}).reset_index()
    
    x = ['']
    y = ['']
    z = [[0.0]]

    z_text = [[round(temp['name'].mean(),0)]]

    fig = px.imshow(z, x=x, y=y, color_continuous_scale='BrBG', aspect = 'auto')#, color_continuous_scale='Viridis', aspect="auto")
    fig.update_traces(text=z_text, texttemplate="%{text}")
    fig.update_xaxes(side="top")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(font=dict(size=18))

    fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    xaxis_tickangle=-45,
    title_text='Average Attendance',
    height = 200
    )
    
    return fig


@app.callback(
    Output('table2','figure'),
    Input('select_cell_group', 'value'),
    Input('select_event_type', 'value'),
    Input('select_attendance_type', 'value'),
    Input('select_role', 'value'),)
def display_cell_group(cell_group, event_type, attendance_type, role):
    if cell_group == 'ALL':
        cell_group = df['cell_group'].unique()
    else:
        cell_group = [cell_group]

    if event_type == 'ALL':
        event_type = df['event_type'].unique()
    else:
        event_type = [event_type]

    if attendance_type == 'ALL':
        attendance_type = df['attendance_type'].unique()
    else:
        attendance_type = [attendance_type]

    if role == 'ALL':
        role = df['role'].unique()
    else:
        role = [role]

    filtered_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['attendance_type'].isin(list(attendance_type)))&
        (df['role'].isin(list(role)))
    ]

    temp = filtered_df.groupby(['date_attended']).agg({'name':'count'}).reset_index().sort_values('date_attended').iloc[-3:,:]
    
    x = ['']
    y = ['']
    z = [[0.0]]

    z_text = [[round(temp['name'].mean(),0)]]

    fig = px.imshow(z, x=x, y=y, color_continuous_scale='BrBG', aspect = 'auto')#, color_continuous_scale='Viridis', aspect="auto")
    fig.update_traces(text=z_text, texttemplate="%{text}")
    fig.update_xaxes(side="top")
    fig.update_coloraxes(showscale=False)
    fig.update_layout(font=dict(size=18))

    fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    xaxis_tickangle=-45,
    title_text='L3W Average Attendance',
    height = 200
    )
    
    return fig


@app.callback(
    Output('heatmap1','figure'),
    Input('select_cell_group', 'value'),
    Input('select_event_type', 'value'),
    Input('select_attendance_type', 'value'),
    Input('select_role', 'value'),)
def display_cell_group(cell_group, event_type, attendance_type, role):
    if cell_group == 'ALL':
        cell_group = df['cell_group'].unique()
    else:
        cell_group = [cell_group]

    if event_type == 'ALL':
        event_type = df['event_type'].unique()
    else:
        event_type = [event_type]

    if attendance_type == 'ALL':
        attendance_type = df['attendance_type'].unique()
    else:
        attendance_type = [attendance_type]

    if role == 'ALL':
        role = df['role'].unique()
    else:
        role = [role]

    filtered_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['attendance_type'].isin(list(attendance_type)))&
        (df['role'].isin(list(role)))
    ]

    filtered_df['week_number'] = pd.to_datetime(filtered_df['date_attended']).dt.isocalendar().week

    test = filtered_df.groupby(['event_type','week_number']).agg({'name':'count'}).reset_index().sort_values('week_number')

    values = test.pivot(index='event_type',columns='week_number',values='name').values
    y = test['event_type'].unique()
    x = ['CW '+ value for value in test['week_number'].unique().astype(str)]

    fig = px.imshow(values, x=x, y=y, color_continuous_scale='BuGn', aspect="auto")
    fig.update_traces(text = values, texttemplate="%{text}")
    fig.update_xaxes(side="top")

    fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    xaxis_tickangle=-45
    )
    
    return fig


@app.callback(
    Output('barplot1','figure'),
    Input('select_cell_group', 'value'),
    Input('select_event_type', 'value'),
    Input('select_attendance_type', 'value'),
    Input('select_role', 'value'),)
def display_cell_group(cell_group, event_type, attendance_type, role):
    if cell_group == 'ALL':
        cell_group = df['cell_group'].unique()
    else:
        cell_group = [cell_group]

    if event_type == 'ALL':
        event_type = df['event_type'].unique()
    else:
        event_type = [event_type]

    if attendance_type == 'ALL':
        attendance_type = df['attendance_type'].unique()
    else:
        attendance_type = [attendance_type]

    if role == 'ALL':
        role = df['role'].unique()
    else:
        role = [role]

    filtered_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['attendance_type'].isin(list(attendance_type)))&
        (df['role'].isin(list(role)))
    ]

    denominator_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['role'].isin(list(role)))
    ]

    temp = filtered_df.groupby(['date_attended','cell_group']).agg({'name':'count'}).reset_index()
    denom = denominator_df.groupby(['date_attended','cell_group']).agg({'name':'count'}).reset_index()

    res = temp.merge(denom, on = ['date_attended','cell_group'], how = 'outer')
    res.fillna(0.0, inplace = True)
    res['percentage'] = round(res['name_x']/res['name_y']*100,1)

    fig = px.bar(res, x="date_attended",  y = 'name_x',
                 labels={'name_x':'Count',
                         'date_attended':'Date'},
                 text_auto=True,
                 color = 'cell_group')
    # fig.add_bar(res, x='date_attended', y='percentage')

    fig.update_layout(
    # plot_bgcolor=colors['background'],
    # paper_bgcolor=colors['background'],
    font_color=colors['text'],
    xaxis_tickangle=-45
    )
    
    return fig



@app.callback(
    Output('barplot2','figure'),
    Input('select_cell_group', 'value'),
    Input('select_event_type', 'value'),
    Input('select_attendance_type', 'value'),
    Input('select_role', 'value'),)
def display_cell_group(cell_group, event_type, attendance_type, role):
    if cell_group == 'ALL':
        cell_group = df['cell_group'].unique()
    else:
        cell_group = [cell_group]

    if event_type == 'ALL':
        event_type = df['event_type'].unique()
    else:
        event_type = [event_type]

    if attendance_type == 'ALL':
        attendance_type = df['attendance_type'].unique()
    else:
        attendance_type = [attendance_type]

    if role == 'ALL':
        role = df['role'].unique()
    else:
        role = [role]

    filtered_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['attendance_type'].isin(list(attendance_type)))&
        (df['role'].isin(list(role)))
    ].copy()

    denominator_df = df[
        (df['cell_group'].isin(list(cell_group)))&
        (df['event_type'].isin(list(event_type)))&
        (df['role'].isin(list(role)))
    ].copy()

    temp = filtered_df.groupby(['date_attended']).agg({'name':'count'}).reset_index()
    denom = denominator_df.groupby(['date_attended']).agg({'name':'count'}).reset_index()

    res = temp.merge(denom, on = 'date_attended', how = 'outer')
    res.fillna(0.0, inplace = True)
    res['percentage'] = round(res['name_x']/res['name_y']*100,1)
    res['type'] = 'Percent'

    fig = px.bar(res, x="date_attended",  y = 'percentage',
                 hover_data=['date_attended'],
                 labels={'percentage':'Percentage',
                         'date_attended':'Date'},
                 text_auto=True,
                 color = 'type')

    fig.update_layout(
    # plot_bgcolor=colors['background'],
    # paper_bgcolor=colors['background'],
    font_color=colors['text'],
    xaxis_tickangle=-45
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)