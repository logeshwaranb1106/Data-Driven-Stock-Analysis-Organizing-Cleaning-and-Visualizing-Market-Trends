import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(query):
  conn = mysql.connector.connect(
    host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port = 4000,
    user = "user",
    password = "password",
    database = "database"
  )
  mycursor=conn.cursor(buffered=True)
  mycursor.execute(query)
  out=mycursor.fetchall()
  columns=[desc[0] for desc in mycursor.description]
  conn.close()
  return pd.DataFrame(out,columns=columns)

option=st.sidebar.selectbox('Select Option',['Data driven stock analysis','Top 5 gainers and losers'],index=0)
if option=='Data driven stock analysis':
  st.title('Data-Driven Stock Analysis: Organizing, Cleaning, and Visualizing Market Trends')
  st.header('1. Top 10 most volatile stocks in Nifty 50')
  volatility=load_data('select symbol,volatility from nifty.volatility_analysis order by volatility desc limit 10')
  fig,ax=plt.subplots()
  ax.bar(volatility['symbol'],volatility['volatility'])
  ax.set_xlabel('Stock Symbol')
  ax.set_ylabel('Volatility')
  ax.tick_params(axis='x',rotation=60)
  st.pyplot(fig)

  st.header('2. Cumulative Return for Top 5 Performing Stocks')
  cumulative=load_data('select symbol,cumulative_returns from nifty.cumulative_returns_analysis order by cumulative_returns desc limit 5')
  fig,ax=plt.subplots()
  ax.plot(cumulative['symbol'],cumulative['cumulative_returns'],marker='o')
  ax.set_xlabel('Stock Symbol')
  ax.set_ylabel('Cumulative Returns (%)')
  st.pyplot(fig)

  st.header('3. Average Yearly Return by Sector')
  sector=load_data('select sector,annual_returns from nifty.sector_performance_analysis')
  fig,ax=plt.subplots()
  ax.bar(sector['sector'],sector['annual_returns'])
  ax.set_xlabel('Sector')
  ax.set_ylabel('Annual Returns (%)')
  ax.tick_params(axis='x',rotation=90)
  st.pyplot(fig)

  st.header('4. Stock Price Correlation Heatmap')
  correlation=load_data('select symbol,close,date from nifty.final')
  correlation['date']=pd.to_datetime(correlation['date'])
  cor_pivot=correlation.pivot(index='date',columns='symbol',values='close')
  returns=cor_pivot.pct_change().dropna()
  corr_matrix=returns.corr()
  fig,ax=plt.subplots(figsize=(15,12))
  sns.heatmap(corr_matrix,cmap='coolwarm',annot=False,center=0,linewidths=0.5, linecolor='gray', square=True)
  ax.tick_params(axis='x',rotation=90)
  ax.tick_params(axis='y',rotation=0)
  st.pyplot(fig)

if option=='Top 5 gainers and losers':
  st.sidebar.subheader('Select Month')
  select_month=st.sidebar.selectbox('Month',['January','February','March','April','May','June','July','August','September','October','November','December'],index=0)
  st.title('Top 5 Gainers and Losers in Nifty 50 for the month of '+select_month)
  top5_gainers=load_data(f"select symbol,monthly_returns from nifty.top5 where month='{select_month}' order by monthly_returns desc limit 5")
  top5_losers=load_data(f"select symbol,monthly_returns from nifty.top5 where month='{select_month}' order by monthly_returns asc limit 5")
  fig,ax=plt.subplots(1,2,figsize=(12,6))
  ax[0].bar(top5_gainers['symbol'],top5_gainers['monthly_returns'],color='lightgreen',linewidth=0.5,edgecolor='black')                        
  ax[0].set_title('Top 5 Gainers')
  ax[0].set_xlabel('Stock Symbol')
  ax[0].set_ylabel('Monthly Returns (%)')
  ax[0].tick_params(axis='x',rotation=60)
  ax[1].bar(top5_losers['symbol'],top5_losers['monthly_returns'],color='salmon',linewidth=0.5,edgecolor='black')
  ax[1].set_title('Top 5 Losers')
  ax[1].set_xlabel('Stock Symbol')
  ax[1].set_ylabel('Monthly Returns (%)')
  ax[1].tick_params(axis='x',rotation=60)
  st.pyplot(fig)
