import random
import numpy as np
import math

from sklearn.cluster import KMeans
from sklearn.cluster import Ward
#from sklearn.decomposition import PCA
from sklearn.decomposition import KernelPCA as PCA
from sklearn.decomposition import FastICA as ICA
from sklearn.neighbors import KNeighborsClassifier as knn
from sklearn.svm import SVC
from sklearn.svm import SVR
from sklearn.cross_validation import KFold
from sklearn import metrics
from sklearn import linear_model
import matplotlib.pyplot as plt




class RegionSplitter_KMean():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        #set to cut dimension 1
        # self.cut_dim = 1
        # self.clusterer = KMeans(n_clusters=2, init='k-means++')
        # self.clusterer.fit(list(zip(data_zipped[self.cut_dim])))
        # return

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            # TODO: need proper clustering
            # k-mean cluster for the dimension
            clusterer = KMeans(n_clusters=2, init='k-means++')

            grouping = clusterer.fit_predict(list(zip(data_zipped[i])))

            groups = [[label[j] for j in range(len(data_zipped[i])) if grouping[j] == 0],
                      [label[j] for j in range(len(data_zipped[i])) if grouping[j] == 1]]

            weighted_avg_variance = []
            for group in groups:
                num_sample = len(group)
                group = zip(*group)

                variance = []
                for group_k in group:
                    mean = math.fsum(group_k)/len(group_k)
                    norm = math.fsum([x**2 for x in group_k])/len(group_k)
                    variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)

            in_group_variance = math.fsum(weighted_avg_variance)

            if dim_min > in_group_variance:

                dim_min = in_group_variance
                self.cut_dim = i
                self.clusterer = clusterer


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        data = [(data[self.cut_dim],)]
        group = self.clusterer.predict(data)

        return group == 0
        # data[self.cut_dim] > self.cut_val


class RegionSplitter_PCA_KMean():
    def __init__(self, data, label):

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        self.n_comp = max(1, data_dim_num)

        self.pca = PCA(n_components=self.n_comp)

        data = self.pca.fit_transform(data)
        data_zipped = list(zip(*data))

        # k-mean cluster for the dimension
        self.clusterer = KMeans(n_clusters=2, init='k-means++')

        self.clusterer.fit(list(zip(*data_zipped)))


    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        data = tuple(self.pca.transform(data)[0])
        group = self.clusterer.predict(data)

        return group == 0


