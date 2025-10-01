"""
    main script containing the setup for the training
"""
import sys
import logging
import torch as pt
from time import time
from os import environ
from os.path import join

from ax.service.ax_client import AxClient
from ax.service.utils.instantiation import ObjectiveProperties

from airfoil_shape_optimization.generate_airfoil import AirfoilGenerator
from airfoil_shape_optimization.modify_simulation_setup import ModifySimulationSetup
from airfoil_shape_optimization.utils import create_run_directories
from airfoil_shape_optimization.local_execution import LocalExecuter
from airfoil_shape_optimization.data_loader import DataLoader


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    force=True)


def run_optimization(settings: dict) -> None:
    # parallel execution not yet supported
    if settings["N_simulations"] > 1 or settings["N_runner"] > 1:
        logger.warning("Parallel execution not implemented. Setting 'N_simulations' and 'N_runner' to one.")
        settings["N_simulations"] = 1
        settings["N_runner"] = 1

    # make sure TU is not set in percent
    if settings["Tu"] > 1:
        logger.warning(f"Found a value for Tu of {settings['Tu']}. Tu is expected to be 0 <= Tu <= 1.")
        exit()

    # start the timer
    t_start = time()

    # initialize dataloader
    dataloader = DataLoader(settings["train_path"], settings["cl_target"], settings["alpha_target"],
                            settings["alpha_range"])

    # create copies of the base case and initialize the global log file
    dirs = [join(settings["train_path"], f"trial_{d}") for d in range(settings["N_simulations"])]
    create_run_directories(settings["base_simulation"], dirs)

    _fmt = "{:." + str(6) + "f}"
    with open(join(settings["train_path"], "log.optimization"), "w") as log_file:
        log_file.write("trial\tf_max\t\tt_max\t\txf\t\t\tKR\t\t\tN1\t\t\tN2\t\t\tobjective\n")
        log_file.write("-----\t--------\t--------\t--------\t--------\t--------\t--------\t---------\n")

    # set IC conditions of the simulation
    simulation = ModifySimulationSetup(dirs, settings["Tu"], settings["Re"], settings["chord"], settings["U_inf"],
                                       settings["Ma"], settings["compute_IC"], settings["T_inf"], settings["rho_inf"])
    simulation.set_inflow_conditions()

    # initialize the executer
    executer = LocalExecuter(dirs, settings["N_runner"])

    # instantiate airfoil generator class
    airfoil_generator = AirfoilGenerator(x_stop=settings["chord"])

    # initialize Ax
    parameters = [{"name": f"{k}", "type": "range", "bounds": settings[k]} for k in
                  ["f_max", "t_max", "xf", "KR", "N1", "N2"]]

    ax = AxClient(random_seed=0, torch_device=pt.device("cpu"))
    ax.create_experiment(name="experiment", parameters=parameters, overwrite_existing_experiment=True,
                         objectives={"loss": ObjectiveProperties(minimize=True)})

    # execute the training
    for t in range(settings["N_trials"]):
        logging.info(f"Starting trial {t}.")

        # sample next CST parameters, currently only sequentiell execution is supported
        airfoils, trial_index = ax.get_next_trial()

        # generate airfoils from the predicted parameters and write the STL files
        for d in range(len(dirs)):
            airfoil_generator.generate_airfoil(airfoils["N1"], airfoils["N2"], airfoils["KR"], airfoils["f_max"],
                                               airfoils["xf"], airfoils["t_max"], airfoil_name=f"airfoil",
                                               write_path=join(dirs[d], "constant", "triSurface"))

        # compute polar in the defined alpha range, since the AoA's are usually very low, we can use float16
        all_alpha = pt.arange(settings["alpha_range"][0], settings["alpha_range"][1]+settings["delta_alpha"],
                              settings["delta_alpha"], dtype=pt.float16)

        # make sure alpha_target is included within the polar
        if settings["alpha_target"] not in all_alpha:
            all_alpha = pt.cat([all_alpha, pt.tensor(settings["alpha_target"]).unsqueeze(-1)])

        for idx, alpha in enumerate(all_alpha):
            logger.info(f"Starting computation for alpha = {'{:.2f}'.format(alpha.item())} deg.")

            # set new alpha in all dicts
            simulation.alpha = alpha

            # map the field from previous alpha as initialization to new alpha to improve convergence
            if idx > 0:
                simulation.initialize_new_aoa()

            # execute simulation
            executer.run_simulation()

        # fetch data from the simulations
        objective = [dataloader.evaluate_trial(t, d) for d in dirs]

        # evaluate the trial, we only have a single trial so take the first entry of the list
        ax.complete_trial(trial_index=trial_index, raw_data={"loss": objective[0]})

        # clean the cases
        executer.clean_simulation()

        # update the log file with the CST parameters and objective
        with open(join(settings["train_path"], "log.optimization"), "a") as log_file:
            log_file.write(f"{t}\t\t{_fmt.format(airfoils['f_max'])}\t{_fmt.format(airfoils['t_max'])}\t"
                           f"{_fmt.format(airfoils['xf'])}\t{_fmt.format(airfoils['KR'])}\t"
                           f"{_fmt.format(airfoils['N1'])}\t{_fmt.format(airfoils['N2'])}\t"
                           f"{_fmt.format(objective[0])}\n")

    logging.info(f"\nFinished optimization after {_fmt.format(time() - t_start)} s.\n")
    logging.info(ax.get_best_parameters())
    pt.save(ax.get_best_parameters(), join(settings["train_path"], "results_final_parameters.pt"))
    pt.save(settings, join(settings["train_path"], "settings_optimization.pt"))


if __name__ == "__main__":
    # TODO: fix transition model & mapFields
    setup = {
        # boundaries for CSM parameters
        "f_max": [0.005, 0.05],  # max. camber
        "t_max": [0.05, 0.15],  # max. thickness
        "xf": [0.35, 0.75],  # position of max. camber
        "KR": [0.2, 0.8],  # shape parameter for thickness distribution
        "N1": [0.4, 0.6],  # shape parameter for leading edge
        "N2": [0.8, 1.1],  # shape parameter for trailing edge

        # initial conditions of the simulation
        "Ma": 0.1,  # Mach number
        "Re": 3e5,  # Reynolds number
        "compute_IC": "U",  # weather to compute initial conditions based on U or Ma
        "U_inf": 20,  # free stream velocity
        "Tu": 0.01,  # turbulence level (not in percent!)
        "rho_inf": 1,  # free stream density
        "T_inf": 273,  # free stream temperature
        "chord": 0.15,  # chord length

        # settings for optimization
        "N_trials": 20,
        "N_runner": 1,
        "N_simulations": 1,
        "base_simulation": "base_simulation",
        "train_path": "execute_training",

        "alpha_target": 0,  # target angle of attack at design point
        "alpha_range": [-2, 5],  # angle of attack range in which the airfoil should perform well
        "delta_alpha": 0.5,  # increment AoA by x deg
        "cl_target": 0.4,  # target c_L at alpha_target
    }
    # add the path to OpenFOAM bashrc when executing from IDE
    environ["WM_PROJECT_DIR"] = "/usr/lib/openfoam/openfoam2412"
    sys.path.insert(0, environ["WM_PROJECT_DIR"])

    # execute the optimization
    run_optimization(setup)
