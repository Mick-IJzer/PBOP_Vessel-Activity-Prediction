import os
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
import datetime as dt
from dash.dependencies import Input, Output, State

# OS configuration
PATH_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_DATA = os.path.join(PATH_DIR, 'data')

# Initialise data
port_info = pd.read_csv(os.path.join(PATH_DATA, 'port_info.csv'))
port_info['port_lat'] = round(port_info['port_lat'],2)
port_info['port_long'] = round(port_info['port_long'],2)
port_info['unique_port_identifier'] = port_info['unique_port_identifier'].str.replace('.0','')
model = pd.read_csv(os.path.join(PATH_DATA, 'DSS_input.csv'))
model['port_lat'] = round(model['port_lat'],2)
model['port_long'] = round(model['port_long'],2)
model["exit_datetime"] = model["exit_datetime"].astype("datetime64")
model["target_entry_datetime"] = model["target_entry_datetime"].astype("datetime64")
model["target_exit_datetime"] = model["target_exit_datetime"].astype("datetime64")

# Define default parameters for the worldmap graph
map_data = [
    go.Scattermapbox(
        lat = model['port_lat'],
        lon = model['port_long'],
        text = model['mmsi'],
        hoverinfo = 'text+lon+lat',
        mode = 'markers',
        marker = go.scattermapbox.Marker(
            size=5
        )
    )
]

map_layout = go.Layout(
    mapbox_style = "carto-darkmatter",
    margin = dict(t=0, b=0, l=0, r=0),
    mapbox = dict(
        zoom = 0.9,
        center = dict (lat=20, lon=0)
    ),
    hovermode = 'closest'
)

fig = {
    'data': map_data,
    'layout': map_layout
}

#Creating the app
app = dash.Dash(__name__)

# Define dashboard layout containing all output elements
app.layout = html.Div(
    children = [
        html.Div([
            html.H1('DSS Vessel Activity Prediction'),
            html.Img(src = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSG1gk65adlP_Bhd2-UPuUOv7YV8xFo49ip9g&usqp=CAU')
        ], className = 'banner'),

        html.Div([
            dcc.Tabs(id='tab_selection', value='tab-1', className='Tabs',children=[
                dcc.Tab(label='Find Vessel', value = 'tab-1', className='Tab'),
                dcc.Tab(label='Find Port', value = 'tab-2', className='Tab')
            ])
        ]),

        html.Br(),
        html.Label(children = 'Search for an MMSI:',className='Label_search', id = 'label'),

        dcc.Dropdown(
            id = 'dropdown',
            className = 'Dropdown',
            options = [{'label': i,'value': i} for i in model['mmsi'].unique()],
            placeholder = "Select an MMSI"
        ),   

        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        id = 'worldmap',
                        figure = fig)
                ],className = "col-md-6"
                ),
                html.Div(
                    id = 'output_table',
                    className = "col-md-6"
                ),
            ], className="row"),
            html.Div(
                id = 'ports_figure'
            )
        ], className="container-fluid")
    ]
)

# Define the callback functions to make the dashboard interactive
@app.callback(
    Output('output_table','children'),
    Output('ports_figure','children'),
    Input('dropdown','value'),
    State('tab_selection','value')
)
def update_output(dropdown_value,selected_tab):
    ''' This function updates the information of the output table and output figure 
        when there occurs a change in the dropdown element. '''
    if selected_tab == 'tab-1':
        if dropdown_value:
            df_mmsi = model[model.mmsi == dropdown_value]
            head = go.Figure(data = [go.Table(
                header = dict(
                    values = [[
                        'MMSI',
                        'Departed From',
                        'Country',
                        'Time of Departure'
                    ],[
                        dropdown_value,
                        df_mmsi.portname,
                        df_mmsi.country,
                        df_mmsi.exit_datetime
                    ]],
                    font_size = 16,
                    height = 40,
                    line_color = 'navy'
                )
            )],
                layout = go.Layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height = 200
            ))

            table = go.Figure(data = [go.Table(
                header = dict(
                    values = [[
                        'Traveling to',
                        'Country',
                        'Time of Arrival',
                        'Duration of Stay in Hours',
                        'Time of departure'],
                        [df_mmsi.target_portname,
                        df_mmsi.target_port_country,
                        df_mmsi.target_entry_datetime,
                        df_mmsi.target_stay_duration.round(2),
                        df_mmsi.target_exit_datetime]],
                    font_size = 16,
                    height = 40,
                    line_color = 'navy'
                    ))],
                layout = go.Layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height = 200
            ))
            return html.Div(children = [
                html.H1('Vessel Information', className = "Label"),
                dcc.Graph(figure = head, className = "Table"),
                html.H1('Predictions', className = "Label"),
                dcc.Graph(figure = table, className = "Table")
            ]),None
        else:
            return None, None
    else:
        if dropdown_value:
            df_port = port_info[port_info.unique_port_identifier == dropdown_value]
            table = go.Figure(
                data = [go.Table(
                    header = dict(
                        values = [[
                            'Port Name',
                            'Country',
                            'Country Code',
                            'Port Type',
                            'Port Size'
                            ],
                            [
                            df_port.portname,
                            df_port.country,
                            df_port.iso3,
                            df_port.prttype,
                            df_port.prtsize                                
                            ]],
                        font_size = 16,
                        height = 30,
                        line_color = 'navy'
                        )
                    )],
                layout = go.Layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height = 200
            )
                )
            port_model = model[model.unique_target_port_identifier == dropdown_value]
            port_model['arrival_date'] = port_model['target_entry_datetime'].dt.floor('d')
            port_model['departure_date'] = port_model['target_exit_datetime'].dt.floor('d')
            port_model_1 = port_model.arrival_date.value_counts().rename_axis('arrival_date').to_frame('arrival_count')
            port_model_2 = port_model.departure_date.value_counts().rename_axis('departure_date').to_frame('departure_count')            
            port_model = pd.concat([port_model_1,port_model_2], axis=1).fillna(0)

            port_fig = go.Figure()
            port_fig.add_trace(go.Bar(x=port_model.index.to_list(),
                y=port_model['arrival_count'].to_list(),
                name='arrival_count',
                marker_color='rgb(55, 83, 109)'
                ))
            port_fig.add_trace(go.Bar(x=port_model.index.to_list(),
                y=port_model['departure_count'].to_list(),
                name='departure_count',
                marker_color='rgb(26, 118, 255)'
                ))

            port_fig.update_layout(
                title='<b>Expected Number of Arrivals and Departures per Day</b>',
                xaxis_tickfont_size=14,
                yaxis=dict(
                    title='Expected Number',
                    titlefont_size=16,
                    tickfont_size=14,
                ),
                xaxis=dict(
                    title='Date',
                    titlefont_size=16,
                    tickfont_size=14,
                ),
                legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                barmode='group',
                bargap=0.15,
                bargroupgap=0.1 
            )
            return html.Div(children = [
                    html.H1('Port Information', className = "Label"),
                    dcc.Graph(
                        figure = table, className = "Table"
                    )
                ]), dcc.Graph(figure = port_fig)
        else:
            return None, None

