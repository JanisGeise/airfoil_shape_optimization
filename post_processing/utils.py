"""
    helper functions
"""
import pandas as pd

from glob import glob
from os.path import join


def load_residuals(load_path, patch_name: str = "airfoil") -> pd.DataFrame:
    names = ["t", "ReThetat_solver", "ReThetat_initial", "ReThetat_final", "ReThetat_iters", "ReThetat_converged", 
             "U_solver", "Ux_initial", "Ux_final", "Ux_iters",	"Uz_initial", "Uz_final", "Uz_iters", "U_converged", 
             "gammaInt_solver", "gammaInt_initial", "gammaInt_final", "gammaInt_iters", "gammaInt_converged", 
             "k_solver", "k_initial", "k_final", "k_iters", "k_converged", 
             "omega_solver", "omega_initial", "omega_final", "omega_iters", "omega_converged",
             "p_solver", "p_initial", "p_final", "p_iters", "p_converged"]
    
    dirs = sorted(glob(join(load_path, "postProcessing", "solverInfo", "0")), key=lambda x: float(x.split("/")[-1]))
    _solverInfo = [pd.read_csv(join(p, "solverInfo.dat"), skiprows=2, sep=r"\s+", header=None, names=names) for p in dirs]

    if len(_solverInfo) == 1:
        _solverInfo = _solverInfo[0]
    else:
        _solverInfo = pd.concat(_solverInfo)
        
    _solverInfo.reset_index(inplace=True, drop=True)

    return _solverInfo


def load_yplus(load_path, patch_name: str = "airfoil") -> pd.DataFrame:
    dirs = sorted(glob(join(load_path, "postProcessing", "yPlus", "*")), key=lambda x: float(x.split("/")[-1]))
    _yplus = [pd.read_csv(join(p, "yPlus.dat"), sep=r"\s+", comment="#", header=None, usecols=list(range(5)),
                          names=["t", "patch", "yPlus_min", "yPlus_max", "yPlus_avg"]) for p in dirs]

    if len(_yplus) == 1:
        _yplus = _yplus[0]
    else:
        _yplus = pd.concat(_yplus)

    # only keep the target patch name
    _yplus = _yplus[_yplus.patch == patch_name]

    # remove duplicates (resulting from dt < write precision) and reset the idx
    _yplus.drop_duplicates(["t"], inplace=True)
    _yplus.reset_index(inplace=True, drop=True)

    return _yplus


def load_force_coeffs(load_path) -> pd.DataFrame:
    names = ["t", "cx", "cy", "cm_pitch"]
    usecols = [0, 1, 4, 7]
    dirs = sorted(glob(join(load_path, "postProcessing", "forces", "*")), key=lambda x: float(x.split("/")[-1]))
    coeffs = [pd.read_csv(join(p, "coefficient.dat"), sep=r"\s+", comment="#", header=None, usecols=usecols, names=names)
              for p in dirs]

    if len(coeffs) == 1:
        coeffs = coeffs[0]
    else:
        coeffs = pd.concat(coeffs)

    # remove duplicates (resulting from dt < write precision) and reset the idx
    coeffs.drop_duplicates(["t"], inplace=True)
    coeffs.reset_index(inplace=True, drop=True)
    return coeffs


def compute_camber_line(x_coordinates, xf_: float, f_max_: float, t_max: float, n_points: int = 1000, c: float = 0.15):
    # use parabolic spline to compute camber line
    # f_max_ *= c
    # xf_ *= c
    x_coordinates /= c
    # a = 1 / xf^2 * f_max
    a = 1 / pow(xf_, 2) * f_max_
    # (1 - 2 * xf) / xf^2
    b = (1 - 2 * xf_) / pow(xf_, 2)
    # y = a * (x * (1 - x) / (1 + b * x))
    _camber = a * (x_coordinates * (1 - x_coordinates) / (1 + b * x_coordinates))
    x_coordinates *= c
    return x_coordinates, _camber


def get_loss_from_log_file(load_dir: str) -> list:
    # assuming single log file per case
    with open(glob(join(load_dir, "*.log"))[0]) as f:
        lines = f.readlines()

    # the line we are interested in looks something like this:
    # [INFO 07-20 17:58:07] ax.service.ax_client: Completed trial 48 with data: {'loss': (0.140475, None)}.
    # omit the las entry, because this shows the final parameters
    lines = [line.split("{'loss':")[-1].split(", ")[0].strip(" (") for line in lines if "{'loss':" in line][:-1]
    return list(map(float, lines))


if __name__ == "__main__":
    pass
