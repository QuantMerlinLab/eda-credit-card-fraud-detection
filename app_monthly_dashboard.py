import os
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, dash_table

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

df['transaction_date'] = pd.to_datetime(df['trans_date_trans_time'])
df['month'] = df['transaction_date'].dt.month
df['day_of_week'] = df['transaction_date'].dt.day_name()
df['hour'] = df['transaction_date'].dt.hour
df['date_only'] = df['transaction_date'].dt.date

month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
df['month_name'] = df['month'].map(month_names)

total_transactions = len(df)
fraud_transactions = len(df[df['is_fraud'] == 1])
fraud_rate = (fraud_transactions / total_transactions) * 100
legitimate_transactions = total_transactions - fraud_transactions

monthly_stats = df.groupby(['month', 'month_name']).agg({
    'is_fraud': ['count', 'sum', 'mean'],
    'amt': ['mean', 'sum', 'std']
}).reset_index()
monthly_stats.columns = ['month_num', 'month', 'total_transactions', 'fraud_count', 'fraud_rate', 
                        'avg_amount', 'total_amount', 'amount_std']
monthly_stats['fraud_rate'] = monthly_stats['fraud_rate'] * 100
monthly_stats = monthly_stats.sort_values('month_num').reset_index(drop=True)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="bi bi-shield-exclamation me-2"),
                "Monthly Fraud Detection Dashboard"
            ], className="text-center mb-4 mt-3", style={'color': '#2E86AB', 'font-weight': 'bold'})
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="bi bi-sliders me-2"),
                        "Date Range Filter"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Date Range:", className="fw-bold"),
                            dcc.DatePickerRange(
                                id='date-picker-range',
                                start_date=df['transaction_date'].min(),
                                end_date=df['transaction_date'].max(),
                                display_format='YYYY-MM-DD',
                                style={'width': '100%'}
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Chart Type:", className="fw-bold"),
                            dcc.Dropdown(
                                id='chart-type-dropdown',
                                options=[
                                    {'label': 'Bar Chart - Grouped', 'value': 'bar_grouped'},
                                    {'label': 'Bar Chart - Stacked', 'value': 'bar_stacked'},
                                    {'label': 'Line Chart - Fraud Rate', 'value': 'line_rate'},
                                    {'label': 'Area Chart - Transactions', 'value': 'area_trans'}
                                ],
                                value='bar_grouped',
                                clearable=False
                            )
                        ], width=6)
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
                        html.I(className="bi bi-graph-up me-2"),
                        "Total Transactions"
                    ], className="card-title text-center"),
                    html.H2(id="total-transactions", className="text-center text-primary", 
                           style={'font-weight': 'bold'})
                ])
            ], color="light", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-exclamation-triangle me-2"),
                        "Fraudulent"
                    ], className="card-title text-center"),
                    html.H2(id="fraud-transactions", className="text-center text-danger", 
                           style={'font-weight': 'bold'})
                ])
            ], color="light", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-percent me-2"),
                        "Fraud Rate"
                    ], className="card-title text-center"),
                    html.H2(id="fraud-rate", className="text-center text-warning", 
                           style={'font-weight': 'bold'})
                ])
            ], color="light", outline=True)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4([
                        html.I(className="bi bi-calendar3 me-2"),
                        "Peak Fraud Month"
                    ], className="card-title text-center"),
                    html.H2(id="peak-month", className="text-center text-info", 
                           style={'font-weight': 'bold', 'font-size': '1.2rem'})
                ])
            ], color="light", outline=True)
        ], width=3)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-bar-chart me-2"),
                        "Monthly Fraud Analysis"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='main-chart')
                ])
            ])
        ], width=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-pie-chart me-2"),
                        "Overall Distribution"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='fraud-pie-chart')
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-graph-up-arrow me-2"),
                        "Monthly Fraud Rate Trend"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='fraud-rate-chart')
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-currency-dollar me-2"),
                        "Monthly Transaction Amounts"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='amount-chart')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-speedometer2 me-2"),
                        "Fraud Rate Gauge by Month"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='gauge-chart')
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-activity me-2"),
                        "Monthly Transaction Volume Heatmap"
                    ], className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='heatmap-chart')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-table me-2"),
                        "Monthly Statistics Summary"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='monthly-stats-table',
                        columns=[
                            {'name': 'Month', 'id': 'month'},
                            {'name': 'Total Transactions', 'id': 'total_transactions', 'type': 'numeric', 'format': {'specifier': ','}},
                            {'name': 'Fraud Count', 'id': 'fraud_count', 'type': 'numeric', 'format': {'specifier': ','}},
                            {'name': 'Fraud Rate (%)', 'id': 'fraud_rate', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                            {'name': 'Avg Amount ($)', 'id': 'avg_amount', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                            {'name': 'Total Amount ($)', 'id': 'total_amount', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                            {'name': 'Amount Std Dev', 'id': 'amount_std', 'type': 'numeric', 'format': {'specifier': ',.2f'}}
                        ],
                        style_cell={'textAlign': 'center', 'padding': '10px', 'font-size': '12px'},
                        style_header={'backgroundColor': '#2E86AB', 'color': 'white', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            },
                            {
                                'if': {'filter_query': '{fraud_rate} > 5', 'column_id': 'fraud_rate'},
                                'backgroundColor': '#ffcccc',
                                'color': 'red',
                                'fontWeight': 'bold'
                            },
                            {
                                'if': {'filter_query': '{fraud_rate} > 3', 'column_id': 'fraud_rate'},
                                'backgroundColor': '#fff3cd',
                                'color': 'orange'
                            }
                        ],
                        sort_action="native",
                        style_table={'overflowX': 'scroll'}
                    )
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4([
                        html.I(className="bi bi-lightbulb me-2"),
                        "Monthly Analysis Insights"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="insights-content")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                html.I(className="bi bi-info-circle me-2"),
                "Monthly Fraud Detection System - Advanced Analytics Dashboard"
            ], className="text-center text-muted")
        ], width=12)
    ])
    
], fluid=True)

