
import tempfile

import numpy as np

import matplotlib.pyplot as plt
plt.ioff()

import ss_timing.conf
import ss_timing.data
import ss_timing.exp


def run():

    conf = ss_timing.conf.get_conf("practice")

    data = ss_timing.data.gen_data_table(conf)

    # pull out the trials for this run
    i_this_run = (data["run_number"] == 1)
    run_data = data[i_this_run]

    run_data["surr_contrast"] = 0.0

    # perform the run
    run_data = ss_timing.exp._run(
        conf,
        run_data,
        wait_to_start=True,
        wait_at_end=False,
        show_finish=False
    )

    temp = tempfile.NamedTemporaryFile(delete=False)

    ss_timing.data.save_data(
        conf,
        run_data,
        temp.name
    )

    print "Saved practice data to " + temp.name

    plot(conf, run_data)

    return run_data


def plot_from_file(path):

    conf = ss_timing.conf.get_conf("practice")

    data = ss_timing.data.load_data(conf, path)

    plot(conf, data)


def plot(conf, data):

    fig = plt.figure()

    fine_x = np.logspace(np.log10(0.001), np.log10(0.5), 100)

    n_bins = 20
    bins = np.logspace(
        np.log10(0.001),
        np.log10(0.5),
        n_bins
    )

    for i_stair in xrange(conf.n_stairs_per_run):

        ax = plt.subplot(1, 2, i_stair + 1)

        stair_data = data[data["stair_num"] == i_stair + 1]

        contrasts = stair_data["target_contrast"]
        corrects = stair_data["correct"]

        i_bins = np.digitize(contrasts, bins)

        resp_data = np.empty((n_bins, 4))
        resp_data.fill(np.NAN)

        for i_bin in xrange(n_bins):

            in_bin = (i_bins == i_bin)

            total = np.sum(in_bin)
            count = np.sum(corrects[in_bin])

            try:
                p = float(count) / float(total)
            except ZeroDivisionError:
                p = 0.0

            resp_data[i_bin, 0] = bins[i_bin]
            resp_data[i_bin, 1] = p
            resp_data[i_bin, 2] = count
            resp_data[i_bin, 3] = total

        ax.scatter(
            resp_data[:, 0],
            resp_data[:, 1],
            s=resp_data[:, 3] * 3
        )

        fine_y = conf.psych_func(
            x=fine_x,
            alpha=stair_data["alpha_hat"][-1],
            beta=stair_data["beta_hat"][-1]
        )

        ax.plot(fine_x, fine_y)

        ax.set_xscale("log")

        ax.set_ylim([-0.05, 1.05])

    plt.show()
