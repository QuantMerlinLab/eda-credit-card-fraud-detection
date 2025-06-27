import os          
import dash        
import numpy as np 
import pandas as pd 
import plotly.express as px 
from dash import dcc, html

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

df['log_amt'] = np.log(df['amt'])

fig = px.histogram(df, x='log_amt', color='is_fraud',
                   title='Log-Scaled Transaction Amount Distribution',
                   nbins=50, opacity=0.8,
                   labels={'log_amt': 'Log(Transaction Amount)'},
                  color_discrete_map={0: 'blue', 1: 'orange'})

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Transaction Amount Distribution"),
    dcc.Graph(id='graph-amount', figure=fig)
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
