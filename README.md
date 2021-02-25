<div style="text-align: center; color: darkred"> <h1>Honey Badger Reader Don't Care</h1> </div>

![Test](https://github.com/hsolbrig/hbreader/workflows/Test/badge.svg)
![Pyversions](https://img.shields.io/pypi/pyversions/hbreader.svg)
![PyPi](https://img.shields.io/pypi/v/hbreader.svg)


**<span style="color: darkred">HBReader</span>** is a toolkit for those of us who are tired of having to use one idiom 
to open a file on a disk, a second to retrieve the same file from the web and yet another to deal with text in memory. 
**<span style="color: darkred">HBReader</span>** allows you to read:

* Files - both relative and absolute file names
* URLs - relative and absolute
* Text - data that has yet to be put in a file or has already been retrieved
* Open file-like things

## hbopen
**<span style="color: darkred">hbopen</span>** returns a text file handle for `source`
```text
def hbopen(source: Union[str, IO],
           open_info: Optional[FileInfo] = None,
           base_path: Optional[str] = None,
           accept_header: Optional[str] = None,
           is_actual_data: Optional[(str) -> bool] = default_str_tester,
           read_codec: str = 'utf-8') -> TextIO
Return an open IO representation of source :param source: anything that can be construed to be a string, a URL, a file name or an open file handle

Params:
source – anything that can be construed to be a string, a URL, a file name or an open file handle
open_info – what we learned about source in the process of converting it
base_path – Base to use if source is a relative URL or file name
accept_header – Accept header to use if it turns out to be a URL
is_actual_data – Function to differentiate plain text from URL or file name
read_codec – Name of codec to use if bytes being read (default = 'utf-8'). (URL only)

Returns:  TextIO representation of open file
```

### Examples
```python
import os
from hbreader import FileInfo, hbopen, hbread

# This removes any absolute paths from the output -- not generally used
FileInfo.rel_offset = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Open a vanilla file
metadata = FileInfo()
with hbopen('../tests/data/test data 1.txt', metadata) as f:
    print(f.read())
    print(metadata)
# I'm some friendly test data
#
# FileInfo(source_file='hbreader/tests/data/test data 1.txt', source_file_date='Wed Feb 17 17:01:09 2021', source_file_size=28, base_path='hbreader/tests/data')

# Open a file using a base address
data_file_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests/data'))
with hbopen('test data 1.txt', base_path=data_file_dir) as f:
    print(f.read())
# I'm some friendly test data

# Open an absolute URL
FileInfo.rel_offset = None
url = "https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test data 1.txt"
with hbopen("https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test data 1.txt", metadata.clear()) as f:
    print(f.read())
    print(metadata)
# I'm some friendly test data
#
# FileInfo(source_file='https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test%20data%201.txt', source_file_date='Thu, 18 Feb 2021 16:02:50 GMT', source_file_size='28', base_path='https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data')

# Open a relative URL
base_address = metadata.base_path
print(f"Base: {base_address}")
# Base: https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data
with hbopen('test data 1.txt', base_path=base_address) as f:
    print(f.read())
# I'm some friendly test data

# Open a file handle
with open('../tests/data/test data 1.txt') as fhandle:
    with hbopen(fhandle, metadata.clear()) as f:
        print(f.read())
        print(metadata)
# I'm some friendly test data
# FileInfo(source_file='../tests/data/test data 1.txt', source_file_date='Wed Feb 17 17:01:09 2021', source_file_size=28, base_path='../tests/data')

# Open an 'latin-1' encoded file
with hbopen('test_8859.txt', base_path=data_file_dir, read_codec='latin-1') as f:
    print(f.read())
# Some Text	With weird  ÒtextÓ	And single ÔquotesÕ

# Open a bytes file handle -- still reads as text
with open('data/test data 1.txt', 'rb') as fhandle:
    with hbopen(fhandle) as f:
        print(f.read())
# I'm some friendly test data

# Open a block of text as a file
some_text = """
    This is the honey badger. Watch it run in slow motion.

    It's pretty badass. Look. It runs all over the place. "Whoa! Watch out!" says that bird.

    Eew, it's got a snake! Oh! It's chasing a jackal! Oh my gosh!

    Oh, the honey badger is just crazy!

    The honey badger has been referred to by the Guiness Book of World Records as the most fearless animal in the animal kingdom. It really doesn't give a shit. If it's hungry, it's hungry.
"""
with hbopen(some_text, metadata.clear()) as f:
    print(f.read())
    print(metadata)
#
# This is the honey badger. Watch it run in slow motion.
#
# It's pretty badass. Look. It runs all over the place. "Whoa! Watch out!" says that bird.
#
# Eew, it's got a snake! Oh! It's chasing a jackal! Oh my gosh!
#
# Oh, the honey badger is just crazy!
#
# The honey badger has been referred to by the Guiness Book of World Records as the most fearless animal in the animal kingdom. It really doesn't give a shit. If it's hungry, it's hungry.

# hbopen doesn't require 'with'
f = hbopen('l1\nl2\nl3\n')
for l in f:
    print(l, end='')
f.close()
# l1
# l2
# l3
```

## hbread
**<span style="color: darkred">hbread</span>** returns the contents of `source`

```text
hbread(source: Union[str, bytes, bytearray, IO],
       open_info: Optional[FileInfo] = None,
       base_path: Optional[str] = None,
       accept_header: Optional[str] = None,
       is_actual_data: Optional[(str) -> bool] = default_str_tester) -> str
Return the string represented by source :param source: anything that can be construed to be a string, a URL, a file name 
or an open file handle

Params:
source – anything that can be construed to be a string, a URL, a file name or an open file handle
open_info – what we learned about source in the process of converting it
base_path – Base to use if source is a relative URL or file name
accept_header – Accept header to use if it turns out to be a URL
is_actual_data – Function to differentiate plain text from URL or file name

Returns: String represented by the source
```
```python
from hbreader import hbread, FileInfo

# hpread returns the content rather than a file handle
print(hbread('test_8859.txt', base_path=data_file_dir, read_codec='latin-1'))
# Some Text	With weird  ÒtextÓ	And single ÔquotesÕ

metadata = FileInfo()
print(hbread("https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test data 1.txt", metadata))
# I'm some friendly test data
print(metadata)
# FileInfo(source_file='https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test%20data%201.txt', source_file_date='Thu, 18 Feb 2021 16:28:37 GMT', source_file_size='28', base_path='https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data')

```
