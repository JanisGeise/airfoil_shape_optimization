"""
    compute the initial conditions for the simulation based on the setup file
"""
from math import sqrt
from typing import Union


class ComputeInitialConditions:
    def __init__(self, tu: Union[int, float], reynolds_number: Union[int, float],
                 c: Union[int, float], gamma: Union[int, float] = 1.4, R: Union[int, float] = 287.053,
                 T: Union[int, float] = 273, ma_number: Union[int, float] = None,
                 u_inf: Union[int, float] = None, rho: Union[int, float] = 1, compute_IC: str = "U"):
        self._rho = rho
        self._T = T
        self._R = R
        self._tu = tu
        self._c = c
        self._gamma = gamma
        self._c_mu = 0.09

        # check either Ma or u_inf has to be given, add logging warning / info
        if u_inf is None or compute_IC.lower() == "ma":
            print("some information regarding IC")
        if ma_number is None or compute_IC.lower() == "u":
            print("some information regarding IC")

        self._u_inf = u_inf
        self._ma_number = ma_number
        self._reynolds_number = reynolds_number

        if ma_number is None:
            self._compute_ma_number()
        elif u_inf is None:
            self._compute_inflow_velocity()

        self._compute_k()
        self._compute_omega()
        self._compute_nu()

    def _compute_k(self) -> None:
        self._k = 1.5 * (self._u_inf * self._tu)**2

    def _compute_omega(self) -> None:
        self._omega = self._k**0.5 / (self._c * self._c_mu**0.25)

    def _compute_nu(self):
        self._nu = self._rho * self._c * self._u_inf / self._reynolds_number

    def _compute_ma_number(self):
        self._ma = self._u_inf / sqrt(self._gamma * self._R * self._T)

    def _compute_inflow_velocity(self):
        return self._ma_number * sqrt(self._gamma * self._R * self._T)


if __name__ == "__main__":
    pass
