#!/usr/bin/env python3
"""
RSA Offline Decryption Script
Hochschule Schmalkalden - Seminar Project

Usage:
    python3 decrypt.py <ciphertext_file> <private_key_file>
    python3 decrypt.py <ciphertext_file> <private_key_file> -o output.txt
"""

import sys
import os
import re


def load_private_key(key_file):
    """Load N and d from private_key.txt"""
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Key file not found: {key_file}")
    
    with open(key_file, 'r') as f:
        content = f.read()
    
    n_match = re.search(r'N\s*=\s*(0x[0-9a-fA-F]+)', content)
    d_match = re.search(r'd\s*=\s*(0x[0-9a-fA-F]+)', content)
    
    if not n_match or not d_match:
        raise ValueError("Could not find N or d in key file")
    
    N = int(n_match.group(1), 16)
    d = int(d_match.group(1), 16)
    
    print(f"[✓] Loaded private key: N={N.bit_length()} bits, d={d.bit_length()} bits")
    return N, d


def load_ciphertext(ciphertext_file):
    """Load ciphertext from file"""
    if not os.path.exists(ciphertext_file):
        raise FileNotFoundError(f"Ciphertext file not found: {ciphertext_file}")
    
    with open(ciphertext_file, 'r') as f:
        content = f.read().strip().replace('\n', '').replace(' ', '').replace('\r', '')
    
    ciphertext = int(content)
    print(f"[✓] Loaded ciphertext: {len(str(ciphertext))} digits")
    return ciphertext


def remove_pkcs1_padding(padded_bytes):
    """
    Remove PKCS#1 v1.5 padding
    Format: 0x00 0x02 [random bytes] 0x00 [message]
    """
    if len(padded_bytes) < 11 or padded_bytes[0] != 0x00 or padded_bytes[1] != 0x02:
        return None  # No valid padding
    
    # Find 0x00 separator
    separator_index = padded_bytes.find(b'\x00', 2)
    if separator_index == -1:
        return None
    
    message = padded_bytes[separator_index + 1:]
    print(f"[✓] Removed PKCS#1 padding: {separator_index - 2} padding bytes")
    return message


def decrypt_and_decode(ciphertext, d, N):
    """Decrypt RSA ciphertext and decode to string"""
    # Step 1: RSA decryption
    print(f"[*] Decrypting: M = C^d mod N")
    plaintext_int = pow(ciphertext, d, N)
    
    # Step 2: Convert to bytes
    byte_length = (N.bit_length() + 7) // 8
    plaintext_bytes = plaintext_int.to_bytes(byte_length, 'big')
    
    # Step 3: Remove padding (if present)
    unpadded = remove_pkcs1_padding(plaintext_bytes)
    
    if unpadded is None:
        print(f"[!] No PKCS#1 padding detected - using textbook RSA")
        unpadded = plaintext_bytes.lstrip(b'\x00')
    
    # Step 4: Decode to string
    for encoding in ['utf-8', 'ascii', 'latin-1']:
        try:
            message = unpadded.decode(encoding)
            if encoding == 'utf-8' or message.isprintable():
                print(f"[✓] Decoded as {encoding.upper()}")
                return message, encoding.upper(), unpadded
        except (UnicodeDecodeError, AttributeError):
            continue
    
    # Fallback: return hex
    print(f"[!] Binary data - showing hex")
    return unpadded.hex(), 'HEX', unpadded


def display_result(message, encoding):
    """Display decrypted message"""
    print("\n" + "="*70)
    print("🔓 DECRYPTION SUCCESSFUL")
    print("="*70)
    print(f"\nDECRYPTED MESSAGE ({encoding}):\n")
    
    if encoding == 'HEX':
        hex_formatted = ' '.join(message[i:i+2] for i in range(0, min(len(message), 200), 2))
        if len(message) > 200:
            hex_formatted += "..."
        print(hex_formatted)
    else:
        print(message)
    
    print("\n" + "="*70)


def main():
    print("\n" + "="*70)
    print("🔓 RSA OFFLINE DECRYPTION")
    print("   Hochschule Schmalkalden - Timing Attack Demo")
    print("="*70 + "\n")
    
    # Parse arguments
    if len(sys.argv) < 3:
        print("[ERROR] Missing arguments!\n")
        print("Usage:")
        print("  python3 decrypt.py <ciphertext_file> <private_key_file>")
        print("  python3 decrypt.py <ciphertext_file> <private_key_file> -o output.txt\n")
        sys.exit(1)
    
    ciphertext_file = sys.argv[1]
    key_file = sys.argv[2]
    output_file = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == '-o' else None
    
    try:
        # Load inputs
        N, d = load_private_key(key_file)
        ciphertext = load_ciphertext(ciphertext_file)
        
        # Decrypt and decode
        message, encoding, raw_bytes = decrypt_and_decode(ciphertext, d, N)
        
        # Display result
        display_result(message, encoding)
        
        # Save if requested
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(raw_bytes)
            print(f"\n[✓] Saved to: {output_file}")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
        sys.exit(0)