class RegionSplitter_oudeyer():

    def __init__(self, data, label):

        self.cut_dim = 1
        self.cut_val = 0
        num_candidates = 50

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.choice(np.linspace(min_val, max_val, num=100))

                groups = [[label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0
                if len(groups[0]) == 0 or len(groups[1]) == 0:
                    continue

                weighted_avg_variance = []
                for group in groups:
                    num_sample = len(group)
                    group = zip(*group)

                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)

                in_group_variance = math.fsum(weighted_avg_variance)

                if in_group_variance < dim_min:

                    dim_min = in_group_variance
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = data[self.cut_dim] <= self.cut_val

        return group == 0

class RegionSplitter_PCA_oudeyer():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0
        num_candidates = 50

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        self.n_comp = max(1, data_dim_num)

        self.pca = PCA(n_components=self.n_comp, kernel='linear')
        # self.ica = ICA(n_components=self.n_comp)

        data = self.pca.fit_transform(data)
        #data = self.ica.fit_transform(data)

        data_zipped = list(zip(*data))

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])


        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.choice(np.linspace(min_val, max_val, num=500))

                groups = [[label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0
                if len(groups[0]) == 0 or len(groups[1]) == 0:
                    continue

                weighted_avg_variance = []
                for group in groups:
                    num_sample = len(group)
                    group = zip(*group)

                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)

                in_group_variance = math.fsum(weighted_avg_variance)

                if in_group_variance < dim_min:

                    dim_min = in_group_variance
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        data = tuple(self.pca.transform(data)[0])
        # data = tuple(self.ica.transform(data)[0])
        group = data[self.cut_dim] <= self.cut_val

        return group == 0


class RegionSplitter_oudeyer_modified():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0
        num_candidates = 100
        min_group_size = 20

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        # model used to evaluate the data
        model = linear_model.LinearRegression()

        # the error of whole partition
        n_fold = 2
        kf = KFold(len(data), n_folds=n_fold)
        rms_error_whole = 0
        for train_index, test_index in kf:
            data_train, data_test = np.array(data)[train_index], np.array(data)[test_index]
            label_train, label_test = np.array(label)[train_index], np.array(label)[test_index]

            model = linear_model.LinearRegression()
            model.fit(data_train, label_train)
            label_predict = model.predict(data_test)

            rms_error_whole += metrics.mean_squared_error(label_test, label_predict)

        rms_error_whole /= n_fold

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.uniform(min_val, max_val)

                groups = [[[data[j], label[j]] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [[data[j], label[j]] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0 or 1

                if len(groups[0]) < min_group_size or len(groups[1]) < min_group_size:
                    continue

                avg_error = []
                weighted_avg_variance = []


                for group in groups:

                    # calculate error with a linear model
                    data_k = list(zip(*group))[0]
                    label_k = list(zip(*group))[1]

                    # the split groups error
                    n_fold = 2
                    kf = KFold(len(data_k), n_folds=n_fold)
                    rms_error_split = 0
                    for train_index, test_index in kf:
                        data_train, data_test = np.array(data_k)[train_index], np.array(data_k)[test_index]
                        label_train, label_test = np.array(label_k)[train_index], np.array(label_k)[test_index]

                        model.fit(data_train, label_train)
                        label_predict = model.predict(data_test)

                        rms_error_split += metrics.mean_squared_error(label_test, label_predict)

                    rms_error_split /= n_fold

                    avg_error.append(rms_error_split)

                    num_sample = len(group)
                    group = zip(*group[0])

                    # calculate variance of data points
                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)



                error_diff = (avg_error[0] - avg_error[1])**2
                smallest_error = min(avg_error)
                try:
                    biggest_error_reduction = max(rms_error_whole - avg_error[0]/rms_error_whole, rms_error_whole-avg_error[1]/rms_error_whole)
                except ZeroDivisionError:
                    biggest_error_reduction = -float("inf")
                in_group_variance = math.fsum(weighted_avg_variance)
                #print('cut_dim=%d cut_val=%f avg_err=%f var=%f'%(i, cut_val, smallest_error, in_group_variance))

                try:
                    score = in_group_variance / (error_diff*biggest_error_reduction)
                except ZeroDivisionError:
                    score = float("inf")

                if score < dim_min:

                    dim_min = score
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = data[self.cut_dim] <= self.cut_val

        return group == 0

class RegionSplitter_PCA_oudeyer_modified():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0
        num_candidates = 500
        min_group_size = 20

        data_dim_num = len(data[0])

        self.n_comp =  max(1, data_dim_num)

        self.pca = PCA(n_components=self.n_comp, kernel='linear')
        #self.pca = ICA(n_components=self.n_comp)

        data = self.pca.fit_transform(data)

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        # model used to evaluate the data
        model = linear_model.LinearRegression()

        # the error of whole partition
        n_fold = 2
        kf = KFold(len(data), n_folds=n_fold)
        rms_error_whole = 0
        for train_index, test_index in kf:
            data_train, data_test = np.array(data)[train_index], np.array(data)[test_index]
            label_train, label_test = np.array(label)[train_index], np.array(label)[test_index]

            model = linear_model.LinearRegression()
            model.fit(data_train, label_train)
            label_predict = model.predict(data_test)

            rms_error_whole += metrics.mean_squared_error(label_test, label_predict)

        rms_error_whole /= n_fold

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.uniform(min_val, max_val)

                groups = [[[data[j], label[j]] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [[data[j], label[j]] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0 or 1

                if len(groups[0]) < min_group_size or len(groups[1]) < min_group_size:
                    continue

                avg_error = []
                weighted_avg_variance = []


                for group in groups:

                    # calculate error with a linear model
                    data_k = list(zip(*group))[0]
                    label_k = list(zip(*group))[1]

                    # the split groups error
                    n_fold = 2
                    kf = KFold(len(data_k), n_folds=n_fold)
                    rms_error_split = 0
                    for train_index, test_index in kf:
                        data_train, data_test = np.array(data_k)[train_index], np.array(data_k)[test_index]
                        label_train, label_test = np.array(label_k)[train_index], np.array(label_k)[test_index]

                        model.fit(data_train, label_train)
                        label_predict = model.predict(data_test)

                        rms_error_split += metrics.mean_squared_error(label_test, label_predict)

                    rms_error_split /= n_fold

                    avg_error.append(rms_error_split)

                    num_sample = len(group)
                    group = zip(*group[0])

                    # calculate variance of data points
                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)



                error_diff = (avg_error[0] - avg_error[1])**2
                smallest_error = min(avg_error)
                biggest_error_reduction = max(rms_error_whole - avg_error[0], rms_error_whole-avg_error[1])
                in_group_variance = math.fsum(weighted_avg_variance)
                #print('cut_dim=%d cut_val=%f avg_err=%f var=%f'%(i, cut_val, smallest_error, in_group_variance))

                try:
                    score = ((in_group_variance+1)*(smallest_error+1)) / (error_diff*(biggest_error_reduction**0.5))
                except ZeroDivisionError:
                    score = float("inf")

                if score < dim_min:

                    dim_min = score
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        data = tuple(self.pca.transform(data)[0])
        group = data[self.cut_dim] <= self.cut_val

        return group == 0

class RegionSplitter():

    def __init__(self, data, label):


        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_label = zip(*(list(zip(*data)) + list(zip(*label))))

        # cluster data with labels
        clusterer = KMeans(n_clusters=2, init='k-means++')
        grouping = clusterer.fit_predict(list(data_label))
        self.classifier = SVC()
        self.classifier.fit(data, grouping)


    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = self.classifier.predict(data)

        return group==0