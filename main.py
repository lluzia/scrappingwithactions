from bs4 import BeautifulSoup
from flask import Flask, render_template
import csv
import datetime
import pandas
import requests

# ----Constants----
PREF_URL = "https://www.uberlandia.mg.gov.br/todas-as-noticias/"
PREF_FILENAME = "prefeitura_data.csv"
G1_MINAS_URL = "https://g1.globo.com/mg/minas-gerais/ultimas-noticias/"
G1_MINAS_FILENAME = "g1minas_data.csv"
TERRA_ENTRETE_URL = "https://www.terra.com.br/diversao/"
TERRA_ENTRETE_FILENAME = "terra_entrete.csv"
MSN_URL = "https://www.msn.com/pt-br"
MSN_FILENAME = "msn.csv"
GLOBOL_URL = "https://www.globo.com/"
GLOBO_FILENAME = "g1_nacional_data.csv"
METROPOLES_URL = "https://www.metropoles.com/"
METROPOLES_FILENAME = "metropoles_data.csv"
# ---App---
app = Flask(__name__)

# ---Weather ---


# ---Page routes---

@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    currente_date = datetime.datetime.today().strftime('%d/%b/%Y')

    return render_template("index.html", year=current_year, date=currente_date)


@app.route("/construcao")
def in_construction():
    current_year = datetime.datetime.now().year
    return render_template("template-in-construction-page.html", year=current_year)


@app.route("/prefeitura")
def prefeitura():
    response = requests.get(PREF_URL)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = PREF_FILENAME
    all_news = []

    for a in soup.select("h3 a", href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        link = a["href"]
        news_dic = {"title": text, "url": link}
        all_news.append(news_dic)

    with open(filename, "w", newline="") as file:
        data_news_file = csv.DictWriter(file, ["title", "url"])
        data_news_file.writeheader()
        for news_dic in all_news:
            data_news_file.writerow(news_dic)

    data = pandas.read_csv(PREF_FILENAME, header=0)
    news_data = data.values
    return render_template("prefeitura-page.html", news_data=news_data)


@app.route("/g1minas")
def g1minas():
    response = requests.get(G1_MINAS_URL)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = G1_MINAS_FILENAME
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

    with open(filename, "w", newline="") as f:
        w = csv.DictWriter(f, ["title", "url"])
        w.writeheader()
        for news_dic in all_news:
            w.writerow(news_dic)
    data = pandas.read_csv(G1_MINAS_FILENAME, header=0)
    news_data_gminas = data.values
    return render_template("g1minas-page.html", news_data_gminas=news_data_gminas)


@app.route("/globo")
def globo():
    response = requests.get(GLOBOL_URL)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = GLOBO_FILENAME
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

    with open(filename, "w", newline="") as f:
        w = csv.DictWriter(f, ["title", "url"])
        w.writeheader()
        for news_dic in all_news:
            w.writerow(news_dic)
    data = pandas.read_csv(GLOBO_FILENAME, header=0)
    news_data_globo = data.values
    return render_template("globo-page.html", news_data_globo=news_data_globo)


@app.route('/terra')
def terra_entrete():
    filename = TERRA_ENTRETE_FILENAME
    all_news = []

    response = requests.get(TERRA_ENTRETE_URL)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    for a in soup.select("h2 a", {"class_": "card-news__text--title main-url"}, href=True):
        text = a.getText().replace("\n", "").replace("\t", "")
        news_dic = {}
        link = a.get("href")
        news_dic["title"] = text
        news_dic["url"] = link
        all_news.append(news_dic)

    with open(filename, "w", newline="") as f:
        data_news_file = csv.DictWriter(f, ["title", "url"])
        data_news_file.writeheader()
        for news_dic in all_news:
            data_news_file.writerow(news_dic)

    data = pandas.read_csv(TERRA_ENTRETE_FILENAME, header=0)
    news_data = data.values

    return render_template("terra-entrete-page.html", news_data=news_data)


@app.route('/msn')
def msn():
    filename = MSN_FILENAME
    all_news = []

    response = requests.get(MSN_URL)
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

    with open(filename, "w", newline="") as f:
        data_news_file = csv.DictWriter(f, ["title", "url"])
        data_news_file.writeheader()
        for news_dic in all_news:
            data_news_file.writerow(news_dic)

    data = pandas.read_csv(MSN_FILENAME, header=1)
    news_data = data.values

    return render_template("msn-page.html", news_data=news_data)


@app.route("/metroples")
def metropoles():
    response = requests.get(METROPOLES_URL)
    web_noticia = response.text
    soup = BeautifulSoup(web_noticia, 'html.parser')

    filename = METROPOLES_FILENAME
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

    with open(filename, "w", newline="") as f:
        w = csv.DictWriter(f, ["title", "url"])
        w.writeheader()
        for news_dic in all_news:
            w.writerow(news_dic)
    data = pandas.read_csv(METROPOLES_FILENAME, header=0)
    news_data_metropoles = data.values
    return render_template("metropoles-page.html", news_data_metropoles=news_data_metropoles)


if __name__ == "__main__":
    app.run(debug=True)
