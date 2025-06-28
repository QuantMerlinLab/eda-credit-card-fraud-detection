import os
import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

max_samples = 15000
sample_df = df.sample(max_samples) if len(df) > max_samples else df.copy()

geo_stats = sample_df.groupby(['state']).agg({
    'is_fraud': ['count', 'sum', 'mean'],
    'amt': ['mean', 'sum'],
    'lat': 'mean',
    'long': 'mean'
}).reset_index()
geo_stats.columns = ['state', 'total_trans', 'fraud_count', 'fraud_rate', 'avg_amount', 'total_amount', 'avg_lat', 'avg_long']
geo_stats['fraud_rate'] = geo_stats['fraud_rate'] * 100

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="bi bi-geo-alt-fill me-2"),
                "Geographical Fraud Analysis Dashboard"
            ], className="text-center mb-4 mt-3", style={'color': '#2E86AB', 'font-weight': 'bold'})
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="bi bi-sliders me-2"),
                        "Map Controls & Filters"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Map Type:", className="fw-bold"),
                            dcc.Dropdown(
                                id='map-type-dropdown',
                                options=[
                                    {'label': 'Scatter Plot - Individual Transactions', 'value': 'scatter'},
                                    {'label': 'State-Level Heatmap', 'value': 'choropleth'},
                                    {'label': 'Density Map - Fraud Hotspots', 'value': 'density'},
                                    {'label': 'Bubble Map - Transaction Volume', 'value': 'bubble'}
                                ],
                                value='scatter',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Sample Size:", className="fw-bold"),
                            dcc.Slider(
                                id='sample-size-slider',
                                min=1000, 
                                max=min(15000, len(df)), 
                                step=1000, 
                                value=min(10000, len(df)),
                                marks={i: f'{i/1000}k' for i in range(1000, min(16000, len(df)+1), 2000)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Fraud Filter:", className="fw-bold"),
                            dcc.Dropdown(
                                id='fraud-filter-dropdown',
                                options=[
                                    {'label': 'All Transactions', 'value': 'all'},
                                    {'label': 'Fraudulent Only', 'value': 'fraud_only'},
                                    {'label': 'Legitimate Only', 'value': 'legit_only'}
                                ],
                                value='all',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Amount Range ($):", className="fw-bold"),
                            dcc.RangeSlider(
                                id='amount-range-slider',
                                min=df['amt'].min(), 
                                max=df['amt'].max(), 
                                step=100,
                                marks={int(i): f'${int(i)}' for i in np.linspace(df['amt'].min(), df['amt'].max(), 6)},
                                value=[df['amt'].min(), df['amt'].quantile(0.75)],
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], width=3)
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-map me-2"),
                        "States Analyzed"
                    ], className="card-title text-center"),
                    html.H2(id="states-count", className="text-center text-primary", 
                           style={'font-weight': 'bold'})
                ])
            ], color="light", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-exclamation-triangle-fill me-2"),
                        "Highest Risk State"
                    ], className="card-title text-center"),
                    html.H2(id="highest-risk-state", className="text-center text-danger", 
                           style={'font-weight': 'bold', 'font-size': '1.5rem'})
                ])
            ], color="light", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-shield-check me-2"),
                        "Safest State"
                    ], className="card-title text-center"),
                    html.H2(id="safest-state", className="text-center text-success", 
                           style={'font-weight': 'bold', 'font-size': '1.5rem'})
                ])
            ], color="light", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-graph-up me-2"),
                        "Geographic Concentration"
                    ], className="card-title text-center"),
                    html.H2(id="geo-concentration", className="text-center text-info", 
                           style={'font-weight': 'bold'})
                ])
            ], color="light", outline=True)
        ], width=3)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4(id="map-title", className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Loading(
                        dcc.Graph(id='geo-fraud-map', style={'height': '600px'}),
                        type="circle", color="#2E86AB"
                    )
                ])
            ])
        ], width=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="bi bi-list-ol me-2"),
                        "Top Risk States"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="state-rankings")
                ], style={'max-height': '300px', 'overflow-y': 'auto'})
            ], className="mb-3"),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="bi bi-lightbulb me-2"),
                        "Geographic Insights"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="geographic-insights")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-bar-chart me-2"),
                        "State-wise Fraud Analysis"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='state-fraud-chart')
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-scatter me-2"),
                        "Fraud Rate vs Transaction Volume"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='scatter-analysis-chart')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-clipboard-check me-2"),
                        "Geographic Risk Management Action Plan"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="action-plan")
                ])
            ])
        ], width=12)
    ], className="mb-4")
    
], fluid=True)