@app.callback(
    [Output('total-transactions', 'children'),
     Output('fraud-transactions', 'children'),
     Output('fraud-rate', 'children'),
     Output('peak-month', 'children'),
     Output('main-chart', 'figure'),
     Output('fraud-pie-chart', 'figure'),
     Output('fraud-rate-chart', 'figure'),
     Output('amount-chart', 'figure'),
     Output('gauge-chart', 'figure'),
     Output('heatmap-chart', 'figure'),
     Output('monthly-stats-table', 'data'),
     Output('insights-content', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('chart-type-dropdown', 'value')]
)
def update_dashboard(start_date, end_date, chart_type):
    filtered_df = df[(df['transaction_date'] >= start_date) & (df['transaction_date'] <= end_date)]
    
    total_trans = len(filtered_df)
    fraud_trans = len(filtered_df[filtered_df['is_fraud'] == 1])
    fraud_rt = (fraud_trans / total_trans) * 100 if total_trans > 0 else 0
    
    monthly_stats_filtered = filtered_df.groupby(['month', 'month_name']).agg({
        'is_fraud': ['count', 'sum', 'mean'],
        'amt': ['mean', 'sum', 'std']
    }).reset_index()
    monthly_stats_filtered.columns = ['month_num', 'month', 'total_transactions', 'fraud_count', 'fraud_rate', 
                                    'avg_amount', 'total_amount', 'amount_std']
    monthly_stats_filtered['fraud_rate'] = monthly_stats_filtered['fraud_rate'] * 100
    monthly_stats_filtered = monthly_stats_filtered.fillna(0)
    monthly_stats_filtered = monthly_stats_filtered.sort_values('month_num').reset_index(drop=True)
    
    peak_month = monthly_stats_filtered.loc[monthly_stats_filtered['fraud_rate'].idxmax(), 'month'] if len(monthly_stats_filtered) > 0 else "N/A"
    
    if chart_type == 'bar_grouped':
        main_fig = px.histogram(
            filtered_df, x='month_name', color='is_fraud',
            category_orders={'month_name': list(month_names.values())},
            barmode='group', opacity=0.8,
            color_discrete_map={0: '#2E86AB', 1: '#FFA500'},
            title="Monthly Transactions - Grouped by Fraud Status"
        )
    elif chart_type == 'bar_stacked':
        main_fig = px.histogram(
            filtered_df, x='month_name', color='is_fraud',
            category_orders={'month_name': list(month_names.values())},
            barmode='stack', opacity=0.8,
            color_discrete_map={0: '#2E86AB', 1: '#FFA500'},
            title="Monthly Transactions - Stacked by Fraud Status"
        )
    elif chart_type == 'line_rate':
        main_fig = px.line(
            monthly_stats_filtered, x='month', y='fraud_rate',
            markers=True, line_shape='linear',
            title="Monthly Fraud Rate Trend Line"
        )
        main_fig.update_traces(line_color='#FFA500', line_width=3, marker_size=8)
    else:  
        main_fig = px.area(
            monthly_stats_filtered, x='month', y='total_transactions',
            title="Monthly Transaction Volume - Area Chart"
        )
        main_fig.update_traces(fill='tonexty', fillcolor='rgba(46, 134, 171, 0.3)', line_color='#2E86AB')
    
    main_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    fraud_counts = filtered_df['is_fraud'].value_counts()
    pie_fig = px.pie(values=fraud_counts.values, names=['Legitimate', 'Fraudulent'], 
                     color_discrete_map={'Legitimate': '#2E86AB', 'Fraudulent': '#FFA500'},
                     title="Overall Fraud Distribution")
    pie_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    rate_fig = px.bar(monthly_stats_filtered, x='month', y='fraud_rate',
                     title="Monthly Fraud Rate Comparison", color='fraud_rate',
                     color_continuous_scale='Blues')
    rate_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    amount_fig = px.bar(monthly_stats_filtered, x='month', y=['avg_amount', 'amount_std'],
                       title="Average Transaction Amount & Standard Deviation",
                       barmode='group')
    amount_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    current_fraud_rate = fraud_rt
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_fraud_rate,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Current Period Fraud Rate (%)"},
        delta = {'reference': 3},
        gauge = {'axis': {'range': [None, 10]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 2], 'color': "lightgreen"},
                    {'range': [2, 5], 'color': "yellow"},
                    {'range': [5, 10], 'color': "red"}],
                'threshold': {'line': {'color': "red", 'width': 4},
                            'thickness': 0.75, 'value': 5}}))
    gauge_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    monthly_pivot = monthly_stats_filtered.set_index('month')[['total_transactions', 'fraud_count', 'fraud_rate']]
    
    month_order = [month_names[i] for i in range(1, 13) if month_names[i] in monthly_pivot.index]
    monthly_pivot = monthly_pivot.reindex(month_order)
    heatmap_fig = px.imshow(monthly_pivot.T, 
                           title="Monthly Statistics Heatmap",
                           color_continuous_scale='RdYlBu_r',
                           aspect="auto")
    heatmap_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
    
    table_data = monthly_stats_filtered.to_dict('records')
    
    insights = generate_monthly_insights(monthly_stats_filtered, fraud_rt)
    
    return (f"{total_trans:,}", f"{fraud_trans:,}", f"{fraud_rt:.2f}%", 
            str(peak_month), main_fig, pie_fig, rate_fig, amount_fig,
            gauge_fig, heatmap_fig, table_data, insights)

