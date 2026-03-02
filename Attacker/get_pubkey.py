#!/usr/bin/env python3
"""
Extract Public Key and Ciphertext from Network Capture
Hochschule Schmalkalden - Seminar Project

Simulates attacker analyzing captured network traffic to extract:
1. Server's RSA public key (N, e) from certificate
2. Encrypted messages (ciphertext) from login attempts

Usage: python3 extract_from_pcap.py <pcap_file>
"""

import subprocess
import re
import sys
import os
import json
from datetime import datetime


def parse_pcap_for_data(pcap_file):
    """
    Parse pcap file to extract both public key and ciphertexts
    Returns: (N, e, list_of_ciphertexts)
    """
    print("="*70)
    print("🔍 EXTRACTING DATA FROM NETWORK CAPTURE")
    print("="*70)
    print(f"[ATTACKER] Analyzing: {pcap_file}\n")
    
    if not os.path.exists(pcap_file):
        print(f"[ERROR] Capture file not found: {pcap_file}")
        return None, None, []
    
    try:
        # Use tshark to extract TCP payload
        print("[ATTACKER] Running tshark to extract TCP payloads...")
        result = subprocess.run(
            ['tshark', '-r', pcap_file, '-T', 'fields', '-e', 'tcp.payload', 
             '-Y', 'tcp.port==8080 and tcp.len > 0'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"[ERROR] tshark failed: {result.stderr}")
            return None, None, []
        
        packet_count = len([l for l in result.stdout.split('\n') if l.strip()])
        print(f"[ATTACKER] Found {packet_count} packets with TCP data\n")
        
        # Storage for extracted data
        N = None
        e = None
        ciphertexts = []
        
        # Parse each packet
        for packet_num, line in enumerate(result.stdout.split('\n'), 1):
            if not line.strip():
                continue
            
            try:
                # Convert hex payload to ASCII
                payload_hex = line.replace(':', '').replace('\n', '')
                payload_bytes = bytes.fromhex(payload_hex)
                payload_str = payload_bytes.decode('utf-8', errors='ignore')
                
                # Look for certificate response (contains N, e)
                if N is None and 'certificate' in payload_str.lower() and '"N"' in payload_str:
                    print(f"[ATTACKER] 🔑 Found certificate in packet #{packet_num}")
                    
                    # Extract N
                    n_match = re.search(r'"N":\s*(\d+)', payload_str)
                    if not n_match:
                        n_match = re.search(r'"N":\s*(0x[0-9a-fA-F]+)', payload_str)
                    
                    # Extract e
                    e_match = re.search(r'"e":\s*(\d+)', payload_str)
                    
                    if n_match and e_match:
                        n_str = n_match.group(1)
                        e_str = e_match.group(1)
                        
                        N = int(n_str, 16) if n_str.startswith('0x') else int(n_str)
                        e = int(e_str)
                        
                        print(f"[ATTACKER]   ✓ Extracted public key")
                        print(f"[ATTACKER]   - Key size: {N.bit_length()} bits")
                        print(f"[ATTACKER]   - N: {hex(N)[:60]}...")
                        print(f"[ATTACKER]   - e: {e}\n")
                
                # Look for encrypted_data (ciphertext from login attempts)
                if '"encrypted_data"' in payload_str or '"ciphertext"' in payload_str:
                    print(f"[ATTACKER] 🔐 Found encrypted message in packet #{packet_num}")
                    
                    # Extract ciphertext
                    ct_match = re.search(r'"encrypted_data":\s*(\d+)', payload_str)
                    if not ct_match:
                        ct_match = re.search(r'"ciphertext":\s*(\d+)', payload_str)
                    
                    if ct_match:
                        ciphertext = int(ct_match.group(1))
                        ciphertexts.append({
                            'ciphertext': ciphertext,
                            'packet_number': packet_num,
                            'length': len(str(ciphertext))
                        })
                        print(f"[ATTACKER]   ✓ Captured ciphertext")
                        print(f"[ATTACKER]   - Length: {len(str(ciphertext))} digits")
                        print(f"[ATTACKER]   - Preview: {str(ciphertext)[:50]}...\n")
                        
            except Exception as e:
                # Skip malformed packets
                continue
        
        # Summary
        print("="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        
        if N and e:
            print(f"[✓] Public Key: Extracted successfully")
        else:
            print(f"[✗] Public Key: NOT FOUND")
        
        print(f"[{'✓' if ciphertexts else '✗'}] Ciphertexts: {len(ciphertexts)} captured")
        print("="*70 + "\n")
        
        return N, e, ciphertexts
        
    except FileNotFoundError:
        print("[ERROR] tshark not installed")
        print("[FIX] Install: sudo apt install tshark")
        return None, None, []
    except subprocess.TimeoutExpired:
        print("[ERROR] tshark analysis timed out")
        return None, None, []
    except Exception as e:
        print(f"[ERROR] Failed to parse pcap: {e}")
        return None, None, []


def save_extracted_data(N, e, ciphertexts):
    """Save all extracted data to files for attack workflow"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save public key
    if N and e:
        public_key_data = {
            "N": hex(N),
            "e": e,
            "key_size_bits": N.bit_length(),
            "extraction_time": timestamp,
            "extraction_source": "network_capture"
        }
        
        public_key_file = f"extracted_public_key_{timestamp}.json"
        with open(public_key_file, 'w') as f:
            json.dump(public_key_data, f, indent=2)
        
        print(f"[ATTACKER] ✓ Public key saved to: {public_key_file}")
        
        # Also save N in cache for timing attack
        with open('.attacker_cache_N.txt', 'w') as f:
            f.write(hex(N))
        print(f"[ATTACKER] ✓ Cached N for timing attack: .attacker_cache_N.txt")
    
    # Save ciphertexts
    if ciphertexts:
        # Save all ciphertexts to JSON
        ciphertext_data = {
            "extraction_time": timestamp,
            "total_captured": len(ciphertexts),
            "ciphertexts": ciphertexts
        }
        
        ciphertext_file = f"extracted_ciphertexts_{timestamp}.json"
        with open(ciphertext_file, 'w') as f:
            json.dump(ciphertext_data, f, indent=2)
        
        print(f"[ATTACKER] ✓ All ciphertexts saved to: {ciphertext_file}")
        
        # Save first ciphertext separately for easy decryption testing
        if len(ciphertexts) > 0:
            first_ct_file = "ciphertext.txt"
            with open(first_ct_file, 'w') as f:
                f.write(str(ciphertexts[0]['ciphertext']))
            print(f"[ATTACKER] ✓ First ciphertext saved to: {first_ct_file}")
    
    # Create summary report
    report_file = f"extraction_report_{timestamp}.txt"
    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("NETWORK CAPTURE EXTRACTION REPORT\n")
        f.write("Hochschule Schmalkalden - Seminar Project\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Extraction Time: {timestamp}\n\n")
        
        f.write("EXTRACTED DATA:\n")
        f.write("-"*70 + "\n")
        
        if N and e:
            f.write(f"✓ Public Key (N, e)\n")
            f.write(f"  - Key Size: {N.bit_length()} bits\n")
            f.write(f"  - Modulus N: {hex(N)}\n")
            f.write(f"  - Exponent e: {e}\n\n")
        else:
            f.write(f"✗ Public Key: NOT FOUND\n\n")
        
        if ciphertexts:
            f.write(f"✓ Encrypted Messages: {len(ciphertexts)} captured\n\n")
            for i, ct in enumerate(ciphertexts, 1):
                f.write(f"  Ciphertext #{i}:\n")
                f.write(f"    Packet: #{ct['packet_number']}\n")
                f.write(f"    Length: {ct['length']} digits\n")
                f.write(f"    Value: {ct['ciphertext']}\n\n")
        else:
            f.write(f"✗ Encrypted Messages: NONE FOUND\n\n")
        
        f.write("="*70 + "\n")
        f.write("NEXT STEPS FOR ATTACK\n")
        f.write("="*70 + "\n\n")
        
        if N and e:
            f.write("1. Run Timing Attack to recover private key:\n")
            f.write("   python3 timing_attack.py --bits 3072 --trials 500\n\n")
        
        if ciphertexts:
            f.write("2. After recovering private key, decrypt messages:\n")
            f.write("   python3 decrypt_simple.py <N> <d> <ciphertext>\n\n")
        
        f.write("3. All intercepted communications will be compromised!\n")
    
    print(f"[ATTACKER] ✓ Extraction report: {report_file}\n")
    
    


def main():
    print("\n" + "="*70)
    print("   Public Key + Ciphertext Capture from PCAP")
    print("="*70 + "\n")
    
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python3 extract_from_pcap.py <pcap_file>")
        print("\nDefault capture: /tmp/rsa_capture.pcap\n")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    
    # Extract both public key and ciphertexts
    N, e, ciphertexts = parse_pcap_for_data(pcap_file)
    
    if N is None and not ciphertexts:
        print("\n[FAILED] Could not extract any useful data from capture")
        print("\n[TROUBLESHOOTING]:")
        print("  • Verify capture includes client-server communication")
        print("  • Check client requests certificate (get_certificate)")
        print("  • Check client sends login (encrypted_data)")
        print("  • Inspect manually: tshark -r {} -Y 'tcp.port==8080' -V".format(pcap_file))
        sys.exit(1)
    
    # Save all extracted data
    save_extracted_data(N, e, ciphertexts)
    
    # Display complete attack workflow
    display_attack_workflow(N, e, ciphertexts)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Extraction interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
