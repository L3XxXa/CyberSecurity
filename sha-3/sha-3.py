import hashlib
import math
from hashlib import sha3_256
import colorama 
from colorama import Fore
import os

print("where to get data: (f)ile or (t)erminal")
type_in = input()
match type_in:
        case "f":
                size = os.stat("test-file.bin").st_size
                print(f"Current size of the file is {size/(1024 ** 2)} mb")
                file = open("test-file.bin", "rb")
                text = file.read()
                input_string = bytearray(text)
        case "t":
                print("Write string to hash")
                str = input()
                text = bytes(str, 'utf-8')
                input_string = bytearray(text)

round_constants = [0x0000000000000001,
        0x0000000000008082,
        0x800000000000808A,
        0x8000000080008000,
        0x000000000000808B,
        0x0000000080000001,
        0x8000000080008081,
        0x8000000000008009,
        0x000000000000008A,
        0x0000000000000088,
        0x0000000080008009,
        0x000000008000000A,
        0x000000008000808B,
        0x800000000000008B,
        0x8000000000008089,
        0x8000000000008003,
        0x8000000000008002,
        0x8000000000000080,
        0x000000000000800A,
        0x800000008000000A,
        0x8000000080008081,
        0x8000000000008080,
        0x0000000080000001,
        0x8000000080008008]

rotation_offsets = [[0, 36, 3, 41, 18],
     [1, 44, 10, 45, 2],
     [62, 6, 43, 15, 61],
     [28, 55, 25, 21, 56],
     [27, 20, 39, 8, 14]]

B = [[0] * 5] * 5
C = [0] * 5
D = [0] * 5
state = []

#SHA3-256, f-1600
f_b = 1600 
w = math.floor(1600 / 25)
log_2 = math.floor(math.log2(w))
n_rounds = 12 + 2 * log_2 
r = 1088 #rate of the sponge func. 
c = 512 #capacity of the sponge func r + c = f_b
res = 0

print(input_string)
#Adding padding
padding = r - (len(input_string) * 8 % r)
if padding == 0:
        input_string.append(0b110)
        for i in range(1, r // 8 - 1):
                input_string.append(0)
        input_string.append(0x80)
elif padding == 8:
        input_string.append(0b110 ^ 0x80)
elif padding == 16:
        input_string.append(0b110)
        input_string.append(0x80)
else:
        input_string.append(0b110)
        for i in range (1, padding // 8 - 1):
                input_string.append(0)
        input_string.append(0x80)
blocks_amount = (len(input_string) * 8) // r

print(input_string)

#variable x shift on n
def rot(x, n):
        return (((x<<n) % (1 << w)) | (x >> (w - n)))

#permutations (absorbing phase)
def roundB(A):
        for it in range(0, n_rounds):
                #θ step
                for i in range (0, 5):
                        C[i] = 0
                        D[i] = 0
                        B[i] = [0, 0, 0, 0, 0]
                for i in range(0, 5):
                        C[i] = (A[i][0] ^ A[i][1] ^ A[i][2] ^ A[i][3] ^ A[i][4])
                for i in range (0, 5):
                        D[i] = C[(i - 1) % 5] ^ rot(C[(i + 1) % 5], 1)
                for i in range(0, 5):
                        for j in range(0, 5):
                                A[i][j] ^= D[i]
                #ρ and π step
                for i in range(0, 5):
                        for j in range(0, 5):
                                B[j][(2 * i + 3 * j) % 5] = rot(A[i][j], rotation_offsets[i][j])   
                #χ step
                for i in range(0, 5):
                        for j in range(0, 5):
                                A[i][j] = B[i][j] ^ ((~B[(i + 1) % 5][j]) & B[(i + 2) % 5][j])
                #ι step
                A[0][0] ^= round_constants[it]
        return A

#squeezing phase
for i in range(0, blocks_amount):
        block_bytes = input_string[i * (r // 8) : (i + 1) * (r // 8)]
        block = []
        for j in range(0, r//8, 8):
                block.append(int.from_bytes(block_bytes[j : j + 8], 'little', signed = False))
        for j in range(r // 8, f_b //8, 8):
                block.append(0)
        block = [block[s : 21 + s : 5] for s in range(0, 5)]
        if i == 0:
                state = block
        else:
                for j in range(0, 5):
                        for k in range(0, 5):
                                state[j][k] ^= block[j][k]
        state = roundB(state)

#getting result
for i in range(4):
        res |= state[i][0] << (i * w)
result = res.to_bytes(32, 'little').hex()
print(f"Result:\n{result}")

#something like unit testing
s = hashlib.sha3_256()
s.update(text)
print(s.hexdigest())
if result == s.hexdigest():
        print(Fore.GREEN + "SUCCESS!")
else:
        print(Fore.RED + "ERROR!")