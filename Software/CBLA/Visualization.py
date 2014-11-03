__author__ = 'Matthew'
import numpy as np
import matplotlib.pyplot as plt


def moving_average(interval, window_size):
    interval = np.asarray(interval)
    interval = interval[:,0]
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def plot_evolution(action_history, fig_num=1, subplot_num=121):

    # plot configuration
    fig = plt.figure(fig_num)
    plot = fig.add_subplot(subplot_num)
    plot.plot(moving_average(action_history, 1), '.')
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
        plt.ylabel("SM(t) [" + str(x_idx) + "]")
        plt.xlabel("S(t+1)")

    # this is leaf node
    if Expert.left is None and Expert.right is None:

        colours = plt.get_cmap('gist_rainbow')(np.linspace(0, 1.0, len(region_ids)))

        # plot the exemplars in the training set
        training_data = list(zip(*Expert.training_data))
        training_label = list(zip(*Expert.training_label))
        X = training_data[x_idx]
        Y = training_label[y_idx]
        plot.plot(Y, X, marker='o', ms=2, mew=0, lw=0, color=colours[region_ids.index(Expert.expert_id)])

        # plot the model
        pts = list(np.arange(round(min(X)), round(max(X)), 0.1))
        try:
            plot.plot(Expert.predict_model.predict(list(zip(*[pts, pts]))), pts, ls='-', color="k", linewidth=1)
        except Exception:
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
