import datetime
import os

import numpy as np
import scipy.misc

import pyglet
import psychopy.logging
psychopy.logging.console.setLevel(psychopy.logging.CRITICAL)
import psychopy.visual
import psychopy.event
import psychopy.core
import psychopy.hardware.crs

import stimuli.psychopy_ext
import stimuli.psi

import ss_timing.conf
import ss_timing.data
import ss_timing.stim


class MonitorError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def run(
    subj_id,
    run_num,
    wait_to_start=True,
    wait_at_end=True,
    show_finish=False,
    screenshots=False
):

    conf = ss_timing.conf.get_conf(subj_id=subj_id)

    (_, data_exists) = ss_timing.data.get_data_path(conf)

    # if the path doesn't exist, then generate a new table
    if not data_exists:
        data = ss_timing.data.gen_data_table(conf)
    else:
        data = ss_timing.data.load_data(conf)

    # pull out the trials for this run
    i_this_run = (data["run_number"] == run_num)
    run_data = data[i_this_run]

    # check that we haven't already done this run
    try:
        assert np.all(run_data["completed"] == 0)
    except:
        AssertionError("Trials for this run are already marked as completed")

    # perform the run
    run_data = _run(
        conf,
        run_data,
        wait_to_start=wait_to_start,
        wait_at_end=wait_at_end,
        show_finish=show_finish,
        screenshots=screenshots
    )

    # check that all the trials have indeed been completed
    assert np.all(run_data["completed"] == 1)

    # update the main dataset
    data[i_this_run] = run_data

    # check again that all is well
    assert np.all(data["completed"][i_this_run] == 1)

    # and save
    ss_timing.data.save_data(conf, data)


def _run(
    conf,
    run_data,
    win=None,
    close_win=True,
    wait_to_start=True,
    wait_at_end=True,
    show_finish=False,
    screenshots=False
):

    trial_timer = psychopy.core.Clock()

    # initialise the staircases
    psis = [
        stimuli.psi.Psi(
            alpha_levels=conf.alpha_levels,
            beta_levels=conf.beta_levels,
            stim_levels=conf.x_levels,
            psych_func=conf.psych_func
        )
        for _ in xrange(conf.n_stairs_per_run)
    ]

    _ = [psi.step() for psi in psis]

    if win is None:
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

        bits = psychopy.hardware.crs.BitsSharp(
            win=win,
            mode=conf.monitor_mode,
            gamma="hardware",
            portName=conf.monitor_port
        )
        bits.temporalDithering = False

        pyglet.gl.glColorMask(1, 1, 0, 1)

        max_attempts = 3
        for _ in xrange(max_attempts):

            # check the refresh
            ms_avg = win.getMsPerFrame(nFrames=120)[0]

            try:

                np.testing.assert_almost_equal(
                    ms_avg,
                    1.0 / 120 * 1000,
                    decimal=1
                )

            except AssertionError:

                pass

            else:
                break

        else:

            bits.mode = "auto++"
            bits.com.close()
            win.close()

            print (
                "This is run number " +
                str(run_data["run_number"][0])
            )

            raise MonitorError(
                "Monitor refresh was detected as {n:.03f}".format(
                    n=ms_avg
                )
            )

    try:

        stim = ss_timing.stim.get_stim(
            conf=conf,
            win=win
        )

        if wait_to_start:

            stim["image"].image = os.path.join(
                conf.image_path,
                "begin.png"
            )

            win.flip()
            stim["image"].draw()
            stim["fixation"].draw()
            win.flip()

            conf.exp_input.clear()
            conf.exp_input.wait()

        stim["fixation"].draw()
        win.flip()

        psychopy.core.wait(0.5)

        for trial_data in run_data:

            if screenshots:
                screenshot_base = "cap_t_{n:d}".format(n=trial_data["run_trial"])
            else:
                screenshot_base = None

            assert trial_data["completed"] == 0

            i_stair = trial_data["stair_num"] - 1

            target_contrast = psis[i_stair].get_curr_stim_level()

            trial_data["target_contrast"] = target_contrast

            trial_timer.reset()

            trial_data = _run_trial(
                conf,
                win,
                stim,
                trial_data,
                screenshot_base
            )

            # update
            psis[i_stair].update(trial_data["correct"])
            psis[i_stair].step()

            (psi_a, psi_b) = psis[i_stair].get_estimates()

            trial_data["alpha_hat"] = psi_a
            trial_data["beta_hat"] = psi_b
            trial_data["completed"] = 1
            trial_data["when"] = str(datetime.datetime.now())

            while trial_timer.getTime() < conf.min_iti:
                pass

        if wait_at_end:

            stim["image"].image = os.path.join(
                conf.image_path,
                "wait.png"
            )

            stim["image"].draw()
            win.flip()

            psychopy.core.wait(conf.min_time_between_runs)

        if show_finish:

            stim["image"].image = os.path.join(
                conf.image_path,
                "finish.png"
            )

            stim["image"].draw()
            win.flip()

            conf.exp_input.wait()

    except:

        raise

    finally:

        if close_win:
            bits.mode = "auto++"
            bits.com.close()
            win.close()

    return run_data


