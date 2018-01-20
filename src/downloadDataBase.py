from bs4 import BeautifulSoup
import requests
from time import sleep
from random import uniform
import time
import json
import queue
import threading

imdbUrl = "http://www.imdb.com"
imdbPopularUrl = "http://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm_8"
imdbSearchTitleUrl = "http://www.imdb.com/search/title"

class DownloadDataBase:
    def __init__(self):
        self.moviesDict = {}
        self.requestText = queue.Queue()
        self.allRequestDone = False
        self.endDownloading = False

    def downloadDatabase(self, moviesPages):
        try:
            moviesPages = int(moviesPages)
        except:
            print("Invalid number of pages")
            return

        self.endDownloading = False

        print("Download has started")
        soup =  BeautifulSoup(requests.get(imdbPopularUrl).text, "html.parser")
        makingRequests = threading.Thread(target = self.makeRequests, args=(soup, moviesPages))
        makingRequests.start()

        self.downloadGenreMovies(moviesPages)
        makingRequests.do_run = False
        makingRequests.join()
        with open('movies.json', 'w') as file:
            json.dump(self.moviesDict, file)

        self.moviesDict.clear()
        print("Download has ended")


    def makeRequests(self, soup, moviesPages):
        sleep(uniform(1.3, 3.7))
        moviesGeresSpan = soup.find('ul', {'class': 'quicklinks'})
        for linkHref in moviesGeresSpan.findAll('a'):

            genreUrl = imdbUrl + linkHref.get("href")
            pageUrl = genreUrl + "&title_type=movie" + "&sort=num_votes" + "&page=1"
            counter = 0
            numberOfPages = self.getNumberOfPages(pageUrl)

            while ((counter + 1) <= numberOfPages and counter < moviesPages):
                self.requestText.put(requests.get(pageUrl, headers={"Accept-Language": "en-US, en;q=0.5"}).text)

                counter += 1
                pageUrl = pageUrl[:-1] + str(int(counter + 1))

                sleep(uniform(1.3, 3.7))

        self.allRequestDone = True



    def downloadGenreMovies(self, moviesNumber):
        nextPageFound = True
        counterPages = 0
        while (not self.requestText.empty() or not self.allRequestDone):
            if (self.requestText.empty()):
                sleep(1)
            else:
                soup = BeautifulSoup(self.requestText.get(), "html.parser")

                movies = soup.findAll('div', {'class': 'lister-item mode-advanced'})

                for movie in movies:
                    self.getMovieData(movie)

                counterPages += 1
                print(counterPages)


    def getNumberOfPages(self, genreUrl):
        soupFirstPage = BeautifulSoup(requests.get(genreUrl).text, "html.parser")
        titlesNumber = soupFirstPage.find('div', {'class': "desc"})

        if titlesNumber is None:
            return 0

        titlesNumber = titlesNumber.text
        titlesNumber = titlesNumber[titlesNumber.find("of") + 2:]
        titlesNumber = titlesNumber[:titlesNumber.find("titles")]
        titlesNumber = titlesNumber.replace(' ' and ',', '')

        numberOfTitles = int(titlesNumber)

        return numberOfTitles


    def getMovieData(self, movie):
        name = movie.h3.a.text
        movieData = {}
        year = movie.find('span', {'class': 'lister-item-year text-muted unbold'}).text

        year = year.replace(' ', '')
        while year.find('(') >= 0:
            if year.find('(') >= 0 and year.find(')') >= 0  and year.find('(') + 1 < len(year):
                if year[year.find('(') + 1].isdigit():
                    year = year[year.find('(') + 1:year.find(')')]
                else:
                    year = year[year.find(')')+1:]

        movieData['Year'] = year

        durationStr = ""
        duration = movie.find('span', {'class': 'runtime'})
        if duration is not None:
            durationStr = duration.text
            durationStr = durationStr.replace(' ' and '\n', '')
        else:
            durationStr = ''

        if (durationStr.find('min') >= 0):
            durationStr = durationStr[:durationStr.find('min')]

        movieData['Duration'] = durationStr

        genres = movie.find('span', {'class': 'genre'})
        if genres is not None:
            movieData['Genres'] = genres.text.replace('\n', '').replace(' ', '')
        else:
            movieData['Genres'] = ''

        imdbRating = movie.strong
        if imdbRating is not None:
            movieData['ImdbRating'] = imdbRating.text
        else:
            movieData['ImdbRating'] = ''

        metascore = movie.find('span', {'class': 'metascore favorable'})
        if metascore is not None:
            movieData['Metascore'] = metascore.text.replace('\n', '').replace(' ', '')
        else:
            movieData['Metascore'] = ''

        bottomData = movie.find('p', {'class': 'sort-num_votes-visible'}).findAll('span', {'name': 'nv'})

        votes = bottomData[0]
        if votes is not None:
            movieData['Votes'] = votes.get('data-value').replace('\n', '').replace(' ', '')
        else:
            movieData['Votes'] = ''

        if len(bottomData) > 1:
            gross = bottomData[1]
            if gross is not None:
                movieData['Gross'] = gross.get('data-value').replace(' ' and ',', '')
            else:
                movieData['Gross'] = ''
        else:
            movieData['Gross'] = ''

        if (movieData['Year'].isdigit()):
            self.moviesDict[name] = movieData
