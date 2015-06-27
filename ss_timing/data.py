import os
import collections

import numpy as np


def gen_data_table(conf):

    (_, dt, _) = get_data_dtype()

    data = np.zeros(0, dtype=dt)

    run_conds = []

    for _ in xrange(conf.n_runs_per_cond):
        for i_onset in xrange(conf.n_surr_onsets):
            for i_ori in xrange(conf.n_surr_oris):
                run_conds.append((i_onset, i_ori))

    np.random.shuffle(run_conds)

    assert len(run_conds) == conf.n_runs

    for (i_run, (i_onset, i_ori)) in enumerate(run_conds):

        run_num = i_run + 1

        run_data = np.zeros(conf.n_trials_per_run, dtype=dt)

        run_data["run_number"] = run_num

        run_data["surr_onset"] = conf.surr_onsets[i_onset]
        run_data["i_surr_onset"] = i_onset
        run_data["surr_ori"] = conf.surr_oris[i_ori]
        run_data["i_surr_ori"] = i_ori
        run_data["target_ori"] = conf.target_ori
        run_data["surr_contrast"] = conf.surr_contrast

        run_data["target_pos"] = np.random.choice(
            a=conf.target_positions.keys(),
            size=conf.n_trials_per_run
        )

        run_data["stair_num"] = np.repeat(
            range(1, conf.n_stairs_per_run + 1),
            conf.n_trials_per_stair
        )

        i_run_seq = np.random.permutation(conf.n_trials_per_run)
        run_data = run_data[i_run_seq]

        for stair_num in xrange(1, conf.n_stairs_per_run + 1):

            stair_trials = (run_data["stair_num"] == stair_num)

            run_data["stair_trial"][stair_trials] = range(
                1,
                conf.n_trials_per_stair + 1
            )

        run_data["run_trial"] = range(1, conf.n_trials_per_run + 1)

        data = np.hstack((data, run_data))

    data["when"] = "-" * 26

    return data


def load_data(conf):

    (_, dt, _) = get_data_dtype()

    (path, path_exists) = get_data_path(conf)

    if not path_exists:
        raise OSError("Path " + path + " does not exist")

    data = np.loadtxt(
        fname=path,
        dtype=dt,
        delimiter="\t"
    )

    return data


def save_data(conf, data):

    (_, dt, formats) = get_data_dtype()

    (path, _) = get_data_path(conf)

    header = conf.study_id + " - " + conf.subj_id + "\n"
    header += "\t".join(dt.names)

    np.savetxt(
        fname=path,
        X=data,
        fmt=formats,
        header=header,
        delimiter="\t"
    )


def get_data_dtype():

    # we care about insertion order
    dt_info = collections.OrderedDict()

    dt_info["run_number"] = {
        "dt": np.uint8,
        "fmt": "%u",
        "description": "Session run number"
    }

    dt_info["run_trial"] = {
        "dt": np.uint16,
        "fmt": "%u",
        "description": "Trial number in the run; 1..rN"
    }

    dt_info["stair_trial"] = {
        "dt": np.uint16,
        "fmt": "%u",
        "description": "Trial number for the staircase in this run; 1..sN"
    }

    dt_info["stair_num"] = {
        "dt": np.uint8,
        "fmt": "%u",
        "description": "Staircase number in this run; 1..S"
    }

    dt_info["surr_onset"] = {
        "dt": (np.str_, 3),
        "fmt": "%s",
        "description": "Surround onset condition"
    }

    dt_info["i_surr_onset"] = {
        "dt": np.uint8,
        "fmt": "%u",
        "description": "Index into the surround offsets"
    }

    dt_info["surr_ori"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Surround orientation, in degrees"
    }

    dt_info["i_surr_ori"] = {
        "dt": np.uint8,
        "fmt": "%u",
        "description": "Index into the surround orientations"
    }

    dt_info["target_ori"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Target orientation, in degrees"
    }

    dt_info["surr_contrast"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Surround contrast"
    }

    dt_info["target_contrast"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Target contrast"
    }

    dt_info["target_pos"] = {
        "dt": (np.str_, 2),
        "fmt": "%s",
        "description": "Target position"
    }

    dt_info["raw_resp"] = {
        "dt": (np.str_, 1),
        "fmt": "%s",
        "description": "Raw trial response"
    }

    dt_info["response_pos"] = {
        "dt": (np.str_, 2),
        "fmt": "%s",
        "description": "Response position"
    }

    dt_info["correct"] = {
        "dt": np.uint8,
        "fmt": "%u",
        "description": "Whether the response was correct"
    }

    dt_info["response_time"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Response time, in seconds"
    }

    dt_info["alpha_hat"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Psi alpha estimate after trial"
    }

    dt_info["beta_hat"] = {
        "dt": np.float,
        "fmt": "%f",
        "description": "Psi beta estimate after trial"
    }

    dt_info["completed"] = {
        "dt": np.uint8,
        "fmt": "%u",
        "description": """
Indicator if the trial has been completed; 0 if not, 1 if so
        """
    }

    dt_info["when"] = {
        "dt": (np.str_, 26),
        "fmt": "%s",
        "description": "When the trial was completed"
    }

    dt = np.dtype(
        [
            (dt_key, dt_info[dt_key]["dt"])
            for dt_key in dt_info.keys()
        ]
    )

    fmt = [dt_entry["fmt"] for dt_entry in dt_info.itervalues()]

    return (dt_info, dt, fmt)


def get_data_path(conf):

    run_path = os.path.join(
        conf.data_path,
        "{s:s}_{p:s}.txt".format(
            s=conf.study_id,
            p=conf.subj_id
        )
    )

    run_path_exists = os.path.exists(run_path)

    return (run_path, run_path_exists)
