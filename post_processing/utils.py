"""
    helper functions
"""
import pandas as pd

from glob import glob
from os.path import join


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


def load_force_coeffs(load_path, usecols=[0, 1, 4], names=["t", "cx", "cy"]) -> pd.DataFrame:
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


def compute_camber_line(x_coordinates, n_points: int = 1000, c: float = 0.15):
    # use parabolic spline to compute camber line
    # x = pt.linspace(0, 1, steps=n_points)

    # dummy values for max. camber and position of max. camber
    xf_max, f_max = 0.5, 0.005

    x_coordinates /= c
    # a = 1 / xf^2 * f_max
    a = 1 / pow(xf_max, 2) * f_max
    # (1 - 2 * xf) / xf^2
    b = (1 - 2 * xf_max) / pow(xf_max, 2)
    # y = a * (x * (1 - x) / (1 + b * x))
    _camber = a * (x_coordinates * (1 - x_coordinates) / (1 + b * x_coordinates))
    x_coordinates *= c
    return x_coordinates, _camber


if __name__ == "__main__":
    pass
