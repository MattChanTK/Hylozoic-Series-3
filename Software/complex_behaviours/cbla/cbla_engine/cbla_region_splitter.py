import random
import numpy as np
import math
import bisect
import statistics as stat
from time import perf_counter
from multiprocessing import Process, Queue, queues

class RegionSplitter():

    def __init__(self, data, label):

        t0 = perf_counter()
        self.cut_dim = 0
        self.cut_val = 0

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        num_candidates = data_dim_num*10

        sample = list(zip(data, label))

        # storage while calculating the best
        best_score = -float("inf")
        # [group_size_diff, var_reduction, cut_dim, cut_val]
        best_cut_arr = [(-float("inf"), self.cut_dim, self.cut_val)]

        # calculate the minimum of the overall variance
        #TODO figure out the best way to compare  multi-D variance
        overall_var = min(np.var(label, axis=0, ddof=1))

        # if all are the same, split quality is -inf (shouldn't be split at all)
        if overall_var <= 0:
            self.__split_quality = -float('inf')

        else:

            # sort in each dimension
            dim_best_q = Queue()
            dim_best_scores = [None] * data_dim_num
            dim_best_cut_arrs = [None] * data_dim_num
            find_best_cut_processes = []
            t_proc = perf_counter()
            for i in range(data_dim_num):

                p = Process(target=self.find_best_cut, args=(sample, i, overall_var, num_candidates, dim_best_q))
                p.start()
                find_best_cut_processes.append(p)
            print("process time: ", perf_counter() - t_proc)
            for p in find_best_cut_processes:
                p.join()
            # print("process time: ", perf_counter() - t_proc)

            while not dim_best_q.empty():
                try:
                    dim_best_score, dim_best_cut_arr = dim_best_q.get_nowait()
                except queues.Empty:
                    break
                else:
                    dim_id = dim_best_cut_arr[0][1]
                    dim_best_scores[dim_id] = dim_best_score
                    dim_best_cut_arrs[dim_id] = dim_best_cut_arr

            # check if any of the dimensions are not populated
            for i in range(data_dim_num):
                if not dim_best_scores[i]:
                    raise ValueError("The best score for dimension %d is missing!" % i)
                if not dim_best_cut_arrs[i]:
                    raise ValueError("The best cut array for dimension %d is missing!" % i)

            # find the dimension with the best score
            for i in range(data_dim_num):
                # if the best score for the dimension is better than the best score
                if dim_best_scores[i] > best_score:
                    # save the best cut array
                    best_cut_arr = dim_best_cut_arrs[i]
                    best_score = dim_best_scores[i]
                # if the best score equals to the dimension's best
                elif dim_best_scores[i] == best_score:
                    # concatenate
                    best_cut_arr += dim_best_cut_arrs[i]

            # sorting the best cut array with smallest group_size_diff at the front
            best_cut_arr = sorted(best_cut_arr, key=lambda x: x[0])

            # the best cut_dim is the one with the smallest group_size_diff
            self.cut_dim = best_cut_arr[0][1]
            self.cut_val = best_cut_arr[0][2]

            # the best split quality
            self.__split_quality = best_cut_arr[0][0]
        #print(self.__split_quality, ', ')
        split_clock = perf_counter() - t0
        if split_clock > 1:
            print("total split time: ", split_clock)
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

    @classmethod
    def find_best_cut(cls, sample, cut_dim_i, overall_var, num_candidates=10, result_q=None):

        # number of dimension in the data
        data_dim_num = len(sample[0][0])

        # default cut val
        cut_val = 0

        # storage while calculating the best score for this dimension
        best_score = -float("inf")
        # [best score, quality, cut_dim, cut_val]
        best_cut_arr = [(-float("inf"), cut_dim_i, cut_val)]

        # sort the data in dimension i
        t_sort = perf_counter()
        sorted_samples = sorted(sample, key=lambda x: x[0][cut_dim_i])
        print("sort time: ", perf_counter() - t_sort)

        # separate the data back into data and label again
        sorted_dim_data = [sample[0][cut_dim_i] for sample in sorted_samples]
        sorted_label = [sample[1] for sample in sorted_samples]

        t_cutting = perf_counter()

        for k in range(num_candidates):
            # pick a random value
            max_val = sorted_dim_data[-1]
            min_val = sorted_dim_data[0]
            cut_val = random.choice(np.linspace(min_val, max_val, num=100))

            # calculate the cut index
            cut_idx = bisect.bisect_left(sorted_dim_data, cut_val)
            groups = [sorted_label[:cut_idx], sorted_label[cut_idx:]]

            # check if any of the group is too small
            if len(groups[0]) < data_dim_num or len(groups[1]) < data_dim_num:
                continue

            variances = []
            for group in groups:
                # calculate the in-group variance
                variances.append(min(np.var(group, axis=0, ddof=1)))
            # take the smallest variance
            avg_var = stat.mean(variances)

            # negate the variance and plus 1
            # (we want low relative variance worst should be 1)
            score = -avg_var

            # split quality is relative variance to the original
            quality = 1 - avg_var/overall_var

            if score > best_score:

                best_score = score
                best_cut_arr = [(quality, cut_dim_i, cut_val),]

            elif score == best_score:
                best_cut_arr.append((quality, cut_dim_i, cut_val))

            else:
                pass
        print("cutting time: ", perf_counter() - t_cutting)

        if isinstance(result_q, queues.Queue):
            result_q.put((best_score, best_cut_arr))
        else:
            return best_score, best_cut_arr




