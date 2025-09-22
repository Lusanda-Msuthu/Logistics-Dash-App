!pip install dash
!pip install dash plotly pandas
!pip install --upgrade dash plotly pandas

import pandas as pd
import dash
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from datetime import datetime
import numpy as np
import pandas as pd
import os

df = pd.read_excel('logistics.xlsx')
df['PlannedDeliveryDate'] = pd.to_datetime(df['PlannedDeliveryDate'])
df['ActualDeliveryDate'] = pd.to_datetime(df['ActualDeliveryDate'])
df['DeliveryDuration'] = (df['ActualDeliveryDate'] - df['PlannedDeliveryDate']).dt.days
df['IsLate'] = df['DeliveryStatus'] == 'Late'
df['IsOnTime'] = df['DeliveryStatus'] == 'On Time'
df['IsEarly'] = df['DeliveryStatus'] == 'Early'
df['Month'] = df['PlannedDeliveryDate'].dt.month_name()
df['Week'] = df['PlannedDeliveryDate'].dt.isocalendar().week

app = dash.Dash(__name__)

light_theme = {
    'background': '#F5F5F7',
    'text': '#2D3748',
    'accent': '#3182CE',
    'card_bg': '#FFFFFF',
    'border': '#E2E8F0',
    'dropdown_bg': '#FFFFFF',
    'dropdown_text': '#2D3748',
    'header_bg': '#4A5568'
}

