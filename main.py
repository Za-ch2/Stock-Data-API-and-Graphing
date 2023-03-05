from flask import Flask, render_template, request
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import io
import base64
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

# Modify the plot function to calculate the average closing price for each ticker
@app.route('/', methods=['POST'])
def plot():
    # Get user input for stock tickers
    tickers = request.form.get('tickers').split()

    # Create an empty dataframe to store the close prices for each ticker
    closeDf = pd.DataFrame()

    # Loop through each ticker and fetch the data
    for ticker in tickers:
        data = yf.download(ticker, period='12mo')
        closeDf[ticker] = data['Close']

    # Calculate the yearly average prices
    # Calculate the average closing prices for each ticker over the past year
    avg_prices = pd.DataFrame(columns=['Ticker', 'Average Closing Prices (1-year)'])
    for ticker in tickers:
        df = closeDf[[ticker]].reset_index()
        df = df.loc[df['Date'] >= (df['Date'].max() - pd.DateOffset(years=1))]
        avg_price = df[ticker].mean()
        avg_prices = avg_prices.append({'Ticker': ticker, 'Average Closing Prices (1-year)': avg_price}, ignore_index=True)



    # Create a trace for each ticker
    traces = []
    for column in closeDf.columns:
        trace = go.Scatter(x=closeDf.index, y=closeDf[column], name=column)
        traces.append(trace)

    # Create the layout for the plot
    layout = go.Layout(title='Closing Prices', xaxis=dict(title='Date'), yaxis=dict(title='Price ($)'))

    # Create the figure and add the traces and layout
    fig = go.Figure(data=traces, layout=layout)

    # Convert the plot to a PNG image
    img = io.BytesIO()
    fig.write_image(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    # Generate the HTML code to display the plot
    plot_html = '<img src="data:image/png;base64, {}">'.format(plot_url)

    # Pass the plot HTML and avg_prices to the plot.html template
    return render_template('plot.html', plot_html=plot_html, avg_prices=avg_prices)

if __name__ == '__main__':
    app.run(debug=True)
