#!/usr/bin/env python3
import socket
import json
import sys
import time

if len(sys.argv) != 4:
    print("Usage: python3 fuzz_all.py <host> <port> <wordlist.txt>")
    sys.exit(1)

host, port, wordlist_file = sys.argv[1], int(sys.argv[2]), sys.argv[3]
print(f"🔍 Fuzzing {host}:{port} with {wordlist_file} (ALL entries)")

with open(wordlist_file) as f:
    cmds = [line.strip() for line in f if line.strip()]
print(f"📜 Loaded {len(cmds)} commands to test...")

hits = []
for i, cmd in enumerate(cmds, 1):
    try:
        s = socket.socket()  # Fresh connection per request (robust)
        s.settimeout(2.0)    # Fail fast on hangs
        s.connect((host, port))
        
        req = json.dumps({"command": cmd})
        s.send(req.encode())
        resp_data = s.recv(8192).decode()  # Bigger buffer
        s.close()
        
        resp = json.loads(resp_data)
        if resp.get("status") == "success":
            hit_info = f"🎯 #{i}/{len(cmds)}: {cmd}"
            if "N" in resp:
                N_hex = hex(resp["N"])[2:20]
                hit_info += f" → N={N_hex}... e={resp.get('e', '?')}"
            if "time_us" in resp:
                hit_info += f" 💥 VULN! time={resp['time_us']}μs"
            print(hit_info)
            hits.append(cmd)
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
        break
    except Exception as e:
        pass  # Silent fail, continue

print(f"\n✅ SCAN COMPLETE | Found {len(hits)}/{len(cmds)} endpoints:")
for h in hits:
    print(f"   - {h}")