@app.callback(
    Output('label','children'),
    Output('dropdown','options'),
    Output('dropdown','placeholder'),
    Output('dropdown','value'),
    Input('tab_selection','value')
)
def reset_dropdown(selected_tab):
    ''' This function resets the dropdown options and clears dropdown selection as soon as 
        the user switches the tab. '''
    if selected_tab == 'tab-1':
        label_value = 'Search for an MMSI:'
        dropdown_options = [{'label': i,'value': i} for i in model['mmsi'].unique()]
        dropdown_placeholder = "Select an MMSI"
    else:
        label_value = 'Search for a Port:'
        dropdown_options = [{'label': i,'value': i} for i in port_info['unique_port_identifier'].unique()]
        dropdown_placeholder = "Select a Port"
    return label_value, dropdown_options, dropdown_placeholder, None


@app.callback(
    Output('worldmap','figure'),
    Input('dropdown','value'),
    State('tab_selection', 'value')
)
def give_dashboard(dropdown_value,selected_tab):
    ''' This function updates the worldmap graph when there occurs a change in the dropdown element.'''
    if selected_tab == 'tab-1':
        if dropdown_value:
            df_mmsi = model[model.mmsi == dropdown_value]
            mmsi_map_data = [
                go.Scattermapbox(
                    lat = df_mmsi['port_lat'].append(df_mmsi['target_port_lat']) ,
                    lon = df_mmsi['port_long'].append(df_mmsi['target_port_long']),
                    text = df_mmsi['mmsi'],
                    hoverinfo='text+lon+lat',
                    mode='markers',
                    marker = go.scattermapbox.Marker(
                        size = 10,
                        color = ['blue','red']
                    )
                    
                )
            ]
            mmsi_fig = {
                'data' : mmsi_map_data,
                'layout' : map_layout
            }
            return mmsi_fig
        else:
            mmsi_map_data = [
                go.Scattermapbox(
                    lat=model['port_lat'],
                    lon=model['port_long'],
                    text=model['mmsi'],
                    hoverinfo='text+lon+lat',
                    mode='markers'
                )
            ]

            mmsi_fig = {
                'data': mmsi_map_data,
                'layout': map_layout
            }
        return mmsi_fig
    else:
        if dropdown_value:
            df_port = port_info[port_info.unique_port_identifier == dropdown_value]
            port_map_data = [
                go.Scattermapbox(
                    lat = df_port['port_lat'],
                    lon = df_port['port_long'],
                    text = df_port['portname'],
                    hoverinfo='text+lon+lat',
                    mode='markers',
                    marker = go.scattermapbox.Marker(
                        size = 10,
                        color = 'red'
                    )
                )
            ]
            port_fig = {
                'data' : port_map_data,
                'layout' : map_layout
            }
            return port_fig
        else:
            port_map_data = [
                go.Scattermapbox(
                    lat=port_info['port_lat'],
                    lon=port_info['port_long'],
                    text=port_info['portname'],
                    hoverinfo='text+lon+lat',
                    mode='markers',
                    marker = go.scattermapbox.Marker(
                        size = 5,
                        color = 'red'
                    )
                )
            ]

            port_fig = {
                'data': port_map_data,
                'layout': map_layout
            }
            return port_fig
    return port_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=2021)