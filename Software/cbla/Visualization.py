__author__ = 'Matthew'
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pydot
import itertools
import os
from save_figure import save


fig_size = (11, 8.5)


def moving_average(interval, window_size, dim=0):
    interval = np.asarray(interval)
    interval = interval[:,dim]
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def plot_evolution(action_history, time=None, title='Action vs Time', y_label='M(t)', y_lim=None, linestyle='None', marker='o', marker_size=1.5, fig_num=1, subplot_num=121):

    # plot configuration
    fig = plt.figure(fig_num, figsize=fig_size)
    plot = fig.add_subplot(subplot_num)

    counter = 0
    action_history = list(zip(*action_history))
    for history in action_history:
        if time is None:
            plot.plot(range(len(history)), history, label=y_label[counter], linestyle=linestyle, marker=marker, ms=marker_size, mew=0.01, fillstyle='full', lw=0)
            plt.xlabel("time step")
        else:
            time_delta_s = [step.total_seconds() for step in (np.array(time) - time[0])]
            plot.plot(time_delta_s, history, label=y_label[counter], linestyle=linestyle,marker=marker, ms=marker_size, mew=0.01, fillstyle='full', lw=0)
            plt.xlabel("s")
        counter += 1
    #plt.ion()
    #plt.show()
    plt.title(title)
    plt.ylabel('M(t)')
    plt.legend(loc=2, prop={'size':12})
    if y_lim is not None and isinstance(y_lim, tuple):
        plt.ylim(y_lim)


    return plot

def plot_model(Expert, region_ids, plot=None, show_model=True, x_idx=1, y_idx=0, fig_num=1, subplot_num=122, x_lim=None, y_lim=None, m_label=None, s_label=None, title="Prediction Models"):

    # plot configuration
    if plot is None:
        fig = plt.figure(fig_num, figsize=fig_size)
        if isinstance(subplot_num, tuple):
            plot = fig.add_subplot(subplot_num[0], subplot_num[1], subplot_num[2])
        else:
            plot = fig.add_subplot(subplot_num)
        #plt.ion()
        #plt.show()
        plt.hold(True)
        plt.title(title)
        if s_label is None or m_label is None:
            plt.xlabel("SM(t) [" + str(x_idx) + "]")
            plt.ylabel("S(t+1) [" + str(y_idx) + "]")
        else:
            plt.xlabel((s_label+m_label)[x_idx], fontsize=10)
            plt.ylabel(s_label[y_idx], fontsize=10)
        if y_lim is not None:
            plt.ylim(y_lim)
        if x_lim is not None:
            plt.xlim(x_lim)

    # this is leaf node
    if Expert.left is None and Expert.right is None:

        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))

        # plot the exemplars in the training set
        training_data = list(zip(*Expert.training_data))
        training_label = list(zip(*Expert.training_label))
        X = training_data[x_idx]
        Y = training_label[y_idx]
        try:
            plot.plot(X, Y, marker='o', ms=3, mew=0.01, lw=0, color=colours[region_ids.index(Expert.expert_id)])
        except ValueError:
            pass

        # plot the model
        if show_model:
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
        plot_model(Expert.left, region_ids, plot, show_model, x_idx, y_idx, fig_num, subplot_num, x_lim, y_lim, m_label, s_label, title)
        plot_model(Expert.right, region_ids, plot, show_model, x_idx, y_idx, fig_num, subplot_num, x_lim, y_lim, m_label, s_label, title)

def plot_model_3D(Expert, region_ids, ax=None, x_idx=(0, 1), y_idx=0, fig_num=2, subplot_num=111, data_only=False, m_label=None, s_label=None):

    # plot configuration
    if ax is None:
        fig = plt.figure(fig_num, figsize=fig_size)
        ax = fig.add_subplot(subplot_num, projection='3d')
        #plt.ion()
        #plt.show()
        plt.hold(True)
        plt.title("Prediction Models")

        if s_label is None or m_label is None:
            ax.set_xlabel("SM(t) [" + str(x_idx[0]) + "]")
            ax.set_ylabel("SM(t) [" + str(x_idx[1]) + "]")
            ax.set_zlabel("S(t+1) [" + str(y_idx) + "]")
        else:
            ax.set_xlabel((s_label+m_label)[x_idx[0]], fontsize=10)
            ax.set_ylabel((s_label+m_label)[x_idx[1]], fontsize=10)
            ax.set_zlabel(s_label[y_idx], fontsize=10)


        #plt.ylim((-200, 200))
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
        try:
            ax.scatter(X, Y, Z, marker='o', s=2.0, color=colours[region_ids.index(Expert.expert_id)])
        except ValueError:
            pass

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
        plot_model_3D(Expert.left, region_ids, ax, x_idx, y_idx, fig_num, subplot_num, data_only, m_label, s_label)
        plot_model_3D(Expert.right, region_ids, ax, x_idx, y_idx, fig_num, subplot_num, data_only, m_label, s_label)

