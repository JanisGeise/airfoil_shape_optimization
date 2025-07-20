"""
    generate the airfoil shape based on given CST parameters. For more information about the CST method on the used
    equations, it is referred to:

        Kulfan, Brenda. (2008). Universal Parametric Geometry Representation Method. Journal of Aircraft -
        J AIRCRAFT. 45. 142-158. 10.2514/1.29958.

    for information about airfoil design using parabolic camber lines, it is referred to literature about airfoil
    aerodynamics, e.g.:

        Schlichting, H. and Truckenbrodt, E.: Aerodynamik des Flugzeuges. 3rd ed. Vol. 1. Berlin,
        Heidelberg: Springer Berlin Heidelberg, 2001. doi: 10.1007/978-3-642-56911-1.

"""
import torch as pt

from os import makedirs
from pyvista import PolyData
from typing import Union, Tuple
from os.path import join, exists


class AirfoilGenerator:
    def __init__(self, n_points: int = 1000, cosine_distributed: bool = True, x_start: Union[int, float] = 0,
                 x_stop: Union[int, float] = 1, output: str = "stl") -> None:
        """
        class for generating the coordinates of the airfoil based on CST method

        :param n_points: number of points per side
        :param cosine_distributed:  distribution of x-coordinates, if 'False' then points are equally distributed
        :param x_start: min. x-coordinate at leading-edge
        :param x_stop: max. x-coordinate at trailing-edge
        :param output: output format for airfoil coordinates, options: "dat" or "stl"
        """
        # set the given parameters
        # TODO: check inputs, e.g. x_start < x_stop, ...
        self._write_dat_file = True if output.lower() == "dat" else False
        self._x_start = x_start
        self._x_stop = x_stop
        self._n_points = n_points
        self._cos_distributed = cosine_distributed
        self._x = None

        # initialize remaining attributes
        self._name = None
        self._write_path = None
        self._write_file = None
        self._n1 = None
        self._n2 = None
        self._kr = None
        self._f_max = None
        self._xf_max = None
        self._t_max = None
        self._y = None
        self._thickness_distribution = None
        self._camber_line = None
        self._reset_coordinates()

    def generate_airfoil(self, n1: Union[int, float], n2: Union[int, float],
                         kr: Union[int, float], f_max: Union[int, float], xf: Union[int, float],
                         t_max: Union[int, float], airfoil_name: str = "airfoil", write_path: str = ".",
                         write_file: bool = True) -> None or Tuple[pt.Tensor, pt.Tensor]:
        """
        generates the airfoil coordinates based on the given parameters

        :param n1:              first shape parameter of CST method, controls the leading edge (LE)
        :param n2:              second shape parameter of CST method, controls the trailing edge (TE)
        :param kr:              parameter defining the thickness distribution
        :param f_max:           max. camber, relative to the chord length
        :param xf:          position of max. camber, relative to the chord length
        :param t_max:           max. thickness of the airfoil, relative to the chord length
        :param airfoil_name:    name of the airfoil
        :param write_path:      path to which directory the dat file should be written to
        :param write_file:      flag for writing the dat file, if 'False', then the airfoil coordinates will be returned
        :return:                the airfoil coordinates if specified, else None
        """
        # set the attributes
        self._name = airfoil_name
        self._write_path = write_path
        self._write_file = write_file
        self._n1 = n1
        self._n2 = n2
        self._kr = kr
        self._f_max = f_max
        self._xf_max = xf
        self._t_max = t_max

        # compute thickness distribution
        self._compute_thickness_distribution()

        # compute parabolic camber line
        self._compute_camber_line()

        # compute the airfoil coordinates, scale thickness with respect to max. thickness (1st normalize to [0, 1]),
        # * 0.5 because here only a single side of airfoil
        _sf = 0.5 * self._t_max / max(self._thickness_distribution)
        _y_ss = self._thickness_distribution * _sf + self._camber_line
        _y_ps = -self._thickness_distribution * _sf + self._camber_line

        # reshape, that it is sorted from TE -> via suction side -> LE -> via pressure side -> TE, remove one of the
        # zeros (each airfoil side has a zero at LE, but we only need one)
        self._x = pt.cat([reversed(self._x)[:-1], self._x])
        self._y = pt.cat([reversed(_y_ss)[:-1], _y_ps])

        # reverse the scaling, y-gets scaled according to the scaling in x
        self._x = self._reverse_min_max_scaling(self._x)
        self._y = self._reverse_min_max_scaling(self._y)

        # either return the coordinates or write them to file
        if not self._write_file:
            _x, _y = self._x, self._y
            self._reset_coordinates()
            return _x, _y
        else:
            # create target directory
            if not exists(self._write_path):
                makedirs(self._write_path)

            if self._write_dat_file:
                self._write_data_to_dat_file()
            else:
                self._write_data_to_stl_file()

            # reset x- and y to avoid issues when generating multiple airfoils at once
            self._reset_coordinates()

    def _reset_coordinates(self) -> None:
        """
        TODO

        :return: None
        """
        # compute a linear distributing
        self._x = pt.linspace(self._x_start, self._x_stop, self._n_points)

        # compute a cosine-distributed x-coordinates if specified
        if self._cos_distributed:
            self._compute_cosine_distribution()

        # scale x-coordinates to [0, 1], required to compute the thickness distribution correctly
        self._scale_x()

        # reset y-coordinates
        self._y = None

    def _compute_cosine_distribution(self) -> None:
        """
        computes cosine distributed points based on given x-coordinates and their boundaries
        """
        self._x = (self._x_stop - self._x_start) / 2 * (1 - pt.cos(pt.pi * self._x))

    def _compute_thickness_distribution(self) -> None:
        """
        computes the coordinates of an airfoil using the CST method
        """
        # class function: C(x) = x^N1 * (1 - x)^N2
        C = pow(self._x, self._n1) * pow((1 - self._x), self._n2)

        # shape function: S(x) = (x / KR) + KR * (1-x)
        S = self._x / self._kr + self._kr * (1 - self._x)
        self._thickness_distribution = C * S

    def _compute_camber_line(self) -> None:
        """
        computes a parabolic camber line based on given x-coordinates. Refer to literature about airfoil design for
        more information.
        """
        # use parabolic spline to compute camber line
        a = 1 / pow(self._xf_max, 2) * self._f_max  # a = 1 / xf^2 * f_max
        b = (1 - 2 * self._xf_max) / pow(self._xf_max, 2)  # (1 - 2 * xf) / xf^2
        self._camber_line = a * (self._x * (1 - self._x) / (1 + b * self._x))  # y = a * (x * (1 - x) / (1 + b * x))

    def _write_data_to_stl_file(self) -> None:
        """
        write extruded airfoil coordinates to an STL file

        :return: None
        """
        _points = pt.stack([self._x, -0.1 * pt.ones(self._x.size()), self._y], dim=-1).numpy()

        # [n_points_in_face, point_index_1, point_index_2, ..., point_index_n]
        _faces = [_points.shape[0]] + list(range(_points.shape[0]))
        _airfoil = PolyData(_points, _faces).extrude((0, 0.5, 0), capping=True)
        _airfoil.save(join(self._write_path, f"{self._name}.stl"))

    def _write_data_to_dat_file(self) -> None:
        """
        write airfoil coordinates to dat file (XFOIL readable write format)

        :return: None
        """
        with open(join(self._write_path, f"{self._name}.dat"), "w") as f:
            f.write(f"{self._name}\n")
            [f.write("{:.8f}  {:.8f}\n".format(c[0], c[1])) for c in zip(self._x, self._y)]

    def _scale_x(self) -> None:
        """
        min-max-normalization of x-coordinates

        :return: None
        """
        self._x = (self._x - self._x.min()) / (self._x.max() - self._x.min())

    def _reverse_min_max_scaling(self, _data: pt.Tensor) -> pt.Tensor:
        """
        reverse the min-max-normalization using scaling with respect to x-bounds

        :param _data: data to rescale
        :return: rescaled data based on boundary values for x-coordinates
        """
        return _data * (self._x_stop - self._x_start) + self._x_start


if __name__ == "__main__":
    airfoil_generator = AirfoilGenerator(x_stop=0.15)
    airfoil_generator.generate_airfoil(0.5, 1, 0.6, 0.01, 0.25, 0.08, airfoil_name="airfoil",
                                       write_path=join("..", "base_simulation", "geometry"))
