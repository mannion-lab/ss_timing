import functools
import socket

import numpy as np

import exp_input
import stimuli.psi
import stimuli.utils


class ConfigContainer(object):
    pass


def get_conf(subj_id):

    conf = ConfigContainer()

    conf.subj_id = subj_id

    conf.study_id = "ss_timing"

    data_dir = {
        "djm_unsw": "/home/damien/venv_study/ss_timing/data",
        "djm_1018_12": "/sci/study/ss_timing/data"
    }
    conf.data_path = data_dir[socket.gethostname()]

    image_dir = {
        "djm_unsw": "/home/damien/venv_study/ss_timing/code/ss_timing/images",
        "djm_1018_12": "/sci/study/gp_unc/code/ss_timing/images"
    }
    conf.image_path = image_dir[socket.gethostname()]

    conf.exp_input = exp_input.InputDevice(use_rb=False)

    # surround onset conditions; pre = before target, sim = simultaneous with
    # target
    conf.surr_onsets = ["pre", "sim"]
    conf.n_surr_onsets = len(conf.surr_onsets)

    # surround ori can be horizontal (orth) or vertical (par)
    conf.surr_oris = [0.0, 90.0]
    conf.n_surr_oris = len(conf.surr_oris)
    # target is vertical
    conf.target_ori = 90.0

    conf.n_trials_per_stair = 40
    conf.n_stairs_per_run = 2
    conf.n_trials_per_run = conf.n_trials_per_stair * conf.n_stairs_per_run

    conf.n_runs_per_cond = 3
    conf.n_conds = conf.n_surr_onsets + conf.n_surr_oris

    conf.n_runs = conf.n_runs_per_cond * conf.n_conds

    conf.n_trials_overall = conf.n_trials_per_run * conf.n_runs

    conf.monitor_name = "1018_12_dpp"
    conf.monitor_res = (1920, 1080)
    conf.monitor_mode = "mono++"

    # 12 * (1/120) = 100ms
    conf.pres_frames = 12
    # 6 * (1/120) = 50ms
    conf.offset_frames = 6

    conf.vis_train_frames = conf.pres_frames + conf.offset_frames

    # visibility train for the pre-surround condition
    surr_pre_train = np.zeros(conf.vis_train_frames)
    surr_pre_train[:conf.pres_frames] = 1

    surr_sim_train = np.zeros(conf.vis_train_frames)
    surr_sim_train[-conf.pres_frames:] = 1

    assert np.sum(surr_pre_train) == np.sum(surr_sim_train)

    target_train = surr_sim_train

    conf.vis_train = {
        "surr": {
            "pre": surr_pre_train,
            "sim": surr_sim_train
        },
        "target": target_train
    }


    # stimulus parameters

    conf.target_cpd = 1.0
    conf.target_diam_dva = 3.0
    conf.target_ecc_dva = 5.0
    conf.target_positions = {
        "NE": stimuli.utils.pol_to_cart(45, conf.target_ecc_dva),
        "NW": stimuli.utils.pol_to_cart(135, conf.target_ecc_dva),
        "SW": stimuli.utils.pol_to_cart(225, conf.target_ecc_dva),
        "SE": stimuli.utils.pol_to_cart(315, conf.target_ecc_dva)
    }

    conf.surr_cpd = 1.0
    conf.surr_diam_dva = 20.0
    conf.surr_contrast = 0.25

    conf.fix_diam_va = 0.25

    fb_ecc = conf.target_ecc_dva + conf.target_diam_dva / 2.0
    conf.fb_positions = {
        "NE": stimuli.utils.pol_to_cart(45, fb_ecc),
        "NW": stimuli.utils.pol_to_cart(135, fb_ecc),
        "SW": stimuli.utils.pol_to_cart(225, fb_ecc),
        "SE": stimuli.utils.pol_to_cart(315, fb_ecc)
    }

    conf.pre_s = 0.25
    conf.on_s = 0.25
    conf.min_iti = 1.5

    conf.psych_func = functools.partial(
        stimuli.psi.weibull,
        lapse_rate=0.02,
        guess_rate=0.25  # 4AFC
    )

    conf.x_levels = np.linspace(0.001, 0.5, 500)
    conf.alpha_levels = np.linspace(0.001, 0.5, 500)
    conf.beta_levels = np.logspace(
        np.log10(0.5),
        np.log10(20.0),
        100
    )

    conf.resp_map = {
        9: "NE",
        7: "NW",
        1: "SW",
        3: "SE"
    }

    conf.min_time_between_runs_s = 30.0

    return conf
