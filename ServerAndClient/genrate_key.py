#!/usr/bin/env python3
"""
RSA Key Pair Generator for Seminar Project
Hochschule Schmalkalden

Generates a fresh RSA key pair ready to copy-paste into server and client files.

Usage:
    python3 generate_keys.py --bits 3072
    python3 generate_keys.py --bits 2048 --output keys.txt
"""

import argparse
from Crypto.PublicKey import RSA
from Crypto.Util.number import isPrime, GCD
import random

def generate_rsa_keypair(key_size=3072):
    """
    Generate RSA key pair using PyCryptodome
    Returns: (N, e, d, p, q)
    """
    print(f"[*] Generating {key_size}-bit RSA key pair...")
    print(f"[*] This may take a few seconds...\n")
    
    # Generate RSA key
    key = RSA.generate(key_size)
    
    N = key.n  # Modulus
    e = key.e  # Public exponent (usually 65537)
    d = key.d  # Private exponent
    p = key.p  # First prime
    q = key.q  # Second prime
    
    print(f"[✓] Key generation complete!")
    print(f"    N: {N.bit_length()} bits")
    print(f"    e: {e}")
    print(f"    d: {d.bit_length()} bits")
    print(f"    p: {p.bit_length()} bits")
    print(f"    q: {q.bit_length()} bits\n")
    
    # Verify key pair
    print(f"[*] Verifying key pair...")
    assert p * q == N, "p × q ≠ N"
    
    # Test encryption/decryption
    test_msg = 12345
    encrypted = pow(test_msg, e, N)
    decrypted = pow(encrypted, d, N)
    assert decrypted == test_msg, "Encryption/decryption test failed"
    
    print(f"[✓] Key pair is mathematically valid!\n")
    
    return N, e, d, p, q

def format_for_python(N, e, d, p, q):
    """Format keys for Python copy-paste"""
    output = []
    
    output.append("="*70)
    output.append("RSA KEY PAIR - COPY THIS INTO YOUR FILES")
    output.append("="*70)
    output.append("")
    output.append("# For server.py and any files that need the full key pair:")
    output.append("")
    output.append("FIXED_KEYS = {")
    output.append(f'    "N": {hex(N)},')
    output.append(f'    "e": {e},')
    output.append(f'    "d": {hex(d)},')
    output.append(f'    "p": {hex(p)},')
    output.append(f'    "q": {hex(q)}')
    output.append("}")
    output.append("")
    output.append("="*70)
    output.append("PUBLIC KEY ONLY (for encryption/client)")
    output.append("="*70)
    output.append("")
    output.append("PUBLIC_KEY = {")
    output.append(f'    "N": {hex(N)},')
    output.append(f'    "e": {e}')
    output.append("}")
    output.append("")
    output.append("="*70)
    output.append("PRIVATE KEY ONLY (for decryption)")
    output.append("="*70)
    output.append("")
    output.append("PRIVATE_KEY = {")
    output.append(f'    "N": {hex(N)},')
    output.append(f'    "d": {hex(d)}')
    output.append("}")
    output.append("")
    output.append("="*70)
    output.append("KEY INFORMATION")
    output.append("="*70)
    output.append(f"Key size: {N.bit_length()} bits")
    output.append(f"Security level: ~{N.bit_length() // 2} bits")
    output.append(f"Public exponent (e): {e}")
    output.append(f"Modulus (N) length: {len(str(N))} digits")
    output.append("")
    output.append("="*70)
    output.append("USAGE INSTRUCTIONS")
    output.append("="*70)
    output.append("")
    output.append("1. SERVER (server.py):")
    output.append("   - Replace the entire FIXED_KEYS dictionary")
    output.append("   - Use all values: N, e, d, p, q")
    output.append("")
    output.append("2. CLIENT/ATTACKER (for encryption):")
    output.append("   - Use PUBLIC_KEY: N and e")
    output.append("   - These are safe to share")
    output.append("")
    output.append("3. DECRYPTION (decrypt.py):")
    output.append("   - Use PRIVATE_KEY: N and d")
    output.append("   - Keep d secret!")
    output.append("")
    output.append("="*70)
    
    return "\n".join(output)

