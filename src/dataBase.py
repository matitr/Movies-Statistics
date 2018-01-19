from downloadDataBase import DownloadDataBase
import os
import json
import sys

class DataBase(DownloadDataBase):
    def __init__(self):
        DownloadDataBase.__init__(self)
        self.genreMovies = {}
        self.genresList = []
        self.years = []

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
                else:
                    self.genresList.append(genre)
                    self.genreMovies[genre] = {}
                    self.genreMovies[genre][movieName] = movieData
            if movieData['Year'] not in self.years:
                self.years.append(movieData['Year'])

        self.genresList.sort()
        self.years.sort()
        print("DataBase has been opened")
        return True
