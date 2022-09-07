import smtplib

from bs4 import BeautifulSoup
from flask import Flask, render_template
import csv
import datetime
import pandas
import requests
import config
import constants

# ---App---
app = Flask(__name__)

# ---API Service ---
# --- an exception is raised if the server has not issued a response
# for timeout seconds
weather_response = requests.get(config.API_ENDPOINT, params=constants.weather_params, timeout=10)
weather_response.raise_for_status()
weather_data = weather_response.json()

# ---Filtering the weather conditions
temp_description = weather_data['hourly'][0]['temp']
feels_like_description = weather_data['hourly'][0]['feels_like']
clima_description = weather_data['hourly'][0]['weather'][0]['description']
iconId = weather_data['hourly'][0]['weather'][0]['icon']
eft = weather_data['hourly'][0]['weather'][0]['id']

# ---Read the first 12h only
weather_slice = weather_data['hourly'][:12]

# ---Getting the weather icon
IMG_CODE = iconId
IMG_SOURCE = f'http://openweathermap.org/img/wn/{IMG_CODE}@2x.png'

# ---To avoid repeated responses
thunderstorm = False
will_rain = False

# ---Checking the weather response to send an email in case of storm or heavy rain
for hour_data in weather_slice:
    condition_code = hour_data['weather'][0]['id']
    # print(condition_code)
    if 500 <= int(condition_code) <= 531:
        will_rain = True
    if int(condition_code) <= 232 or int(condition_code) == 781:
        thunderstorm = True

if will_rain:
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(user=config.sender_email, password=config.password)
        connection.sendmail(
            from_addr=config.sender_email,
            to_addrs=config.receiver_email,
            msg='Subject:Alerta de Tempo - Pimentinha Noticias\n\n Nu-bá, alerta de chuva forte para hoje. ⛈'.encode(
                'utf-8')
        )
if thunderstorm:
    with smtplib.SMTP('smtp.gmail.com') as connection:
        connection.starttls()
        connection.login(user=config.sender_email, password=config.password)
        connection.sendmail(
            from_addr=config.sender_email,
            to_addrs=config.receiver_email,
            msg='Subject:Alerta de Tempo - Pimentinha Noticias\n\n Nu-bá, alerta de tempestade para hoje. 🌪'.encode(
                'utf-8')
        )


# ---Page routes---

@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    currente_date = datetime.datetime.today().strftime('%d/%b/%Y')
    icon_source = f'http://openweathermap.org/img/wn/{IMG_CODE}@2x.png'

    return render_template("index.html", year=current_year, date=currente_date,
                           temp_description=temp_description, feels_like_description=feels_like_description,
                           clima_description=clima_description, icon_source=icon_source)


@app.route("/construcao")
def in_construction():
    current_year = datetime.datetime.now().year
    return render_template("template-in-construction-page.html", year=current_year)


