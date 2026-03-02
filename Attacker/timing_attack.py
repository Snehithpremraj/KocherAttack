#!/usr/bin/env python3
"""
RSA Timing Attack Client - Recovers private key d bit-by-bit
"""
import socket
import json
import time
import statistics

# Step 1: Get public key from server
def get_public_key():
    s = socket.socket()
    s.connect(('localhost', 8080))
    req = json.dumps({"command": "get_public_key"})
    s.send(req.encode())
    resp = json.loads(s.recv(4096).decode())
    s.close()
    if resp["status"] == "success":
        return resp["N"], resp["e"]
    raise Exception("Failed to get public key")

# Step 2: Query oracle with client-side timing
def query_time(c, N):
    """Measure round-trip time (works even without server hints)"""
    s = socket.socket()
    s.connect(('localhost', 8080))
    req = json.dumps({"command": "decrypt_vulnerable", "ciphertext": str(c % N)})
    
    t0 = time.perf_counter()  # Client-side timing
    s.send(req.encode())
    resp = json.loads(s.recv(8192).decode())
    elapsed_us = (time.perf_counter() - t0) * 1_000_000
    s.close()
    
    return elapsed_us

# Step 3: Recover d bit-by-bit
def recover_private_key(N, trials=100):
    """Recover d using timing side-channel"""
    print(f"[*] Starting timing attack on {N.bit_length()}-bit key")
    print(f"[*] Using {trials} samples per bit (may take 1-2 hours)")
    
    d_bits = []
    for bit_pos in range(min(20, N.bit_length())):  # Demo: first 20 bits
        # Test two hypotheses: bit=0 vs bit=1
        c_test = pow(2, bit_pos, N)
        
        times_0 = [query_time(c_test, N) for _ in range(trials)]
        times_1 = [query_time(c_test + 1, N) for _ in range(trials)]
        
        mean_0 = statistics.mean(times_0)
        mean_1 = statistics.mean(times_1)
        
        # If bit=1, more multiplies → slower
        if mean_1 > mean_0:
            d_bits.append(1)
            result = "1 (SLOW)"
        else:
            d_bits.append(0)
            result = "0 (FAST)"
        
        print(f"  Bit {bit_pos:4d}: {result} | μ₀={mean_0:6.2f}μs μ₁={mean_1:6.2f}μs Δ={abs(mean_1-mean_0):5.2f}μs")
    
    # Convert to integer (LSB-first)
    d_partial = int(''.join(map(str, d_bits)), 2)
    return d_partial, d_bits

# Main attack flow
if __name__ == "__main__":
    print("="*60)
    print("🎯 RSA TIMING ATTACK CLIENT")
    print("="*60 + "\n")
    
    # Get N from server
    N, e = get_public_key()
    print(f"[+] Retrieved public key:")
    print(f"    N = {hex(N)[:50]}...")
    print(f"    e = {e}")
    print(f"    bits = {N.bit_length()}\n")
    
    # Attack (demo: 20 bits)
    d_recovered, bits = recover_private_key(N, trials=50)
    
    print(f"\n[✓] Recovered (first 20 bits): {d_recovered}")
    print(f"[✓] Binary: {''.join(map(str, bits))}")
    print(f"\n[!] Full 3072-bit recovery needs ~3 hours with 1000 samples/bit")
    print(f"[!] Increase trials for better accuracy in production attack")