def _plot_regional_data(data, region_ids, time=None, fig_num=2, subplot_num=111, title="", y_label="", x_label="Time Step"):

     # plot configuration
    fig = plt.figure(fig_num, figsize=fig_size)
    plot = fig.add_subplot(subplot_num)
    #plt.ion()
    #plt.show()
    plt.hold(True)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)


    # creating an empty list for each region
    region_data = dict()
    region_data_time = dict()
    for id in region_ids:
        region_data[id] = [None]*len(data)
        region_data_time[id] = [None]*len(data)

    # group data into groups corresponding to their region ids
    for t in range(len(data)):
        for val in data[t]:
            if val[0] in region_ids:
                region_data[val[0]][t] = val[1]

    if time is None:
        time = range(len(region_data[id]))
    else:
        time = [step.total_seconds() for step in (np.array(time) - time[0])]

    colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))
    for id in region_data:
        plot.plot(time, region_data[id], ls='-', lw=2, color=colours[region_ids.index(id)])

def plot_regional_mean_errors(mean_error_history, region_ids, time=None, fig_num=2, subplot_num=111):

    if time is None:
        x_label = "Time Step"
    else:
        x_label = 's'

    _plot_regional_data(mean_error_history, region_ids, time=time, fig_num=fig_num, subplot_num=subplot_num, title="Mean Error vs Time", y_label="Mean Error", x_label=x_label)

def plot_regional_action_values(value_history, region_ids, time=None, fig_num=1, subplot_num=111):

    if time is None:
        x_label = "Time Step"
    else:
        x_label = 's'

    _plot_regional_data(value_history, region_ids, time=time, fig_num=fig_num, subplot_num=subplot_num, title="Action Value vs Time", y_label="Action Value", x_label=x_label)

def plot_regional_action_rate(action_count_history, region_ids, time=None, fig_num=1, subplot_num=111):

    action_rate_history = []
    for action_count in action_count_history:
        action_count = list(zip(*action_count))
        region_id = action_count[0]
        action_count = action_count[1]
        total_count = 1 #sum(action_count)
        action_rate = np.array(action_count)/total_count
        action_rate_history.append(tuple(zip(region_id, action_rate)))

    if time is None:
        x_label = "Time Step"
    else:
        x_label = 's'

    _plot_regional_data(tuple(action_rate_history), region_ids, time=time, fig_num=fig_num, subplot_num=subplot_num, title="Action Count vs Time", y_label="Action Count", x_label=x_label)

def plot_expert_tree(Expert, region_ids, graph=None, level=0, folder_name=None, filename=None, ):

    # if it is the root
    is_root = False
    if graph is None:
        graph = pydot.Dot(graph_type='graph', ordering='out')
        is_root = True

    # this is leaf node
    if Expert.left is None and Expert.right is None:


        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))
        colour = colours[region_ids.index(Expert.expert_id)]

        for c in range(len(colour)-1):
            colour[c] = round(colour[c]*0xFF)

        this_node = pydot.Node('Node %d.%d'%(level, Expert.expert_id),
                               label='Err=%.2f\nVal=%.2f\n# data=%d\n# new data=%d' %
                                     (Expert.mean_error, Expert.action_value, len(Expert.training_data), Expert.training_count),
                               style="filled", fillcolor="#%x%x%x%x"%(colour[0], colour[1], colour[2], colour[3]))

        if is_root:
            graph.add_node(this_node)

    # if not a left node
    else:
        # create the node
        #this_node = pydot.Node('%d. %d' % (level, Expert.expert_id))
        try:
            this_node = pydot.Node('Node %d.%d'%(level, Expert.expert_id),
                                    label='cut dim=%d \ncut val=%.*f' % (Expert.region_splitter.cut_dim, 2, Expert.region_splitter.cut_val))
        except AttributeError:
            this_node = pydot.Node('Node %d.%d'% (level, Expert.expert_id))
        graph.add_node(this_node)

        # find the child nodes
        left_node = plot_expert_tree(Expert=Expert.left, region_ids=region_ids, graph=graph, level=level+1)
        right_node = plot_expert_tree(Expert=Expert.right, region_ids=region_ids, graph=graph, level=level+1)
        graph.add_node(left_node)
        graph.add_node(right_node)

        edge_left = pydot.Edge(this_node, left_node, label='<=')
        graph.add_edge(edge_left)
        edge_right = pydot.Edge(this_node, right_node, label='>')
        graph.add_edge(edge_right)

    if is_root:


        folder = os.path.join(os.getcwd(), '%s tree_graphs' % folder_name )
        if not os.path.exists(folder):
            os.makedirs(folder)

        if filename is None:
            graph.write_png(os.path.join(folder, 'tree_graph.png'))
        else:
            graph.write_png(os.path.join(folder, filename +'_tree_graph.png'))

    return this_node


def plot_show(block=False):
    pass
    plt.ioff()
    plt.show(block=block)
    #plt.ion()

def plot_ion():
    plt.ion()

def plot_draw():
    plt.draw()

def plot_close():
    plt.close()