@app.route("/prefeitura")
def prefeitura():
    response = requests.get(constants.PREF_URL, timeout=10)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = constants.PREF_FILENAME
    all_news = []

    for a in soup.select("h3 a", href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        link = a["href"]
        news_dic = {"title": text, "url": link}
        all_news.append(news_dic)

    with open(filename, "w", newline="", encoding='utf-8') as file:
        data_news_file = csv.DictWriter(file, ["title", "url"])
        data_news_file.writeheader()
        for news_dic in all_news:
            data_news_file.writerow(news_dic)

    data = pandas.read_csv(constants.PREF_FILENAME, header=0)
    news_data = data.values
    return render_template("prefeitura-page.html", news_data=news_data)


@app.route("/g1minas")
def g1minas():
    response = requests.get(constants.G1_MINAS_URL, timeout=10)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = constants.G1_MINAS_FILENAME
    all_news = []

    for a in soup.select("a", {"_class": "bastian-feed-item"}, href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        news_dic = {}
        if len(text) > 20:
            link = a.get("href")
            news_dic["title"] = text
            news_dic["url"] = link
            all_news.append(news_dic)
            if len(all_news) > 10:
                break

    with open(filename, "w", newline="", encoding='utf-8') as f:
        w = csv.DictWriter(f, ["title", "url"])
        w.writeheader()
        for news_dic in all_news:
            w.writerow(news_dic)
    data = pandas.read_csv(constants.G1_MINAS_FILENAME, header=0)
    news_data_gminas = data.values
    return render_template("g1minas-page.html", news_data_gminas=news_data_gminas)


@app.route("/globo")
def globo():
    response = requests.get(constants.GLOBOL_URL, timeout=10)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = constants.GLOBO_FILENAME
    all_news = []

    for a in soup.select("a", {"_class": "post"}, href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        news_dic = {}
        if len(text) > 25:
            link = a.get("href")
            news_dic["title"] = text
            news_dic["url"] = link
            all_news.append(news_dic)
            if len(all_news) > 61:
                break

    with open(filename, "w", newline="", encoding='utf-8') as f:
        w = csv.DictWriter(f, ["title", "url"])
        w.writeheader()
        for news_dic in all_news:
            w.writerow(news_dic)
    data = pandas.read_csv(constants.GLOBO_FILENAME, header=0)
    news_data_globo = data.values
    return render_template("globo-page.html", news_data_globo=news_data_globo)


@app.route('/terra')
def terra_entrete():
    filename = constants.TERRA_ENTRETE_FILENAME
    all_news = []

    response = requests.get(constants.TERRA_ENTRETE_URL, timeout=10)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    for a in soup.select("h2 a", {"class_": "card-news__text--title main-url"}, href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        news_dic = {}
        link = a.get("href")
        news_dic["title"] = text
        news_dic["url"] = link
        all_news.append(news_dic)

    with open(filename, "w", newline="", encoding='utf-8') as f:
        data_news_file = csv.DictWriter(f, ["title", "url"])
        data_news_file.writeheader()
        for news_dic in all_news:
            data_news_file.writerow(news_dic)

    data = pandas.read_csv(constants.TERRA_ENTRETE_FILENAME, header=0)
    news_data = data.values

    return render_template("terra-entrete-page.html", news_data=news_data)


@app.route('/msn')
def msn():
    filename = constants.MSN_FILENAME
    all_news = []

    response = requests.get(constants.MSN_URL, timeout=10)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    for a in soup.select("div a", {"class_": "title"}, href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        news_dic = {}
        if len(text) > 20:
            link = a.get("href")
            news_dic["title"] = text
            news_dic["url"] = link
            all_news.append(news_dic)
    # delete the two itens because they're links to another page, not news.
    del all_news[-2:]

    with open(filename, "w", newline="", encoding='utf-8') as f:
        data_news_file = csv.DictWriter(f, ["title", "url"])
        data_news_file.writeheader()
        for news_dic in all_news:
            data_news_file.writerow(news_dic)

    data = pandas.read_csv(constants.MSN_FILENAME, header=1)
    news_data = data.values

    return render_template("msn-page.html", news_data=news_data)


@app.route("/metroples")
def metropoles():
    response = requests.get(constants.METROPOLES_URL, timeout=10)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = constants.METROPOLES_FILENAME
    all_news = []

    for a in soup.select("a", {"_class": "m-title"}, href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        news_dic = {}
        if len(text) > 35:
            link = a.get("href")
            news_dic["title"] = text
            news_dic["url"] = link
            all_news.append(news_dic)
            if len(all_news) > 120:
                break

    with open(filename, "w", newline="", encoding='utf-8') as f:
        w = csv.DictWriter(f, ["title", "url"])
        w.writeheader()
        for news_dic in all_news:
            w.writerow(news_dic)
    data = pandas.read_csv(constants.METROPOLES_FILENAME, header=0)
    news_data_metropoles = data.values
    return render_template("metropoles-page.html", news_data_metropoles=news_data_metropoles)


if __name__ == "__main__":
    app.run(debug=True)
