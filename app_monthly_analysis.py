import os
import dash
import pandas as pd
from dash import dcc, html
import plotly.express as px

df = pd.read_csv('eda_fraud_balanced_sorted.csv')

df['transaction_date'] = pd.to_datetime(df['trans_date_trans_time'])
df['month'] = df['transaction_date'].dt.month

month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
df['month'] = df['month'].map(month_names)

fig_month = px.histogram(df, x='month', color='is_fraud',
                         category_orders={'month': list(month_names.values())},
                         title='Fraud Occurrence by Month of the Year',
                         labels={'month': 'Month', 'count': 'Number of Transactions'},
                         height=600,
                         barmode='group', opacity=0.8, color_discrete_map={0: 'blue', 1: 'orange'})

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Fraud Detection - Monthly Analysis", style={'textAlign': 'center'}),
    dcc.Graph(id='fraud-by-month', figure=fig_month)
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)

