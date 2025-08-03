"""
    executer class for local execution
"""
from subprocess import Popen
from multiprocessing import Pool
from typing import Union

from .execution import Executer


class LocalExecuter(Executer):
    def __init__(self, dirs: list, n_runner: int = 1, timeout: Union[int, float] = 1e4):
        super().__init__()
        self._dirs = dirs
        self._timeout = timeout
        self._n_runner = n_runner

        # names of the shell scripts
        self._run_script = "Allrun"
        self._pre_run_script = "Allrun.pre"
        self._clean_script = "Allclean"

        # add the path of OpenFOAM to bashrc
        for d in dirs:
            self.set_openfoam_bashrc(d, self._pre_run_script, self._run_script, self._clean_script)

    def run_simulation(self) -> None:
        # execute simulation, don't use Pool() in case of seriell execution since this crashes the debugger...
        if self._n_runner == 1:
            for d in self._dirs:
                self._execute(d, self._run_script)
        else:
            with Pool(min(self._n_runner, len(self._dirs))) as pool:
                pool.starmap(self._execute, [(d, self._run_script) for d in self._dirs])

    def clean_simulation(self) -> None:
        # clean simulation, don't use Pool() in case of seriell execution since this crashes the debugger...
        if self._n_runner == 1:
            for d in self._dirs:
                self._execute(d, self._clean_script)
        else:
            with Pool(min(self._n_runner, len(self._dirs))) as pool:
                pool.starmap(self._execute, [(d, self._clean_script) for d in self._dirs])

    def _execute(self, directory: str, script: str) -> None:
        Popen([f"./{script}"], cwd=directory).wait(timeout=self._timeout)


if __name__ == "__main__":
    pass
