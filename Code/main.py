# -*- coding: utf-8 -*-
"""
Created on Tue May  2 02:23:37 2017

@author: Houssam
"""

import sys
import matplotlib.pyplot as plt

from PyQt5 import uic
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


from datapreparing import DataPreparing
 

import random

initial_path='Features'

 
class App(QWidget):

    """Launches the main window, and is the main user interface.

    It has a 3 QPushButton, that are herited from uic.loadUI 
    which calls 'GUI/mainwindow.ui'. Open the previous file in Qt
    Creator to see all the widgets. It also creates plots from itself, 
    that are supposed to be placed with move method.(FigureCanvas object).
    This class calls Plot class in order to plot the charts.

    """

    def __init__(self):

        QWidget.__init__(self)
        self.UI = uic.loadUi('GUI/mainwindow_.ui', self,
                             package='GUI')
        self.list_diseases = ['ArtG','ArtH','AVC','CER','Genou','LCA','LEC','LER','NC','NEUP','PAR','T-']
        self.diseases_selected = []
        #self.completed = False
        self.initUI()

 
    def initUI(self): 
        
        #----------------------
        # Working on ACP button
        #----------------------

        acp = Plot(self, width=5, height=4, mode='acp') # Creating the plot object for acp
        acp.move(1200,0)
        
        # Heriting ACP_Button from the mainwindow.ui file, see Qt Creator
        ACP_Button = self.UI.ACP_Button 
        # Information when clicking on the button  
        ACP_Button.setToolTip('Effectuer une analyse en composantes principales') 
        # Signal/Slot, connecting the click to the function that will display the chart
        ACP_Button.clicked.connect(lambda : App.on_click(self,acp)) 

        #----------------------
        # Working on Kernel button
        #---------------------- 
        
        kernel = Plot(self, width=5, height=4, mode='kernel') # Creating the plot object for kernel
        kernel.move(1200,0)
        
        # Heriting AKERNEL_Button from the mainwindow.ui file, see Qt Creator
        AKERNEL_Button = self.UI.AKERNEL_Button
        # Information when clicking on the button 
        AKERNEL_Button.setToolTip('Effectuer une analyse en composantes principales à noyaux')
        # Signal/Slot, connecting the click to the function that will display the chart
        AKERNEL_Button.clicked.connect(lambda : App.on_click(self,kernel))

        #----------------------
        # Working on Sparse button
        #---------------------- 
        
        sparse = Plot(self, width=5, height=4, mode='sparse')
        sparse.move(1200,0)
        
        # Heriting ASPARSE_Button from the mainwindow.ui file, see Qt Creator
        ASPARSE_Button = self.UI.ASPARSE_Button
        # Information when clicking on the button
        ASPARSE_Button.setToolTip('Effectuer une analyse en composantes principales sparse')
        # Signal/Slot, connecting the click to the function that will display the chart
        ASPARSE_Button.clicked.connect(lambda : App.on_click(self,sparse))

        # See the mainwindow.ui file on QT creator
        # Adding possible disease to the possible choices of the user
        self.UI.Disease_1.addItems(['Faire un choix'] + self.list_diseases + ['None'])
        self.UI.Disease_2.addItems(['Faire un choix'] + self.list_diseases + ['None'])
        self.UI.Disease_3.addItems(['Faire un choix'] + self.list_diseases + ['None'])
        self.UI.Disease_4.addItems(['Faire un choix'] + self.list_diseases + ['None'])

        # Connecting the choices of the user with the slot function

        self.UI.Disease_1.activated[str].connect(self.disease_activated)
        self.UI.Disease_2.activated[str].connect(self.disease_activated)
        self.UI.Disease_3.activated[str].connect(self.disease_activated)
        self.UI.Disease_4.activated[str].connect(self.disease_activated)
        
        self.showMaximized() # Maximazing the size of the window
        self.show() # Showing the window

    def disease_activated(self,text):
        if text != 'None' and text != 'Faire un choix':
            self.diseases_selected += [text]
        if len(self.diseases_selected) == 4:
            self.completed = True
    
    def on_click(self,m):
        m.plot()
        #m.plot_test() #if you want to test with the random file.

class Plot(FigureCanvas):

    """FigureCanvas object, see https://matplotlib.org/users/artists.html

    It has a 3 QPushButton, that are herited from uic.loadUI 
    which calls 'GUI/mainwindow.ui'. Open the previous file in Qt
    Creator to see all the widgets. It also creates plots from itself, 
    that are supposed to be placed with move method.(FigureCanvas object).
    This class calls Plot class in order to plot the charts.

    """
 
    def __init__(self, parent=None, width=5, height=4, dpi=100, mode='pca'):
        """ Pris sur internet : https://pythonspot.com/en/pyqt5-matplotlib/

        """
        self.visu = False
        self.fig = plt.figure()
        self.matplotlibWidget = MatplotlibWidget(self.fig)
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
 
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.mode = mode  # Je l'ai rajouté
 
    
    def plot_test(self):
        """ Taken from the internet

        """
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()
     
    def plot(self) : 
        """ Plotting the charts
        
        - To plot the charts, you have to select the diseases, 
        for example AVC, PAR, Témoin,etc...
        - Then you have to prepare the data, that is to say, 
        only selecting patients who have those diseases,
        and only sorting the data, and preparing it for the 
        method you want to use when visualizing the dataset.
        - DataPreparing.prepare() returns a list c with the 
        occurences of each diseases. You can select at most 
        4 diseases. 
        - The mode is fixed when you press on one of the QPushButtons
        above. Therefore self.mode is known. X_plot_method applies 
        the method.
        - Then, data_plot_preparation gives the "ordonnées" and 
        "absisses" (je sais pas comment on dit en anglais et il est
        2h du mat je suis KO) for every disease to be displayed.

        """

        diseases_selected = ex.diseases_selected
        process = DataPreparing(initial_path,diseases_selected)
        tab_std,c = DataPreparing.prepare(process)
        X_a = DataPreparing.X_plot_method(process,tab_std,self.mode)
        X1,Y1,X2,Y2,X3,Y3,X4,Y4 = DataPreparing.data_plot_preparation(process,X_a,c)

        #ax = self.figure.add_subplot(111) # Adds the plot to the place you tell when using move (voir plus haut).

        self.fig.clf()
        self.subplot = self.fig.add_subplot(111)
        
        self.subplot.plot(X1, Y1, "ro", color='red', picker=4.0)
        self.subplot.plot(X2, Y2, "ro", color='blue', picker=4.0)
        self.subplot.plot(X3, Y3, "ro", color='green', picker=4.0)
        self.subplot.plot(X4, Y4, "ro", color='yellow', picker=4.0)
        self.subplot.legend()
        self.matplotlibWidget.draw()
        self.show()



        print(X1,Y1)
        """
        ax.plot(X1,Y1,cmap=plt.cm.Paired,c='orange')   # Je suis pas sûr que scatter soit la bonne fonction
        ax.plot(X2,Y2,cmap=plt.cm.Paired,c='red')  # à utiliser, à voir
        ax.plot(X3,Y3,cmap=plt.cm.Paired,c='green')
        ax.plot(X4,Y4,cmap=plt.cm.Paired,c='blue')
        ax.set_title('Analysis - ' + self.mode) # sets the title
        self.draw # draws the plot.
        print('coucou2')
        """
    

class MatplotlibWidget(FigureCanvas):
    """
    Initialisation du matplotlib pour le plot
    """
    def __init__(self, fig):
        super(MatplotlibWidget, self).__init__(fig)

   
# Launching the general application

if __name__ == '__main__':
    app=0
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()

