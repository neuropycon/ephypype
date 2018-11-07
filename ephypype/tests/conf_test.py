import pytest
import tempfile
import os


@pytest.fixture(scope="module")
def change_wd():
    """Create temporary directory"""

    tmp_dir = tempfile.mkdtemp()
    os.chdir(tmp_dir)
