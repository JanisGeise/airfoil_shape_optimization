"""
    helper functions
"""
from os.path import join
from shutil import copytree
from pandas import read_csv, DataFrame
import torch as pt
from typing import Union


def min_max_scaling(data: pt.Tensor) -> pt.Tensor:
    return (data - data.min()) / (data.max() - data.min())


def reverse_min_max_scaling(_x_min: Union[int, float], _x_max: Union[int, float], _data: pt.Tensor) -> pt.Tensor:
    return _data * (_x_max - _x_min) + _x_min


def create_run_directories(base_path: str, directories: Union[str, list]) -> None:
    directories = [directories] if type(directories) is str else directories
    for d in directories:
        copytree(base_path, d, dirs_exist_ok=True)


def load_force_coefficients(load_path, folder_name: str = "0") -> DataFrame:
    names = ["t", "cx", "cy", "cm_pitch"]
    pwd = join(load_path, "postProcessing", "forces", folder_name, "coefficient.dat")
    return read_csv(pwd, sep=r"\s+", comment="#", header=None, usecols=[0, 1, 4, 7], names=names).iloc[-1]


if __name__ == "__main__":
    pass
