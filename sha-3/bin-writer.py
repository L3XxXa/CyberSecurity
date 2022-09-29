import os
file = open("test-file.bin", "wb")
file.write(b"Hello, world")

while(os.stat("test-file.bin").st_size / (1024 * 1024) < 1):
    file.write(b"hello, world\n")

