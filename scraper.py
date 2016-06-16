from bs4 import BeautifulSoup
import requests
import datetime
import csv
import time
import os
import re
import pdfkit
import wkhtmltopdf
from django.utils import text as text_util

fieldnames_list = ['title', 'identifier', 'no', 'year', 'month', 'day', 'division', 'ponente', 'link']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
URL = "http://elibrary.judiciary.gov.ph/"
ALL_DOCS = "thebookshelf/docmonth/"
PDF_FRIENDLY = "thebookshelf/showdocsfriendly/"
DOC_VIEW = "thebookshelf/showdocs/"


def write_csv(writer, title, identifier, id_no, dt_date, division, ponente, link):
    writer.writerow([title.encode('ascii', 'ignore'), identifier.encode('ascii', 'ignore'),
                     id_no.encode('ascii', 'ignore'), str(dt_date.year), dt_date.strftime('%B'), str(dt_date.day),
                     division.encode('ascii', 'ignore'), ponente.encode('ascii', 'ignore'),
                     link.encode('ascii', 'ignore')])


def scrape_month(url, url_params, month, year):
    print url + url_params + month + "/" + year + "/1"
    # fetch
    site_html = requests.request('GET', url + url_params + month + "/" + year + "/1").text
    # parse
    soup = BeautifulSoup(site_html, "lxml")
    site_data = soup.find(id="container_title")
    filename = year + "_" + month + ".csv"
    with open(filename, 'w') as csvFile:
        fieldnames_list = ['title', 'identifier', 'no', 'year', 'month', 'day', 'division', 'ponente', 'link']
        writer = csv.writer(csvFile, lineterminator='\n')
        writer.writerow(fieldnames_list)
        # writer.writeheader()
        for list_item in site_data.find_all('li'):
            title = list_item.find('small').text.strip().replace('\n', '')
            id_temp = list_item.find('strong').text.strip().replace('\n', '')
            identifier = id_temp.split()[0]
            id_no = "".join(id_temp.split()[2:])
            link = list_item.find('a')['href']
            try:
                dt_date = datetime.datetime.strptime(list_item.find('a').text.split('\n')[-1].strip(' '), '%B %d, %Y')
            except ValueError:
                print ValueError
                dt_date = ""
            # print requests.get(link).text
            site_item_soup = BeautifulSoup(requests.get(link).text, "lxml")

            try:
                site_item_data = site_item_soup.find(id="left").find(class_="single_content")
            except AttributeError:
                writer.writerow([title.encode('ascii', 'ignore'), identifier, id_no, dt_date.year, dt_date.strftime('%B'),
                                dt_date.day, "", "", link])
                continue

            division = site_item_data.find_all('h2')[0].text
            ponente = site_item_data.find_all('strong')[0].text.strip(':')
            print ""
            print "title:\t" + title
            print "Identifier:\t" + identifier
            print "No.:\t" + id_no
            if dt_date is "":
                print "date:\t" + " "
            else:
                print "date:\t" + dt_date.strftime('%B %d, %Y')
            print "division:\t" + division
            print "ponente:\t" + ponente
            print "link:\t" + link
            print ""
            if dt_date == "":
                writer.writerow([title.encode('ascii', 'ignore'), identifier.encode('ascii', 'ignore'),
                                 id_no.encode('ascii', 'ignore'), year, month, " ",
                                 division.encode('ascii', 'ignore'), ponente.encode('ascii', 'ignore'),
                                 link.encode('ascii', 'ignore')])

            else:
                writer.writerow([title.encode('ascii', 'ignore'), identifier.encode('ascii', 'ignore'),
                                 id_no.encode('ascii', 'ignore'), dt_date.year, dt_date.strftime('%B'),
                                 dt_date.day, division.encode('ascii', 'ignore'), ponente.encode('ascii', 'ignore'),
                                 link])


