"""
    main script containing the setup for the training
"""
import sys
from multiprocessing import Pool
from os import environ, system
from os.path import join
from subprocess import Popen

from ax.service.ax_client import AxClient
from ax.service.utils.instantiation import ObjectiveProperties
from torch import device

from airfoil_shape_optimization.generate_airfoil import AirfoilGenerator
from airfoil_shape_optimization.utils import create_run_directories, load_force_coefficients


def set_openfoam_bashrc(case_path: str) -> None:
    # taken from: https://github.com/JanisGeise/drlfoam/blob/mb_drl/examples/debug.py
    # check if the path to bashrc was already added
    with open(f"{case_path}/Allrun.pre", "r") as f:
        check = [True for line in f.readlines() if line.startswith("# source bashrc")]

    command = ". /usr/lib/openfoam/openfoam2412/etc/bashrc"
    # if not then add
    if not check:
        system(f"sed -i '5i # source bashrc for OpenFOAM \\n{command}' {case_path}/Allrun.pre")
        system(f"sed -i '4i # source bashrc for OpenFOAM \\n{command}' {case_path}/Allrun")
        system(f"sed -i '4i # source bashrc for OpenFOAM \\n{command}' {case_path}/Allclean")


def execute_openfoam(path: str, script: str):
    Popen([f"./{script}"], cwd=path).wait(timeout=1e4)


def run_optimization(settings: dict) -> None:
    # parallel execution not yet supported
    settings["N_simulations"] = 1
    settings["N_runner"] = 1

    # create copies of the base case
    dirs = [join(settings["train_path"], f"trial_{d}") for d in range(settings["N_simulations"])]
    create_run_directories(settings["base_simulation"], dirs)

    # instantiate airfoil generator class
    airfoil_generator = AirfoilGenerator(x_stop=settings["chord"])

    # initialize Ax TODO: make parameter list from settings dict more efficiently, define type float etc.
    parameters = [{"name": f"{k}", "type": "range", "bounds": settings[k]} for k in
                  ["f_max", "t_max", "xf", "KR", "N1", "N2"]]

    ax = AxClient(random_seed=0, torch_device=device("cpu"))
    ax.create_experiment(name="experiment", parameters=parameters, overwrite_existing_experiment=True,
                         objectives={"loss": ObjectiveProperties(minimize=True)})

    # execute the training
    for t in range(settings["N_trials"]):
        print(f"Starting trial {t}.")

        # sample next CST parameters, currently only sequentiell execution is supported
        airfoils, trial_index = ax.get_next_trial()

        # generate airfoils from the predicted parameters and write the STL files
        for d in range(len(dirs)):
            airfoil_generator.generate_airfoil(airfoils["N1"], airfoils["N2"], airfoils["KR"], airfoils["f_max"],
                                               airfoils["xf"], airfoils["t_max"], airfoil_name=f"airfoil",
                                               write_path=join(dirs[d], "constant", "triSurface"))

            # add the path to OpenFOAN bashrc if executed from IDE
            set_openfoam_bashrc(dirs[d])

        # TODO: implement OOP once it works
        # execute simulation
        with Pool(min(settings["N_runner"], len(dirs))) as pool:
            pool.starmap(execute_openfoam, [(d, "Allrun") for d in dirs])

        # fetch data TODO: account for crashed simulations, crashed meshing etc.
        coefficients = [load_force_coefficients(simulation) for simulation in dirs]

        # compute objective function: maximize cl, minimize cd and pitching moment, here just for testing purposes
        c1, c2, c3 = 0.5, 0.4, 0.1
        objective = [c1 * c["cx"] + c2 / c["cy"] + c3 * c["cm_pitch"] for c in coefficients]

        # evaluate the trial, we only have a single trial so take the first entry of the list
        ax.complete_trial(trial_index=trial_index, raw_data={"loss": objective[0]})

        # clean the cases
        with Pool(min(settings["N_runner"], len(dirs))) as pool:
            pool.starmap(execute_openfoam, [(d, "Allclean") for d in dirs])

        # write a log file or pt file containing the settings, coefficients, objective etc.
    print(ax.get_best_parameters())


if __name__ == "__main__":
    setup = {
        # boundaries for CSM parameters
        "f_max": [0.01, 0.05],          # max. camber
        "t_max": [0.075, 0.1],           # max. thickness
        "xf": [0.35, 0.5],               # position of max. camber
        "KR": [0.35, 0.75],               # shape parameter for thickness distribution
        "N1": [0.48, 0.52],               # shape parameter for leading edge
        "N2": [0.98, 1.02],               # shape parameter for trailing edge

        # IC TODO: adjust in simulation setup based on these values
        "Ma": 0.1,                      # Mach number
        "Re": 3e5,               # Reynolds number
        "compute_BC": "U",       # weather to compute initial conditions based on U or Ma
        "U_inf": 20,            # free stream velocity
        "Tu": 0.01,             # turbulence level
        "rho_inf": 1,           # free stream density
        "p_inf": 1,           # free stream pressure
        "T_inf": 273,           # free stream temperature
        "chord": 0.15,          # chord length      TODO: parameterize meshing based on chord

        # settings for optimization
        "N_trials": 15,
        # TODO: sequentiell execution only at the moment
        # "N_runner": 1,
        # "N_simulations": 1,
        "base_simulation": "base_simulation",
        "train_path": "execute_training",

        "alpha_target": 0,              # target angle of attack at design point
        "alpha": [-2, 5],              # angle of attack range in which the airfoil should perform well
        "design_param": "alpha",        # optimize airfoil for AOA or C_L
        "cl_target": None,              # target C_L at design point
        "cl": None,                     # C_L range in which the airfoil should perform well
    }
    # add the path to OpenFOAM bashrc when executing from IDE
    environ["WM_PROJECT_DIR"] = "/usr/lib/openfoam/openfoam2412"
    sys.path.insert(0, environ["WM_PROJECT_DIR"])

    # execute the optimization
    run_optimization(setup)
