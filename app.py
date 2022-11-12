import imp
from distutils.log import debug
from lib2to3.pgen2.token import NAME
from re import X
import io
from flask import Response
from unicodedata import name
from urllib import request
import numpy as np
from urllib.request import Request, urlopen
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

app=Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result', methods=['POST','GET'])
def result():
    tickers=request.form.get('ticker')
    
    finviz_url='https://finviz.com/quote.ashx?t='
    #tickers=input("Enter the code: ")
    news_tables={}
    url=finviz_url+tickers
    req=Request(url=url,headers={'user-agent': 'my-app'})
    response=urlopen(req)
    html=BeautifulSoup(response,'html')
    news_table=html.find(id='news-table')
    news_tables[tickers]=news_table
    print(news_tables)
    ticker_data=news_tables[tickers]
    ticker_rows=ticker_data.findAll('tr')

    for index,row in enumerate(ticker_rows):
       title=row.a.text
       timestamp=row.td.text
       print(timestamp + " " + title)
    
    parsed_data = [ ]
    for ticker , news_table in news_tables.items():
        for row in news_table.findAll('tr'):
        
            title=row.a.text
            
            date_data=row.td.text.split(' ')
        
            if len(date_data)==1:
               time=date_data[0]
            else:
               date=date_data[0]
               time=date_data[1]
            
        parsed_data.append([ticker,date,time,title])

    print(parsed_data)

    df=pd.DataFrame(parsed_data, columns=['ticker','date','time','title'])
    print(df.head())

    vader=SentimentIntensityAnalyzer()
    print(vader.polarity_scores("I dont like apple is a good company"))

    f=lambda title: vader.polarity_scores(title)['compound']
    df['compound']=df['title'].apply(f)
    print(df.head())


    df['date']=pd.to_datetime(df.date).dt.date
    print(df)

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    
    axis.plot(df.title, df.compound)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return render_template('result.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)



    










if __name__=="__main__":
    app.run(debug=True)