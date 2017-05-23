# -*- coding: utf-8 -*-
"""
Created on Tue May  2 02:23:37 2017
@author: Houssam
"""

import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np


from PyQt5 import uic
from sklearn.cluster import KMeans
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QTextBrowser
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale


from datapreparing import DataPreparing
 

initial_path='Features'

 
class Visualisation(QWidget):

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
        self.diseases_selected = ['','','','']
        self.visualisation_mode = ''
        self.total_data = []
        self.X_a = []
        self.initUI()

 
    def initUI(self): 
        
        #----------------------
        # Working on ACP button
        #----------------------

        
        # Heriting ACP_Button from the mainwindow.ui file, see Qt Creator
        ACP_Button = self.UI.ACP_Button 
        # Information when clicking on the button  
        ACP_Button.setToolTip('Effectuer une analyse en composantes principales') 
        # Signal/Slot, connecting the click to the function that will display the chart
        ACP_Button.clicked.connect(lambda : Visualisation.on_click(self,'acp')) 

        #----------------------
        # Working on Kernel button
        #---------------------- 
        
        
        # Heriting AKERNEL_Button from the mainwindow.ui file, see Qt Creator
        AKERNEL_Button = self.UI.AKERNEL_Button
        # Information when clicking on the button 
        AKERNEL_Button.setToolTip('Effectuer une analyse en composantes principales à noyaux')
        # Signal/Slot, connecting the click to the function that will display the chart
        AKERNEL_Button.clicked.connect(lambda : Visualisation.on_click(self,'kernel'))

        #----------------------
        # Working on Sparse button
        #---------------------- 
        
        #sparse = Plot(self, width=5, height=4, mode='sparse')
        #sparse.move(1200,0)
        
        # Heriting ASPARSE_Button from the mainwindow.ui file, see Qt Creator
        ASPARSE_Button = self.UI.ASPARSE_Button
        # Information when clicking on the button
        ASPARSE_Button.setToolTip('Effectuer une analyse en composantes principales sparse')
        # Signal/Slot, connecting the click to the function that will display the chart
        ASPARSE_Button.clicked.connect(lambda : Visualisation.on_click(self,'sparse'))

        Clustering_Button = self.UI.Clustering_Button
        Clustering_Button.setToolTip('Effectuer un clustering K-Means')
        Clustering_Button.clicked.connect(self.clustering)

        reset_button = self.UI.reset_button
        reset_button.setToolTip('Réinitialiser le graphe')
        reset_button.clicked.connect(self.graph_reset)
        # See the mainwindow.ui file on QT creator
        # Adding possible disease to the possible choices of the user
        self.UI.Disease_1.addItems(['Faire un choix'] + self.list_diseases + ['None'])
        self.UI.Disease_2.addItems(['Faire un choix'] + self.list_diseases + ['None'])
        self.UI.Disease_3.addItems(['Faire un choix'] + self.list_diseases + ['None'])
        self.UI.Disease_4.addItems(['Faire un choix'] + self.list_diseases + ['None'])

        # Connecting the choices of the user with the slot function

        self.UI.Disease_1.activated[str].connect(self.disease_1_activated)
        self.UI.Disease_2.activated[str].connect(self.disease_2_activated)
        self.UI.Disease_3.activated[str].connect(self.disease_3_activated)
        self.UI.Disease_4.activated[str].connect(self.disease_4_activated)

        ######PARTIE A LANCIENNE#######

        # plot_data
        self.fig = plt.figure()

        # on crée le widget matplotlib
        self.matplotlibWidget = MatplotlibWidget(self.fig)

        # on l'ajoute au layout
        self.UI.verticalLayout_plot.addWidget(self.matplotlibWidget)

        # on ajoute la toolbar (pour zoomer par exemple)
        self.toolbar = NavigationToolbar(self.matplotlibWidget, self)
        self.UI.verticalLayout_plot.addWidget(self.toolbar)

        # échelle du plot
        self.xlim = []
        self.ylim = []

        # fiche pour un certain point
        self.text_point = QTextBrowser()
        self.UI.verticalLayout_plot.addWidget(self.text_point)

        #Signal/slot pour connecter points contactés

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)

        ####FIN PARTIE A LANCIENNE#####
        
        self.showMaximized() # Maximazing the size of the window
        self.show() # Showing the window

    def disease_1_activated(self,text):
        if text != 'None' and text != 'Faire un choix':
            self.diseases_selected[0] = text

    def disease_2_activated(self,text):
        if text != 'None' and text != 'Faire un choix':
            self.diseases_selected[1] = text

    def disease_3_activated(self,text):
        if text != 'None' and text != 'Faire un choix':
            self.diseases_selected[2] = text

    def disease_4_activated(self,text):
        if text != 'None' and text != 'Faire un choix':
            self.diseases_selected[3] = text
    
    def on_click(self,mode):
 
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

        self.visualisation_mode = mode

        process = DataPreparing(initial_path,self.diseases_selected)
        tab_std,c = DataPreparing.prepare(process)
        X_a = DataPreparing.X_plot_method(process,tab_std,mode)
        X1,Y1,X2,Y2,X3,Y3,X4,Y4 = DataPreparing.data_plot_preparation(process,X_a,c)
        self.X_a = X_a
        #ax = self.figure.add_subplot(111) # Adds the plot to the place you tell when using move (voir plus haut).
        self.total_data = [(X1,Y1),(X2,Y2),(X3,Y3),(X4,Y4)]

        self.fig.clf()
        self.subplot = self.fig.add_subplot(111)
        
        self.subplot.plot(X1, Y1, "ro", color='red', picker=4.0)
        self.subplot.plot(X2, Y2, "ro", color='blue', picker=4.0)
        self.subplot.plot(X3, Y3, "ro", color='green', picker=4.0)
        self.subplot.plot(X4, Y4, "ro", color='yellow', picker=4.0)
        self.subplot.legend()
        self.matplotlibWidget.draw()
        self.show()


    def on_pick(self, event):
        """
        S'active au clic sur un point
        """
        self.text_point.clear()

        # pour garder l'échelle courante
        self.xlim = self.subplot.get_xlim()
        self.ylim = self.subplot.get_ylim()

        thisPoint = event.artist
        xdata = thisPoint.get_xdata()
        ydata = thisPoint.get_ydata()
        ind = event.ind
        x, y = xdata[ind][0], ydata[ind][0]

        # on affiche la fiche associée au point
        self.fiche_patient(x, y)

    def fiche_patient(self, x, y):
        """
        Affiche les données du patient correspondant
        au point de coordonnées (x,y)
        """
        mode = self.visualisation_mode
        total_data = self.total_data

        list_exercice = os.listdir('Features')
        index = ""
        for i in range(len(total_data)):
            (X,Y) = total_data[i]
            for j in range(len(X)):
                if X[j] == x:
                    if Y[j] == y:
                        for k in range(len(list_exercice)):
                            exercice = list_exercice[k]
                            if exercice.startswith(self.diseases_selected[i]):
                                index = list_exercice[k+j]
                                break



        label = index[:-9]+"label.js"

        ### A voir ####

        dict_fiche = json.load(open("Labels/" + label))

        affiche = "Date de naissance:" + " " + str(dict_fiche["Date de naissance"][:2]) + "/" + str(dict_fiche["Date de naissance"][2:4]) + "/" + str(dict_fiche["Date de naissance"][4:]) + "\n"
        affiche += "Date de la mesure:" + " " + str(dict_fiche["Date de la mesure"][:2]) + "/" + str(dict_fiche["Date de la mesure"][2:4]) + "/" + str(dict_fiche["Date de la mesure"][4:]) + "\n"
        if str(dict_fiche["Sexe"]) == "Homme":
            affiche += "Sexe:" + " Homme" + "\n"
        else:
            affiche += "Sexe :" + " Femme" + "\n"
        affiche += "Taille :" + " " + str(dict_fiche["Taille"]) + " cm" + "\n"
        affiche += "Poids :" + " " + str(dict_fiche["Poids"]) + " kg" + "\n"

        try:
            affiche += "Atteinte :" + " "
            for item in dict_fiche["Atteinte"]:
                affiche += str(item) + " - "
            affiche = affiche[:-2] + "\n"
        except KeyError:
            affiche += " - " + "\n"

        self.text_point.append(affiche)

    def clustering(self):

        reduced_data = self.X_a
        kmeans = KMeans(init='k-means++', n_clusters=8, n_init=10)
        kmeans.fit(reduced_data)

        # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
        y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        # Obtain labels for each point in mesh. Use last trained model.
        Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

        # Put the result into a color plot
        Z = Z.reshape(xx.shape)

        self.fig.clf()
        self.fig.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

        self.fig.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
        # Plot the centroids as a white X
        centroids = kmeans.cluster_centers_
        self.fig.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
        self.fig.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
          'Centroids are marked with white cross')
        self.fig.xlim(x_min, x_max)
        self.fig.ylim(y_min, y_max)
        self.fig.xticks(())
        self.fig.yticks(())
        self.show()
        
    def graph_reset(self):

        self.fig.clf()
        self.matplotlibWidget.draw()
        self.show()

        
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
    ex = Visualisation()
    app.exec_()