def scrape_year(url, url_params, year):
    filename = year + ".csv"
    with open(filename, 'w') as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        writer.writerow(fieldnames_list)
        for month in months:
            print url + url_params + month + "/" + year + "/1"
            # fetch
            site_html = requests.request('GET', url + url_params + month + "/" + year + "/1").text
            # parse
            soup = BeautifulSoup(site_html, "lxml")
            site_data = soup.find(id="container_title")
            for list_item in site_data.find_all('li'):
                title = list_item.find('small').text.strip().replace('\n', '')
                id_temp = list_item.find('strong').text.strip().replace('\n', '')
                identifier = id_temp.split()[0]
                id_no = "".join(id_temp.split()[2:])
                link = list_item.find('a')['href']
                try:
                    dt_date = datetime.datetime.strptime(list_item.find('a').text.split('\n')[-1].strip(' '), '%B %d, %Y')
                except ValueError:
                    print ValueError
                    dt_date = ""
                # print requests.get(link).text
                site_item_soup = BeautifulSoup(requests.get(link).text, "lxml")
                try:
                    site_item_data = site_item_soup.find(id="left").find(class_="single_content")
                    division = site_item_data.find_all('h2')[0].text
                    ponente = site_item_data.find_all('strong')[0].text.strip(':')
                except AttributeError:
                    division = ""
                    ponente = ""

                print ""
                print "title:\t" + title
                print "Identifier:\t" + identifier
                print "No.:\t" + id_no
                if dt_date is "":
                    print "date:\t" + " "
                else:
                    print "date:\t" + dt_date.strftime('%B %d, %Y')
                print "division:\t" + division
                print "ponente:\t" + ponente
                print "link:\t" + link
                print ""
                if dt_date == "":
                    writer.writerow([title.encode('ascii', 'ignore'), identifier.encode('ascii', 'ignore'),
                                     id_no.encode('ascii', 'ignore'), year, month, " ",
                                     division.encode('ascii', 'ignore'), ponente.encode('ascii', 'ignore'),
                                     link.encode('ascii', 'ignore')])

                else:
                    writer.writerow([title.encode('ascii', 'ignore'), identifier.encode('ascii', 'ignore'),
                                     id_no.encode('ascii', 'ignore'), dt_date.year, dt_date.month,
                                     dt_date.day, division.encode('ascii', 'ignore'), ponente.encode('ascii', 'ignore'),
                                     link])


def get_list_by_ponente(ponente, year):
    if not os.path.exists(ponente):
        os.makedirs(ponente)
    if not os.path.exists(ponente + '/' + year):
        os.makedirs(ponente + '/' + year)
    csvfile = year + ".csv"
    with open(csvfile, 'r') as csvFile:
        reader = csv.DictReader(csvFile, fieldnames=fieldnames_list)
        for row in reader:
            print row['ponente']
            print row['year']
            print row['month']
            print row['day']
            if row['ponente'].find(ponente) is not -1:
                linkfriendly = row['link'].replace(DOC_VIEW, PDF_FRIENDLY)
                month = row['month']
                day = row['day']
                pdf_filename = ponente + '/' + year + '/' + month + '_' + day
                month_count = 0
                while os.path.isfile(pdf_filename + '.pdf'):
                    month_count += 1
                    pdf_filename = ponente + '/' + year + '/' + month + '_' + day + '_' + str(month_count)

                pdfkit.from_url(linkfriendly, pdf_filename + '.pdf')
                print pdf_filename + 'saved!'


def get_list_by_ponente_save_as_title(ponente, year):
    if not os.path.exists(ponente):
        os.makedirs(ponente)
    if not os.path.exists(ponente + '/' + year):
        os.makedirs(ponente + '/' + year)
    csvfile = year + ".csv"
    with open(csvfile, 'r') as csvFile:
        reader = csv.DictReader(csvFile, fieldnames=fieldnames_list)
        for row in reader:
            print row['ponente']
            print row['year']
            print row['month']
            print row['day']
            print text_util.slugify(row['title'].replace('\n', ' '))
            if row['ponente'].find(ponente) is not -1:
                linkfriendly = row['link'].replace(DOC_VIEW, PDF_FRIENDLY)
                pdf_filename = ponente + '/' + year + '/' + text_util.slugify(row['title']) + '(' + year + ')'
                pdf_filename.replace('\n', ' ')
                month_count = 0
                while os.path.isfile(pdf_filename + '.pdf'):
                    month_count += 1
                    pdf_filename = ponente + '/' + year + '/' + text_util.slugify(row['title']) + '(' + str(month_count) + ')' + '(' + year + ')'
                    pdf_filename.replace('\n', ' ')

                pdfkit.from_url(linkfriendly, pdf_filename + '.pdf')
                print pdf_filename + ' saved!'


def main():
    # month = "Jan"
    # year = "2015"
    for ctr in range(2012, 2017):
        year = str(ctr)
    # scrape_year(url, url_params, "2014")
    # scrape_month(url, url_params, "Mar", "2007")
        get_list_by_ponente_save_as_title('VELASCO', '2007')
    return 0

start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
