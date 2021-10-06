import requests
import smtplib
from email.message import EmailMessage

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
USER = "rubix.send@gmail.com"
PWD = "*(d7ZO!Si449!QjNI"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
stock_parameters = {
    "apikey": "8YOVH3RQFPD9CXXF",
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    # "interval": "5min",
}
news_parameters = {
    "apikey": "bbf1dcc1f02f41f08138709429b504d9",
    "qInTitle": COMPANY_NAME,
    # "sortBy": "popularity"
}


def get_stock():
    r = requests.get(STOCK_ENDPOINT, params=stock_parameters)
    data = r.json()
    dates = list(data['Time Series (Daily)'].keys())[:2]
    close_prices = []
    for date in dates:
        close_prices.append(float(data['Time Series (Daily)'][date]['4. close']))
        print(f"{date}: {data['Time Series (Daily)'][date]['4. close']}")
    check_diff(close_prices[0], close_prices[1])


def check_diff(new_val, old_val):
    pos_diff = abs(new_val - old_val)
    diff_percent = round((pos_diff / new_val) * 100,2)

    if diff_percent > 0.5:
        subject = f"{COMPANY_NAME} 🔺{diff_percent}%"
        print(subject)
        content = get_news()
        # send_mail(subject, content)
    else:
        subject = f"{COMPANY_NAME} 🔻{diff_percent}%"
        print(subject)

    return subject


def get_news():
    r = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news = r.json()['articles'][:3]
    content=""
    for article in news:
        content += "".join(f"Headline: {article['title']} \nBrief: {article['description']}")
    print(content)
    return content


def send_mail(sub, msg):

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=USER, password=PWD)
        connection.sendmail(
            from_addr=USER,
            to_addrs='p.jesal.work@gmail.com',
            msg=f"Subject: {sub} Stock update \n\n{msg}"
        )
        print("email sent!")


get_stock()

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
