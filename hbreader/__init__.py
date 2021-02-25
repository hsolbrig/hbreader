import datetime
import json
import os
import ssl
import time
from dataclasses import dataclass
from io import StringIO
from typing import Union, Optional, Callable, IO, TextIO, cast, ClassVar
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit, quote
from urllib.request import Request, urlopen

__all__ = ['FileInfo', 'default_str_tester', 'hbopen', 'hbread']


class Pathilizer(str):

    def __str__(self):
        return self._strifier(self)


@dataclass
class FileInfo:
    source_file: Optional[str] = None
    source_file_date: Optional[str] = None
    source_file_size: Optional[int] = None
    base_path: Optional[str] = None
    rel_offset: ClassVar[Optional[str]] = None      # Used where you don't want full paths showing up

    def __post_init__(self):
        self._locked = True

    def clear(self) -> 'FileInfo':
        self.source_file = self.source_file_date = self.source_file_size = self.base_path = None
        return self

    def __setattr__(self, key, value):
        # As it is sort of easy to mistype some of the variables above, we "lock" the resource
        if getattr(self, '_locked', False) and key not in self.__dict__:
            raise AttributeError(f'No {key} variable')
        if value is not None and key in ('source_file', 'base_path'):
            value = Pathilizer(value)
            value._strifier = lambda s: str(os.path.relpath(s, self.rel_offset)) if self.rel_offset else s
        return super().__setattr__(key, value)


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

    # coerce  everything else into a string
    if callable(getattr(source, 'decode', None)):
        # bytes or bytearray
        return source.decode()

    # str-able
    return str(source)


def _wrapped_close(fp: TextIO) -> None:
    native_closer = getattr(fp, 'native_closer', None)
    if native_closer:
        fp.close = native_closer
        delattr(fp, 'native_closer')
    if hasattr(fp, 'native_reader'):
        fp.read = fp.native_reader
        delattr(fp, 'native_reader')
        delattr(fp, 'decoder')
    fp.close()


def _auto_decode(fp: IO, nbytes: Optional[int] = None) -> str:
    # We have a file opened in binary mode and haven't formally established a decoder.
    # We may need as many as four bytes to determine the encoding.
    # TODO: should the BOM (if present) count in nbytes?
    if not fp.decoder:
        if nbytes and nbytes < 4:
            # Nothing we can do if they're asking for less than 4 bytes
            data = fp.native_reader(nbytes)
            return data.decode() if data else data
        # Use the BOM to figure out what is toing on.  If no BOM, we always go to UTF-8
        bom = fp.native_reader(4)
        if len(bom) < 4:
            return bom.decode(fp.decoder if fp.decoder else 'utf-8')
        fp.decoder = json.detect_encoding(bom)
        if nbytes is None:
            return (bom + fp.native_reader()).decode(fp.decoder)
        else:
            return (bom + fp.native_reader(nbytes - 4)).decode(fp.decoder)
    else:
        return fp.native_reader(nbytes).decode(fp.decoder)



def _to_textio(fp: IO, mode: str, read_codec: str) -> TextIO:
    if 'b' in mode:
        fp = cast(TextIO, fp)
        # TODO: FIx me
        fp.decoder = read_codec
        fp.native_reader = fp.read
        fp.read = lambda *args: _auto_decode(fp, *args)
    if getattr(fp, 'native_closer', None):
        fp.native_closer = fp.close
        fp.close = lambda *a: _wrapped_close(fp)
    return fp


def hbopen(source: Union[str, bytes, bytearray, IO],
           open_info: Optional[FileInfo] = None,
           base_path: Optional[str] = None,
           accept_header: Optional[str] = None,
           is_actual_data: Optional[Callable[[str], bool]] = default_str_tester,
           read_codec: str = None) -> TextIO:
    """
    Return an open IO representation of source
    :param source: anything that can be construed to be a string, a URL, a file name or an open file handle
    :param open_info: what we learned about source in the process of converting it
    :param base_path: Base to use if source is a relative URL or file name
    :param accept_header: Accept header to use if it turns out to be a URL
    :param is_actual_data: Function to differentiate plain text from URL or file name
    :param read_codec: Name of codec to use if bytes being read. (URL only)
    :return: TextIO representation of open file
    """
    source_as_str = _try_stringify(source, is_actual_data)
    if source_as_str is not None:
        if open_info:
            open_info.source_file = ""
            open_info.source_file_size = len(source_as_str)
            open_info.source_file_date = str(datetime.datetime.now())
            open_info.base_path = ""
        return StringIO(source_as_str)

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
            req = Request(quote(url, '/:'))
            if accept_header:
                req.add_header("Accept", accept_header)
            try:
                response = urlopen(req, context=ssl._create_unverified_context())
            except HTTPError as e:
                # This is here because the message out of urllib doesn't include the file name
                e.msg = f"{e.filename}"
                raise e
            if open_info:
                open_info.source_file = response.url
                open_info.source_file_date = response.headers['Last-Modified']
                if not open_info.source_file_date:
                    open_info.source_file_date = response.headers['Date']
                open_info.source_file_size = response.headers['Content-Length']
                parts = urlsplit(response.url)
                open_info.base_path = urlunsplit((parts.scheme, parts.netloc, os.path.dirname(parts.path),
                                                 parts.query, None))
            # Auto convert byte stream to
            return _to_textio(response, response.fp.mode, read_codec)

        else:
            # source is a file name
            if not base_path:
                fname = os.path.abspath(source)
            else:
                fname = source if os.path.isabs(source) else os.path.abspath(os.path.join(base_path, source))
            f = open(fname, encoding=read_codec if read_codec else 'utf-8')
            if open_info:
                open_info.source_file = fname
                fstat = os.fstat(f.fileno())
                open_info.source_file_date = time.ctime(fstat.st_mtime)
                open_info.source_file_size = fstat.st_size
                open_info.base_path = os.path.dirname(fname)
            return _to_textio(f, f.mode, read_codec)

    else:
        # Source is an open file handle
        if open_info:
            open_info.source_file = source.name
            if getattr(source, 'fileno', None):
                fstat = os.fstat(source.fileno())
                open_info.source_file_date = time.ctime(fstat.st_mtime)
                open_info.source_file_size = fstat.st_size
            else:
                open_info.source_file_date = str(datetime.datetime.now())
            open_info.base_path = os.path.dirname(source.name)
        return _to_textio(source, source.mode, read_codec)


def hbread(source: Union[str, bytes, bytearray, IO],
           open_info: Optional[FileInfo] = None,
           base_path: Optional[str] = None,
           accept_header: Optional[str] = None,
           is_actual_data: Optional[Callable[[str], bool]] = default_str_tester,
           read_codec: str = None) -> str:
    """
    Return the string represented by source
    :param source: anything that can be construed to be a string, a URL, a file name or an open file handle
    :param open_info: what we learned about source in the process of converting it
    :param base_path: Base to use if source is a relative URL or file name
    :param accept_header: Accept header to use if it turns out to be a URL
    :param is_actual_data: Function to differentiate plain text from URL or file name
    :param read_codec: decoder to use for non-ascii data
    :return: String represented by the source
    """
    source_as_str = _try_stringify(source, is_actual_data)
    if source_as_str is not None:
        if open_info:
            open_info.source_file_size = len(source)
        return source_as_str
    with hbopen(source, open_info, base_path, accept_header, is_actual_data, read_codec) as f:
        return f.read()