app.layout = html.Div([
    html.H1("Delivery Efficiency Dashboard", style={'textAlign': 'center', 'color': 'white', 'padding': '20px', 'backgroundColor': light_theme['header_bg']}),
    html.Div([
        html.Div([
            html.H3("Total Deliveries", style={'color': light_theme['text']}),
            html.H2(id='total-deliveries', style={'color': '#38A169'})
        ], style={'textAlign': 'center', 'padding': '15px', 'width': '22%', 'display': 'inline-block', 'backgroundColor': light_theme['card_bg'], 'borderRadius': '10px', 'margin': '5px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
        html.Div([
            html.H3("On-Time Rate", style={'color': light_theme['text']}),
            html.H2(id='on-time-rate', style={'color': '#D69E2E'})
        ], style={'textAlign': 'center', 'padding': '15px', 'width': '22%', 'display': 'inline-block', 'backgroundColor': light_theme['card_bg'], 'borderRadius': '10px', 'margin': '5px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
        html.Div([
            html.H3("Late Deliveries", style={'color': light_theme['text']}),
            html.H2(id='late-deliveries', style={'color': '#E53E3E'})
        ], style={'textAlign': 'center', 'padding': '15px', 'width': '22%', 'display': 'inline-block', 'backgroundColor': light_theme['card_bg'], 'borderRadius': '10px', 'margin': '5px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
        html.Div([
            html.H3("Avg Cost (ZAR)", style={'color': light_theme['text']}),
            html.H2(id='avg-cost', style={'color': '#3182CE'})
        ], style={'textAlign': 'center', 'padding': '15px', 'width': '22%', 'display': 'inline-block', 'backgroundColor': light_theme['card_bg'], 'borderRadius': '10px', 'margin': '5px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '10px'}),
    html.Div([
        html.Div([
            html.Label("Select Destination:", style={'color': light_theme['text'], 'marginBottom': '5px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='destination-filter',
                options=[{'label': 'All Destinations', 'value': 'all'}] + [{'label': dest, 'value': dest} for dest in sorted(df['Destination'].unique())],
                value='all',
                clearable=False,
                style={
                    'backgroundColor': light_theme['dropdown_bg'],
                    'color': light_theme['dropdown_text'],
                    'border': f"1px solid {light_theme['border']}",
                    'borderRadius': '5px'
                }
            )
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        html.Div([
            html.Label("Select Vehicle Type:", style={'color': light_theme['text'], 'marginBottom': '5px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='vehicle-filter',
                options=[{'label': 'All Vehicles', 'value': 'all'}] + [{'label': vehicle, 'value': vehicle} for vehicle in sorted(df['Vehicle'].unique())],
                value='all',
                clearable=False,
                style={
                    'backgroundColor': light_theme['dropdown_bg'],
                    'color': light_theme['dropdown_text'],
                    'border': f"1px solid {light_theme['border']}",
                    'borderRadius': '5px'
                }
            )
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        html.Div([
            html.Label("Select Date Range:", style={'color': light_theme['text'], 'marginBottom': '5px', 'fontWeight': 'bold'}),
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['ActualDeliveryDate'].min(),  
                end_date=df['ActualDeliveryDate'].max(),    
                display_format='YYYY-MM-DD',
                style={'color': light_theme['text'], 'display': 'inline-block'}
            )
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ], style={'padding': '20px', 'backgroundColor': light_theme['card_bg'], 'borderRadius': '10px', 'margin': '10px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)', 'display': 'flex', 'alignItems': 'flex-start'}),
    html.Div([
        html.Div([
            dcc.Graph(id='status-pie-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([
            dcc.Graph(id='destination-efficiency-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='vehicle-performance-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div([
            dcc.Graph(id='time-trend-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='cost-analysis-chart')
        ], style={'width': '100%', 'padding': '10px'})
    ]),
    html.Div([
        dcc.Graph(id='delivery-map')
    ], style={'padding': '10px'}),
    html.Div([
        html.H4("Delivery Data", style={'color': light_theme['text']}),
        html.Div(id='data-table', style={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'auto'})
    ], style={'padding': '10px'})
], style={'backgroundColor': light_theme['background'], 'minHeight': '100vh', 'padding': '20px'})

def format_zar(amount):
    if pd.isna(amount):
        return "R0,00"
    amount = float(amount)
    if amount == 0:
        return "R0,00"
    
    whole_part = int(amount)
    decimal_part = round((amount - whole_part) * 100)
    
    whole_str = f"{whole_part:,}".replace(",", " ")
    
    return f"R{whole_str},{decimal_part:02d}"

@app.callback(
    [Output('total-deliveries', 'children'),
     Output('on-time-rate', 'children'),
     Output('late-deliveries', 'children'),
     Output('avg-cost', 'children')],
    [Input('destination-filter', 'value'),
     Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_kpis(selected_destination, selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) &  
            (filtered_df['ActualDeliveryDate'] <= end_date)      
        ]
    
    total_deliveries = len(filtered_df)
    on_time_count = filtered_df['IsOnTime'].sum()
    on_time_rate = f"{(on_time_count / total_deliveries * 100):.1f}%" if total_deliveries > 0 else "0%"
    late_deliveries = filtered_df['IsLate'].sum()
    
    avg_cost = filtered_df['DeliveyCost'].mean() if total_deliveries > 0 else 0
    avg_cost_formatted = format_zar(avg_cost)
    
    return total_deliveries, on_time_rate, late_deliveries, avg_cost_formatted

@app.callback(
    Output('status-pie-chart', 'figure'),
    [Input('destination-filter', 'value'),
     Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_pie_chart(selected_destination, selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) &  
            (filtered_df['ActualDeliveryDate'] <= end_date)      
        ]
    
    status_counts = filtered_df['DeliveryStatus'].value_counts()
    color_map = {
        'Late': '#E53E3E',
        'On Time': '#38A169',
        'Early': '#D69E2E'
    }
    
    fig = px.pie(values=status_counts.values, names=status_counts.index, title='Delivery Status Distribution', color=status_counts.index, color_discrete_map=color_map)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor=light_theme['card_bg'],
        paper_bgcolor=light_theme['card_bg'],
        font_color=light_theme['text'],
        title_font_color=light_theme['text']
    )
    return fig

@app.callback(
    Output('destination-efficiency-chart', 'figure'),
    [Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_destination_chart(selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) &  
            (filtered_df['ActualDeliveryDate'] <= end_date)      
        ]
    
    destination_stats = filtered_df.groupby('Destination').agg({
        'IsOnTime': 'mean',
        'IsLate': 'mean',
        'IsEarly': 'mean',
        'DeliveryID': 'count'
    }).reset_index()
    
    melted_stats = destination_stats.melt(id_vars=['Destination'], value_vars=['IsOnTime', 'IsLate', 'IsEarly'], var_name='Status', value_name='Percentage')
    
    fig = px.bar(melted_stats, x='Destination', y='Percentage', color='Status', title='Delivery Efficiency by Destination', labels={'Percentage': 'Percentage', 'Destination': 'Destination'}, color_discrete_map={'IsOnTime': '#38A169', 'IsLate': '#E53E3E', 'IsEarly': '#D69E2E'})
    fig.update_layout(
        barmode='stack',
        plot_bgcolor=light_theme['card_bg'],
        paper_bgcolor=light_theme['card_bg'],
        font_color=light_theme['text'],
        title_font_color=light_theme['text']
    )
    return fig

@app.callback(
    Output('vehicle-performance-chart', 'figure'),
    [Input('destination-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_vehicle_chart(selected_destination, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) &  
            (filtered_df['ActualDeliveryDate'] <= end_date)      
        ]
    
    vehicle_stats = filtered_df.groupby('Vehicle').agg({
        'IsOnTime': 'mean',
        'DistanceKM': 'mean',
        'DeliveryID': 'count'
    }).reset_index()
    
    fig = px.scatter(vehicle_stats, x='DistanceKM', y='IsOnTime', size='DeliveryID', color='Vehicle', title='Performance: On-Time Rate vs Distance', labels={'IsOnTime': 'On-Time Delivery Rate', 'DistanceKM': 'Average Distance (KM)'}, hover_data=['Vehicle', 'DistanceKM', 'IsOnTime'])
    fig.update_layout(
        plot_bgcolor=light_theme['card_bg'],
        paper_bgcolor=light_theme['card_bg'],
        font_color=light_theme['text'],
        title_font_color=light_theme['text']
    )
    return fig

@app.callback(
    Output('time-trend-chart', 'figure'),
    [Input('destination-filter', 'value'),
     Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),  
     Input('date-range', 'end_date')]    
)
def update_time_chart(selected_destination, selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) &  
            (filtered_df['ActualDeliveryDate'] <= end_date)     
        ]
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=month_order, ordered=True)
    
    monthly_stats = filtered_df.groupby('Month').agg({
        'IsOnTime': 'mean',
        'IsLate': 'mean',
        'DeliveryID': 'count'
    }).reset_index()
    
    fig = px.line(monthly_stats, x='Month', y=['IsOnTime', 'IsLate'], title='Monthly Delivery Performance Trend', labels={'value': 'Percentage', 'variable': 'Status'}, color_discrete_map={'IsOnTime': '#38A169', 'IsLate': '#E53E3E'})
    fig.update_layout(
        plot_bgcolor=light_theme['card_bg'],
        paper_bgcolor=light_theme['card_bg'],
        font_color=light_theme['text'],
        title_font_color=light_theme['text'],
        xaxis={'tickangle': 270}
    )
    return fig

@app.callback(
    Output('delivery-map', 'figure'),
    [Input('destination-filter', 'value'),
     Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_map(selected_destination, selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) & 
            (filtered_df['ActualDeliveryDate'] <= end_date)      
        ]
    
    map_df = filtered_df.sample(min(30, len(filtered_df)))
    
    fig = px.scatter_geo(map_df, lat='DestLat', lon='DestLon', hover_name='Destination', hover_data=['Origin', 'Vehicle', 'DeliveryStatus'], title='Delivery Destinations Map', projection='natural earth')
    fig.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
    fig.update_layout(
        plot_bgcolor=light_theme['card_bg'],
        paper_bgcolor=light_theme['card_bg'],
        font_color=light_theme['text'],
        title_font_color=light_theme['text']
    )
    return fig

@app.callback(
    Output('cost-analysis-chart', 'figure'),
    [Input('destination-filter', 'value'),
     Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_cost_chart(selected_destination, selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) & 
            (filtered_df['ActualDeliveryDate'] <= end_date)      
        ]
    
    vehicle_cost = filtered_df.groupby('Vehicle').agg({
        'DeliveyCost': 'mean',
        'DeliveryID': 'count'
    }).reset_index()
    
    vehicle_cost['FormattedCost'] = vehicle_cost['DeliveyCost'].apply(format_zar)
    
    fig = px.bar(vehicle_cost, x='Vehicle', y='DeliveyCost',
                 title='Average Delivery Cost by Vehicle Type (ZAR)',
                 labels={'DeliveyCost': 'Average Cost (ZAR)', 'Vehicle': 'Vehicle Type'},
                 hover_data=['FormattedCost', 'DeliveryID'])
    
    fig.update_layout(
        yaxis_tickformat=',.2f',
        plot_bgcolor=light_theme['card_bg'],
        paper_bgcolor=light_theme['card_bg'],
        font_color=light_theme['text'],
        title_font_color=light_theme['text']
    )
    
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Average Cost: %{customdata[0]}<br>Delivery Count: %{customdata[1]}<extra></extra>',
                      customdata=vehicle_cost[['FormattedCost', 'DeliveryID']].values)
    
    return fig

@app.callback(
    Output('data-table', 'children'),
    [Input('destination-filter', 'value'),
     Input('vehicle-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_table(selected_destination, selected_vehicle, start_date, end_date):
    filtered_df = df.copy()
    if selected_destination != 'all':
        filtered_df = filtered_df[filtered_df['Destination'] == selected_destination]
    if selected_vehicle != 'all':
        filtered_df = filtered_df[filtered_df['Vehicle'] == selected_vehicle]
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['ActualDeliveryDate'] >= start_date) &  
            (filtered_df['ActualDeliveryDate'] <= end_date)     
        ]
    
    display_df = filtered_df.copy()
    display_df['DeliveyCost'] = display_df['DeliveyCost'].apply(format_zar)
    display_cols = ['DeliveryID', 'CustomerName', 'Origin', 'Destination', 'Route', 'Vehicle', 'DistanceKM', 'DeliveyCost', 'PlannedDeliveryDate', 'ActualDeliveryDate', 'DeliveryStatus']
    
    return dash.dash_table.DataTable(
        data=display_df[display_cols].to_dict('records'),
        columns=[{'name': col, 'id': col} for col in display_cols],
        page_size=10,
        style_table={'overflowX': 'auto', 'backgroundColor': light_theme['card_bg']},
        style_cell={'textAlign': 'left', 'padding': '5px', 'backgroundColor': light_theme['card_bg'], 'color': light_theme['text'], 'border': f"1px solid {light_theme['border']}"},
        style_header={'backgroundColor': light_theme['accent'], 'fontWeight': 'bold', 'color': 'white'},
        style_data={'border': f"1px solid {light_theme['border']}"}
    )

if __name__ == '__main__':
    app.run(port = 8069, debug=True)
