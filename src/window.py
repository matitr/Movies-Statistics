from dataBase import DataBase
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
import os, psutil


class Window:
    def __init__(self):
        self.root = Tk()
        self.rightFrames = {}
        self.dataBase = DataBase()
        self.xList = []
        self.yList = []
        self.labels = []

        for rightF in (DownloadFrame, RatingFrame, MetascoreFrame, GrossFrame):
            frame = rightF(self)
            self.rightFrames[rightF] = frame

        topBar = TopBar(self.root, self)

        self.figure = Figure(figsize=(13,9.5), dpi=100)
        self.subplot = self.figure.add_subplot(111)
        self.subplot.bar(self.xList, self.yList)
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

        self.rightFrames[DownloadFrame].pack(side=RIGHT, anchor=N, pady=30, padx=55)
        self.rightBarShowing = DownloadFrame
        self.rightFrames[RatingFrame].radioBAvarageR.invoke()

        self.figure.subplots_adjust(top=0.8)


    def run(self):
        self.root.mainloop()


    def showRightFrame(self, changeToFrame):
        if not bool(self.dataBase.moviesDict) and changeToFrame != DownloadFrame:
            print("No movie database")
            return

        frame = self.rightFrames[changeToFrame]
        self.rightFrames[self.rightBarShowing].pack_forget()
        frame.pack(side=RIGHT, anchor=N, pady=30, padx=55)
        self.rightBarShowing = changeToFrame



    def openDataBase(self, ):
        self.dataBase.openDataBase()
        genres = self.dataBase.genresList[:]
        genres.insert(0, "All genres within years")
        self.rightFrames[RatingFrame].showForCB['values'] = genres
        self.rightFrames[RatingFrame].showForCB.current(0)

        self.rightFrames[MetascoreFrame].showForCB['values'] = genres
        self.rightFrames[MetascoreFrame].showForCB.current(0)

        self.rightFrames[GrossFrame].showForCB['values'] = genres
        self.rightFrames[GrossFrame].showForCB.current(0)

        self.showRightFrame(DownloadFrame)


    def showGraphRating(self):
        showRatingType = self.rightFrames[RatingFrame].showRatingType.get()
        genre = self.rightFrames[RatingFrame].showForType.get()

        self.labels.clear()
        xValues = []
        yValues = []
        yMin = 99999.0

        if showRatingType == "Avarage":
            xValues, yValues, yMin = self.getYListAvarage('ImdbRating', genre)
        else: # Best
            xValues, yValues, yMin = self.getYListBest('ImdbRating', genre)

        self.drawGraph(xValues, yValues, yMin)


    def showGraphMetascore(self):
        showRatingType = self.rightFrames[MetascoreFrame].showMetascoreType.get()
        genre = self.rightFrames[MetascoreFrame].showForType.get()

        self.labels.clear()
        xValues = []
        yValues = []
        yMin = 99999.0

        if showRatingType == "Avarage":
            xValues, yValues, yMin = self.getYListAvarage('Metascore', genre)
        else: # Best
            xValues, yValues, yMin = self.getYListBest('Metascore', genre)

        self.drawGraph(xValues, yValues, yMin)


    def showGraphGross(self):
        showRatingType = self.rightFrames[GrossFrame].showGrossType.get()
        genre = self.rightFrames[GrossFrame].showForType.get()

        self.labels.clear()
        xValues = []
        yValues = []
        yMin = 99999.0

        if showRatingType == "Avarage":
            xValues, yValues, yMin = self.getYListAvarage('Gross', genre)
        else: # Best
            xValues, yValues, yMin = self.getYListBest('Gross', genre)

        self.drawGraph(xValues, yValues, yMin)


    def getYListAvarage(self, dataToGet, genre):
        xValues = []
        yValues = []
        yMin = 99999.0
        if genre == "All genres within years":
            xValues = self.dataBase.genresList[:]
            for genre, movies in self.dataBase.genreMovies.items():
                sum = 0
                counter = 0
                for movie, movieData in movies.items():
                    if not movieData[dataToGet] == "":
                        sum += float(movieData[dataToGet])
                        counter += 1
                if counter == 0:
                    yValues.append(0)
                else:
                    yValues.append(float(sum / counter))#
                if yValues[-1] < yMin:
                    yMin = yValues[-1]
        else: # For one genre
            xValues = self.dataBase.genreYears[genre][:]
            movies = self.dataBase.genreMovies[genre]
            yearValue = {} # (0,1)  0 - rating sum, 1 - rating counter
            for year in self.dataBase.genreYears[genre]:
                yearValue[year] = [0.0,0]

            for movieName, movieData in movies.items():
                if not movieData[dataToGet] == "":
                    yearValue[movieData['Year']][0] += float(movieData[dataToGet])
                    yearValue[movieData['Year']][1] += 1

            for year in self.dataBase.genreYears[genre]:
                if yearValue[year][1] != 0:
                    yValues.append(float(yearValue[year][0]/yearValue[year][1]))
                    if yValues[-1] < yMin:
                        yMin = yValues[-1]
                else:# delete from list. Do not show on graph
                    xValues.remove(year)


        return xValues, yValues, yMin



    def getYListBest(self, dataToGet, genre):
        xValues = []
        yValues = []
        yMin = 99999.0
        if genre == "All genres within years":
            xValues = self.dataBase.genresList[:]
            for genre, movies in self.dataBase.genreMovies.items():
                bestRating = [0.0, ""]
                for movie, movieData in movies.items():
                    if not movieData[dataToGet] == "" and float(movieData[dataToGet]) > bestRating[0]:
                        bestRating[0] = float(movieData[dataToGet])
                        bestRating[1] = movie

                yValues.append(bestRating[0])
                self.labels.append(bestRating[1])
                if yValues[-1] < yMin:
                    yMin = yValues[-1]
        else: # For one genre
            xValues = self.dataBase.genreYears[genre][:]
            movies = self.dataBase.genreMovies[genre]
            yearBest = {} # (0,1)  0 - rating sum, 1 - rating counter
            for year in self.dataBase.genreYears[genre]:
                yearBest[year] = [-1, ""]

            for movieName, movieData in movies.items():
                if not movieData[dataToGet] == "" and float(movieData[dataToGet]) > yearBest[movieData['Year']][0]:
                    yearBest[movieData['Year']][0] = float(movieData[dataToGet])
                    yearBest[movieData['Year']][1] = movieName

            for year in self.dataBase.genreYears[genre]:
                if yearBest[year][0] != -1:
                    yValues.append(float(yearBest[year][0]))
                    self.labels.append(yearBest[year][1])
                    if yValues[-1] < yMin:
                        yMin = yValues[-1]
                else:# delete from list. Do not show on graph
                    xValues.remove(year)


        return xValues, yValues, yMin



    def drawGraph(self, xlist, ylist, yMin, width=0.5, color='r'):
        if yMin - yMin * 0.8 > 0:
            yMin = yMin - 1

        self.canvas.get_tk_widget().delete(self.subplot)

        self.figure.delaxes(self.subplot)
        self.subplot = self.figure.add_subplot(111)

        self.xList = xlist[:]
        self.yList = ylist[:]

 #       self.subplot.clear()
 #       self.subplot.cla()

        self.subplot.bar(self.xList, self.yList, .5)
        self.subplot.set_ylim(ymin=yMin)

        for tick in self.subplot.get_xticklabels():
            tick.set_rotation(-75)

        if len(self.labels) > 0:
            yMin, yMax = self.subplot.get_ylim()
            self.subplot.set_ylim(ymax=yMax + yMax * 0.12)

            rects = self.subplot.patches

            for rect, label in zip(rects, self.labels):
                height = rect.get_height()
                xPos = rect.get_x() + rect.get_width()/2

                self.subplot.text(xPos, height + height*0.005, label, ha='center', va='bottom', rotation=-90, fontsize=9.5)