@app.callback(
    [Output('states-count', 'children'),
     Output('highest-risk-state', 'children'),
     Output('safest-state', 'children'),
     Output('geo-concentration', 'children'),
     Output('geo-fraud-map', 'figure'),
     Output('map-title', 'children'),
     Output('state-rankings', 'children'),
     Output('geographic-insights', 'children'),
     Output('state-fraud-chart', 'figure'),
     Output('scatter-analysis-chart', 'figure'),
     Output('action-plan', 'children')],
    [Input('map-type-dropdown', 'value'),
     Input('sample-size-slider', 'value'),
     Input('fraud-filter-dropdown', 'value'),
     Input('amount-range-slider', 'value')]
)
def update_geographic_analysis(map_type, sample_size, fraud_filter, amount_range):
    filtered_df = sample_df.copy()
    
    filtered_df = filtered_df[
        (filtered_df['amt'] >= amount_range[0]) & 
        (filtered_df['amt'] <= amount_range[1])
    ]
    
    original_filtered_df = filtered_df.copy()
    
    display_df = filtered_df.copy()
    if fraud_filter == 'fraud_only':
        display_df = display_df[display_df['is_fraud'] == 1]
    elif fraud_filter == 'legit_only':
        display_df = display_df[display_df['is_fraud'] == 0]
    
    if len(display_df) > sample_size:
        display_df = display_df.sample(sample_size)
    
    geo_stats_filtered = original_filtered_df.groupby(['state']).agg({
        'is_fraud': ['count', 'sum', 'mean'],
        'amt': ['mean', 'sum'],
        'lat': 'mean',
        'long': 'mean'
    }).reset_index()
    geo_stats_filtered.columns = ['state', 'total_trans', 'fraud_count', 'fraud_rate', 
                                 'avg_amount', 'total_amount', 'avg_lat', 'avg_long']
    geo_stats_filtered['fraud_rate'] = geo_stats_filtered['fraud_rate'] * 100
    geo_stats_filtered = geo_stats_filtered.sort_values('fraud_rate', ascending=False)
    
    if fraud_filter == 'fraud_only':
        display_stats_text = f"Showing {len(display_df):,} fraudulent transactions"
        filter_info = "🚨 Fraudulent Transactions Only"
    elif fraud_filter == 'legit_only':
        display_stats_text = f"Showing {len(display_df):,} legitimate transactions"
        filter_info = "✅ Legitimate Transactions Only"
    else:
        display_stats_text = f"Showing {len(display_df):,} total transactions"
        filter_info = "📊 All Transactions"
    
    states_count = len(geo_stats_filtered)
    highest_risk = geo_stats_filtered.iloc[0]['state'] if len(geo_stats_filtered) > 0 else "N/A"
    safest_state = geo_stats_filtered.iloc[-1]['state'] if len(geo_stats_filtered) > 0 else "N/A"
    
    fraud_counts = geo_stats_filtered['fraud_count'].values
    geo_concentration = f"{np.std(fraud_counts)/np.mean(fraud_counts):.2f}" if len(fraud_counts) > 0 and np.mean(fraud_counts) > 0 else "N/A"
    
    if map_type == 'scatter':
        map_fig = px.scatter(
            display_df, x='long', y='lat', color='is_fraud',
            title=f'Individual Transaction Locations - {filter_info}',
            opacity=0.6, size='amt',
            color_discrete_map={0: '#2E86AB', 1: '#F24236'},
            hover_data=['state', 'amt']
        )
        map_title = f"Scatter Plot - {display_stats_text}"
        
    elif map_type == 'bubble':
        map_fig = px.scatter(
            geo_stats_filtered, x='avg_long', y='avg_lat', 
            size='total_trans', color='fraud_rate',
            hover_data=['state', 'fraud_count'],
            title=f'State-wise Transaction Volume & Fraud Rate - {filter_info}',
            color_continuous_scale='Reds'
        )
        map_title = f"Bubble Map - State Statistics ({filter_info})"
        
    elif map_type == 'density':
        if fraud_filter == 'legit_only':
            density_data = display_df
            density_title = 'Legitimate Transaction Density'
        elif fraud_filter == 'fraud_only':
            density_data = display_df
            density_title = 'Fraudulent Transaction Density'
        else:
            density_data = display_df
            density_title = 'Transaction Density (All)'
            
        map_fig = px.density_mapbox(
            density_data, 
            lat='lat', lon='long', z='amt',
            radius=10, center=dict(lat=39.5, lon=-98.35), zoom=3,
            mapbox_style="open-street-map",
            title=f'{density_title} - {filter_info}'
        )
        map_title = f"Density Map - {display_stats_text}"
        
    else:  
        map_fig = px.choropleth(
            geo_stats_filtered, locations='state',
            color='fraud_rate', locationmode='USA-states',
            scope="usa", title=f'State-wise Fraud Rate - {filter_info}',
            color_continuous_scale='Reds'
        )
        map_title = f"Choropleth - State Fraud Rates ({filter_info})"
    
    map_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    rankings = []
    for i, row in geo_stats_filtered.head(10).iterrows():
        color = "danger" if row['fraud_rate'] > 5 else "warning" if row['fraud_rate'] > 2 else "success"
        rankings.append(
            dbc.ListGroupItem([
                html.Div([
                    html.Strong(f"{row['state']}: {row['fraud_rate']:.1f}%"),
                    html.Small(f" ({row['fraud_count']} frauds)", className="text-muted")
                ])
            ], color=color, className="d-flex justify-content-between align-items-center")
        )
    
    rankings_component = dbc.ListGroup(rankings)
    
    insights = generate_geographic_insights(geo_stats_filtered, filter_info, display_stats_text)
    
    top_10_states = geo_stats_filtered.head(10)
    state_chart = px.bar(
        top_10_states, x='state', y='fraud_rate',
        title=f'Top 10 States by Fraud Rate - {filter_info}',
        color='fraud_rate', color_continuous_scale='Reds'
    )
    state_chart.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    scatter_chart = px.scatter(
        geo_stats_filtered, x='total_trans', y='fraud_rate',
        size='fraud_count', hover_data=['state'],
        title=f'Fraud Rate vs Transaction Volume - {filter_info}',
        trendline="ols"
    )
    scatter_chart.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    action_plan = generate_action_plan(geo_stats_filtered, filter_info)
    
    return (states_count, highest_risk, safest_state, geo_concentration,
            map_fig, map_title, rankings_component, insights,
            state_chart, scatter_chart, action_plan)

