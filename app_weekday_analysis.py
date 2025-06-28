import os
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, dash_table

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

filtered_df = None

df['transaction_date'] = pd.to_datetime(df['trans_date_trans_time'])
df['day_of_week'] = df['transaction_date'].dt.dayofweek
day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
             4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
df['day_of_week'] = df['day_of_week'].map(day_names)

daily_stats = df.groupby('day_of_week').agg({
    'is_fraud': ['count', 'sum'],
    'amt': ['mean', 'sum']
}).reset_index()

daily_stats.columns = ['Day', 'Total_Transactions', 'Total_Frauds', 'Avg_Amount', 'Total_Amount']
daily_stats['Fraud_Rate'] = (daily_stats['Total_Frauds'] / daily_stats['Total_Transactions'] * 100).round(2)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_stats['Day'] = pd.Categorical(daily_stats['Day'], categories=day_order, ordered=True)
daily_stats = daily_stats.sort_values('Day')

def create_fraud_histogram(data_df):
    fig = px.histogram(data_df, x='day_of_week', color='is_fraud',
                       category_orders={'day_of_week': day_order},
                       title='Fraud Occurrence by Day of the Week',
                       labels={'day_of_week': 'Day of the Week', 'count': 'Number of Transactions'},
                       barmode='group',
                       opacity=0.8,
                       height=500,
                       color_discrete_map={0: 'lightblue', 1: 'orange'})
    
    fig.for_each_trace(lambda t: t.update(name='Normal' if t.name == '0' else 'Fraud'))
    
    fig.update_layout(legend_title_text='Transaction Type')
    
    return fig

def create_fraud_rate_chart(data_df):
    filtered_daily_stats = data_df.groupby('day_of_week').agg({
        'is_fraud': ['count', 'sum'],
        'amt': ['mean', 'sum']
    }).reset_index()
    
    filtered_daily_stats.columns = ['Day', 'Total_Transactions', 'Total_Frauds', 'Avg_Amount', 'Total_Amount']
    filtered_daily_stats['Fraud_Rate'] = (filtered_daily_stats['Total_Frauds'] / filtered_daily_stats['Total_Transactions'] * 100).round(2)
    
    filtered_daily_stats['Day'] = pd.Categorical(filtered_daily_stats['Day'], categories=day_order, ordered=True)
    filtered_daily_stats = filtered_daily_stats.sort_values('Day')
    
    fig = px.line(filtered_daily_stats, x='Day', y='Fraud_Rate',
                  title='Fraud Rate by Day of Week',
                  markers=True,
                  line_shape='spline',
                  height=400)
    fig.update_traces(line_color='orange', marker_size=8)
    fig.update_layout(yaxis_title='Fraud Rate (%)')
    return fig

def create_amount_analysis(data_df):
    fraud_amounts = data_df[data_df['is_fraud'] == 1].groupby('day_of_week')['amt'].mean().reset_index()
    normal_amounts = data_df[data_df['is_fraud'] == 0].groupby('day_of_week')['amt'].mean().reset_index()
    
    fig = go.Figure()
    
    if not fraud_amounts.empty:
        fig.add_trace(go.Bar(x=fraud_amounts['day_of_week'], y=fraud_amounts['amt'],
                             name='Fraud Avg Amount', marker_color='#27ae60', opacity=0.7))
    if not normal_amounts.empty:
        fig.add_trace(go.Bar(x=normal_amounts['day_of_week'], y=normal_amounts['amt'],
                             name='Normal Avg Amount', marker_color='lightblue', opacity=0.7))
    
    fig.update_layout(title='Average Transaction Amount by Day',
                      xaxis_title='Day of Week',
                      yaxis_title='Average Amount ($)',
                      barmode='group',
                      height=400)
    return fig

def create_heatmap(data_df):
    df_temp = data_df.copy()
    df_temp['hour'] = df_temp['transaction_date'].dt.hour
    heatmap_data = df_temp.groupby(['day_of_week', 'hour'])['is_fraud'].sum().reset_index()
    
    heatmap_pivot = heatmap_data.pivot(index='hour', columns='day_of_week', values='is_fraud')
    
    for day in day_order:
        if day not in heatmap_pivot.columns:
            heatmap_pivot[day] = 0
    
    heatmap_pivot = heatmap_pivot.reindex(columns=day_order)
    heatmap_pivot = heatmap_pivot.fillna(0)  
    
    fig = px.imshow(heatmap_pivot.T, 
                    title='Fraud Heatmap: Day vs Hour',
                    labels=dict(x="Hour", y="Day", color="Fraud Count"),
                    aspect="auto",
                    color_continuous_scale='Blues',
                    height=400)
    return fig

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("Fraud Detection Dashboard - Day of Week Analysis", 
               style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#2c3e50'})
    ]),
    
    html.Div(id='stats-cards', style={'marginBottom': '30px'}),
    
    html.Div([
        html.Div([
            html.H5("Visualization Controls", style={'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Label("Select Chart Type:", style={'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='chart-type-dropdown',
                        options=[
                            {'label': 'Fraud Histogram', 'value': 'histogram'},
                            {'label': 'Fraud Rate Line Chart', 'value': 'line'},
                            {'label': 'Amount Analysis', 'value': 'amount'},
                            {'label': 'Fraud Heatmap', 'value': 'heatmap'}
                        ],
                        value='histogram'
                    )
                ], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("Day Filter:", style={'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='day-filter',
                        options=[{'label': 'All Days', 'value': 'all'}] + 
                                [{'label': day, 'value': day} for day in day_order],
                        value=['all'],
                        multi=True
                    )
                ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ])
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'border': '1px solid #dee2e6', 
                 'borderRadius': '5px', 'marginBottom': '30px'})
    ]),
    
    html.Div([
        dcc.Graph(id='main-chart')
    ], style={'marginBottom': '30px'}),
    
    html.Div([
        html.H4("Daily Statistics Table", style={'marginBottom': '15px'}),
        html.Div(id='stats-table-container')
    ])
], style={'margin': '20px'})

