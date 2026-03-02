#!/usr/bin/env python3
"""
Legitimate Client - Secure Communication with RSA
Hochschule Schmalkalden - Seminar Project

Simulates TLS/HTTPS handshake:
1. Request server certificate (contains public key)
2. Encrypt sensitive data with server's public key
3. Send encrypted message to server

In production: This would be the TLS handshake + application data
"""

import socket
import json
import os


def pkcs1_v15_pad(message_bytes, key_size_bits):
    """
    Add PKCS#1 v1.5 padding to message
    Format: 0x00 0x02 [random non-zero bytes] 0x00 [message]
    """
    key_size_bytes = (key_size_bits + 7) // 8
    message_len = len(message_bytes)
    
    # Check if message is too long
    if message_len > key_size_bytes - 11:
        raise ValueError(f"Message too long: {message_len} bytes (max: {key_size_bytes - 11})")
    
    # Calculate padding length
    padding_len = key_size_bytes - message_len - 3
    
    # Generate random non-zero padding
    padding = bytearray()
    while len(padding) < padding_len:
        byte = os.urandom(1)[0]
        if byte != 0:  # PKCS#1 requires non-zero padding bytes
            padding.append(byte)
    
    # Format: 0x00 0x02 [random padding] 0x00 [message]
    padded = bytes([0x00, 0x02]) + bytes(padding) + bytes([0x00]) + message_bytes
    
    print(f"[CLIENT] Added PKCS#1 v1.5 padding:")
    print(f"  Original: {message_len} bytes")
    print(f"  Padded:   {len(padded)} bytes")
    print(f"  Padding:  {padding_len} random bytes")
    
    return padded


def request_certificate():
    """
    Request server's public key certificate
    Simulates TLS handshake where server sends X.509 certificate
    """
    print("[CLIENT] ═══ TLS HANDSHAKE SIMULATION ═══")
    print("[CLIENT] Requesting server certificate...\n")
    
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect(('localhost', 8080))
        
        # Send certificate request (like ClientHello in TLS)
        req = json.dumps({"command": "get_certificate"})
        s.send(req.encode())
        
        # Receive certificate (like ServerHello + Certificate in TLS)
        resp_data = s.recv(4096).decode()
        resp = json.loads(resp_data)
        s.close()
        
        if resp.get("status") != "success":
            print(f"[ERROR] Certificate request failed: {resp}")
            return None, None
        
        N = resp["N"]
        e = resp["e"]
        
        print(f"[CLIENT] ✓ Received server certificate")
        print(f"[CLIENT] Certificate Info: {resp.get('certificate_info', 'RSA Public Key')}")
        print(f"[CLIENT] Key Size: {N.bit_length()} bits")
        print(f"[CLIENT] Modulus (N): {hex(N)[:60]}...")
        print(f"[CLIENT] Exponent (e): {e}")
        print(f"[CLIENT] ✓ Certificate validated (in production: verify CA signature)\n")
        
        return N, e
        
    except ConnectionRefusedError:
        print("[ERROR] Cannot connect to server on localhost:8080")
        print("[FIX] Start server: python3 server.py")
        return None, None
    except socket.timeout:
        print("[ERROR] Server connection timed out")
        return None, None
    except Exception as e:
        print(f"[ERROR] Certificate request failed: {e}")
        return None, None


def send_encrypted_message(N, e):
    """
    Encrypt and send sensitive message to server
    Uses server's public key from certificate
    """
    print("[CLIENT] ═══ ENCRYPTED DATA TRANSMISSION ═══")
    
    # Prepare secret message
    secret_flag = b"flag{HS_Schmalkalden_MITM_Attack_Success_2026}"
    print(f"[CLIENT] Plaintext: {secret_flag.decode()}")
    print(f"[CLIENT] Encrypting with server's public key (RSA)...\n")
    
    # ========== ADD PADDING (FIX) ==========
    padded_message = pkcs1_v15_pad(secret_flag, N.bit_length())
    
    # Convert padded message to integer
    m = int.from_bytes(padded_message, 'big')
    # ========================================
    
    # RSA Encryption: C = M^e mod N
    ciphertext = pow(m, e, N)
    
    print(f"[CLIENT] ✓ Encryption complete")
    print(f"[CLIENT] Ciphertext: {str(ciphertext)[:80]}...")
    print(f"[CLIENT] Length: {len(str(ciphertext))} digits\n")
    
    # Send encrypted data to server
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect(('localhost', 8080))
        
        payload = json.dumps({
            "command": "login",
            "username": "admin",
            "encrypted_data": ciphertext
        })
        
        print(f"[CLIENT] Sending encrypted message to server...")
        s.send(payload.encode())
        
        resp_data = s.recv(4096).decode()
        resp = json.loads(resp_data)
        s.close()
        
        print(f"[CLIENT] Server response: {resp.get('message', resp.get('status'))}")
        print(f"[CLIENT] ✓ Transmission complete\n")
        
        return True
        
    except ConnectionRefusedError:
        print("[ERROR] Cannot connect to server")
        return False
    except socket.timeout:
        print("[ERROR] Server connection timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Transmission failed: {e}")
        return False


def main():
    print("="*60)
    print("🔐 LEGITIMATE CLIENT - Secure RSA Communication")
    print("   Hochschule Schmalkalden - Seminar Project")
    print("="*60 + "\n")
    
    # Phase 1: TLS Handshake - Get Server Certificate
    N, e = request_certificate()
    if N is None or e is None:
        print("[FATAL] Cannot proceed without server certificate")
        return
    
    # Phase 2: Application Data - Send Encrypted Message
    success = send_encrypted_message(N, e)
    
    if success:
        print("="*60)
        print("✓ SECURE COMMUNICATION ESTABLISHED")
        print("="*60)
        print("\n[INFO] In production environment:")
        print("  • Client would verify certificate signature (CA chain)")
        print("  • Session would use AES symmetric key (hybrid encryption)")
        print("  • Perfect Forward Secrecy would protect past sessions")
        print("  • However, timing vulnerabilities can still leak private keys!")
        print("="*60)
    else:
        print("\n[FAILED] Communication error")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
