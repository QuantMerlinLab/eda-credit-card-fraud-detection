import os
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df['transaction_date'] = pd.to_datetime(df['trans_date_trans_time'])
df['transaction_hour'] = df['transaction_date'].dt.hour

hourly_stats = df.groupby('transaction_hour').agg({
    'is_fraud': ['count', 'sum']
}).reset_index()

hourly_stats.columns = ['Hour', 'Transactions', 'Frauds']
hourly_stats['Rate (%)'] = (hourly_stats['Frauds'] / hourly_stats['Transactions'] * 100).round(2)

table_fig = go.Figure(data=[go.Table(
    header=dict(values=['Hour', 'Transactions', 'Frauds', 'Rate (%)'],
                fill_color='paleturquoise',
                align='center',
                font=dict(size=12)),
    cells=dict(values=[hourly_stats['Hour'], 
                      hourly_stats['Transactions'], 
                      hourly_stats['Frauds'], 
                      hourly_stats['Rate (%)']],
               fill_color='lavender',
               align='center',
               font=dict(size=11)))
])
table_fig.update_layout(title="HOUR STATISTICS", height=600)

fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Number of Transactions by Hour', 'Fraud Rate by Hour'),
    specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
    vertical_spacing=0.12
)

fig.add_trace(
    go.Bar(
        x=hourly_stats['Hour'],
        y=hourly_stats['Transactions'] - hourly_stats['Frauds'],
        name='Normal Transactions',
        marker_color='blue'
    ),
    row=1, col=1
)

fig.add_trace(
    go.Bar(
        x=hourly_stats['Hour'],
        y=hourly_stats['Frauds'],
        name='Frauds',
        marker_color='orange'
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=hourly_stats['Hour'],
        y=hourly_stats['Rate (%)'],
        mode='lines+markers',
        name='Fraud Rate (%)',
        line=dict(color='orange', width=3),
        marker=dict(size=8)
    ),
    row=2, col=1
)

fig.update_layout(
    title='Fraud Analysis by Hour of Day',
    height=800,
    showlegend=True,
    barmode='stack'
)

fig.update_xaxes(title_text="Hour", row=1, col=1)
fig.update_xaxes(title_text="Hour", row=2, col=1)
fig.update_yaxes(title_text="Number of Transactions", row=1, col=1)
fig.update_yaxes(title_text="Fraud Rate (%)", row=2, col=1)

# Dash application layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Fraud Analysis by Hour", 
                   className="text-center mb-4 text-primary",
                   style={'fontWeight': 'bold'})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H3("Hourly Statistics", className="mb-0 text-info")
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='hourly-stats-table',
                        figure=table_fig
                    )
                ])
            ], className="shadow-sm")
        ])
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H3("Analysis Charts", className="mb-0 text-info")
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='fraud-analysis-chart',
                        figure=fig
                    )
                ])
            ], className="shadow-sm")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Hr(className="my-4"),
            dbc.Alert([
                html.H5("Analysis Description", className="alert-heading"),
                html.P([
                    "This analysis shows the distribution of transactions and frauds by hour of day. ",
                    "The top chart shows the total number of transactions (normal in blue, frauds in orange). ",
                    "The bottom chart shows the fraud rate percentage by hour."
                ]),
                html.Hr(),
                html.H6("Key Findings:", className="fw-bold text-danger"),
                html.P([
                    "We observe that the hours with the highest fraud percentages are during late night and early morning hours: ",
                    "10PM, 11PM, 12AM, 1AM, 2AM, and 3 AM. These critical time periods show significantly elevated fraud activity:"
                ]),
                html.Ul([
                    html.Li([html.Strong("10:00 PM:"), " 1,931 fraudulent transactions (85.29%)"]),
                    html.Li([html.Strong("11:00 PM:"), " 1,904 fraudulent transactions (85.57%)"]),
                    html.Li([html.Strong("12:00 AM:"), " 635 fraudulent transactions (72.49%)"]),
                    html.Li([html.Strong("1:00 AM:"), " 658 fraudulent transactions (73.19%)"]),
                    html.Li([html.Strong("2:00 AM:"), " 625 fraudulent transactions (71.27%)"]),
                    html.Li([html.Strong("3:00 AM:"), " 609 fraudulent transactions (71.56%)"])
                ], className="mb-2"),
                html.P([
                    html.Strong("Business Impact: "), 
                    "These findings suggest implementing enhanced security measures and monitoring during these high-risk hours (10PM-3AM) ",
                    "could significantly reduce fraud exposure and protect both customers and business operations."
                ], className="mb-0 text-muted")
            ], color="light", className="border")
        ])
    ], className="mt-4")
    
], fluid=True, className="py-4")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