def _run_trial(
    conf,
    win,
    stim,
    trial_data,
    screenshot_base=None
):

    if screenshot_base is not None:
        cap_count = 1

    timer = psychopy.core.Clock()
    conf.exp_input.set_clock(timer)

    grating_phase = np.random.rand()

    stim["surr"].phase = grating_phase
    stim["surr"].ori = stimuli.utils.math_to_nav_polar(trial_data["surr_ori"])

    for target in stim["targets"].values():
        # not entirely sure why, but 0.5 needs to be added to the target phase
        # so that it stays aligned with the surround
        target.phase = grating_phase + 0.5
        target.contrast = 0.0

    # ready to start the trial

    # pre
    stim["fixation"].set_fix_col([-1] * 3)
    timer.reset()
    while timer.getTime() < conf.pre_s:
        stim["fixation"].draw()
        win.flip()

    # stim
    win.recordFrameIntervals = True
    win.nDroppedFrames = 0

    for i_frame in xrange(conf.vis_train_frames):

        # set the contrasts of the surround and target based on which frame it
        # is
        stim["surr"].contrast = (
            trial_data["surr_contrast"] *
            conf.vis_train["surr"][trial_data["surr_onset"]][i_frame]
        )

        stim["targets"][trial_data["target_pos"]].contrast = (
            trial_data["target_contrast"] *
            conf.vis_train["target"][i_frame]
        )

        # update the fixation colour if the target is being shown
        if conf.vis_train["target"][i_frame] == 1:
            stim["fixation"].set_fix_col([1] * 3)
        else:
            stim["fixation"].set_fix_col([-1] * 3)

        stim["surr"].draw()
        _ = [target.draw() for target in stim["targets"].values()]
        stim["fixation"].draw()

        win.flip()

    if screenshot_base is not None:

        img = win.getMovieFrame()

        scipy.misc.imsave(
            screenshot_base + "_{n:d}.png".format(n=cap_count),
            np.array(img)[..., -1].astype("uint8")
        )

        cap_count += 1

    if win.nDroppedFrames > 0:
        print "Frame dropped"

    win.recordFrameIntervals = False

    # response
    stim["fixation"].set_fix_col([-0.5] * 3)
    stim["fixation"].draw()
    _ = [ring.draw() for ring in stim["rings"]]
    win.flip()

    conf.exp_input.clear()
    keys = conf.exp_input.wait(
        valid_keys=conf.resp_map.keys() + ["q"]
    )

    for (key, key_rt) in keys:

        if key == "q":
            raise ValueError("User aborted")
        else:
            resp_pos = conf.resp_map[key]
            trial_data["raw_resp"] = key
            trial_data["response_pos"] = resp_pos
            trial_data["response_time"] = key_rt

    trial_data["correct"] = int(
        trial_data["response_pos"] == trial_data["target_pos"]
    )

    stim["fb"][trial_data["correct"]].pos = conf.fb_positions[
        trial_data["target_pos"]
    ]

    _ = [ring.draw() for ring in stim["rings"]]
    stim["fb"][trial_data["correct"]].draw()
    stim["fixation"].draw()
    win.flip()

    if screenshot_base is not None:

        img = win.getMovieFrame()

        scipy.misc.imsave(
            screenshot_base + "_{n:d}.png".format(n=cap_count),
            np.array(img)[..., -1].astype("uint8")
        )

        cap_count += 1

    psychopy.core.wait(conf.fb_s)

    stim["fixation"].draw()
    win.flip()

    return trial_data