def generate_geographic_insights(geo_stats, filter_info, display_stats):
    insights = []
    
    if len(geo_stats) == 0:
        return [dbc.Alert("No data available for analysis.", color="warning")]
    
    insights.append(dbc.Alert(f"📍 Current Filter: {filter_info} | {display_stats}", color="primary"))
    
    avg_fraud_rate = geo_stats['fraud_rate'].mean()
    high_risk_states = len(geo_stats[geo_stats['fraud_rate'] > avg_fraud_rate])
    
    insights.extend([
        dbc.Alert(f"📊 {high_risk_states} states above average fraud rate ({avg_fraud_rate:.1f}%)", color="info"),
        dbc.Alert(f"🏴 Geographic spread: {len(geo_stats)} states analyzed", color="primary"),
        dbc.Alert(f"⚠️ Risk concentration: Top 3 states show significant patterns", color="warning")
    ])
    
    return insights

def generate_action_plan(geo_stats, filter_info):
    if len(geo_stats) == 0:
        return [dbc.Alert("No data available for action planning.", color="warning")]
    
    high_risk_states = geo_stats[geo_stats['fraud_rate'] > 5]['state'].tolist()
    
    plan = dbc.Card([
        dbc.CardBody([
            dbc.Alert(f"Analysis based on: {filter_info}", color="info", className="mb-3"),
            
            html.H6("🎯 Immediate Actions (0-30 days):", className="text-danger fw-bold"),
            html.Ul([
                html.Li(f"Deploy additional fraud monitoring in: {', '.join(high_risk_states[:3]) if high_risk_states else 'No high-risk states identified'}"),
                html.Li("Implement state-specific transaction limits and velocity checks"),
                html.Li("Enhance merchant verification in high-risk geographic areas")
            ]),
            
            html.H6("📊 Medium-term Strategy (1-6 months):", className="text-warning fw-bold"),
            html.Ul([
                html.Li("Develop geographic risk scoring models"),
                html.Li("Create state-specific fraud prevention campaigns"),
                html.Li("Establish partnerships with local law enforcement in high-risk areas"),
                html.Li("Implement geofencing alerts for suspicious location patterns")
            ]),
            
            html.H6("🚀 Long-term Initiatives (6+ months):", className="text-success fw-bold"),
            html.Ul([
                html.Li("Build comprehensive geographic fraud intelligence platform"),
                html.Li("Develop cross-state fraud pattern analysis capabilities"),
                html.Li("Create predictive models for emerging geographic fraud trends"),
                html.Li("Establish industry-wide geographic threat sharing network")
            ])
        ])
    ], color="light")
    
    return plan

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
