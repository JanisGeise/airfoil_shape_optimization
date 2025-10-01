"""
    execute the simulation for the final airfoil found in the optimization
"""
import sys
import torch as pt

from os import environ
from os.path import join

from airfoil_shape_optimization.data_loader import DataLoader
from airfoil_shape_optimization.generate_airfoil import AirfoilGenerator
from airfoil_shape_optimization.local_execution import LocalExecuter
from airfoil_shape_optimization.modify_simulation_setup import ModifySimulationSetup
from airfoil_shape_optimization.utils import create_run_directories


if __name__ == "__main__":
    # paths to the training directory
    train_path = join("..", "execute_training")
    validation_path = join(train_path, "validation_run")

    # add the path to OpenFOAM bashrc when executing from IDE
    environ["WM_PROJECT_DIR"] = "/usr/lib/openfoam/openfoam2412"
    sys.path.insert(0, environ["WM_PROJECT_DIR"])

    # chord length
    chord = 0.15

    # parameters for polar computation
    alpha_range = [-5, 10]
    delta_alpha = 0.25
    alpha_target = 0

    # end time of the simulation
    end_time = 3500

    # create the simulation setup
    create_run_directories(join("..", "base_simulation"), validation_path)

    # generate the airfoil based on the final results of the optimization
    final_params = pt.load(join(train_path, "results_final_parameters.pt"), weights_only=False)[0]
    airfoil_generator = AirfoilGenerator(x_stop=chord)
    airfoil_generator.generate_airfoil(final_params["N1"], final_params["N2"], final_params["KR"],
                                       final_params["f_max"], final_params["xf"], final_params["t_max"],
                                       airfoil_name=f"airfoil",
                                       write_path=join(validation_path, "constant", "triSurface"))

    # set IC conditions of the simulation
    simulation = ModifySimulationSetup(validation_path, 0.01, 3e5, chord, 20,
                                       0.1, "U", 273, 1)
    simulation.set_inflow_conditions()
    simulation.set_endTime(end_time)

    # initialize the executer
    executer = LocalExecuter(validation_path, 1)

    # initialize dataloader
    dataloader = DataLoader(validation_path, 0.4, alpha_target, alpha_range)

    for idx, alpha in enumerate(pt.arange(alpha_range[0], alpha_range[1] + delta_alpha, delta_alpha)):
        print(f"Starting computation for alpha = {'{:.2f}'.format(alpha.item())} deg.")

        # map the field from previous alpha as initialization to new alpha to improve convergence
        if idx > 0:
            simulation.initialize_new_aoa()

        # execute simulation
        executer.run_simulation()

    # write coefficients to a polar file
    _ = dataloader.evaluate_trial(0, validation_path)

    print("Finished validation run.")