def save_to_files(N, e, d, p, q, prefix="rsa_keys"):
    """Save keys to separate files"""
    
    # Full key pair
    with open(f"{prefix}_full.txt", 'w') as f:
        f.write("FULL RSA KEY PAIR\n")
        f.write("="*70 + "\n\n")
        f.write(f"N = {hex(N)}\n")
        f.write(f"e = {e}\n")
        f.write(f"d = {hex(d)}\n")
        f.write(f"p = {hex(p)}\n")
        f.write(f"q = {hex(q)}\n")
    
    # Public key only
    with open(f"{prefix}_public.txt", 'w') as f:
        f.write("PUBLIC KEY (N, e)\n")
        f.write("="*70 + "\n\n")
        f.write(f"N = {hex(N)}\n")
        f.write(f"e = {e}\n")
    
    # Private key only
    with open(f"{prefix}_private.txt", 'w') as f:
        f.write("PRIVATE KEY (N, d)\n")
        f.write("="*70 + "\n\n")
        f.write(f"N = {hex(N)}\n")
        f.write(f"d = {hex(d)}\n")
    
    # Python format
    with open(f"{prefix}_python.txt", 'w') as f:
        f.write(format_for_python(N, e, d, p, q))
    
    print(f"[✓] Keys saved to:")
    print(f"    - {prefix}_full.txt       (all values)")
    print(f"    - {prefix}_public.txt     (N, e only)")
    print(f"    - {prefix}_private.txt    (N, d only)")
    print(f"    - {prefix}_python.txt     (formatted for copy-paste)")

def main():
    parser = argparse.ArgumentParser(
        description='Generate RSA key pair for seminar project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 3072-bit key (BSI/NIST standard)
  python3 generate_keys.py --bits 3072
  
  # Generate 2048-bit key (faster)
  python3 generate_keys.py --bits 2048
  
  # Generate and save to files
  python3 generate_keys.py --bits 3072 --output my_keys
  
  # Quick demo with 1024-bit (INSECURE - demo only!)
  python3 generate_keys.py --bits 1024

Key sizes:
  - 1024 bits: INSECURE (demo/testing only)
  - 2048 bits: Current standard (until 2030)
  - 3072 bits: BSI/NIST recommended (2024+)
  - 4096 bits: Long-term security
        """
    )
    
    parser.add_argument('-b', '--bits', type=int, default=3072,
                       choices=[1024, 2048, 3072, 4096],
                       help='RSA key size in bits (default: 3072)')
    
    parser.add_argument('-o', '--output', type=str,
                       help='Output file prefix (optional)')
    
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save to files, only print')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🔑 RSA KEY PAIR GENERATOR")
    print("   Hochschule Schmalkalden - Seminar Project")
    print("="*70 + "\n")
    
    if args.bits < 2048:
        print("⚠️  WARNING: Key size < 2048 bits is INSECURE!")
        print("    Use only for testing/demo purposes.\n")
    
    # Generate keys
    N, e, d, p, q = generate_rsa_keypair(args.bits)
    
    # Format output
    output = format_for_python(N, e, d, p, q)
    print(output)
    
    # Save to files
    if not args.no_save:
        prefix = args.output if args.output else f"rsa_keys_{args.bits}bit"
        save_to_files(N, e, d, p, q, prefix)
    
    print("\n" + "="*70)
    print("✅ KEY GENERATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Copy the FIXED_KEYS dictionary above")
    print("  2. Paste it into your server.py file")
    print("  3. Copy PUBLIC_KEY to any client/encryption scripts")
    print("  4. Keep PRIVATE_KEY secret!")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
