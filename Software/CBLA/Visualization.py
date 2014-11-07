__author__ = 'Matthew'
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pydot
import itertools



def moving_average(interval, window_size):
    interval = np.asarray(interval)
    interval = interval[:,0]
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def plot_evolution(action_history, fig_num=1, subplot_num=121):

    # plot configuration
    fig = plt.figure(fig_num)
    plot = fig.add_subplot(subplot_num)
    plot.plot(moving_average(action_history, 1), marker='o', ms=1.5, mew=0, lw=0)
    plt.ion()
    plt.show()
    plt.title("Action vs Time")
    plt.xlabel("Time Step")
    plt.ylabel("M(t)")

    return plot

def plot_model(Expert, region_ids, plot=None, x_idx=1, y_idx=0, fig_num=1, subplot_num=122):

    # plot configuration
    if plot is None:
        fig = plt.figure(fig_num)
        plot = fig.add_subplot(subplot_num)
        plt.ion()
        plt.show()
        plt.hold(True)
        plt.title("Prediction Models")
        plt.xlabel("SM(t) [" + str(x_idx) + "]")
        plt.ylabel("S(t+1)")

    # this is leaf node
    if Expert.left is None and Expert.right is None:

        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))

        # plot the exemplars in the training set
        training_data = list(zip(*Expert.training_data))
        training_label = list(zip(*Expert.training_label))
        X = training_data[x_idx]
        Y = training_label[y_idx]
        plot.plot(X, Y, marker='o', ms=2, mew=0, lw=0, color=colours[region_ids.index(Expert.expert_id)])

        # plot the model
        num_sample = 100
        pts = [[0]*num_sample]*len(Expert.training_data[0])
        max_val = round(max(training_data[x_idx]))
        min_val = round(min(training_data[x_idx]))
        try:
            pts[x_idx] = list(np.linspace(min_val, max_val, 100))
        except ZeroDivisionError:
            pts[x_idx] = [min_val]

        #pts = list(itertools.product(*pts))
        pts = list(zip(*pts))

        try:
            plot.plot(list(zip(*pts))[x_idx], list(list(zip(*Expert.predict_model.predict(pts)))[0]),'-', color='k', linewidth=1)
        except ValueError:
            pass

    else:
        plot_model(Expert.left, region_ids, plot, x_idx, y_idx, fig_num, subplot_num)
        plot_model(Expert.right, region_ids, plot, x_idx, y_idx, fig_num, subplot_num)

def plot_model_3D(Expert, region_ids, plot=None, x_idx=1, y_idx=0, fig_num=1, subplot_num=122):

    # plot configuration
    if plot is None:
        fig = plt.figure(fig_num)
       # ax = fig.add_su
        plot = fig.add_subplot(subplot_num)
        plt.ion()
        plt.show()
        plt.hold(True)
        plt.title("Prediction Models")
        plt.xlabel("SM(t) [" + str(x_idx) + "]")
        plt.ylabel("S(t+1)")

    # this is leaf node
    if Expert.left is None and Expert.right is None:

        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))

        # plot the exemplars in the training set
        training_data = list(zip(*Expert.training_data))
        training_label = list(zip(*Expert.training_label))
        X = training_data[x_idx]
        Y = training_label[y_idx]
        plot.plot(X, Y, marker='o', ms=2, mew=0, lw=0, color=colours[region_ids.index(Expert.expert_id)])

        # plot the model
        pts = [None]*len(Expert.training_data[0])
        for i in range(len(pts)):
            max_val = round(max(training_data[i]))
            min_val = round(min(training_data[i]))
            try:
                pts[i] = list(np.linspace(min_val, max_val, 100))
            except ZeroDivisionError:
                pts[i] = [min_val]

        pts = list(itertools.product(*pts))

        try:
            plot.plot(list(zip(*pts))[x_idx], list(list(zip(*Expert.predict_model.predict(pts)))[0]),'.', color='k', linewidth=0.2)
        except ValueError:
            pass

    else:
        plot_model(Expert.left, region_ids, plot, x_idx, y_idx, fig_num, subplot_num)
        plot_model(Expert.right, region_ids, plot, x_idx, y_idx, fig_num, subplot_num)

def plot_regional_mean_errors(mean_error_history, region_ids, fig_num=2, subplot_num=111):

     # plot configuration
    fig = plt.figure(fig_num)
    plot = fig.add_subplot(subplot_num)
    plt.ion()
    plt.show()
    plt.hold(True)
    plt.title("Mean Error vs Time")
    plt.xlabel("Time Step")
    plt.ylabel("Mean Error")


    # creating an empty list for each region
    region_error = dict()
    for id in region_ids:
        region_error[id] = [None]*len(mean_error_history)

    # group errors into groups corresponding to their region ids
    for t in range(len(mean_error_history)):
        for mean_error in mean_error_history[t]:
            if mean_error[0] in region_ids:
                region_error[mean_error[0]][t] = mean_error[1]


    colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))
    for id in region_error:
        plot.plot(range(len(region_error[id])), region_error[id], ls='-', lw=2, color=colours[region_ids.index(id)])


def plot_expert_tree(Expert, graph=None, level=0):

    # if it is the root
    is_root = False
    if graph is None:
        graph = pydot.Dot(graph_type='graph')
        is_root = True



    # this is leaf node
    if Expert.left is None and Expert.right is None:
        this_node = pydot.Node('Node %d.%d\nErr=%.*f\nER=%f\n# data=%d\n# new data=%d' % (level, Expert.expert_id,
                                                                       2, Expert.mean_error, Expert.rewards_history[-1],
                                                                       len(Expert.training_data), Expert.training_count))
    # if not a left node
    else:
        # create the node
        #this_node = pydot.Node('%d. %d' % (level, Expert.expert_id))
        this_node = pydot.Node('cut dim=%d \ncut val=%.*f' % (Expert.region_splitter.cut_dim, 2, Expert.region_splitter.cut_val))
        graph.add_node(this_node)

        # find the child nodes
        left_node = plot_expert_tree(Expert.left, graph, level+1)
        right_node = plot_expert_tree(Expert.right, graph, level+1)

        edge_left = pydot.Edge(this_node, left_node)
        graph.add_edge(edge_left)
        edge_right = pydot.Edge(this_node, right_node)
        graph.add_edge(edge_right)

    if is_root:
        graph.write_png('tree_graph.png')

    return this_node






