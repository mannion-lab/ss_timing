import os

import psychopy.visual
import psychopy.filters

import stimuli.psychopy_ext
import stimuli.utils


def get_stim(conf, win):

    stim = {}

    grating_size = stimuli.utils.nearest_power_of_two(conf.surr_diam_pix)

    grating = psychopy.filters.makeGrating(
        res=grating_size,
        cycles=grating_size / conf.grating_cpp
    )

    surr_mask = psychopy.filters.makeMask(
        matrixSize=grating_size,
        shape="raisedCosine",
        radius=[conf.surr_diam_pix / grating_size] * 2
    )


    stim["surr"] = psychopy.visual.GratingStim(
        win=win,
        tex="sin",
        mask="raisedCos",
        units="deg",
        pos=[0.0, 0.0],
        size=[conf.surr_diam_dva] * 2,
        sf=[conf.surr_cpd, 1],
        ori=0.0,  # will be updated
        phase=0.0,  # will be updated
        contrast=conf.surr_contrast,
        autoLog=False
    )

    stim["targets"] = {
        target_pos: psychopy.visual.GratingStim(
            win=win,
            tex="sin",
            mask="raisedCos",
            units="deg",
            pos=conf.target_positions[target_pos],
            size=[conf.target_diam_dva] * 2,
            sf=[conf.grating_cpd, 1],
            ori=stimuli.utils.math_to_nav_polar(conf.target_ori),
            phase=0.0,  # will be updated
            contrast=0.0,  # will be updated
            autoLog=False
        )
        for target_pos in conf.target_positions.keys()
    }

    stim["rings"] = [
        psychopy.visual.Circle(
            win=win,
            radius=conf.target_diam_dva / 2.0,
            edges=64,
            pos=conf.target_positions[target_pos],
            autoLog=False
        )
        for target_pos in conf.target_positions.keys()
    ]

    stim["fb"] = {
        corr: psychopy.visual.ImageStim(
            win=win,
            size=conf.target_diam_dva * 0.25,
            autoLog=False,
            image=os.path.join(
                conf.image_path,
                corr_file + ".png"
            )
        )
        for (corr, corr_file) in zip(
            (0, 1), ("cross", "tick")
        )
    }

    stim["fixation"] = stimuli.psychopy_ext.Fixation(
        win=win,
        fix_diam_va=conf.fix_diam_va,
        fix_fill_col=[0] * 3,
        fix_edge_col=[-1] * 3,
        fix_edge_width_pix=2,
        lock_pres=False,
        lock_diam_va=0.0,
        lock_phase=0.0
    )

    stim["image"] = psychopy.visual.ImageStim(
        win=win,
        units="pix",
        size=conf.monitor_res_pix
    )

    return stim
