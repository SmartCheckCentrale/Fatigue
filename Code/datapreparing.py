# -*- coding: utf-8 -*-
"""
Created on Fri May  5 20:23:05 2017

@author: Houssam
"""

import json
import os
import numpy as np

from sklearn.decomposition import KernelPCA,PCA,SparsePCA
from sklearn.preprocessing import StandardScaler


class DataPreparing:
    
    """Prepares the data for analyzing it

    Attributes : 
        initial_path (str): the path for opening the file
        position_model (list): is the model in order to find position
        position (list): result of the get_position method
        plus d'énergie, je dois aller faire ma valise ... 

    """

    def __init__(self,initial_path,diseases_selected):
        self.initial_path = initial_path
        self.position_model = ['DoubleStance','SwingMeanStrideDuration',
                               'AvgSpeed','RoliTronc','CycleVariability',
                               'MeanStepDuration']
        self.position = self.get_position()
        self.list_samples = os.listdir(self.initial_path)
        self.diseases_selected = diseases_selected
    
    def get_position(self):
        
        position = []
        try:
            sample = open(self.initial_path +'/ArtG-1aa0221-1-feat.json')
        except IOError:
            raise
        sample_dict = json.load(sample)
        # Keys list for features in the dictionnary
        keys_list = list(sample_dict.keys())

        for label in self.position_model:
            k = 0 
            while (k < len(keys_list)) and label != keys_list[k]:
                k += 1
            position.append(k)  
        return position

        #on a désormais la position des 6 features choisis
    
    def prepare(self):
        
        data = []

        c1=0
        c2=0
        c3=0
        c4=0
        
        for sample_name in self.list_samples:
            path = self.initial_path+'/' + sample_name
            sample = open(path)

            sample_dict = json.load(sample)
            sample_values, local_list = list(sample_dict.values()),[]

            for position in self.position:
                local_list.append(sample_values[position])
            
            if sample_name.startswith(self.diseases_selected[0]): #first disease
                data.append(local_list)
                c1 += 1

            if sample_name.startswith(self.diseases_selected[1]): #second disease
                data.append(local_list)
                c2 += 1

            if sample_name.startswith(self.diseases_selected[2]): #third disease
                data.append(local_list)
                c3 += 1

            if sample_name.startswith(self.diseases_selected[3]): #fourth disease
                data.append(local_list)
                c4 += 1
            
        c = [c1,c2,c3,c4]
        
        tab = np.asarray(data)
        tab_std = StandardScaler().fit_transform(tab)
        
        return tab_std,c

    def X_plot_method(self, tab_std,mode):

        if mode == 'acp':
            pca = PCA()
        if mode == 'kernel':
            pca = KernelPCA()
        if mode == 'sparse':
            pca = SparsePCA()

        X_a = pca.fit_transform(tab_std)
        return X_a


    def data_plot_preparation(self,tab_std,c):
        
        c1=c[0]
        c2=c[1]
        c3=c[2]
        c4=c[3]

        X1=[]
        Y1=[]
        X2=[]
        Y2=[]     
        X3=[]
        Y3=[]
        X4=[]
        Y4=[]
        
        C=c1
        for i in range(C):
            X1.append(tab_std[i,0])
            Y1.append(tab_std[i,1])
        for i in range(C,C+c2):  
            X2.append(tab_std[i,0])
            Y2.append(tab_std[i,1])
        C+=c2
        for i in range(C,C+c3):
            X3.append(tab_std[i,0])
            Y3.append(tab_std[i,1])
        C+=c3
        for i in range(C,C+c4):
            X4.append(tab_std[i,0])
            Y4.append(tab_std[i,1])

        print('coucou')

        return X1,Y1,X2,Y2,X3,Y3,X4,Y4
