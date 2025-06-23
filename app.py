import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from dash import dcc, html, Input, Output

# Load your actual data
df = pd.read_csv('eda_fraud_balanced_sorted.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Fraudulent Transaction Analysis", 
            style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        html.Div([
            html.Label("Alert Threshold ($):", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='threshold-slider',
                min=50,
                max=1000,
                step=25,
                value=200,
                marks={i: f'${i}' for i in range(50, 1001, 150)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
        
        html.Div([
            html.Label("X-axis Max Limit ($):", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='xlim-slider',
                min=500,
                max=3000,
                step=100,
                value=1500,
                marks={i: f'${i}' for i in range(500, 3001, 500)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'})
    ], style={'marginBottom': 30}),
    
    html.Div([
        html.Div([
            html.Label("Chart Type:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='plot-type',
                options=[
                    {'label': 'KDE Density', 'value': 'kde'},
                    {'label': 'Histogram', 'value': 'hist'},
                    {'label': 'Box Plot', 'value': 'box'}
                ],
                value='kde',
                style={'marginTop': 5}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
        
        html.Div([
            html.Label("Display:", style={'fontWeight': 'bold'}),
            dcc.Checklist(
                id='display-options',
                options=[
                    {'label': 'Show threshold', 'value': 'threshold'},
                    {'label': 'Show statistics', 'value': 'stats'}
                ],
                value=['threshold', 'stats'],
                style={'marginTop': 10}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
        
        html.Div([
            html.Label("Y Scale:", style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='y-scale',
                options=[
                    {'label': 'Linear', 'value': 'linear'},
                    {'label': 'Log', 'value': 'log'}
                ],
                value='linear',
                style={'marginTop': 10}
            )
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'marginBottom': 30}),
    
    dcc.Graph(id='fraud-plot', style={'height': '600px'}),
    
    html.Div(id='statistics-panel', style={'marginTop': 20})
])

@app.callback(
    [Output('fraud-plot', 'figure'),
     Output('statistics-panel', 'children')],
    [Input('threshold-slider', 'value'),
     Input('xlim-slider', 'value'),
     Input('plot-type', 'value'),
     Input('display-options', 'value'),
     Input('y-scale', 'value')]
)
def update_plot(threshold, xlim, plot_type, display_options, y_scale):
    
    df_filtered = df[df['amt'] <= xlim].copy()
    
    fig = go.Figure()
    
    if plot_type == 'kde':
        
        fraud_data = df_filtered[df_filtered['is_fraud'] == 1]['amt']
        non_fraud_data = df_filtered[df_filtered['is_fraud'] == 0]['amt']
        
        x_range = np.linspace(0, xlim, 1000)  
        
        if len(fraud_data) > 0:
            kde_fraud = stats.gaussian_kde(fraud_data)
            fraud_density = kde_fraud(x_range)
            fraud_density = fraud_density / np.trapz(fraud_density, x_range)
            
            fig.add_trace(go.Scatter(
                x=x_range, y=fraud_density,
                mode='lines', name='Fraud',
                line=dict(color='orange', width=2),
                fill='tonexty' if len(fig.data) == 0 else None
            ))
        
        if len(non_fraud_data) > 0:
            kde_non_fraud = stats.gaussian_kde(non_fraud_data)
            non_fraud_density = kde_non_fraud(x_range)
            non_fraud_density = non_fraud_density / np.trapz(non_fraud_density, x_range)
            
            fig.add_trace(go.Scatter(
                x=x_range, y=non_fraud_density,
                mode='lines', name='Non-Fraud',
                line=dict(color='blue', width=2),
                fill='tonexty' if len(fig.data) == 0 else None
            ))
    
    elif plot_type == 'hist':
        
        fig.add_trace(go.Histogram(
            x=df_filtered[df_filtered['is_fraud'] == 1]['amt'],
            name='Fraud', opacity=0.7, nbinsx=50,
            marker_color='orange', histnorm='probability density'
        ))
        
        fig.add_trace(go.Histogram(
            x=df_filtered[df_filtered['is_fraud'] == 0]['amt'],
            name='Non-Fraud', opacity=0.7, nbinsx=50,
            marker_color='blue', histnorm='probability density'
        ))
    
    elif plot_type == 'box':
        
        fig.add_trace(go.Box(
            y=df_filtered[df_filtered['is_fraud'] == 1]['amt'],
            name='Fraud', marker_color='orange',
            x=['Fraud'] * len(df_filtered[df_filtered['is_fraud'] == 1])
        ))
        
        fig.add_trace(go.Box(
            y=df_filtered[df_filtered['is_fraud'] == 0]['amt'],
            name='Non-Fraud', marker_color='blue',
            x=['Non-Fraud'] * len(df_filtered[df_filtered['is_fraud'] == 0])
        ))
    
    if 'threshold' in display_options and plot_type != 'box':
        fig.add_vline(
            x=threshold, line_dash="dash", line_color="black",
            annotation_text=f"Threshold: ${threshold}",
            annotation_position="top"
        )
    
    fig.update_layout(
        title=f'Amount Distribution: Fraud vs Non-Fraud (Threshold: ${threshold:,})',
        xaxis_title='Amount ($)' if plot_type != 'box' else 'Transaction Type',
        yaxis_title='Density' if plot_type != 'box' else 'Amount ($)',
        yaxis_type=y_scale,
        template='plotly_white',
        hovermode='x unified' if plot_type != 'box' else 'closest',
        legend=dict(x=0.7, y=0.95)
    )

    if plot_type != 'box':
        fig.update_layout(xaxis=dict(range=[0, xlim]))
    else:
        fig.update_layout(
            xaxis=dict(type='category'),
            yaxis=dict(range=[0, xlim] if y_scale == 'linear' else [1, xlim]),
            margin=dict(l=60, r=60, t=80, b=60)
        )
    
    if plot_type == 'hist':
        fig.update_layout(barmode='overlay')
    
    stats_content = []
    if 'stats' in display_options:
        fraud_stats = df_filtered[df_filtered['is_fraud'] == 1]['amt']
        non_fraud_stats = df_filtered[df_filtered['is_fraud'] == 0]['amt']
        
        fraud_above_threshold = len(fraud_stats[fraud_stats > threshold])
        non_fraud_above_threshold = len(non_fraud_stats[non_fraud_stats > threshold])
        total_above_threshold = fraud_above_threshold + non_fraud_above_threshold
        
        fraud_rate_above_threshold = (fraud_above_threshold / total_above_threshold * 100) if total_above_threshold > 0 else 0
        
        fraud_count = len(fraud_stats)
        non_fraud_count = len(non_fraud_stats)
        
        stats_content = [
            html.H3("Statistics", style={'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.H4(f"Fraudulent Transactions (is_fraud=1)", style={'color': 'orange'}),
                    html.P(f"Total count: {fraud_count:,} / {len(df[df['is_fraud'] == 1]):,} total"),
                    html.P(f"Average amount: ${fraud_stats.mean():.2f}" if len(fraud_stats) > 0 else "Average amount: N/A"),
                    html.P(f"Median amount: ${fraud_stats.median():.2f}" if len(fraud_stats) > 0 else "Median amount: N/A"),
                    html.P(f"Above threshold: {fraud_above_threshold:,}")
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
                
                html.Div([
                    html.H4(f"Legitimate Transactions (is_fraud=0)", style={'color': 'blue'}),
                    html.P(f"Total count: {non_fraud_count:,} / {len(df[df['is_fraud'] == 0]):,} total"),
                    html.P(f"Average amount: ${non_fraud_stats.mean():.2f}" if len(non_fraud_stats) > 0 else "Average amount: N/A"),
                    html.P(f"Median amount: ${non_fraud_stats.median():.2f}" if len(non_fraud_stats) > 0 else "Median amount: N/A"),
                    html.P(f"Above threshold: {non_fraud_above_threshold:,}")
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
                
                html.Div([
                    html.H4("Threshold Analysis", style={'color': 'black'}),
                    html.P(f"Total above: {total_above_threshold:,}"),
                    html.P(f"Fraud rate: {fraud_rate_above_threshold:.1f}%"),
                    html.P(f"Precision: {(fraud_above_threshold/(fraud_above_threshold + non_fraud_above_threshold)*100):.1f}%" if total_above_threshold > 0 else "Precision: N/A"),
                    html.P(f"Recall: {(fraud_above_threshold/len(fraud_stats)*100):.1f}%")
                ], style={'width': '30%', 'display': 'inline-block'})
            ])
        ]
    
    return fig, stats_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)
