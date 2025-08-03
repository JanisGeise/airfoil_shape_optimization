"""
    compute the initial conditions for the simulation based on the setup file
"""
import logging
from math import sqrt
from typing import Union


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    force=True)


class ComputeInitialConditions:
    def __init__(self, tu: Union[int, float], reynolds_number: Union[int, float],
                 c: Union[int, float], gamma: Union[int, float] = 1.4, R: Union[int, float] = 287.053,
                 T: Union[int, float] = 273, ma_number: Union[int, float] = None,
                 u_inf: Union[int, float] = None, rho: Union[int, float] = 1, compute_IC: str = "U"):
        """
        compute the initial conditions of the simulation according to the defined setup

        the initial conditions for the turbulence properties are computed according to:

                https://www.openfoam.com/documentation/guides/latest/doc/guide-turbulence-ras-k-omega-sst.html

        :param tu: turbulence level
        :param reynolds_number: Reynolds number based on the chord length
        :param c: chord length of the airfoil; used to compute mu based on the Reynolds number, rho and inflow velocity
        :param gamma: isentropic exponent
        :param R: ideal gas constant
        :param T: free-stream temperature, used for calculation of the Mach number or inflow velocity (depending on
                      what is given)
        :param ma_number: free-stream Mach number, if 'None' then u_inf has to be given
        :param u_inf: free-stream velocity, if 'None' then ma_number has to be given
        :param rho: free-stream density, used for cl and cd calculation
        :param compute_IC: parameter which should be used for computing the initial conditions; either 'U' or 'Ma'
                           denoting the free-stream velocity and Mach number, respectively
        """
        self._rho = rho
        self._T = T
        self._R = R
        self._tu = tu
        self._c = c
        self._gamma = gamma
        self._c_mu = 0.09

        # check either Ma or u_inf has to be given
        if u_inf is None or compute_IC.lower() == "ma":
            logging.info("Computing initial conditions based on the Mach number.")
        if ma_number is None or compute_IC.lower() == "u":
            logging.info("Computing initial conditions based on the velocity.")

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
        self._compute_Re_theta()

    def _compute_k(self) -> None:
        """
        compute the turbulent kinetic energy:

                k = 3/2 (UI)^ 2

        :return: None
        """
        self._k = 1.5 * (self._u_inf * self._tu)**2

    def _compute_omega(self) -> None:
        """
        compute the turbulence specific dissipation rate:

            omega = k^0.5 / (L * C_mu^0.25)

        with C_mu = 0.09

        :return: None
        """
        self._omega = self._k**0.5 / (self._c * self._c_mu**0.25)

    def _compute_Re_theta(self) -> None:
        """
        compute the Re_theta for the kOmegaSSTLM transition model as:

            Tu ≤ 1.3 (in percent):
                Re_theta = 1173.51 − 589.428 * Tu + 0.2196 / Tu^2

            else:

                Re_theta = 331.5 / (Tu - 0.5658)^0.671

        refer to:

            https://www.openfoam.com/documentation/guides/latest/doc/guide-turbulence-ras-k-omega-sst-lm.html

        for more information.
        It is important to note that Tu is assumed here to be in percent

        :return: None
        """
        if self._tu >= 0.013:
            self._re_theta = 1173.51 - 589.428 * (self._tu * 100) + 0.2196 / (self._tu * 100)**2
        else:
            self._re_theta = 331.5 / ((self._tu * 100) - 0.5658)**0.671

    def _compute_nu(self):
        """
        compute the required dynamic viscosity base on the Reynolds number, chord length, density and inflow velocity

        :return: None
        """
        self._nu = self._rho * self._c * self._u_inf / self._reynolds_number

    def _compute_ma_number(self):
        """
        compute the Mach number:

            Ma = U_inf / sqrt(gamma * R * T)

        :return: None
        """
        self._ma = self._u_inf / sqrt(self._gamma * self._R * self._T)

    def _compute_inflow_velocity(self):
        """
        compute the inflow velocity based on the Mach number

        :return: None
        """
        return self._ma_number * sqrt(self._gamma * self._R * self._T)


if __name__ == "__main__":
    pass
