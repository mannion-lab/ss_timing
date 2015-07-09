import os

import numpy as np

import pyglet
import psychopy.logging
psychopy.logging.console.setLevel(psychopy.logging.CRITICAL)

import psychopy.visual

import stimuli.psychopy_ext

import ss_timing.conf
import ss_timing.exp
import ss_timing.data


def run(bits_mode=True):

    conf = ss_timing.conf.get_conf("instruct")

    image_files = os.listdir(conf.image_path)
    image_files.sort(reverse=True)

    image_files = [
        os.path.join(conf.image_path, image_file)
        for image_file in image_files
        if image_file.endswith("png")
    ]


    (_, trial_dt, _) = ss_timing.data.get_data_dtype()

    trial_info = np.zeros(1, dtype=trial_dt)[0]

    win = psychopy.visual.Window(
        size=conf.monitor_res_pix,
        monitor=conf.monitor_name,
        fullscr=True,
        allowGUI=False,
        autoLog=False,
        units="deg",
        gamma=1.0,
        useFBO=True,
        waitBlanking=False  # HACK
    )

    if bits_mode:

        bits = psychopy.hardware.crs.BitsSharp(
            win=win,
            mode=conf.monitor_mode,
            gamma="hardware",
            portName=conf.monitor_port
        )
        bits.temporalDithering = False

        pyglet.gl.glColorMask(1, 1, 0, 1)

    try:

        win.flip()

        stim = ss_timing.stim.get_stim(conf, win)

        # 01-0
        target = psychopy.visual.GratingStim(
            win=win,
            tex="sin",
            mask="raisedCos",
            units="deg",
            pos=[0, 0],
            size=[conf.target_diam_dva] * 2,
            sf=conf.target_cpd,
            ori=stimuli.utils.math_to_nav_polar(conf.target_ori),
            phase=0.0,
            contrast=0.5,
            autoLog=False
        )
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"], target], win)

        # 02-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"], stim["fixation"]] + stim["rings"], win)

        # 03-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"], stim["fixation"]] + stim["rings"], win)

        # 04-0
        for (pos_x, contrast) in zip(
            [-10, -5, 0, 5, 10],
            [0.02, 0.05, 0.1, 0.2, 0.4]
        ):
            target.contrast = contrast
            target.pos = [pos_x, 0.0]
            target.draw()

        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"]], win)

        # 05-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"]], win)

        # 06-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"]], win)

        # 07-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"], stim["fixation"]], win)

        # 08-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"]], win)

        # begin
        begin_file = [
            image_file
            for image_file in image_files
            if image_file.endswith("begin.png")
        ][0]
        stim["image"].image = begin_file
        _draw_and_wait(conf, [stim["image"], stim["fixation"]], win)

        # trials
        trial_info["surr_onset"] = "sim"
        trial_info["i_surr_onset"] = 1
        trial_info["surr_contrast"] = 0.0

        for target_contrast in [0.2, 0.1, 0.01, 0.02, 0.05, 0.1]:

            trial_info["target_contrast"] = target_contrast
            trial_info["target_pos"] = np.random.choice(
                conf.target_positions.keys()
            )

            _ = ss_timing.exp._run_trial(
                conf=conf,
                win=win,
                stim=stim,
                trial_data=trial_info
            )

        # 09-0
        stim["image"].image = image_files.pop()
        _draw_and_wait(conf, [stim["image"]], win)

    except:

        raise

    finally:

        if bits_mode:
            bits.mode = "auto++"
            bits.com.close()
        win.close()


def _draw_and_wait(conf, stim_to_draw, win):

    _ = [stim.draw() for stim in stim_to_draw]

    win.flip()

    conf.exp_input.clear()
    resp = conf.exp_input.wait()

    if "q" in resp:
        raise ValueError("User quit")

    return resp
