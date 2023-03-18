from spider import Spider
import numpy as np
from tqdm import tqdm
import pandas as pd
from csv import writer
from sklearn.preprocessing import MinMaxScaler

class AISpider(Spider):
    def __init__(self, 
            data='',
            r_step=100, 
            f_split=0.7, 
            t_split=0.9):
        super().__init__(data)
        self.s_data = self.rolling_split(r_step)
        self.features, self.labels = self.create_features_labels(f_split)
        self.f_train, self.f_test = self.test_split(self.features, t_split)
        self.l_train, self.l_test = self.test_split(self.labels, t_split)

    def rolling_split(self, steps):
        """
        Rolling split of dataset into features

        Arguments:
        steps - Number of datapoints in each split

        Returns: Numpy Array
        """
        features = []
        
        scaler = MinMaxScaler(feature_range = (0, 1))
        
        for col in tqdm(self.data.columns):
            c = self.data[col]
            c = c.loc[c!=0.0]
            c = c.loc[c.notna()]
            for w in c.rolling(steps):
                if len(w.values) == steps:
                    features.append(w.values)
        features = np.dstack(features)[0]
        features = scaler.fit_transform(features)
        features = features.transpose()
        return features

    def create_features_labels(self, split):
        """
        Creates arrays of features and labels

        Takes rolling split of data and creates feature
        and label for each split. Labels are created from
        rise/fall over portion of data after split

        Arguments:
        split -- feature/label split. Float from 0 to 1

        Return: features (np array), labels (np array)
        """

        if split < 0 or split > 1:
            raise ValueError('split must be between 0 and 1')
        
        s = int(self.s_data.shape[1] * split)
        features = self.s_data[:, :s]
        features = np.reshape(features,
                (features.shape[0], features.shape[1], 1))
        labels = self.s_data[:, s:][:, -1] - self.s_data[:, s:][:, 0]
        return features, labels
    
    def test_split(self, data, split):
        """Split data into two arrays, for training and testing"""
        if split < 0 or split > 1:
            raise ValueError('split must be between 0 and 1')
        
        s_index = int(len(data) * split)
        train = data[:s_index]
        test = data[s_index:]
        return train, test