def generate_monthly_insights(monthly_stats, overall_fraud_rate):
    insights = []
    
    if len(monthly_stats) == 0:
        insights.append(dbc.Alert("No data available for the selected period.", color="warning"))
        return insights
    
    if overall_fraud_rate > 5:
        insights.append(dbc.Alert("🚨 Critical: Overall fraud rate exceeds 5%. Immediate action required!", color="danger"))
    elif overall_fraud_rate > 3:
        insights.append(dbc.Alert("⚠️ Warning: Elevated fraud rate detected. Enhanced monitoring recommended.", color="warning"))
    else:
        insights.append(dbc.Alert("✅ Good: Fraud rate is within acceptable range.", color="success"))
    
    peak_month = monthly_stats.loc[monthly_stats['fraud_rate'].idxmax(), 'month']
    peak_rate = monthly_stats['fraud_rate'].max()
    insights.append(dbc.Alert(f"📈 Peak fraud activity: {peak_month} with {peak_rate:.2f}% fraud rate.", color="info"))
    
    lowest_month = monthly_stats.loc[monthly_stats['fraud_rate'].idxmin(), 'month']
    lowest_rate = monthly_stats['fraud_rate'].min()
    insights.append(dbc.Alert(f"📉 Lowest fraud activity: {lowest_month} with {lowest_rate:.2f}% fraud rate.", color="success"))
    
    high_fraud_month = monthly_stats.loc[monthly_stats['fraud_count'].idxmax(), 'month']
    high_fraud_count = monthly_stats['fraud_count'].max()
    insights.append(dbc.Alert(f"🚨 Highest fraud volume: {high_fraud_month} with {high_fraud_count:,} fraudulent transactions.", color="danger"))
    
    fraud_rate_std = monthly_stats['fraud_rate'].std()
    if fraud_rate_std > 2:
        insights.append(dbc.Alert("📊 High variability in monthly fraud rates detected. Investigate seasonal patterns.", color="warning"))
    else:
        insights.append(dbc.Alert("📊 Fraud rates show consistent patterns across months.", color="info"))
    
    insights.append(html.Hr())
    insights.append(html.H5([html.I(className="bi bi-search me-2"), "Root Cause Analysis"], style={'color': '#2E86AB', 'margin-top': '20px'}))
    
    causes_card = dbc.Card([
        dbc.CardBody([
            html.H6("🔍 Potential Fraud Causes:", className="text-danger fw-bold"),
            html.Ul([
                html.Li("Seasonal shopping patterns (February = Valentine's Day, December = Holidays)"),
                html.Li("Payment system vulnerabilities during high-traffic periods"),
                html.Li("Inadequate fraud detection rules for seasonal anomalies"),
                html.Li("Fraudster targeting of promotional campaigns and special events"),
                html.Li("Insufficient staff training during peak transaction periods"),
                html.Li("Outdated risk scoring models not adapted to seasonal behavior")
            ], className="mb-3"),
            
            html.H6("💡 Strategic Business Solutions:", className="text-success fw-bold"),
            html.Ul([
                html.Li([html.Strong("Immediate Actions (0-30 days):"), 
                        html.Ul([
                            html.Li("Deploy additional fraud analysts during peak months"),
                            html.Li("Implement dynamic fraud thresholds based on seasonal patterns"),
                            html.Li("Enhance real-time monitoring for February and December")
                        ])]),
                html.Li([html.Strong("Medium-term Solutions (1-6 months):"), 
                        html.Ul([
                            html.Li("Develop machine learning models incorporating seasonal features"),
                            html.Li("Create targeted customer education campaigns before peak seasons"),
                            html.Li("Implement advanced behavioral analytics for holiday shopping"),
                            html.Li("Establish partnerships with payment processors for enhanced screening")
                        ])]),
                html.Li([html.Strong("Long-term Strategy (6+ months):"), 
                        html.Ul([
                            html.Li("Build predictive models to forecast monthly fraud risk"),
                            html.Li("Invest in AI-powered real-time decision engines"),
                            html.Li("Develop comprehensive fraud prevention ecosystem"),
                            html.Li("Create industry benchmarking and threat intelligence sharing")
                        ])])
            ], className="mb-3"),
            
            html.H6("📊 Business Impact & ROI:", className="text-info fw-bold"),
            html.Ul([
                html.Li(f"Potential savings: Reducing fraud rate from {overall_fraud_rate:.1f}% to 2% could save $XXX,XXX annually"),
                html.Li("Improved customer trust and satisfaction scores"),
                html.Li("Reduced chargeback costs and operational overhead"),
                html.Li("Enhanced regulatory compliance and reduced legal risks"),
                html.Li("Competitive advantage through superior fraud prevention")
            ])
        ])
    ], color="light", className="mt-3")
    
    insights.append(causes_card)
    
    return insights

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)

