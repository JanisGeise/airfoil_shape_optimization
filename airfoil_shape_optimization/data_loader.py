"""
    handles loading of the simulation data and computation of the objective function
"""
import logging

from glob import glob
from os.path import join
from pandas import Series

from .utils import load_force_coefficients

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, simulation_path: str, cl_target: float,  alpha_target: float, alpha_range: list,
                 write_precision: int = 6):
        self._path = simulation_path
        self._cl_target = cl_target
        self._alpha_target = alpha_target
        self._alpha_min = min(alpha_range)
        self._alpha_max = max(alpha_range)
        self._coefficients = {}
        self._trial_no = 0
        self._objective = 0
        self._alpha = []
        self._header = "alpha\t\tcl  \t\tcd\t\t\tcm_pitch\n"
        self._header += "\t".join(4 * ["".join((write_precision + 2) * ["-"])])
        self._precision = "{:." + str(write_precision) + "f}"

    def evaluate_trial(self, trial_no: int, run_directory: str) -> float:
        self._trial_no = trial_no
        self._load_force_coefficients(run_directory)
        self._compute_objective()
        self._write_polar_file()

        # reset
        _obj = self._objective
        self._objective = 0

        return _obj

    def _compute_objective(self, value_not_converged: int = 10, c1: float = 0.45, c2: float = 0.25,
                           c3: float = 0.2) -> None:
        # loop over alpha and compute objective for each AoA, then compute a weighted, global objective from that
        _obj, _weight = [], []
        for a in self._alpha:
            if isinstance(self._coefficients[a], Series):
                if float(a) == self._alpha_target:
                    _obj.append((c1 * self._coefficients[a]["cx"] + c2 *
                                 abs(self._cl_target - self._coefficients[a]["cy"]) +
                                 c3 * abs(self._coefficients[a]["cm_pitch"])))
                else:
                    _obj.append(c1 * self._coefficients[a]["cx"])
            else:
                _obj.append(value_not_converged)
            _weight.append(1 - abs(self._alpha_target - float(a)) / (self._alpha_max - self._alpha_min))

        # weigh with distance to alpha_target
        self._objective = sum(w * o for w, o in zip(_weight, _obj))

    def _load_force_coefficients(self, run_directory: str) -> None:
        _directories = glob(join(run_directory, "postProcessing", "forces", "alpha_*"))
        for d in sorted(_directories, key=lambda x: float(x.split("_")[-1])):
            alpha = str(d.split("_")[-1])
            try:
                self._coefficients[alpha] = load_force_coefficients(run_directory, f"alpha_{alpha}")
            except FileNotFoundError:
                logging.warning(f"Trial {self._trial_no} is not converged.")
                self._coefficients[alpha] = []
            self._alpha.append(alpha)

    def _write_polar_file(self) -> None:
        with open(join(self._path, f"polar_trial_{self._trial_no}.dat"), "w") as file_out:
            file_out.write(f"{self._header}\n")
            for a in self._alpha:
                file_out.write(f"{self._precision.format(float(a))}\t"
                               f"{self._precision.format(self._coefficients[a]["cx"])}\t"
                               f"{self._precision.format(self._coefficients[a]["cy"])}\t"
                               f"{self._precision.format(self._coefficients[a]["cm_pitch"])}\n")

        self._coefficients = {}
        self._alpha = []


if __name__ == "__main__":
    pass
