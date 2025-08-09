"""
    helper functions
"""
import pandas as pd

from glob import glob
from os.path import join


def load_residuals(load_path, name: str = "alpha_0.00000") -> pd.DataFrame:
    # we have to read in the header separately since there is a # which causes misalignment of the columns
    with open(join(load_path, "postProcessing", "solverInfo", name, "solverInfo.dat"), "r") as f:
        lines = f.readlines()
        header_line = lines[1].lstrip("#").strip()  # Remove leading "#" and strip spaces
        _names = header_line.split()

    # now we can load the file with the correct header
    _solverInfo = pd.read_csv(join(load_path, "postProcessing", "solverInfo", name, "solverInfo.dat"), names=_names,
                              sep=r"\s+", comment="#")
    _solverInfo.drop_duplicates(["Time"], inplace=True)
    _solverInfo.reset_index(inplace=True, drop=True)

    return _solverInfo


def load_yplus(load_path, name: str = "alpha0.000000", patch_name: str = "airfoil") -> pd.DataFrame:
    _yplus = pd.read_csv(join(load_path, "postProcessing", "yPlus", name, "yPlus.dat"), sep=r"\s+", comment="#",
                         header=None, usecols=list(range(5)),
                         names=["t", "patch", "yPlus_min", "yPlus_max", "yPlus_avg"])

    # only keep the target patch name
    _yplus = _yplus[_yplus.patch == patch_name]

    # remove duplicates (resulting from dt < write precision) and reset the idx
    _yplus.drop_duplicates(["t"], inplace=True)
    _yplus.reset_index(inplace=True, drop=True)

    return _yplus


def load_force_coeffs(load_path, name: str = "alpha_0.00000") -> pd.DataFrame:
    names = ["t", "cx", "cy", "cm_pitch"]
    usecols = [0, 1, 4, 7]
    coeffs = pd.read_csv(join(load_path, "postProcessing", "forces", name, "coefficient.dat"), sep=r"\s+", comment="#",
                         header=None, usecols=usecols, names=names)

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


def load_optimization_log(load_path: str, file_name: str = "log.optimization") -> pd.DataFrame:
    names = ["trial", "f_max", "t_max", "xf", "KR", "N1", "N2", "objective"]
    return pd.read_csv(join(load_path, file_name), sep=r"\s+", comment="#", header=None, skiprows=2, names=names)


def load_polar_files(load_path: str) -> list:
    names = ["alpha", "cd", "cl", "cm_pitch"]
    return [pd.read_csv(p, sep=r"\s+", comment="#", header=None, usecols=[0, 1, 2, 3], names=names, skiprows=2)
            for p in sorted(glob(join(load_path, f"polar_trial_*.dat")),
                            key=lambda x: int(x.split("_")[-1].split(".")[0]))]


if __name__ == "__main__":
    pass
