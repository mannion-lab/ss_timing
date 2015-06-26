import functools
import socket

import numpy as np

import exp_input
import stimuli.psi


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

    # 12 * (1/120) = 100ms
    conf.pres_frames = 12
    # 6 * (1/120) = 50ms
    conf.offset_frames = 6

    conf.vis_train_frames = conf.pres_frames + conf.offset_frames

    # visibility train for the pre-surround condition
    surr_pre_train = np.zeros(conf.vis_train_frames)
    surr_pre_train[:pres_frames] = 1

    surr_sim_train = np.zeros(conf.vis_train_frames)
    surr_sim_train[-pres_frames:] = 1

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

    conf.gp_radius_deg = 7.0
    # deg/sq
    conf.gp_density_deg_sq = 40.0
    conf.gp_n_dots = conf.gp_radius_deg ** 2 * conf.gp_density_deg_sq
    conf.gp_n_dipoles = np.round(conf.gp_n_dots).astype("int")
    conf.gp_pole_sep_deg = 0.15
    conf.gp_dot_size_deg = 0.25
    # this is the point of full contrast; the mask starts at this minus the
    # fringe width
    conf.gp_mask_in_deg = 2.0
    # this is the maximum extent of the mask, including the fringe
    conf.gp_mask_out_deg = conf.gp_radius_deg
    conf.gp_mask_fringe_deg = 1.0

    conf.ref_len_deg = 0.5

    conf.fix_diam_va = 0.25

    conf.pre_s = 0.25
    conf.on_s = 0.25
    conf.min_iti = 1.5

    conf.psych_func = functools.partial(
        stimuli.psi.logistic,
        lapse_rate=0.04,
        guess_rate=0.04
    )

    # the staircase parameters depend on the GP type
    if conf.gp_type == "trans":
        # staircase potential stimulus levels
        conf.x_levels = np.linspace(45.0, 90.0, 90, endpoint=True)
        # potential alpha levels
        conf.alpha_levels = np.arange(45.0, 90.0, 0.5)
        # potential beta levels
        conf.beta_levels = np.logspace(
            np.log10(0.05),
            np.log10(1),
            100
        )
    else:
        # staircase potential stimulus levels
        conf.x_levels = np.linspace(0, 90.0, 90, endpoint=True)
        # potential alpha levels
        conf.alpha_levels = np.arange(0, 90.0, 0.5)
        # potential beta levels
        conf.beta_levels = np.logspace(
            np.log10(0.025),
            np.log10(1),
            100
        )

    conf.resp_map = {
        ("P", "left"): ("S", 0),  # polar, left is starburst
        ("P", "right"): ("C", 1),  # polar, right is concentric
        ("T", "left"): ("V", 1),  # trans, left is vertical
        ("T", "right"): ("O", 0)  # trans, right is oblique
    }

    conf.min_time_between_runs = 30.0

    return conf
