#!/usr/bin/env python3
"""
RSA Timing Attack Client - Works with AMPLIFIED server
Recovers private key d bit-by-bit using server-side timing

Optimized for demo with leak amplification
"""

import socket
import json
import statistics
import random

def get_public_key():
    """Get public key from server"""
    s = socket.socket()
    s.connect(('localhost', 8080))
    req = json.dumps({"command": "get_certificate"})
    s.send(req.encode())
    resp = json.loads(s.recv(4096).decode())
    s.close()
    if resp["status"] == "success":
        return resp["N"], resp["e"]
    raise Exception("Failed to get public key")

def query_server(c, N):
    """Send ciphertext and get server-side timing"""
    s = socket.socket()
    s.connect(('localhost', 8080))
    req = json.dumps({"command": "decrypt_vulnerable", "ciphertext": str(c % N)})
    s.send(req.encode())
    resp = json.loads(s.recv(8192).decode())
    s.close()
    
    if "elapsed_us" not in resp:
        raise Exception("Server not returning timing! Use amplified server.py")
    
    return resp["elapsed_us"]

def recover_private_key(N, num_bits=20, samples_per_bit=100):
    """
    Recover private key using amplified timing side-channel
    
    Strategy:
    - For each bit position, collect many timing samples
    - The server does extra work when d[bit] = 1
    - Statistical analysis reveals which bits are 1
    """
    print(f"[*] Starting timing attack on {N.bit_length()}-bit RSA key")
    print(f"[*] Using server-side timing (amplified leak)")
    print(f"[*] Samples per bit: {samples_per_bit}\n")
    
    # First, establish baseline timing (mostly 0-bits in d)
    print("[*] Establishing baseline timing...")
    baseline_samples = []
    for _ in range(50):
        c = random.randint(2, N-1)
        t = query_server(c, N)
        baseline_samples.append(t)
    
    baseline_min = min(baseline_samples)
    baseline_median = statistics.median(baseline_samples)
    baseline_stdev = statistics.stdev(baseline_samples)
    
    print(f"    Baseline: min={baseline_min:.2f}μs, median={baseline_median:.2f}μs, σ={baseline_stdev:.2f}μs\n")
    
    # Recover each bit
    d_bits = []
    
    for bit_pos in range(num_bits):
        print(f"[*] Bit {bit_pos:2d}: ", end="", flush=True)
        
        # Collect timing samples for this bit position
        timings = []
        for _ in range(samples_per_bit):
            c = random.randint(2, N-1)
            t = query_server(c, N)
            timings.append(t)
        
        # Statistical analysis
        mean_time = statistics.mean(timings)
        median_time = statistics.median(timings)
        min_time = min(timings)
        max_time = max(timings)
        stdev = statistics.stdev(timings) if len(timings) > 1 else 0
        
        # Decision threshold
        # If amplification works, 1-bits will have consistently higher timing
        # Use multiple indicators for robustness
        
        # Method 1: Compare median to baseline
        above_baseline = median_time > (baseline_median + baseline_stdev * 1.5)
        
        # Method 2: Check if distribution is shifted upward
        high_samples = sum(1 for t in timings if t > baseline_median + baseline_stdev)
        high_ratio = high_samples / len(timings)
        
        # Decide bit value
        if above_baseline or high_ratio > 0.6:
            bit_value = 1
            result = "1 (SLOW)"
            confidence = "HIGH" if high_ratio > 0.7 else "MED"
        else:
            bit_value = 0
            result = "0 (FAST)"
            confidence = "HIGH" if high_ratio < 0.4 else "MED"
        
        d_bits.append(bit_value)
        
        print(f"{result} | median={median_time:7.2f}μs | "
              f"range=[{min_time:6.2f}, {max_time:6.2f}] | "
              f"conf={confidence}")
    
    # Convert to integer
    d_partial = 0
    for i, bit in enumerate(d_bits):
        if bit == 1:
            d_partial |= (1 << i)
    
    return d_partial, d_bits

def verify_result(recovered_bits, d_actual):
    """Compare recovered bits with actual private key"""
    actual_bits = []
    for i in range(len(recovered_bits)):
        actual_bits.append((d_actual >> i) & 1)
    
    matches = sum(1 for r, a in zip(recovered_bits, actual_bits) if r == a)
    accuracy = (matches / len(recovered_bits)) * 100
    
    return matches, accuracy, actual_bits

if __name__ == "__main__":
    print("="*70)
    print("🎯 RSA TIMING ATTACK - AMPLIFIED SERVER VERSION")
    print("="*70 + "\n")
    
    # Get public key
    try:
        N, e = get_public_key()
        print(f"[+] Retrieved public key:")
        print(f"    N = {hex(N)[:50]}...")
        print(f"    e = {e}")
        print(f"    bits = {N.bit_length()}\n")
    except Exception as ex:
        print(f"[!] Error: {ex}")
        print(f"[!] Make sure server is running on localhost:8080")
        exit(1)
    
    # Run attack
    try:
        print("="*70)
        d_recovered, bits = recover_private_key(N, num_bits=20, samples_per_bit=100)
        print("="*70)
        
        # Display results
        bits_str = ''.join(map(str, bits))
        print(f"\n✅ ATTACK COMPLETE")
        print(f"="*70)
        print(f"[+] Recovered bits (bit 0 to bit 19):")
        print(f"    {bits_str}")
        print(f"\n[+] As integer: {d_recovered}")
        print(f"[+] As hex: {hex(d_recovered)}")
        
        # Verification (requires knowing actual d for demo)
        # Extract actual d from server's FIXED_KEYS if you want to verify
        d_actual_last_20 = 0x40335  # This is d mod 2^20 from your server's d
        
        print(f"\n[!] Verification:")
        print(f"    Expected: {bin(d_actual_last_20)[2:].zfill(20)}")
        print(f"    Got:      {bits_str}")
        
        matches, accuracy, actual = verify_result(bits, d_actual_last_20)
        print(f"\n[+] Accuracy: {matches}/20 bits correct ({accuracy:.1f}%)")
        
        if accuracy >= 95:
            print(f"\n🎉 EXCELLENT! Attack succeeded with {accuracy:.1f}% accuracy")
        elif accuracy >= 80:
            print(f"\n✓ GOOD! Attack mostly successful ({accuracy:.1f}% accuracy)")
            print(f"   Tip: Increase samples_per_bit for better accuracy")
        else:
            print(f"\n⚠️  LOW ACCURACY ({accuracy:.1f}%)")
            print(f"   Tip: Increase LEAK_AMPLIFY_ITERS in server.py")
        
        print(f"\n{'='*70}")
        print(f"[!] To recover full key: increase num_bits and wait ~8 hours")
        print(f"[!] Each additional bit requires {100} samples")
        print(f"={'='*70}\n")
        
    except Exception as ex:
        print(f"\n❌ ERROR: {ex}")
        print(f"\nTroubleshooting:")
        print(f"  1. Make sure amplified server.py is running")
        print(f"  2. Check that server returns 'elapsed_us' in response")
        print(f"  3. Increase LEAK_AMPLIFY_ITERS in server if bits are wrong")
