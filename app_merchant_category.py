import os
import dash
import math
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

max_fraud_rate = df.groupby(['category', 'is_fraud']).size().unstack().fillna(0)
max_fraud_rate['fraud_rate'] = max_fraud_rate[1] / (max_fraud_rate[0] + max_fraud_rate[1]) * 100
max_value = math.ceil(max_fraud_rate['fraud_rate'].max() / 5) * 5

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Fraud Analysis by Merchant Category", 
                   className="text-center mb-4 text-primary",
                   style={'fontWeight': 'bold'})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Interactive Filters", className="mb-0 text-info")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Filter by minimum fraud rate (%):", 
                                     className="fw-bold mb-2"),
                            dcc.Slider(
                                id='fraud-filter',
                                min=0,
                                max=max_value,
                                step=0.5,
                                value=0,
                                marks={i: str(i) for i in range(0, int(max_value) + 1, 5)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], md=8),
                        dbc.Col([
                            html.Label("Chart Type:", className="fw-bold mb-2"),
                            dbc.RadioItems(
                                id='chart-type',
                                options=[
                                    {'label': 'Absolute Count', 'value': 'count'},
                                    {'label': 'Percentage', 'value': 'percent'}
                                ],
                                value='count',
                                inline=True
                            )
                        ], md=4)
                    ])
                ])
            ], className="shadow-sm")
        ])
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Category Analysis Chart", className="mb-0 text-info")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='fraud-chart')
                ])
            ], className="shadow-sm")
        ])
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Detailed Statistics", className="mb-0 text-info")
                ]),
                dbc.CardBody([
                    html.Div(id='stats-table')
                ])
            ], className="shadow-sm")
        ])
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Hr(className="my-4"),
            dbc.Alert([
                html.H5("Analysis Description", className="alert-heading"),
                html.P([
                    "This interactive analysis examines fraud patterns across different merchant categories. ",
                    "Use the slider to filter categories by minimum fraud rate and toggle between absolute counts and percentages."
                ]),
                html.Hr(),
                html.H6("Key Insights:", className="fw-bold text-danger"),
                html.P([
                    "This analysis reveals which merchant categories are most vulnerable to fraudulent activities. ",
                    "The interactive filters allow you to focus on high-risk categories and understand both the volume and rate of fraud."
                ]),
                html.P([
                    html.Strong("Business Applications: "),
                    html.Br(),
                    "• Identify high-risk merchant categories for enhanced monitoring",
                    html.Br(),
                    "• Implement category-specific fraud prevention strategies",
                    html.Br(),
                    "• Optimize resource allocation based on fraud concentration",
                    html.Br(),
                    "• Develop targeted risk assessment models for different business types"
                ], className="mb-2"),
                html.P([
                    html.Strong("Strategic Value: "), 
                    "Understanding fraud distribution by merchant category enables proactive risk management, ",
                    "helping businesses implement preventive measures before fraud patterns escalate. ",
                    "This data-driven approach can significantly reduce financial losses and improve customer trust."
                ], className="mb-0 text-muted")
            ], color="light", className="border")
        ])
    ])
    
], fluid=True, className="py-4")

@callback(
    [Output('fraud-chart', 'figure'),
     Output('stats-table', 'children')],
    [Input('fraud-filter', 'value'),
     Input('chart-type', 'value')]
)
def update_chart(min_fraud_rate, chart_type):
    fraud_stats = df.groupby(['category', 'is_fraud']).size().unstack().fillna(0)
    fraud_stats['fraud_rate'] = fraud_stats[1] / (fraud_stats[0] + fraud_stats[1]) * 100
    filtered_stats = fraud_stats[fraud_stats['fraud_rate'] >= min_fraud_rate].rename(columns={0: 'Not Fraud', 1: 'Fraud'})
    
    if chart_type == 'count':
        fig = px.bar(
            filtered_stats.reset_index(),
            x='category',
            y=['Not Fraud', 'Fraud'],
            title=f"Fraud Distribution by Category (≥{min_fraud_rate}% fraud rate)",
            labels={'value': 'Transaction Count', 'variable': 'Type'},
            color_discrete_map={'Not Fraud': '#3498db', 'Fraud': 'orange'}
        )
    else:
        fig = px.bar(
            filtered_stats.reset_index(),
            x='category',
            y='fraud_rate',
            title=f"Fraud Rate by Category (≥{min_fraud_rate}%)",
            labels={'fraud_rate': 'Fraud Rate (%)'},
            color='fraud_rate',
            color_continuous_scale='Reds'
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode='x unified',
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    if len(filtered_stats) > 0:
        stats_table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Category", className="text-center"), 
                    html.Th("Total Transactions", className="text-center"), 
                    html.Th("Fraudulent", className="text-center"), 
                    html.Th("Fraud Rate (%)", className="text-center")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(cat, className="fw-bold"),
                    html.Td(f"{int(row.iloc[0] + row.iloc[1]):,}", className="text-center"),
                    html.Td(f"{int(row.iloc[1]):,}", className="text-center text-danger fw-bold"),
                    html.Td(f"{row['fraud_rate']:.2f}%", 
                           className="text-center fw-bold",
                           style={'color': '#e74c3c' if row['fraud_rate'] > 10 else '#f39c12' if row['fraud_rate'] > 5 else '#27ae60'})
                ]) for cat, row in filtered_stats.iterrows()
            ])
        ], striped=True, bordered=True, hover=True, responsive=True, className="mt-3")
    else:
        stats_table = dbc.Alert("No categories match the selected criteria.", color="warning")
    
    return fig, stats_table

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
