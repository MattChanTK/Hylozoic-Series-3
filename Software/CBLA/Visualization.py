__author__ = 'Matthew'
import numpy as np
import matplotlib.pyplot as plt


def moving_average(interval, window_size):
    interval = np.asarray(interval)
    interval = interval[:,0]
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def plot_evolution(action_history, fig_num=1):

    # plot configuration
    fig = plt.figure(fig_num)
    plot = fig.add_subplot(121)
    plot.plot(moving_average(action_history, 1), '.')
    plt.ion()
    plt.show()
    return plot

def plot_model(Expert, x_idx=1, y_idx=0, fig_num=1):

    # plot configuration
    fig = plt.figure(fig_num)
    plot = fig.add_subplot(122)
    plt.ion()
    plt.show()
    plt.hold(True)

    # this is leaf node
    if Expert.left is None and Expert.right is None:


        # plot the exemplars in the training set
        training_data = list(zip(*Expert.training_data))
        training_label = list(zip(*Expert.training_label))
        X = training_data[x_idx]
        Y = training_label[y_idx]
        plot.plot(X, Y, ".")

        # plot the model
        pts = list(range(round(min(X)), round(max(X))))
        try:
            plot.plot(pts, Expert.predict_model.predict(list(zip(*[pts, pts]))), color="k", linewidth=3)
        except Exception:
            pass

    else:
        plot_model(Expert.left, x_idx, y_idx, fig_num)
        plot_model(Expert.right, x_idx, y_idx, fig_num)
