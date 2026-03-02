#!/usr/bin/env python3
"""
Generate fixed RSA keys for demo (run once)
Output: Keys in HEXADECIMAL format for server.py
Hochschule Schmalkalden - Seminar Project
"""
import random


def miller_rabin_prime(n, k=40):
    """Probabilistic primality test"""
    if n < 2 or n % 2 == 0: 
        return n == 2
    r, s = 0, n - 1
    while s % 2 == 0:
        s //= 2
        r += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1: 
            continue
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1: 
                break
        else: 
            return False
    return True


def get_prime(bits):
    """Generate a prime number of specified bit length"""
    while True:
        p = random.randrange(1 << (bits - 1), 1 << bits)
        if p % 2 and miller_rabin_prime(p): 
            return p


print("Generating 3072-bit RSA keys (this may take a minute)...\n")

# RSA key generation
e = 65537
p = get_prime(1536)
q = get_prime(1536)
while p == q: 
    q = get_prime(1536)

N = p * q
phi = (p - 1) * (q - 1)
d = pow(e, phi - 2, phi)

# ========== HEXADECIMAL OUTPUT ==========
print("="*70)
print("FIXED RSA KEYS FOR DEMO (HEXADECIMAL FORMAT)")
print("="*70)

print(f"\nPublic Key (N, e):")
print(f"N = 0x{N:x}")
print(f"e = {e}")

print(f"\nPrivate Key (d, p, q):")
print(f"d = 0x{d:x}")
print(f"p = 0x{p:x}")
print(f"q = 0x{q:x}")

print(f"\nKey Size: {N.bit_length()} bits")

# ========== FORMATTED FOR COPY-PASTE ==========
print("\n" + "="*70)
print("COPY-PASTE INTO server.py FIXED_KEYS:")
print("="*70)
print("""
FIXED_KEYS = {""")
print(f'    "N": 0x{N:x},')
print(f'    "e": {e},')
print(f'    "d": 0x{d:x},')
print(f'    "p": 0x{p:x},')
print(f'    "q": 0x{q:x}')
print("}")

# ========== SAVE TO FILE ==========
output_file = "generated_keys_hex.txt"
with open(output_file, 'w') as f:
    f.write("FIXED_KEYS = {\n")
    f.write(f'    "N": 0x{N:x},\n')
    f.write(f'    "e": {e},\n')
    f.write(f'    "d": 0x{d:x},\n')
    f.write(f'    "p": 0x{p:x},\n')
    f.write(f'    "q": 0x{q:x}\n')
    f.write("}\n")

print("\n" + "="*70)
print(f"✓ Saved to: {output_file}")
print("="*70)

# ========== VERIFICATION ==========
print("\n" + "="*70)
print("VERIFICATION:")
print("="*70)
print(f"N bit length:   {N.bit_length()} bits")
print(f"p bit length:   {p.bit_length()} bits")
print(f"q bit length:   {q.bit_length()} bits")
print(f"d bit length:   {d.bit_length()} bits")
print(f"N = p × q:      {N == p * q}")
print(f"e × d ≡ 1 (mod φ(N)): {(e * d) % phi == 1}")
print("="*70)
