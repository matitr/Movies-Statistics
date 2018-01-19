from dataBase import DataBase
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as pyplot
from tkinter import ttk


class Window:
    def __init__(self):
        self.root = Tk()
        self.rightFrames = {}
        self.dataBase = DataBase()
        self.xList = []
        self.yList = []

        for rightF in (DownloadFrame, RatingFrame, MetascoreFrame, GrossFrame):
            frame = rightF(self)
            self.rightFrames[rightF] = frame

        pyplot.xticks(rotation=45)
        topBar = TopBar(self.root, self)
        self.figure = Figure(figsize=(10,7), dpi=100)
        self.subplot = self.figure.add_subplot(111)
        self.subplot.plot(self.xList, self.yList)
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

        self.rightFrames[DownloadFrame].pack(side=RIGHT, anchor=N, pady=30, padx=55)
        self.rightBarShowing = DownloadFrame
        self.rightFrames[RatingFrame].radioBAvarageR.invoke()


 #       self.drawGraph(["lol","asd"],[1,4],0)
 #       self.subplot.bar([5,8,9],[7,9,4])

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
        self.showRightFrame(DownloadFrame)


    def showGraphRating(self):
        showRatingType = self.rightFrames[RatingFrame].showRatingType.get()
        genre = self.rightFrames[RatingFrame].showForType.get()

        xValues = []
        yValues = []
        yMin = 99999.0
        if genre == "All genres within years":
            xValues = self.dataBase.genresList[:]
            if showRatingType == "Avarage":
                for genre, movies in self.dataBase.genreMovies.items():
                    sum = 0
                    for movie, movieData in movies.items():
                        if not movieData['ImdbRating'] == "":
                            sum += float(movieData['ImdbRating'])

                    yValues.append(float(sum / len(movies)))
                    if yValues[-1] < yMin:
                        yMin = yValues[-1]
            else: # Best
                for genre, movies in self.dataBase.genreMovies.items():
                    bestRating = 0.0
                    for movie, movieData in movies.items():
                        if not movieData['ImdbRating'] == "" and float(movieData['ImdbRating']) > bestRating:
                            bestRating = float(movieData['ImdbRating'])

                    yValues.append(bestRating)
                    if yValues[-1] < yMin:
                        yMin = yValues[-1]
        else: # show for one genre within years
            xValues = self.dataBase.years[:]
            movies = self.dataBase.genreMovies[genre]
            if showRatingType == "Avarage":
                yearRating = {} # (0,1)  0 - rating sum, 1 - rating counter
                for year in self.dataBase.years:
                    yearRating[year] = [0.0,0]

                for movieName, movieData in self.dataBase.moviesDict.items():
                    if not movieData['ImdbRating'] == "":
                        yearRating[movieData['Year']][0] += float(movieData['ImdbRating'])
                        yearRating[movieData['Year']][1] += 1

                for year in self.dataBase.years:
                    yValues.append(float(yearRating[year][0]/yearRating[year][1]))
                    if yValues[-1] < yMin:
                        yMin = yValues[-1]



            else: # Best



                x=0

        self.drawGraph(xValues, yValues, yMin)



    def drawGraph(self, xlist, ylist, yMin, width=0.5, color='r'):
        if yMin - 1 > 0:
            yMin = yMin - 1

        self.subplot.clear()
        self.xList = self.dataBase.genresList[:]
        self.yList = ylist[:]
        self.subplot.cla()
        self.subplot.bar(self.xList, self.yList, .5)

        self.subplot.set_ylim(ymin=yMin)

        for tick in self.subplot.get_xticklabels():
            tick.set_rotation(-45)

        self.canvas.draw()



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

        self.radioBAvarageR = Radiobutton(self, text="Avarage ratings", variable=self.showRatingType, value='Avarage')
        self.radioBAvarageR.grid(row=2, column=0, sticky=W)
        self.radioBBestR = Radiobutton(self, text="Best ratings", variable=self.showRatingType, value='Best')
        self.radioBBestR.grid(row=3, column=0, pady=10, sticky=W)

        self.showGraph_btn = Button(self, text="Show graph", command=window.showGraphRating)
        self.showGraph_btn.grid(columnspan=2, pady=10)


class MetascoreFrame(Frame):
    def __init__(self, window):
        Frame.__init__(self, window.root)

        label = Label(self, text="MetascoreFrame")
        label.pack()


class GrossFrame(Frame):
    def __init__(self, window):
        Frame.__init__(self, window.root)

        label = Label(self, text="GrossFrame")
        label.pack()

