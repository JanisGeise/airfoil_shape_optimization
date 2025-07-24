"""
    adjust the initial conditions of the numerical setup according to the settings defined in the setup file
"""
from os.path import join
from typing import Union

from .compute_initial_conditions import ComputeInitialConditions


class ModifySimulationSetup(ComputeInitialConditions):
    def __init__(self, simulation_path: str, tu: Union[int, float], reynolds_number: Union[int, float],
                 c: Union[int, float], u_inf: Union[int, float] = None, ma_number: Union[int, float] = None,
                 compute_ic: str = "U", T_inf: Union[int, float] = 273, rho_inf: Union[int, float] = 1):
        super().__init__(tu, reynolds_number, c, T=T_inf, rho=rho_inf, u_inf=u_inf, ma_number=ma_number,
                         compute_IC=compute_ic)
        self._path = simulation_path
        self._alpha = 0.0

        # base paths
        self._zero = "0.orig"
        self._constant = "constant"
        self._forces_FO = "system"

    def set_inflow_conditions(self) -> None:
        self._set_k()
        self._set_omega()
        self._set_nu()

        self._set_inflow_velocity()
        self._set_free_stream_density()

    def _set_k(self) -> None:
        self._replace_line(join(self._path, self._zero, "k"), "kInlet", "kInlet          8.557;",
                           "kInlet          {:.6f};".format(self._k))

    def _set_omega(self) -> None:
        self._replace_line(join(self._path, self._zero, "omega"), "omegaInlet", "omegaInlet      35.605;",
                           "omegaInlet      {:.6f};".format(self._omega))

    def _set_inflow_velocity(self) -> None:
        self._replace_line(join(self._path, self._zero, "U"), "Uinlet", "Uinlet          20.0;",
                           "Uinlet          {:.6f};".format(self._u_inf))

        self._replace_line(join(self._path, self._forces_FO, "FO_forces"), "Uinlet", "Uinlet          20.0;",
                           "Uinlet          {:.6f};".format(self._u_inf))

    def _set_nu(self) -> None:
        self._replace_line(join(self._path, self._constant, "transportProperties"), "nu", "nu              1e-05;",
                           "nu              {:.8e};".format(self._nu))

    def _set_free_stream_density(self) -> None:
        self._replace_line(join(self._path, self._forces_FO, "FO_forces"), "    rhoInf", "   rhoInf      1;",
                           "   rhoInf      {:.6f};".format(self._rho))

    def _set_angle_of_attack(self) -> None:
        self._replace_line(join(self._path, self._zero, "U"), "alpha", "alpha           0.0;",
                           "alpha          {:.6f};".format(self._alpha))

        self._replace_line(join(self._path, self._forces_FO, "FO_forces"), "alpha", "alpha           0.0;",
                           "alpha          {:.6f};".format(self._alpha))

    @staticmethod
    def _replace_line(pwd: str, key: str, old: str, new: str) -> None:
        with open(pwd, "r") as f:
            lines = f.readlines()

        with open(pwd, "w") as f:
            f.write("".join([line if not line.startswith(key) else line.replace(old, new) for line in lines]))

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        self._alpha = alpha
        self._set_angle_of_attack()


if __name__ == "__main__":
    pass
