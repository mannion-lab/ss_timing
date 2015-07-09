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

    return run_data
