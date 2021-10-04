import requests
import html
import smtplib
from email.message import EmailMessage

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
USER = ""
PWD = ""

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
stock_parameters = {
    "apikey": "8YOVH3RQFPD9CXXF",
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "interval": "5min",
}
news_parameters = {
    "apikey": "bbf1dcc1f02f41f08138709429b504d9",
    "q": COMPANY_NAME,
    "sortBy": "popularity"
}


def get_stock():
    r = requests.get(STOCK_ENDPOINT, params=stock_parameters)
    data = r.json()
    dates = list(data['Time Series (Daily)'].keys())[:2]
    close_prices = []
    for date in dates:
        close_prices.append(float(data['Time Series (Daily)'][date]['4. close']))
        print(f"{date}: {data['Time Series (Daily)'][date]['4. close']}")
    check_profit(close_prices[0], close_prices[1])


def check_profit(new_val, old_val):
    pos_diff = abs(new_val - old_val)
    print(pos_diff, old_val * 0.05)
    if pos_diff < old_val * 0.05:
        print("+")
        subject = f"{COMPANY_NAME} 🔺{(pos_diff * 100) / new_val}%"
        content = get_news()
        send_mail(subject, content)
    else:
        print("-")
        subject = f"{COMPANY_NAME} 🔻{(pos_diff * 100) / new_val}%"


def get_news():
    r = requests.get(NEWS_ENDPOINT, params=news_parameters)
    news = html.unescape(r.json()['articles'][:3])
    content = ""
    for article in range(len(news)):
        content += f"\narticle: {article} \n{news[article]['title']} \n{news[article]['description']}"
    print(content)
    return content


def send_mail(sub, msg):
    msg = EmailMessage()
    msg.set_content(msg)

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
