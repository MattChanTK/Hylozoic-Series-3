__author__ = 'Matthew'
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pydot
import itertools



def moving_average(interval, window_size, dim=0):
    interval = np.asarray(interval)
    interval = interval[:,dim]
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def plot_evolution(action_history, title='Action vs Time', y_label='M(t)', marker_size=1.5, y_dim=0, fig_num=1, subplot_num=121):

    # plot configuration
    fig = plt.figure(fig_num)
    plot = fig.add_subplot(subplot_num)

    plot.plot(action_history, marker='o', ms=marker_size, mew=0.01, fillstyle='full', lw=0)
    plt.ion()
    plt.show()
    plt.title(title)
    plt.xlabel("Time Step")
    plt.ylabel(y_label)

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
        plot.plot(X, Y, marker='o', ms=2, mew=0.01, lw=0, color=colours[region_ids.index(Expert.expert_id)])

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

def plot_model_3D(Expert, region_ids, ax=None, x_idx=(0, 1), y_idx=0, fig_num=2, subplot_num=111, data_only=False):

    # plot configuration
    if ax is None:
        fig = plt.figure(fig_num)
        ax = fig.add_subplot(subplot_num, projection='3d')
        plt.ion()
        plt.show()
        plt.hold(True)
        plt.title("Prediction Models")
        ax.set_xlabel("SM(t) [" + str(x_idx[0]) + "]")
        ax.set_ylabel("SM(t) [" + str(x_idx[1]) + "]")
        ax.set_zlabel("S(t+1)")
        #ax.set_alpha(0.5)

    # making sure the the first x index and smaller than the second x index
    if (x_idx[1] < x_idx[0]):

        swapped_x_idx = [x_idx[1], x_idx[0]]
        x_idx = tuple(swapped_x_idx)


    # this is leaf node
    if Expert.left is None and Expert.right is None:

        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))

        # plot the exemplars in the training set
        training_data = list(zip(*Expert.training_data))
        training_label = list(zip(*Expert.training_label))
        X = training_data[x_idx[0]]
        Y = training_data[x_idx[1]]
        Z = training_label[y_idx]
        ax.scatter(X, Y, Z, marker='o', s=2.0, color=colours[region_ids.index(Expert.expert_id)])

        if data_only:
            return

        # plot the model
        pts = [None]*2
        pts[0] = list(np.linspace(round(min(X)), round(max(X)), 100))
        pts[1] = list(np.linspace(round(min(Y)), round(max(Y)), 100))

        pts = np.meshgrid(pts[0], pts[1])

        # padding 0 for not visualized components
        num_dim = len(Expert.training_data[0])
        f_pad = [0]*x_idx[0]
        m_pad = [0]*(x_idx[1]-x_idx[0]-1)
        b_pad = [0]*(num_dim-x_idx[1]-1)


        zs = np.array([Expert.predict_model.predict(tuple(f_pad + [x] + m_pad + [y] + b_pad)) [y_idx]
                       for x,y in zip(np.ravel(pts[0]), np.ravel(pts[1]))])

        # for x, y in zip(np.ravel(pts[0]), np.ravel(pts[1])):
        #     zs = Expert.predict_model.predict(tuple(f_pad + [x] + m_pad + [y] + b_pad))
        # zs = np.array(zs)

        z = zs.reshape(pts[0].shape)
        ax.plot_surface(pts[0], pts[1], z, color='k', alpha=0.5, linewidth=0, antialiased=True)


    else:
        plot_model_3D(Expert.left, region_ids, ax=ax, x_idx=x_idx, y_idx=y_idx, fig_num=fig_num, subplot_num=subplot_num, data_only=data_only)
        plot_model_3D(Expert.right, region_ids, ax=ax, x_idx=x_idx, y_idx=y_idx, fig_num=fig_num, subplot_num=subplot_num, data_only=data_only)

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


def plot_expert_tree(Expert, region_ids, filename=None, graph=None, level=0):

    # if it is the root
    is_root = False
    if graph is None:
        graph = pydot.Dot(graph_type='graph')
        is_root = True

    # this is leaf node
    if Expert.left is None and Expert.right is None:


        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))
        colour = colours[region_ids.index(Expert.expert_id)]

        for c in range(len(colour)-1):
            colour[c] = round(colour[c]*0xFF)

        this_node = pydot.Node('Node %d.%d\nErr=%.*f\nER=%f\n# data=%d\n# new data=%d' % (level, Expert.expert_id,
                                                                       2, Expert.mean_error, Expert.rewards_history[-1],
                                                                       len(Expert.training_data), Expert.training_count),
                               style="filled", fillcolor="#%x%x%x%x"%(colour[0], colour[1], colour[2], colour[3]))
    # if not a left node
    else:
        # create the node
        #this_node = pydot.Node('%d. %d' % (level, Expert.expert_id))
        try:
            this_node = pydot.Node('Node %d.%d\ncut dim=%d \ncut val=%.*f' % (level, Expert.expert_id,Expert.region_splitter.cut_dim, 2, Expert.region_splitter.cut_val))
        except AttributeError:
            this_node = pydot.Node('Node %d.%d'% (level, Expert.expert_id))
        graph.add_node(this_node)

        # find the child nodes
        left_node = plot_expert_tree(Expert=Expert.left, region_ids=region_ids, graph=graph, level=level+1)
        right_node = plot_expert_tree(Expert=Expert.right, region_ids=region_ids, graph=graph, level=level+1)
        graph.add_node(left_node)
        graph.add_node(right_node)

        edge_left = pydot.Edge(this_node, left_node)
        graph.add_edge(edge_left)
        edge_right = pydot.Edge(this_node, right_node)
        graph.add_edge(edge_right)

    if is_root:
        if filename is None:
            graph.write_png('tree_graph.png')
        else:
            graph.write_png(filename +'_tree_graph.png')

    return this_node


def plot_show():

    plt.ioff()
    plt.show()