#                self.subplot.text(300, 300, label, size=50)
#                self.subplot.annotate('B', xy=(rect.get_x() + rect.get_width() / 2, height + height * 0.05))

#        self.figure.set_size_inches(18.5, 10.5)
        self.canvas.draw()

def get_axis_limits(ax, scale=.9):
    return ax.get_xlim()[1]*scale, ax.get_ylim()[1]*scale

class TopBar(Frame):
    def __init__(self, parent, window):
        Frame.__init__(self, parent)
        self.pack(side=TOP, pady=10)
        self.rightBar = Frame(parent)
        self.openDatabase_btn = Button(self, text="Open database",
                                   command=lambda:window.openDataBase())
        self.download_btn = Button(self, text="Download database",
                                   command=lambda:window.showRightFrame(DownloadFrame))
        self.rating_btn = Button(self, text="Rating",
                                   command=lambda:window.showRightFrame(RatingFrame))
        self.metascore_btn = Button(self, text="Metascore",
                                   command=lambda:window.showRightFrame(MetascoreFrame))
        self.gross_btn = Button(self, text="Gross",
                                   command=lambda:window.showRightFrame(GrossFrame))

        self.openDatabase_btn.pack(side=LEFT, padx=30)
        self.download_btn.pack(side=LEFT, padx=30)
        self.rating_btn.pack(side=LEFT, padx=30)
        self.metascore_btn.pack(side=LEFT, padx=30)
        self.gross_btn.pack(side=LEFT, padx=30)


