import random
import numpy as np
import bisect
from time import perf_counter
from sklearn.decomposition import PCA

class RegionSplitter():

    def __init__(self, data, label):

        t0 = perf_counter()
        comp_count = 0
        self.cut_dim = 0
        self.cut_val = 0

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        num_candidates = 5
        zoom_range = 1
        max_zoom_num = 4

        data_num = len(data)
        # if too few data (need enough so that the subgroups can still not be under-fit)
        if data_num < data_dim_num*2:
            self.__split_quality = -float('inf')
            return

        # if just enough data, it can only cut in the middle
        elif data_num == data_dim_num*2:
            cut_idx_arr_0 = (data_dim_num,)
        elif data_num < num_candidates:
            cut_idx_arr_0 = tuple(range(data_dim_num, data_num-data_dim_num))
        else:
            cut_idx_arr_0 = sorted(tuple(set(np.linspace(data_dim_num, data_num-data_dim_num-1, num_candidates).astype(int))))

        # transform the label using PCA
        label_tf = PCA().fit_transform(np.array(label))

        sample = list(zip(data, label_tf))

        # storage while calculating the best
        best_score = -float("inf")
        # [group_size_diff, var_reduction, cut_dim, cut_val]
        best_cut_arr = [(-float("inf"), self.cut_dim, self.cut_val, 0)]

        # calculate the norm of the overall variance
        overall_var = np.linalg.norm(np.var(label_tf, axis=0, ddof=1))

        # if all are the same, split quality is -inf (shouldn't be split at all)
        if overall_var <= 0:
            self.__split_quality = -float('inf')

        else:

            # sort in each dimension
            for i in range(data_dim_num):

                # sort the data in dimension i
                sorted_samples = sorted(sample, key=lambda x: x[0][i])
                # separate the data back into data and label again
                sorted_dim_data = [sample[0][i] for sample in sorted_samples]
                sorted_label = [sample[1] for sample in sorted_samples]

                # start with the evenly spaced cut_idx_arr
                cut_idx_arr = cut_idx_arr_0
                zoom_num = 0

                while len(cut_idx_arr) >= 1 and zoom_num < max_zoom_num:

                    # storage while calculating the best
                    dim_best_score = -float("inf")
                    # [group_size_diff, var_reduction, cut_dim, cut_val]
                    dim_best_cut_arr = [(-float("inf"), i, self.cut_val, 0)]

                    for k in range(len(cut_idx_arr)):
                        cut_idx = cut_idx_arr[k]
                        cut_val = sorted_dim_data[cut_idx]

                        # split into groups
                        groups = [sorted_label[:cut_idx], sorted_label[cut_idx:]]

                        # check if any of the group is too small
                        if len(groups[0]) < data_dim_num or len(groups[1]) < data_dim_num:
                            continue

                        score, quality = RegionSplitter.calc_split_score(groups, overall_var=overall_var)
                        comp_count += 1

                        if score > dim_best_score:

                            dim_best_score = score
                            dim_best_cut_arr = [(quality, i, cut_val, k),]

                        elif score == dim_best_score:
                            dim_best_cut_arr.append((quality, i, cut_val, k))

                        else:
                            pass

                    # sorting the best cut array with best quality at the front
                    dim_best_cut_arr = sorted(dim_best_cut_arr, key=lambda x: x[0], reverse=True)
                    dim_best_k = dim_best_cut_arr[0][3]

                    # get out when there's only one to consider
                    if len(cut_idx_arr) <= zoom_range*2 + 1:
                        break
                    else:
                        # zoom in to the neighbouring area
                        low_cut_idx = cut_idx_arr[max(0, dim_best_k - zoom_range)]
                        high_cut_idx = cut_idx_arr[min(len(cut_idx_arr) - 1, dim_best_k + zoom_range)]

                        cut_idx_arr = sorted(tuple(set(np.linspace(low_cut_idx, high_cut_idx, num_candidates).astype(int))))
                        zoom_num += 1

                # check how this dimension stacks up against others
                if dim_best_score > best_score:
                    best_score = dim_best_score
                    best_cut_arr = dim_best_cut_arr

                elif dim_best_score == best_score:
                    dim_best_cut_arr.append(dim_best_cut_arr)

                else:
                    pass

            # sorting the best cut array with best quality at the front
            best_cut_arr = sorted(best_cut_arr, key=lambda x: x[0], reverse=True)

            # the best cut_dim is the one with the highest quality
            self.cut_dim = best_cut_arr[0][1]
            self.cut_val = best_cut_arr[0][2]

            # the best split quality
            self.__split_quality = best_cut_arr[0][0]
        #print(self.__split_quality, ', ')
        split_clock = perf_counter() - t0
        #if split_clock > 1:
        print(split_clock, ', ', comp_count, ', ', self.cut_dim, ', ', self.cut_val)
        # just cut in half
        # self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    @property
    def split_quality(self):
        return self.__split_quality

    def classify(self, data):

        if self.split_quality == -float('inf'):
            raise ValueError("Split Quality should not be -inf!")

        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = data[self.cut_dim] <= self.cut_val

        return group == 0

    @staticmethod
    def calc_split_score(groups, overall_var=None):
        if not len(groups) == 2:
            raise ValueError("There can only be two groups")

        # calculate overall variance if not provided
        if overall_var == None:
            overall_var = np.linalg.norm(np.var(groups[0] + groups[1], axis=0, ddof=1))

        variances = []
        weights = []
        for group in groups:
            # calculate the in-group variance
            variances.append(np.linalg.norm(np.var(group, axis=0, ddof=1)))
            weights.append(len(group))
        # take the mean variance
        avg_var = np.average(variances, weights=weights)

        # negate the variance and plus 1
        # (we want low relative variance worst should be 1)
        score = -avg_var

        # split quality is relative variance to the original
        quality = 1 - avg_var/overall_var

        return score, quality
