import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import yfinance as yf

ticker = 'AAPL'

app = dash.Dash(__name__)
app.title = "Real Time Stock Price Data Visualization"

app.layout = html.Div([
    html.H1("Real Time Stock Price Data Visualization", style={'textAlign': 'center'}),
    html.Div(f"Displaying real-time data for {ticker}", style={'textAlign': 'center'}),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='graph-update',
        interval=60*1000,  
        n_intervals=0
    )
])

@app.callback(Output('live-graph', 'figure'),
            Input('graph-update', 'n_intervals'))
def update_graph(n_intervals):
    data = yf.download(ticker, period='1d', interval='1m')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines+markers',
        name='Close Price'
    ))
    fig.update_layout(
        title=f"{ticker} Stock Price",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
