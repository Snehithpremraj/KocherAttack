#!/usr/bin/env python3
"""
RSA Timing Attack Server - HARDCODED KEYS with Certificate Exchange
Hochschule Schmalkalden - Seminar Project

Features:
- TLS handshake simulation (certificate exchange)
- Timing-vulnerable RSA decryption (AMPLIFIED for demo)
- Message storage (simulates database)
- Web UI (coffee shop demo)

BSI 3072-bit, no dependencies (pure Python)
"""

import socket
import json
import time
import threading
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============ RSA KEY GENERATION (Pure Python) ============

def is_prime(n, k=40):
    """Miller-Rabin primality test"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True

def generate_prime(bits):
    """Generate a random prime of given bit length"""
    print(f"    Generating {bits}-bit prime... ", end="", flush=True)
    while True:
        # Generate random odd number
        p = random.randrange(2**(bits-1), 2**bits)
        p |= 1  # Make it odd
        
        if is_prime(p):
            print(f"✓")
            return p

def modinv(a, m):
    """Modular inverse using Extended Euclidean Algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise Exception('Modular inverse does not exist')
    return (x % m + m) % m

def generate_rsa_keypair(bits=3072):
    """
    Generate RSA key pair
    Returns: (N, e, d, p, q)
    """
    print(f"\n[*] Generating {bits}-bit RSA key pair...")
    print(f"[*] This may take 30-60 seconds...\n")
    
    # Generate two large primes
    half_bits = bits // 2
    p = generate_prime(half_bits)
    q = generate_prime(half_bits)
    
    # Ensure p != q
    while p == q:
        q = generate_prime(half_bits)
    
    # Calculate N and φ(N)
    N = p * q
    phi = (p - 1) * (q - 1)
    
    # Choose e (standard value)
    e = 65537
    
    # Calculate d (private exponent)
    print(f"    Computing private exponent... ", end="", flush=True)
    d = modinv(e, phi)
    print(f"✓\n")
    
    return N, e, d, p, q

# =========================================================

# =============================================================================

