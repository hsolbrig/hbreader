import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from typing import Union, Optional, Callable, IO, Any
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

__all__ = ['FileInfo', 'default_str_tester', 'avid_open', 'avid_read']

@dataclass
class FileInfo:
    source_file: Optional[str] = None
    source_file_date: Optional[str] = None
    source_file_size: Optional[int] = None
    base_path: Optional[str] = None

    def clear(self) -> 'FileInfo':
        self.source_file = self.source_file_date = self.source_file_size = self.base_path = None
        return self


def default_str_tester(s: str) -> bool:
    """
    Default test whether s URL, file name or just data.  This is pretty simple - if it has a c/r, a quote
    :param s: string to test
    :return: True if this is a vanilla string, otherwise try to treat it as a file name
    """
    return not s.strip() or any(c in s for c in ['\r', '\n', '\t', '  ', '"', "'"])


def _try_stringify(source: Union[str, bytes, bytearray, IO],
                   is_actual_data: Optional[Callable[[str], bool]]) -> Optional[str]:
    """
    Handle all forms of string being passed directly

    :param source: The element to decode
    :param is_actual_data: Function to differentiate text from URL or file name
    :return: string form if source was string to begin with
    """

    if isinstance(source, str):
        # Vanilla non-URL, non-File string
        return source if is_actual_data(source) else None

    if callable(getattr(source, 'read', None)):
        # File handle
        return None

    # Co-orce everything else into a string
    if callable(getattr(source, 'decode', None)):
        # bytes or bytearray
        return source.decode()

    # str-able
    return str(source)



@contextmanager
def avid_open(source: Union[str, IO],
              open_info: Optional[FileInfo] = None,
              base_path: Optional[str] = None,
              accept_header: Optional[str] = None,
              is_actual_data: Optional[Callable[[str], bool]] = default_str_tester ):
    """
    Return an open IO representation of source
    :param source: anything that can be construed to be a string, a URL, a file name or an open file handle
    :param open_info: what we learned about source in the process of converting it
    :param base_path: Base to use if source is a relative URL or file name
    :param accept_header: Accept header to use if it turns out to be a URL
    :param is_actual_data: Function to differentiate plain text from URL or file name
    :return: File like representation of source
    """
    source_as_str = _try_stringify(source, is_actual_data)
    if source_as_str is not None:
        if open_info:
            open_info.source_file_size = len(source_as_str)
        yield StringIO(source_as_str)
        return

    if isinstance(source, str):
        # source is a URL or a file name
        if open_info:
            assert open_info.source_file is None, "source_file parameter not allowed if data is a file or URL"
            assert open_info.source_file_date is None, "source_file_date parameter not allowed if data is a file or URL"
            assert open_info.source_file_size is None, "source_file_size parameter not allowed if data is a file or URL"

        if '://' in source or (base_path and '://' in base_path):
            # source is a URL
            url = source if '://' in source else urljoin(base_path + ('' if base_path.endswith('/') else '/'),
                                                         source, allow_fragments=True)
            req = Request(url)
            if accept_header:
                req.add_header("Accept", accept_header)
            try:
                response = urlopen(req)
            except HTTPError as e:
                # This is here because the message out of urllib doesn't include the file name
                e.msg = f"{e.filename}"
                raise e
            with response:
                if open_info:
                    open_info.source_file = url
                    open_info.source_file_date = response.info()['Last-Modified']
                    if not open_info.source_file_date:
                        open_info.source_file_date = response.info()['Date']
                    open_info.source_file_size = response.info()['Content-Length']
                    if not base_path:
                        parts = urlsplit(url)
                        open_info.base_dir = urlunsplit((parts.scheme, parts.netloc, os.path.dirname(parts.path),
                                                         parts.query, None))
                yield response.fp

        else:
            # source is a file name
            if not base_path:
                fname = os.path.abspath(source)
            else:
                fname = source if os.path.isabs(source) else os.path.abspath(os.path.join(base_path, source))
            f = None
            try:
                f = open(fname)
                if open_info:
                    open_info.source_file = fname
                    fstat = os.fstat(f.fileno())
                    open_info.source_file_date = time.ctime(fstat.st_mtime)
                    open_info.source_file_size = fstat.st_size
                    open_info.base_path = os.path.dirname(fname)
                yield f
            finally:
                if f is not None:
                    f.close()
    else:
        # Source is an open file handle
        yield source


def avid_read(source: Union[str, bytes, bytearray, IO, Any],
              open_info: Optional[FileInfo] = None,
              base_path: Optional[str] = None,
              accept_header: Optional[str] = None,
              is_actual_data: Optional[Callable[[str], bool]] = default_str_tester) -> str:
    """
    Return the string represented by source
    :param source: anything that can be construed to be a string, a URL, a file name or an open file handle
    :param open_info: what we learned about source in the process of converting it
    :param base_path: Base to use if source is a relative URL or file name
    :param accept_header: Accept header to use if it turns out to be a URL
    :param is_actual_data: Function to differentiate plain text from URL or file name
    :return: String represented by the source
    """
    source_as_str = _try_stringify(source, is_actual_data)
    if source_as_str is not None:
        if open_info:
            open_info.source_file_size = len(source)
        return source_as_str
    with avid_open(source, open_info, base_path, accept_header, is_actual_data) as f:
        return f.read()