@app.callback(
    [Output('main-chart', 'figure'),
     Output('stats-cards', 'children'),
     Output('stats-table-container', 'children')],
    [Input('chart-type-dropdown', 'value'),
     Input('day-filter', 'value')]
)
def update_dashboard(chart_type, day_filter):
    global filtered_df
    
    filtered_df = df.copy()
    
    if day_filter != ['all'] and isinstance(day_filter, list) and len(day_filter) > 0:
        filtered_df = filtered_df[filtered_df['day_of_week'].isin(day_filter)]
    
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No data available for selected filters")
        return empty_fig, html.Div("No data available"), html.Div("No data available")
    
    filtered_daily_stats = filtered_df.groupby('day_of_week').agg({
        'is_fraud': ['count', 'sum'],
        'amt': ['mean', 'sum']
    }).reset_index()
    
    filtered_daily_stats.columns = ['Day', 'Total_Transactions', 'Total_Frauds', 'Avg_Amount', 'Total_Amount']
    filtered_daily_stats['Fraud_Rate'] = (filtered_daily_stats['Total_Frauds'] / filtered_daily_stats['Total_Transactions'] * 100).round(2)
    
    filtered_daily_stats['Day'] = pd.Categorical(filtered_daily_stats['Day'], categories=day_order, ordered=True)
    filtered_daily_stats = filtered_daily_stats.sort_values('Day')
    
    if chart_type == 'histogram':
        fig = create_fraud_histogram(filtered_df)
    elif chart_type == 'line':
        fig = create_fraud_rate_chart(filtered_df)
    elif chart_type == 'amount':
        fig = create_amount_analysis(filtered_df)
    elif chart_type == 'heatmap':
        fig = create_heatmap(filtered_df)
    
    total_transactions = filtered_daily_stats['Total_Transactions'].sum()
    total_frauds = filtered_daily_stats['Total_Frauds'].sum()
    overall_fraud_rate = (total_frauds / total_transactions * 100) if total_transactions > 0 else 0
    avg_amount = filtered_daily_stats['Avg_Amount'].mean()
    
    stats_cards = html.Div([
        html.Div([
            html.Div([
                html.H4(f"{total_transactions:,}", 
                       style={'color': '#3498db', 'margin': '0'}),
                html.P("Total Transactions", style={'margin': '5px 0'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'border': '1px solid #dee2e6', 
                     'borderRadius': '5px', 'textAlign': 'center'})
        ], style={'width': '23%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.Div([
                html.H4(f"{total_frauds:,}", 
                       style={'color': '#e74c3c', 'margin': '0'}),
                html.P("Total Frauds", style={'margin': '5px 0'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'border': '1px solid #dee2e6', 
                     'borderRadius': '5px', 'textAlign': 'center'})
        ], style={'width': '23%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.Div([
                html.H4(f"{overall_fraud_rate:.2f}%", 
                       style={'color': '#f39c12', 'margin': '0'}),
                html.P("Overall Fraud Rate", style={'margin': '5px 0'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'border': '1px solid #dee2e6', 
                     'borderRadius': '5px', 'textAlign': 'center'})
        ], style={'width': '23%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            html.Div([
                html.H4(f"${avg_amount:.2f}", 
                       style={'color': '#27ae60', 'margin': '0'}),
                html.P("Avg Transaction Amount", style={'margin': '5px 0'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'border': '1px solid #dee2e6', 
                     'borderRadius': '5px', 'textAlign': 'center'})
        ], style={'width': '23%', 'display': 'inline-block', 'margin': '1%'})
    ])
    
    max_fraud_rate_day = filtered_daily_stats.loc[filtered_daily_stats['Fraud_Rate'].idxmax(), 'Day'] if not filtered_daily_stats.empty else None
    
    stats_table = dash_table.DataTable(
        id='stats-table',
        columns=[
            {'name': 'Day', 'id': 'Day'},
            {'name': 'Total Transactions', 'id': 'Total_Transactions', 'type': 'numeric', 'format': {'specifier': ','}},
            {'name': 'Total Frauds', 'id': 'Total_Frauds', 'type': 'numeric', 'format': {'specifier': ','}},
            {'name': 'Fraud Rate (%)', 'id': 'Fraud_Rate', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Avg Amount ($)', 'id': 'Avg_Amount', 'type': 'numeric', 'format': {'specifier': '.2f'}},
            {'name': 'Total Amount ($)', 'id': 'Total_Amount', 'type': 'numeric', 'format': {'specifier': ',.2f'}}
        ],
        data=filtered_daily_stats.to_dict('records'),
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': f'{{Day}} = {max_fraud_rate_day}'},
                'backgroundColor': '#ffebee',
                'color': 'black',
            }
        ] if max_fraud_rate_day is not None else []
    )
    
    return fig, stats_cards, stats_table

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
