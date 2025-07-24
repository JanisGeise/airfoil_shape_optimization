"""
    execute the simulation for the final airfoil found in the optimization
"""

import sys
import torch as pt

from os import environ
from os.path import join
from subprocess import Popen

from airfoil_shape_optimization.generate_airfoil import AirfoilGenerator
from airfoil_shape_optimization.utils import create_run_directories
from main import set_openfoam_bashrc

if __name__ == "__main__":
    # paths to the training directory
    train_path = join("..", "execute_training")
    validation_path = join(train_path, "validation_run")

    # chord length
    chord = 0.15

    # create the simulation setup
    create_run_directories(join("..", "base_simulation"), validation_path)

    # generate the airfoil based on the final results of the optimization
    final_params = pt.load(join(train_path, "results_final_parameters.pt"), weights_only=False)[0]
    airfoil_generator = AirfoilGenerator(x_stop=chord)
    airfoil_generator.generate_airfoil(final_params["N1"], final_params["N2"], final_params["KR"],
                                       final_params["f_max"], final_params["xf"], final_params["t_max"],
                                       airfoil_name=f"airfoil",
                                       write_path=join(validation_path, "constant", "triSurface"))

    # add the path to OpenFOAM bashrc when executing from IDE
    environ["WM_PROJECT_DIR"] = "/usr/lib/openfoam/openfoam2412"
    sys.path.insert(0, environ["WM_PROJECT_DIR"])

    # add the path to OpenFOAN bashrc if executed from IDE
    set_openfoam_bashrc(validation_path)

    # execute simulation
    Popen([f"./Allrun"], cwd=validation_path).wait(timeout=1e4)
    print("Finished validation run.")
