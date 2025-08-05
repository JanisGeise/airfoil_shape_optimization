"""
    handles everything concerning the execution of OpenFOAM
"""
from abc import ABC, abstractmethod
from os import system


class Executer(ABC):
    def __init__(self, path_OF: str = "/usr/lib/openfoam/openfoam2412/etc/bashrc"):
        self._path_of = path_OF

    def set_openfoam_bashrc(self, simulation_path: str, pre_run_script: str = "Allrun.pre",  run_script: str = "Allrun",
                            clean_script: str = "Allclean", map_fields_script: str = "mapFields") -> None:
        # taken from: https://github.com/JanisGeise/drlfoam/blob/mb_drl/examples/debug.py
        # check if the path to bashrc was already added
        with open(f"{simulation_path}/{pre_run_script}", "r") as f:
            check = [True for line in f.readlines() if line.startswith("# source bashrc")]

        command = f". {self._path_of}"
        # if not then add
        if not check:
            system(f"sed -i '5i # source bashrc for OpenFOAM \\n{command}' {simulation_path}/{pre_run_script}")
            system(f"sed -i '4i # source bashrc for OpenFOAM \\n{command}' {simulation_path}/{run_script}")
            system(f"sed -i '4i # source bashrc for OpenFOAM \\n{command}' {simulation_path}/{clean_script}")
            system(f"sed -i '4i # source bashrc for OpenFOAM \\n{command}' {simulation_path}/{map_fields_script}")

    @abstractmethod
    def run_simulation(self):
        pass

    @abstractmethod
    def clean_simulation(self):
        pass

    @abstractmethod
    def set_initial_fields(self):
        pass

    @abstractmethod
    def _execute(self, directory: str, script: str):
        pass


if __name__ == "__main__":
    pass
