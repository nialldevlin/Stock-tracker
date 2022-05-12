from screener import Screener
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email import encoders
import os
import pandas as pd

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    s = Screener('https://en.wikipedia.org/wiki/List_of_S&P_500_companies')
    list = s.getList()
    data = s.getData(list)
    buy = s.getBuy(data)
    print(buy)