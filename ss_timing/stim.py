import psychopy.visual

import stimuli.psychopy_ext


def get_stim(conf, win):

    stim = {}

    stim["surr"] = psychopy.visual.GratingStim(
        win=win,
        tex="sin",
        mask="raisedCos",
        units="deg",
        pos=[0.0, 0.0],
        size=[conf.surr_diam_dva] * 2,
        sf=conf.surr_cpd,
        ori=45.0,  # will be updated
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
            sf=conf.target_cpd,
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

    stim["ticks"] = {
        fb_pos: psychopy.visual.TextStim(
            win=win,
            font="wingdings",
            text=u"\uF0FC",
            pos=conf.fb_positions[fb_pos],
            height=1.0,
            autoLog=False
        )
        for fb_pos in conf.fb_positions.keys()
    }

    stim["checks"] = {
        fb_pos: psychopy.visual.TextStim(
            win=win,
            font="wingdings",
            text=u"\uF0FB",
            pos=conf.fb_positions[fb_pos],
            height=1.0,
            autoLog=False
        )
        for fb_pos in conf.fb_positions.keys()
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
        size=conf.monitor_res
    )

    return stim
