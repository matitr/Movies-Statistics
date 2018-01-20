from downloadDataBase import DownloadDataBase
import os
import json
import sys
from collections import OrderedDict

class DataBase(DownloadDataBase):
    def __init__(self):
        DownloadDataBase.__init__(self)
        self.genreMovies = {}
        self.genresList = []
        self.genreYears = {}

    def downloadDatabase(self, moviesPages):
        super(DataBase,self).downloadDatabase(moviesPages)

    def openDataBase(self):
        if os.path.exists("movies.json"):
            with open('movies.json') as file:
                try:
                    self.genreMovies.clear()
                    self.moviesDict.clear()
                    self.genresList.clear()
                    lines = file.read()
                    self.moviesDict = json.loads(lines)
                except:
                    print("DataBase file error", sys.exc_info())
                    return False
        else:
            print("DataBase does not exist")
            return False


        for movieName, movieData in self.moviesDict.items():
            for genre in movieData['Genres'].split(','):
                if genre in self.genreMovies:
                    self.genreMovies[genre][movieName] = movieData

                    if movieData['Year'] not in self.genreYears[genre]:
                        self.genreYears[genre].append(movieData['Year'])
                else:
                    self.genresList.append(genre)
                    self.genreMovies[genre] = {}
                    self.genreMovies[genre][movieName] = movieData

                    self.genreYears[genre] = []
                    self.genreYears[genre].append(movieData['Year'])


        self.genresList.sort()
        self.genreMovies = OrderedDict(sorted(self.genreMovies.items()))
        self.genreYears = OrderedDict(sorted(self.genreYears.items()))
        for movieGenre in self.genresList:
            self.genreYears[movieGenre].sort()


        print("DataBase has been opened")
        return True
