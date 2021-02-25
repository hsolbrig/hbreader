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


# hpread returns the content rather than a file handle
print(hbread('test_8859.txt', base_path=data_file_dir, read_codec='latin-1'))
# Some Text	With weird  ÒtextÓ	And single ÔquotesÕ

print(hbread("https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test data 1.txt", metadata.clear()))
# I'm some friendly test data
print(metadata)
# FileInfo(source_file='https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data/test%20data%201.txt', source_file_date='Thu, 18 Feb 2021 16:28:37 GMT', source_file_size='28', base_path='https://raw.githubusercontent.com/hsolbrig/hbreader/master/tests/data')
