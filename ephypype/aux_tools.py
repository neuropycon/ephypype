"""Aux functions"""

# Authors: Dmitrii Altukhov <daltuhov@hse>
#          Annalisa Pascarella <a.pascarella@iac.cnr.it>
#
# License: BSD (3-clause)

from contextlib import contextmanager
import os


# Define a context manager to suppress stdout and stderr.

class suppress_stdout_stderr(object):  # noqa
    """Context manager.

    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        """Enter context."""
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        """Exit context."""
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])


@contextmanager
def nostdout():
    """Kill standart output.

    Example
    -------
    >> with nostdout():
           raw = mne.io.Raw(fname)

    """
    # -- Works both in python2 and python3 -- #
    import sys

    try:
        from io import StringIO
    except ImportError:
        from io import StringIO
    # --------------------------------------- #
    save_stdout = sys.stdout
    sys.stdout = StringIO()
    yield
    sys.stdout = save_stdout


def _get_freq_band(freq_band_name, freq_band_names, freq_bands):
    """Get frequency band."""
    if freq_band_name in freq_band_names:
        print(freq_band_name)
        print(freq_band_names.index(freq_band_name))

        return freq_bands[freq_band_names.index(freq_band_name)]
    return None


def _parse_string(string, token):
    """Find a token in a string.

    Parameters
    ----------
        string : str
            String to parse
        token : list of str
            List of token

    Returns
    -------
        return_string : str
            The token if contained in the string
    """
    if not isinstance(token, list):
        raise ValueError('{} has to be a list of string'.format(token))
    for t in token:
        if string.find(t) > -1:
            return t
        else:
            return_string = ''

    return return_string