class DownloadFrame(Frame):
    def __init__(self, window):
        Frame.__init__(self, window.root)

        self.label = Label(self, text="Movie pages per genre")
        self.entryMovPerGen = Entry(self)
        self.download_btn = Button(self, text="Download",
                                command=lambda: window.dataBase.downloadDatabase(self.entryMovPerGen.get()))

        self.label.grid(row=0, column=0)
        self.entryMovPerGen.grid(row=0, column=1)
        self.download_btn.grid(columnspan=2, pady=10)



class RatingFrame(Frame):
    def __init__(self, window):
        Frame.__init__(self, window.root)

        self.label = Label(self, text="Show for")
        self.label.grid(row=0, column=0,pady=10)

        self.showForType = StringVar()
        self.showForType.set('All genres within years')

        self.showForCB = ttk.Combobox(self, textvariable=self.showForType, values=["All genres within years"], state='readonly')
        self.showForCB.current(0)
        self.showForCB.grid(row=0, column=1)

        self.showRatingType = StringVar()
        self.showRatingType.set('Avarage')

        self.radioBAvarageR = Radiobutton(self, text="Avarage rating", variable=self.showRatingType, value='Avarage')
        self.radioBAvarageR.grid(row=2, column=0, sticky=W)
        self.radioBBestR = Radiobutton(self, text="Best rating", variable=self.showRatingType, value='Best')
        self.radioBBestR.grid(row=3, column=0, pady=10, sticky=W)

        self.showGraph_btn = Button(self, text="Show graph", command=window.showGraphRating)
        self.showGraph_btn.grid(columnspan=2, pady=10)


class MetascoreFrame(Frame):
    def __init__(self, window):
        Frame.__init__(self, window.root)

        self.label = Label(self, text="Show for")
        self.label.grid(row=0, column=0,pady=10)

        self.showForType = StringVar()
        self.showForType.set('All genres within years')

        self.showForCB = ttk.Combobox(self, textvariable=self.showForType, values=["All genres within years"], state='readonly')
        self.showForCB.current(0)
        self.showForCB.grid(row=0, column=1)

        self.showMetascoreType = StringVar()
        self.showMetascoreType.set('Avarage')

        self.radioBAvarageR = Radiobutton(self, text="Avarage metascore", variable=self.showMetascoreType, value='Avarage')
        self.radioBAvarageR.grid(row=2, column=0, sticky=W)
        self.radioBBestR = Radiobutton(self, text="Best metascore", variable=self.showMetascoreType, value='Best')
        self.radioBBestR.grid(row=3, column=0, pady=10, sticky=W)

        self.showGraph_btn = Button(self, text="Show graph", command=window.showGraphMetascore)
        self.showGraph_btn.grid(columnspan=2, pady=10)


class GrossFrame(Frame):
    def __init__(self, window):
        Frame.__init__(self, window.root)

        self.label = Label(self, text="Show for")
        self.label.grid(row=0, column=0,pady=10)

        self.showForType = StringVar()
        self.showForType.set('All genres within years')

        self.showForCB = ttk.Combobox(self, textvariable=self.showForType, values=["All genres within years"], state='readonly')
        self.showForCB.current(0)
        self.showForCB.grid(row=0, column=1)

        self.showGrossType = StringVar()
        self.showGrossType.set('Avarage')

        self.radioBAvarageR = Radiobutton(self, text="Avarage gross", variable=self.showGrossType, value='Avarage')
        self.radioBAvarageR.grid(row=2, column=0, sticky=W)
        self.radioBBestR = Radiobutton(self, text="Best gross", variable=self.showGrossType, value='Best')
        self.radioBBestR.grid(row=3, column=0, pady=10, sticky=W)

        self.showGraph_btn = Button(self, text="Show graph", command=window.showGraphGross)
        self.showGraph_btn.grid(columnspan=2, pady=10)