class PureRSAServer:
    def __init__(self, key_bits=3072):
        # Generate fresh RSA keys on startup
        self.N, self.e, self.d, self.p, self.q = generate_rsa_keypair(key_bits)
        
        # Storage for encrypted messages
        self.stored_messages = []
        
        print("\n" + "="*70)
        print("🔓 RSA TIMING ATTACK SERVER (LEAK AMPLIFIED)")
        print("   Hochschule Schmalkalden - Seminar Project")
        print("="*70)
        print("Configuration:")
        print(f"  • Key size: {self.N.bit_length()} bits (BSI recommendation)")
        print(f"  • Public key distribution: TLS certificate simulation")
        print(f"  • Vulnerability: AMPLIFIED timing side-channel")
        print(f"  • Leak amplification: ENABLED (for demo purposes)")
        print("="*70)
        print("\n🔑 GENERATED KEY INFORMATION:")
        print("="*70)
        print(f"N (modulus):")
        print(f"  {self.N}")
        print(f"\ne (public exponent):")
        print(f"  {self.e}")
        print(f"\nd (private exponent):")
        print(f"  {self.d}")
        print(f"\np (first prime):")
        print(f"  {self.p}")
        print(f"\nq (second prime):")
        print(f"  {self.q}")
        print("\n" + "="*70)
        print(f"First 20 bits of d (LSB-first): ", end="")
        bits_str = ''.join(str((self.d >> i) & 1) for i in range(20))
        print(f"{bits_str}")
        print(f"Expected recovery value: {int(bits_str, 2)} (hex: {hex(int(bits_str, 2))})")
        print("="*70)
        print("\nEndpoints:")
        print("  • get_certificate - Simulates TLS handshake (public key exchange)")
        print("  • login - Accepts encrypted messages")
        print("  • decrypt_vulnerable - VULNERABLE timing oracle (amplified)")
        print("="*70 + "\n")

    def decrypt_vulnerable(self, ciphertext):
        """
        TIMING VULNERABLE RSA decryption WITH LEAK AMPLIFICATION
        Uses square-and-multiply algorithm WITHOUT constant-time protection
        
        Vulnerability: Execution time leaks bits of private exponent d
        - If d[i] = 1: Extra multiplication + DUMMY WORK → MUCH SLOWER
        - If d[i] = 0: Only squaring → FASTER
        
        LEAK AMPLIFICATION: Added deterministic extra work for 1-bits
        This makes the timing difference obvious for educational demo
        """
        c = ciphertext % self.N
        result = 1
        base = c
        exponent = self.d
        
        # LEAK AMPLIFIER: tune this to make timing difference obvious
        LEAK_AMPLIFY_ITERS = 500  # Increase if bits still wrong
        
        # VULNERABLE: Non-constant-time modular exponentiation
        while exponent > 0:
            if exponent & 1:
                # Normal multiply (already leaks)
                result = (result * base) % self.N
                
                # ⚠️ LEAK AMPLIFIER: Deterministic extra work for 1-bits
                # This makes the side-channel OBVIOUS for demo purposes
                dummy = 1
                for _ in range(LEAK_AMPLIFY_ITERS):
                    dummy = (dummy * 3) % self.N
                # (dummy is discarded, doesn't affect result)
            
            base = (base * base) % self.N
            exponent >>= 1
        
        return result
    
    def handle_tcp(self, data):
        """Handle incoming TCP requests"""
        try:
            req = json.loads(data)
            cmd = req.get("command")
            print(f"[TCP] Command: {cmd}")
            
            # ========== CERTIFICATE EXCHANGE (Simulates TLS Handshake) ==========
            if cmd == "get_certificate":
                print("[SERVER] Certificate requested (TLS handshake simulation)")
                print(f"[SERVER] Sending public key: N={self.N.bit_length()} bits, e={self.e}")
                return {
                    "status": "success",
                    "N": self.N,
                    "e": self.e,
                    "certificate_info": "Simulates X.509 certificate",
                    "issuer": "Hochschule Schmalkalden Demo CA",
                    "subject": "demo-server.schmalkalden.de",
                    "key_size": self.N.bit_length()
                }
            
            # ========== ENCRYPTED LOGIN (Application Data) ==========
            elif cmd == "login":
                username = req.get("username")
                enc_data = req.get("encrypted_data")
                
                if enc_data is None:
                    return {"status": "error", "message": "Missing encrypted_data"}
                
                # Store encrypted message (simulates database)
                message_id = len(self.stored_messages) + 1
                self.stored_messages.append({
                    "id": message_id,
                    "username": username,
                    "ciphertext": enc_data,
                    "timestamp": time.time()
                })
                
                print(f"[SERVER] Login from: {username}")
                print(f"[SERVER] Stored encrypted message #{message_id}")
                print(f"[SERVER] Ciphertext: {str(enc_data)[:60]}...")
                
                return {
                    "status": "success",
                    "message": f"Login accepted (ID: {message_id})"
                }
            
            # ========== VULNERABLE DECRYPTION ORACLE (AMPLIFIED + TIMING RETURNED) ==========
            elif cmd == "decrypt_vulnerable":
                c = int(req.get("ciphertext", 0)) % self.N
                
                # Measure timing (for attacker analysis)
                t0 = time.perf_counter()
                pt = self.decrypt_vulnerable(c)
                elapsed_us = round((time.perf_counter() - t0) * 1_000_000, 2)
                
                print(f"[SERVER] Decryption oracle called")
                print(f"[SERVER] Ciphertext: {str(c)[:40]}...")
                print(f"[SERVER] Time: {elapsed_us} μs")
                
                # Return plaintext AND timing (makes attack easier)
                return {
                    "status": "success",
                    "plaintext": pt,
                    "elapsed_us": elapsed_us  # ⚡ SERVER-SIDE TIMING RETURNED
                }
            
            # ========== UNKNOWN COMMAND ==========
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {cmd}"
                }
        
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def start_tcp(self):
        """Start TCP server on port 8080"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8080))
        s.listen(5)
        print("[TCP] Server listening on localhost:8080\n")
        
        while True:
            client, addr = s.accept()
            print(f"[TCP] Connection from {addr}")
            try:
                data = client.recv(8192).decode()
                if data:
                    response = json.dumps(self.handle_tcp(data))
                    client.send(response.encode())
            except Exception as e:
                print(f"[TCP] Error: {e}")
            finally:
                client.close()

class WebHandler(BaseHTTPRequestHandler):
    """HTTP handler for coffee shop demo UI"""
    rsa_server = None
    
    def log_message(self, format, *args):
        """Suppress HTTP access logs"""
        pass
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Schmalkalden Coffee Roasters - Artisan Coffee Since 1985</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Georgia', serif; 
            background: linear-gradient(135deg, #f5e6d3 0%, #d4a373 100%);
            color: #3e2723;
            line-height: 1.6;
        }
        header { 
            background: linear-gradient(to right, #3e2723, #5d4037); 
            color: #fff; 
            padding: 2rem; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        header p { 
            font-style: italic; 
            opacity: 0.9; 
            font-size: 1.1rem;
        }
        .container { 
            max-width: 1200px; 
            margin: 3rem auto; 
            padding: 0 2rem; 
        }
        .coffee-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 2rem; 
            margin: 3rem 0; 
        }
        .coffee-card { 
            background: #fff; 
            padding: 2rem; 
            border-radius: 12px; 
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 4px solid #8d6e63;
        }
        .coffee-card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 12px 24px rgba(0,0,0,0.25);
        }
        .coffee-card h3 { 
            color: #5d4037; 
            font-size: 1.5rem; 
            margin-bottom: 1rem;
            border-bottom: 2px solid #d4a373;
            padding-bottom: 0.5rem;
        }
        .coffee-card p { 
            color: #6d4c41; 
            line-height: 1.8;
        }
        .login-section { 
            background: #fff; 
            padding: 3rem; 
            border-radius: 12px; 
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            max-width: 500px; 
            margin: 3rem auto;
            border-top: 4px solid #8d6e63;
        }
        .login-section h2 { 
            color: #3e2723; 
            margin-bottom: 1.5rem;
            text-align: center;
            font-size: 1.8rem;
        }
        input { 
            width: 100%; 
            padding: 0.8rem; 
            margin: 0.5rem 0; 
            border: 2px solid #d4a373; 
            border-radius: 6px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        input:focus {
            outline: none;
            border-color: #8d6e63;
        }
        button { 
            width: 100%; 
            padding: 1rem; 
            background: linear-gradient(to right, #5d4037, #3e2723); 
            color: #fff; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 1.1rem;
            margin-top: 1rem;
            transition: background 0.3s ease;
            font-weight: bold;
        }
        button:hover { 
            background: linear-gradient(to right, #4e342e, #3e2723); 
        }
        #message { 
            margin-top: 1rem; 
            padding: 1rem; 
            border-radius: 6px; 
            display: none;
            text-align: center;
            font-weight: bold;
        }
        .success { 
            background: #c8e6c9; 
            color: #2e7d32; 
            border: 2px solid #4caf50;
        }
        .error { 
            background: #ffcdd2; 
            color: #c62828; 
            border: 2px solid #f44336;
        }
        .about-section {
            background: #fff;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            margin: 3rem 0;
            border-top: 4px solid #8d6e63;
        }
        .about-section h2 {
            color: #3e2723;
            margin-bottom: 1.5rem;
            font-size: 2rem;
        }
        .about-section p {
            color: #6d4c41;
            line-height: 1.8;
            font-size: 1.1rem;
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: #5d4037;
            font-style: italic;
            margin-top: 3rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>☕ Schmalkalden Coffee Roasters</h1>
        <p>Artisan Coffee from the Heart of Thuringia</p>
    </header>
    
    <div class="container">
        <div class="coffee-grid">
            <div class="coffee-card">
                <h3>Highland Blend</h3>
                <p>Handcrafted blends from Thuringian highlands. Freshly roasted daily since 1985.</p>
            </div>
            <div class="coffee-card">
                <h3>Morning Sunrise</h3>
                <p>100% Arabica from sustainable farms. Notes of citrus and almond with a smooth finish.</p>
            </div>
            <div class="coffee-card">
                <h3>Dark Forest</h3>
                <p>Rich chocolate and caramel flavors. Perfect for espresso and cold brew.</p>
            </div>
            <div class="coffee-card">
                <h3>Winter Spice</h3>
                <p>Seasonal blend with cinnamon and nutmeg. Limited edition for cozy evenings.</p>
            </div>
        </div>
        
        <div class="login-section">
            <h2>Customer Login</h2>
            <input type="text" id="username" placeholder="Username" />
            <input type="password" id="password" placeholder="Password" />
            <button onclick="login()">Login to Order</button>
            <div id="message"></div>
        </div>
        
        <div class="about-section">
            <h2>Our Story</h2>
            <p>Family-owned since 1985, Schmalkalden Roasters sources premium coffee beans directly from small farms worldwide. We roast in small batches using traditional drum roasters to preserve the unique flavor profiles and aromas of each origin.</p>
            <p>Our commitment to quality and sustainability has made us Thuringia's favorite coffee destination. Visit our café to experience the art of coffee roasting firsthand.</p>
        </div>
    </div>
    
    <footer>
        <p>🔒 Secure Login - Protected by RSA Encryption</p>
    </footer>
    
    <script>
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const msg = document.getElementById('message');
            
            if (!username || !password) {
                msg.textContent = 'Please enter both username and password';
                msg.className = 'error';
                msg.style.display = 'block';
                return;
            }
            
            try {
                // Get public key
                const pubkeyResp = await fetch('/api/get_certificate', {
                    method: 'POST'
                });
                const pubkey = await pubkeyResp.json();
                
                if (pubkey.status !== 'success') {
                    throw new Error('Failed to get public key');
                }
                
                // In real implementation, encrypt password with public key
                // For demo: just send plaintext (INSECURE!)
                const loginResp = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: username,
                        encrypted_data: password  // Should be RSA-encrypted!
                    })
                });
                
                const result = await loginResp.json();
                
                if (result.status === 'success') {
                    msg.textContent = '✓ Login successful! Welcome to Schmalkalden Roasters';
                    msg.className = 'success';
                } else {
                    msg.textContent = '✗ Login failed: ' + result.message;
                    msg.className = 'error';
                }
                msg.style.display = 'block';
                
            } catch (error) {
                msg.textContent = '✗ Connection error: ' + error.message;
                msg.className = 'error';
                msg.style.display = 'block';
            }
        }
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path in ['/api/get_certificate', '/api/login']:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                req_data = json.loads(post_data.decode())
                
                if self.path == '/api/get_certificate':
                    req_data['command'] = 'get_certificate'
                elif self.path == '/api/login':
                    req_data['command'] = 'login'
                
                response = self.server.rsa_server.handle_tcp(json.dumps(req_data))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

def main():
    # You can change key_bits here (default 3072 for BSI standard)
    # Use smaller value for faster generation during testing: key_bits=2048
    server = PureRSAServer(key_bits=3072)
    
    # Start TCP server in background
    tcp_thread = threading.Thread(target=server.start_tcp, daemon=True)
    tcp_thread.start()
    
    # Start HTTP server
    http_server = HTTPServer(('0.0.0.0', 8000), WebHandler)
    http_server.rsa_server = server
    print("[HTTP] Web UI available at http://localhost:8000\n")
    
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped")

if __name__ == "__main__":
    main()
