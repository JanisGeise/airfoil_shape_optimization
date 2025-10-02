"""
Create a logfile for the optimization
"""
from os.path import join


class LogFile:
    def __init__(self, write_path: str, name: str = "log.optimization", header=None):
        self._path = write_path
        self._name = name

        # use the standard header if nothing is specified
        if header is None:
            header = ("trial\tf_max\t\tt_max\t\txf\t\t\tKR\t\t\tN1\t\t\tN2\t\t\tobjective\n-----\t--------\t--------\t"
                      "--------\t--------\t--------\t--------\t---------\n")
        self._header = header

        # write the header
        self._write_header()

    def _write_header(self) -> None:
        """
        Writes he file header.

        :return: None
        """
        with open(join(self._path, self._name), "w") as log_file:
            log_file.write(self._header)

    def update(self, msg: str) -> None:
        """
        Appends the msg string to the log file.

        :param msg: Message to append to file.
        :return: None
        """
        with open(join(self._path, self._name), "a") as log_file:
            log_file.write(msg)


if __name__ == "__main__":
    pass
