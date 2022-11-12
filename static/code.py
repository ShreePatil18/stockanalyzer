from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

finviz_url='https://finviz.com/quote.ashx?t='
tickers=input("Enter the code: ")
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

import matplotlib.pyplot as plt

plt.figure(figsize=(10,8))

mean_df=df.groupby(['ticker','date']).mean()
mean_df=mean_df.unstack()
mean_df=mean_df.xs('compound',axis="columns").transpose()

mean_df.plot(kind='bar')
plt.show