"""
    adjust the initial conditions of the numerical setup according to the settings defined in the setup file
"""
import logging

from glob import glob
from os.path import join
from typing import Union
from shutil import rmtree, move
from os import remove
from math import sin, cos, pi

from .compute_initial_conditions import ComputeInitialConditions


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    force=True)


class ModifySimulationSetup(ComputeInitialConditions):
    def __init__(self, simulation_path: Union[str, list], tu: Union[int, float], reynolds_number: Union[int, float],
                 c: Union[int, float], u_inf: Union[int, float] = None, ma_number: Union[int, float] = None,
                 compute_ic: str = "U", T_inf: Union[int, float] = 273, rho_inf: Union[int, float] = 1):
        """
        modify the initial conditions of the simulation according to the defined setup

        :param simulation_path: path to the simulation directories
        :param tu: turbulence level
        :param reynolds_number: Reynolds number based on the chord length
        :param c: chord length of the airfoil; used to compute mu based on the Reynolds number, rho and inflow velocity
        :param u_inf: free-stream velocity, if 'None' then ma_number has to be given
        :param ma_number: free-stream Mach number, if 'None' then u_inf has to be given
        :param compute_ic: parameter which should be used for computing the initial conditions; either 'U' or 'Ma'
                           denoting the free-stream velocity and Mach number, respectively
        :param T_inf: free-stream temperature, used for calculation of the Mach number or inflow velocity (depending on
                      what is given)
        :param rho_inf: free-stream density, used for cl and cd calculation
        """
        super().__init__(tu, reynolds_number, c, T=T_inf, rho=rho_inf, u_inf=u_inf, ma_number=ma_number,
                         compute_IC=compute_ic)
        self._path = simulation_path if isinstance(simulation_path, list) else [simulation_path]
        self._alpha = 0.0
        self._alpha_old = 0.0
        self._end_time = 2000

        # base paths
        self._zero = "0.orig"
        self._constant = "constant"
        self._forces_FO = "system"
        self._allrun = "Allrun"

    def set_inflow_conditions(self) -> None:
        """
        modify the initial conditions of the simulation according to the defined setup

        :return: None
        """
        self._set_k()
        self._set_omega()
        self._set_tu()
        self._set_Re_theta()
        self._set_nu()

        self._set_inflow_velocity()
        self._set_free_stream_density()
        # TODO: set endtime

    def _set_k(self) -> None:
        """
        modify the turbulent kinetic energy k

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._zero, "k"), "kInlet", "kInlet          8.557;",
                               "kInlet          {:.6f};".format(self._k))

    def _set_omega(self) -> None:
        """
        modify the turbulence specific dissipation rate

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._zero, "omega"), "omegaInlet", "omegaInlet      35.605;",
                               "omegaInlet      {:.6f};".format(self._omega))

    def _set_inflow_velocity(self) -> None:
        """
        modify the inflow velocity

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._zero, "U"), "Uinlet", "Uinlet          20.0;",
                               "Uinlet          {:.6f};".format(self._u_inf))

            self._replace_line(join(p, self._forces_FO, "FO_forces"), "    Uinlet", "Uinlet          20.0;",
                               "    Uinlet          {:.6f};".format(self._u_inf))

    def _set_nu(self) -> None:
        """
        modify the dynamic viscosity

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._constant, "transportProperties"), "nu", "nu              1e-05;",
                               "nu              {:.8e};".format(self._nu))

    def _set_free_stream_density(self) -> None:
        """
        modify the density

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._forces_FO, "FO_forces"), "    rhoInf", "   rhoInf      1;",
                               "   rhoInf      {:.6f};".format(self._rho))

    def _set_angle_of_attack(self) -> None:
        """
        modify the angle of attack of the inflow velocity vector

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._zero, "U"),
                               "alpha", "alpha           {:.6f};".format(self._alpha_old),
                               "alpha           {:.6f};".format(self._alpha))

            self._replace_line(join(p, self._forces_FO, "FO_forces"),
                               "alpha", "    alpha           {:.6f};".format(self._alpha_old),
                               "    alpha           {:.6f};".format(self._alpha))

            self._replace_line(join(p, self._allrun),
                               "alpha", "alpha={:.6f}".format(self._alpha_old), "alpha={:.6f}".format(self._alpha))

    def _set_tu(self) -> None:
        """
        set the turbulence level for the kOmegaSSTLM transition model

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._zero, "gammaInt"), "internalField", "internalField   uniform 0.01;",
                               "internalField   uniform {:.6f};".format(self._tu))

    def _set_Re_theta(self) -> None:
        """
        set Re_theta for the kOmegaSSTLM transition model

        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._zero, "ReThetat"), "internalField", "internalField   uniform 1000;",
                               "internalField   uniform {:.6f};".format(self._re_theta))

    def initialize_new_aoa(self):
        # TODO: replace with new AoA in file manipulation
        logger.info("Initializing new AoA.")
        _new_AoA = f"( {self._u_inf * cos(self._alpha * pi/180)} 0 {self._u_inf * sin(self._alpha * pi/180)} )"

        # then modify the inlet velocity vector TODO: loop over all paths, change endtime
        _files = join(self._path[0], "processor*", "*00")
        for p in glob(_files):
            with open(join(p, "U"), "rb") as file:
                lines = file.readlines()

            # check if the processor contains any domain boundaries
            check = [idx for idx, l in enumerate(lines) if b"        freestreamValue " in l][0]

            # if so, replace with new AoA and write back to file
            if b" uniform" in lines[check]:
                old = lines[check].split(b"uniform ")[-1].split(b";")[0]
                lines[check] = lines[check].replace(old, _new_AoA.encode("utf-8"))

                with open(join(p, "U"), "wb") as f_out:
                    f_out.writelines(lines)

            # reset time in processor*/*/uniform/time
            with open(join(p, "uniform", "time"), "rb") as file:
                lines = file.readlines()

            # get the lines to replace
            check = [idx for idx, l in enumerate(lines) if l.startswith(b"value") or l.startswith(b"name") or
                     l.startswith(b"index")]
            for c in check:
                lines[c] = lines[c].replace(str(self._end_time).encode("utf-8"), "0".encode("utf-8"))

            with open(join(p, "uniform", "time"), "wb") as f_out:
                f_out.writelines(lines)

            # overwrite 0 directory with last time step
            rmtree(join("/".join(p.split("/")[:-1]), "0"))
            move(p, join("/".join(p.split("/")[:-1]), "0"))

        # remove log files of the simulation, so we can execute the next one
        [remove(l) for l in glob(join(self._path[0], "log.*"))]

        # finally update the end_time, since we now don't need 2000 iterations anymore
        self.set_endTime(500)

    @staticmethod
    def _replace_line(pwd: str, key: str, old: str, new: str) -> None:
        """
        replace a line in a file with another line

        :param pwd: path to the file
        :param key: keyword identifying the start of the line
        :param old: old line
        :param new: new line
        :return: None
        """
        with open(pwd, "r") as f:
            lines = f.readlines()

        with open(pwd, "w") as f:
            f.write("".join([line if not line.strip().startswith(key) else line.replace(old, new) for line in lines]))

    @property
    def alpha(self) -> float:
        """
        angle of attack

        :return: float
        """
        return self._alpha

    @alpha.setter
    def alpha(self, alpha) -> None:
        """
        set a new angle of attack and modify the forces function object and inflow velocity vector accordingly

        :param alpha: new angle of attack
        :return: None
        """
        self._alpha_old = self._alpha
        self._alpha = alpha
        self._set_angle_of_attack()

    def set_endTime(self, end_time: int = 3500) -> None:
        """
        overwrite the end time of the simulation

        :param end_time: new end time of the simulation
        :return: None
        """
        for p in self._path:
            self._replace_line(join(p, self._forces_FO, "controlDict"), "endTime", f"endTime         {self._end_time};",
                               "endTime         {:.0f};".format(end_time))

        # update the current end_time
        self._end_time = end_time


if __name__ == "__main__":
    pass
