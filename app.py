import yfinance as yahooFinance
import pandas as pd
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import streamlit as st

def get_company_news(company, from_date, to_date, language='en'):
    newsapi = NewsApiClient(api_key='d0991d9186da4c259f29b078bd9d7550') 
    news_articles = newsapi.get_everything(q=company, from_param=from_date, to=to_date, language=language)
    articles = []
    for article in news_articles['articles']:
        try:

            date_parts = article['publishedAt'].split('T')[0]
            news_date = datetime.strptime(date_parts, '%Y-%m-%d').date()
            articles.append(article)
        except Exception as e:

            print(f"Ignoring article with invalid date: {article['publishedAt']}")
            continue
    return articles


def get_stock_data(company_ticker):
    GetCompanyInformation = yahooFinance.Ticker(company_ticker)
    return GetCompanyInformation.history(period="max")
def main():
    st.title('Stock News App')


    company_ticker = st.text_input('Enter company ticker (e.g., "AAPL" for Apple):')


    if company_ticker:
        try:
            stock_data = get_stock_data(company_ticker)
        except Exception as e:
            st.error(f"Error retrieving stock data: {str(e)}")
            return

        if stock_data.empty:
            st.warning("No stock data available for the provided company ticker.")
            return

        today = datetime.now().date()
        one_week_ago = today - timedelta(days=7)
        from_date = one_week_ago.strftime('%Y-%m-%d')
        to_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        news_articles = get_company_news(company_ticker, from_date, to_date)


        st.subheader("Latest News Articles:")
        for idx, article in enumerate(news_articles):
            st.write(f"{idx+1}. [{article['title']}]({article['url']}) - {article['publishedAt']}")
            

            try:
                date_parts = article['publishedAt'].split('T')[0]
                news_date = datetime.strptime(date_parts, '%Y-%m-%d').date()
            except Exception as e:

                continue

            try:
                closest_date = min(stock_data.index, key=lambda x: abs(x.date() - news_date))
            except ValueError:

                continue


            if closest_date.date() < news_date:
                price_on_news_date = stock_data.loc[closest_date]['Close']
                next_date = closest_date + pd.Timedelta(days=1)
                while next_date not in stock_data.index:
                    next_date += pd.Timedelta(days=1)
                price_next_day = stock_data.loc[next_date]['Close']
            else:
                next_date = closest_date
                price_next_day = stock_data.loc[next_date]['Close']
                prev_date = closest_date - pd.Timedelta(days=1)
                while prev_date not in stock_data.index:
                    prev_date -= pd.Timedelta(days=1)
                price_on_news_date = stock_data.loc[prev_date]['Close']


            percentage_change = ((price_next_day - price_on_news_date) / price_on_news_date) * 100
            st.write(f"   - Percentage change after {news_date}: {percentage_change:.2f}%")

if __name__ == "__main__":
    main()
