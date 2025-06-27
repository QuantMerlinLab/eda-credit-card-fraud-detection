import os
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
df['hour'] = df['trans_date_trans_time'].dt.hour

fig = px.histogram(
    df, 
    x='hour', 
    color='is_fraud',
    barmode='group',
    title='<b>Hourly Transaction Analysis</b><br><sup>Normal vs Fraudulent Activity Patterns</sup>',
    labels={
        'hour': 'Hour of Day (24h format)',
        'count': 'Transaction Count',
        'is_fraud': 'Transaction Type'
    },
    opacity=0.85,
    color_discrete_map={0: '#1f77b4', 1: '#ff7f0e'},  
    template='plotly_white'
)

fig.update_layout(
    hovermode='x unified',
    legend_title_text='',
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        className='app-header',
        children=[
            html.H1('Real-Time Fraud Monitoring Dashboard', 
                   style={'textAlign': 'center', 'color': '#2c3e50'})
        ]
    ),
    
    html.Div(
        className='app-description',
        children=[
            html.P('Explore temporal patterns in transaction fraud risk', 
                  style={'textAlign': 'center', 'fontSize': 16})
        ]
    ),
    
    dcc.Graph(
        id='hourly-analysis',
        figure=fig,
        config={'displayModeBar': True}
    ),

    html.P(
        "📌 Fraud spikes around 10 PM and 11 PM suggest increased suspicious activity late in the day. "
        "This may reflect an attempt to exploit reduced monitoring during off-peak hours or operational handovers.",
        style={
            'textAlign': 'center',
            'fontStyle': 'italic',
            'marginTop': '10px',
            'color': '#555'
        }
    ),
    
    html.Div(
        className='app-footer',
        children=[
            html.P('Data updated: ' + pd.Timestamp.now().strftime('%Y-%m-%d')),
            html.P('Filter range: 00:00 - 23:59 (UTC)')
        ]
    )
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
