import os
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

df['transaction_date'] = pd.to_datetime(df['trans_date_trans_time'])
df['day_of_week'] = df['transaction_date'].dt.dayofweek
day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
             4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
df['day_of_week'] = df['day_of_week'].map(day_names)

day_stats = df.groupby('day_of_week').agg({
    'is_fraud': ['count', 'sum', 'mean']
}).round(4)
day_stats.columns = ['total_transactions', 'fraud_count', 'fraud_rate']
day_stats = day_stats.reset_index()

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_stats = day_stats.set_index('day_of_week').reindex(day_order).reset_index()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            html.H1("🔍 Fraud Analysis by Day of the Week", 
                   className="text-center mb-4 text-primary"),
            html.P("Interactive dashboard to analyze fraud patterns by day",
                  className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{len(df):,}", className="text-primary mb-0"),
                    html.P("Total Transactions", className="text-muted")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{df['is_fraud'].sum():,}", className="text-danger mb-0"),
                    html.P("Fraudulent Transactions", className="text-muted")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{df['is_fraud'].mean()*100:.2f}%", className="text-warning mb-0"),
                    html.P("Global Fraud Rate", className="text-muted")
                ])
            ], className="text-center")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{day_stats['fraud_rate'].max()*100:.2f}%", className="text-info mb-0"),
                    html.P("Max Rate per Day", className="text-muted")
                ])
            ], className="text-center")
        ], width=3)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Display Options", className="card-title"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Chart type:", className="form-label"),
                            dcc.Dropdown(
                                id='chart-type',
                                options=[
                                    {'label': '📊 Grouped Histogram', 'value': 'histogram'},
                                    {'label': '📈 Fraud Rate', 'value': 'rate'},
                                    {'label': '🔄 Comparison', 'value': 'comparison'}
                                ],
                                value='histogram',
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Color palette:", className="form-label"),
                            dcc.Dropdown(
                                id='color-scheme',
                                options=[
                                    {'label': '🔵 Blue-Orange', 'value': 'blue_orange'},
                                    {'label': '🔴 Red-Green', 'value': 'red_green'},
                                    {'label': '🟣 Viridis', 'value': 'viridis'},
                                    {'label': '🌈 Plotly', 'value': 'plotly'}
                                ],
                                value='blue_orange',
                                clearable=False
                            )
                        ], width=6)
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='main-chart', style={'height': '500px'})
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Detailed Statistics", className="card-title mb-3"),
                    html.Div(id='stats-table')
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📈 Time Evolution", className="card-title"),
                    dcc.Graph(id='time-series-chart', style={'height': '400px'})
                ])
            ])
        ])
    ])
], fluid=True)

@app.callback(
    [Output('main-chart', 'figure'),
     Output('stats-table', 'children'),
     Output('time-series-chart', 'figure')],
    [Input('chart-type', 'value'),
     Input('color-scheme', 'value')]
)
def update_charts(chart_type, color_scheme):
    color_maps = {
        'blue_orange': {0: '#1f77b4', 1: '#ff7f0e'},
        'red_green': {0: '#2ca02c', 1: '#d62728'},
        'viridis': {0: '#440154', 1: '#fde725'},
        'plotly': {0: '#636efa', 1: '#ef553b'}
    }
    colors = color_maps[color_scheme]
    
    if chart_type == 'histogram':
        fig_main = px.histogram(
            df, x='day_of_week', color='is_fraud',
            category_orders={'day_of_week': day_order},
            title='Transaction Distribution by Day of the Week',
            labels={'day_of_week': 'Day of the Week', 'count': 'Number of Transactions'},
            barmode='group',
            color_discrete_map=colors
        )
        fig_main.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font_size=16,
            legend_title_text="Transaction Type",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        fig_main.update_traces(opacity=0.8)
        
    elif chart_type == 'rate':
        fig_main = px.bar(
            day_stats, x='day_of_week', y='fraud_rate',
            title='Fraud Rate by Day of the Week',
            labels={'day_of_week': 'Day of the Week', 'fraud_rate': 'Fraud Rate'},
            color='fraud_rate',
            color_continuous_scale='Reds'
        )
        fig_main.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font_size=16,
            xaxis_categoryorder='array',
            xaxis_categoryarray=day_order
        )
        
    else:  
        fig_main = go.Figure()
        
        fig_main.add_trace(go.Bar(
            name='Normal Transactions',
            x=day_order,
            y=[day_stats[day_stats['day_of_week']==day]['total_transactions'].iloc[0] - 
               day_stats[day_stats['day_of_week']==day]['fraud_count'].iloc[0] 
               for day in day_order],
            marker_color=colors[0],
            opacity=0.8
        ))
        
        fig_main.add_trace(go.Bar(
            name='Fraudulent Transactions',
            x=day_order,
            y=[day_stats[day_stats['day_of_week']==day]['fraud_count'].iloc[0] 
               for day in day_order],
            marker_color=colors[1],
            opacity=0.8
        ))
        
        fig_main.update_layout(
            title='Transaction Comparison by Day',
            xaxis_title='Day of the Week',
            yaxis_title='Number of Transactions',
            barmode='stack',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title_font_size=16,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
    stats_cards = []
    for day in day_order:  
        row = day_stats[day_stats['day_of_week'] == day].iloc[0]
        card = dbc.Card([
            dbc.CardBody([
                html.H6(day, className="card-title text-primary"),
                html.P([
                    html.Strong(f"{row['total_transactions']:,}"), " total transactions"
                ], className="card-text mb-1"),
                html.P([
                    html.Strong(f"{row['fraud_count']:,}", className="text-danger"), " frauds"
                ], className="card-text mb-1"),
                html.P([
                    html.Strong(f"{row['fraud_rate']*100:.2f}%", className="text-warning"), " rate"
                ], className="card-text mb-0")
            ])
        ], className="mb-2")
        stats_cards.append(card)
    
    df_weekly = df.copy()
    df_weekly['week'] = df_weekly['transaction_date'].dt.to_period('W')
    weekly_fraud = df_weekly.groupby(['week', 'day_of_week'])['is_fraud'].mean().reset_index()
    weekly_fraud['week_str'] = weekly_fraud['week'].astype(str)
    
    fig_time = px.line(
        weekly_fraud.tail(len(day_order)*4),  
        x='week_str', y='is_fraud', color='day_of_week',
        title='Fraud Rate Evolution (Last 4 weeks)',
        labels={'week_str': 'Week', 'is_fraud': 'Fraud Rate', 'day_of_week': 'Day of Week'},
        category_orders={'day_of_week': day_order}
    )
    fig_time.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=14,
        legend_title_text="Day of Week"
    )
    fig_time.update_traces(line=dict(width=2), marker=dict(size=6))
    
    return fig_main, stats_cards, fig_time

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
