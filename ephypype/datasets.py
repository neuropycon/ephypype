"""Functions to fetch online data."""

# Authors: Mainak Jas <mainakjas@gmail.com>
#
# License: BSD (3-clause)

import os
import time
import shutil
import zipfile

from tqdm import tqdm
from urllib import parse, request


def fetch_omega_dataset(base_path):
    src_url = ('https://www.dropbox.com/sh/feqtjna1ymok445/'
               'AACStCwNgIlG3VcePkkTALgBa?dl=1')

    data_path = os.path.join(base_path, 'sample_BIDS_omega')
    target = os.path.join(base_path, 'sample_BIDS_omega.zip')

    if not os.path.exists(data_path):
        if not os.path.exists(target):
            _fetch_file(src_url, target)
        zf = zipfile.ZipFile(target, 'r')
        print('Extracting files. This may take a while ...')
        zf.extractall(path=data_path)
        os.remove(target)
    return os.path.abspath(data_path)


def fetch_ieeg_dataset(base_path):
    src_url = ('https://www.dropbox.com/s/njqtyk8j8bzdz8s/'
               'SubjectUCI29_data.mat?dl=1')

    data_path = os.path.join(base_path, 'ieeg')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    target = os.path.join(data_path, 'SubjectUCI29_data.mat')
    if not os.path.exists(target):
        _fetch_file(src_url, target)
        print('Downloading files ...')
    return os.path.abspath(data_path)


def fetch_erpcore_dataset(base_path):
    src_url = ('https://www.dropbox.com/sh/alcgilgobduusv0/'
               'AADoXFMCxRAwcMlLJ7zVS7q8a?dl=1')

    data_path = os.path.join(base_path, 'ERP_CORE')
    target = os.path.join(base_path, 'ERP_CORE.zip')

    if not os.path.exists(data_path):
        if not os.path.exists(target):
            _fetch_file(src_url, target)
        zf = zipfile.ZipFile(target, 'r')
        print('Extracting files. This may take a while ...')
        zf.extractall(path=data_path)
        os.remove(target)
    return os.path.abspath(data_path)


def _fetch_file(url, file_name, resume=True, timeout=30.):
    """Load requested file, downloading it if needed or requested.

    Parameters
    ----------
    url: string
        The url of file to be downloaded.
    file_name: string
        Name, along with the path, of where downloaded file will be saved.
    resume: bool, optional
        If true, try to resume partially downloaded files.
    timeout : float
        The URL open timeout.
    """
    # Adapted from MNE version < 0.24:
    temp_file_name = file_name + ".part"
    try:
        # Check file size and displaying it alongside the download url
        # this loop is necessary to follow any redirects
        for _ in range(10):  # 10 really should be sufficient...
            u = request.urlopen(url, timeout=timeout)
            try:
                last_url, url = url, u.geturl()
                if url == last_url:
                    file_size = int(
                        u.headers.get('Content-Length', '1').strip())
                    break
            finally:
                u.close()
                del u
        else:
            raise RuntimeError('Too many redirects')

        # Triage resume
        if not os.path.exists(temp_file_name):
            resume = False
        if resume:
            with open(temp_file_name, 'rb', buffering=0) as local_file:
                local_file.seek(0, 2)
                initial_size = local_file.tell()
            del local_file
        else:
            initial_size = 0
        # This should never happen if our functions work properly
        if initial_size > file_size:
            raise RuntimeError('Local file is larger than remote '
                               'file , cannot resume download')
        elif initial_size == file_size:
            # This should really only happen when a hash is wrong
            # during dev updating
            print('Local file appears to be complete (file_size == '
                  'initial_size == %s)' % (file_size,))
        else:
            # Need to resume or start over
            scheme = parse.urlparse(url).scheme
            if scheme not in ('http', 'https'):
                raise NotImplementedError('Cannot use %s' % (scheme,))
            _get_http(url, temp_file_name, initial_size, file_size, timeout)

        shutil.move(temp_file_name, file_name)
        print('File saved as %s.\n' % file_name)
    except Exception:
        os.error('Error while fetching file %s.'
                 ' Dataset fetching aborted.' % url)
        raise


def _get_http(url, temp_file_name, initial_size, file_size, timeout):
    """Safely (resume a) download to a file from http(s)."""
    # Actually do the reading
    req = request.Request(url)
    if initial_size > 0:
        req.add_header('Range', "bytes=%s-" % (initial_size,))
        try:
            response = request.urlopen(req, timeout=timeout)
            content_range = response.info().get('Content-Range')
            if (content_range is None or not content_range.startswith(
                    'bytes %s-' % (initial_size,))):
                raise IOError('Server does not support resuming')
        except Exception:
            # A wide number of errors can be raised here. HTTPError,
            # URLError... I prefer to catch them all and rerun without
            # resuming.
            return _get_http(
                url, temp_file_name, 0, file_size, timeout)
    else:
        response = request.urlopen(req, timeout=timeout)
    total_size = int(response.headers.get('Content-Length', '1').strip())
    if initial_size > 0 and file_size == total_size:
        print('Resuming download failed (resume file size '
              'mismatch). Attempting to restart downloading the '
              'entire file.')
        initial_size = 0
    total_size += initial_size
    if total_size != file_size:
        raise RuntimeError('URL could not be parsed properly '
                           '(total size %s != file size %s)'
                           % (total_size, file_size))
    mode = 'ab' if initial_size > 0 else 'wb'

    chunk_size = 8192  # 2 ** 13
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(temp_file_name, mode) as local_file:
        while True:
            t0 = time.time()
            chunk = response.read(chunk_size)
            dt = time.time() - t0
            if dt < 0.005:
                chunk_size *= 2
            elif dt > 0.1 and chunk_size > 8192:
                chunk_size = chunk_size // 2
            if not chunk:
                break
            data_size = local_file.write(chunk)
            progress_bar.update(data_size)
    progress_bar.close()
