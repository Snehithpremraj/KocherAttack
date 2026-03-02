#!/usr/bin/env python3
"""
cipher.py - Test RSA Encryption/Decryption
Hochschule Schmalkalden - Seminar Project
"""

# Keys from server.py
N = 0x529d6c0634528a29ba4800abf257e40fa88432b3f6980e7b02f84773fd2f713733c9c9b863f33748e4bea1fcbcf4796fce21d8cf5fe53f3aeb7c3531bf8094d12338c5939b4013fc19df40c92281c537306b605cafcfcb8e999f8477b2a10f4a17c4c7693febc1cc11204e2a47240cc2a86de1c928574603351907f6e9dc5049b8e6255d4fd7751bb9466ee1ecfea41c8ad7abd71af613c11184135189ce330ba66a60290667789c2ea6e770084f3cbfa387f876fb4d0e0e234851c42fe286d8a75ca478655da2cdcc0abf858fffb166e78c9f2c3cce4231a7ec43a8b72f68d7008e8f529e76907a62052e0616a7b5a85a76cf29bd14e7b4e164b48f6f3b0cafa1c9fc08f57430bb82b3c468efaa07072cdff352e0445f0ad38885d8371f3719dd3dfc867f21ccdc30d8fc87cf40505adfe95d09cbe4d1eab5238142037db8fbc5433a4fb907b9dfbaf59998600abd00469730f965d29d444d660b4e5a84aab13a01f62ee59d66ea529630bc2d5344a25b5d138e8e0d4aae5d7ea096632a1e11

e = 65537

d = 0x4305a3bca402f0bb15fa3f4f074fea0d57100cf707a908de6119807b89f1374327d53720475cec85ce67ca104a06ab2ea0b4badc0c09aa161a50fe1f5d54522a67990caefaa763c2ea806f72cbddc2b9a6fbe71adba8b1f6590f89d64019a60b8e3e7561afe00c27efa9fb4cedaba50fc192ec57b5c4ba29b9bd301022d7b3737d06ff40be08f66b257b361f8aff9fdeb358a634aecbdf87a952d63055ff34cb4b7c9b544641246a8bb7704862e9c937006d8d48eb095eb77f29b4fc8904f85c3f3375662ebcf4da8a44c869545d1df586ebae6c623d7a36002202f21606b832246630aea036fded10ef46dbae1fd3dff4f6aca67d77193e97e6d6d26fccde8692242db321002cf9ad40de0f2099394a5d1fd7c62a8f4389e6efe7b47279b058017ef2330ac666d7cdb62315f5b4828fe992d5b1aef5f35c5680b95e2ed8be770ac55ba0a3f09d5eb0d1f2c379eb254728a931e5b4654d7fef3fff3f529abd147dbe0c7e4c871fa49ec6a357a41be91392727a12325f43debf9a1793a523f81

print("="*60)
print("TEST: Encrypt then Decrypt")
print("="*60)

# Original message
original = b"flag{HS_Schmalkalden_MITM_Attack_Success_2026}"
print(f"Original: {original.decode()}")
print(f"Original bytes: {len(original)} bytes")
print(f"Original hex: {original.hex()}\n")

# ========== ENCRYPTION ==========
print("[*] Encrypting...")
m = int.from_bytes(original, 'big')
print(f"    Message as integer: {m}")

ciphertext = pow(m, e, N)
print(f"    Ciphertext: {str(ciphertext)[:60]}...")
print(f"    Length: {len(str(ciphertext))} digits\n")

# ========== DECRYPTION ==========
print("[*] Decrypting...")
plaintext_int = pow(ciphertext, d, N)
print(f"    Plaintext as integer: {plaintext_int}")

# Convert back to bytes - IMPORTANT: Use correct byte length
message_byte_length = (plaintext_int.bit_length() + 7) // 8
plaintext_bytes = plaintext_int.to_bytes(message_byte_length, 'big')

print(f"    Plaintext bytes: {len(plaintext_bytes)} bytes")
print(f"    Plaintext hex: {plaintext_bytes.hex()}")

# Decode to string
try:
    decrypted = plaintext_bytes.decode('utf-8')
    print(f"    Decrypted: {decrypted}\n")
    
    # ========== VERIFICATION ==========
    print("="*60)
    if original.decode() == decrypted:
        print("✓ SUCCESS: Encryption/Decryption works correctly!")
    else:
        print("✗ FAILED: Messages don't match!")
        print(f"  Expected: {original.decode()}")
        print(f"  Got:      {decrypted}")
    print("="*60)
    
except UnicodeDecodeError as e:
    print(f"\n✗ ERROR: Cannot decode plaintext bytes")
    print(f"  Error: {e}")
    print(f"  Expected hex: {original.hex()}")
    print(f"  Got hex:      {plaintext_bytes.hex()}")
    print("\n[!] This means the keys don't match or there's a calculation error")
