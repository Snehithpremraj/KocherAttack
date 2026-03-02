#!/usr/bin/env python3
"""
RSA Key Verification and Test Encryption/Decryption
Hochschule Schmalkalden - Seminar Project

This script:
1. Verifies your key pair is mathematically valid
2. Creates a test message and encrypts it
3. Decrypts it to verify everything works
4. Then tries your actual ciphertext
"""

# Your FIXED_KEYS from server
FIXED_KEYS = {
    "N": 0x1771857005336953658518999659009240305834526953693897433758233644933438398464807721602276745287329606755410789615980891669228814736165758491738250883167532106482094911540022341509583871312208888418559879012060489932497536402208026098982538129621816866231928031161404282106862468625535295162216671090886363381455159222133003356590854668597311815626983256514199350808309869735358324369489917670676349901439640251196179097477906083678315347243699542254826693827035961671705073110176263352803265969763090111241608913951612326193292374679242190449727220650252706119369628276453905391832220912849749587171779057541601046448035727133921762768029561379311322413091217520962406102156756646250139646708334251229051648813082603543267267936730715292169603061665392633721071737687278253546800643381498460819616209323830469454929593242725297539968984874968331832521063140810255498216799007190236893326162203566595480846544339727754318145073,
    "e": 65537,
    "d": 0x13237059768075901468957602097911030334952397187734153174473677280360697221049544970071444846168385564783730981775148832753287920460048225784945920863191283289341183652193973128767867088395961643264835584450408395916882346057139885234396182245007516162156946355004897668681302185431577516007084791259087597063027049653152716533115247585236705925008805880271328881968388390478191537463324664275025704252346694925424284375182911002878241299655689414009650739415011431323705976807590146895760209791103033495239718773415317447367728036069722104954497007144484616838556478373098177514883275328792046004822578494592086319128328934118365219397312876786708839596164326483558445040839591688234605713988523439618224500751616215694635500489766868130218543157751600708479125908759706302704965315271653311524758523670592500880588027132888196838839047819153746332466427502570425234669492542428437518291100287824129965568941400965073941501143,
}

import os

def pkcs1_v15_pad(message_bytes, key_size_bytes):
    """Add PKCS#1 v1.5 padding"""
    message_len = len(message_bytes)
    
    if message_len > key_size_bytes - 11:
        raise ValueError("Message too long")
    
    # Calculate padding length
    padding_len = key_size_bytes - message_len - 3
    
    # Generate random non-zero padding
    padding = bytearray()
    while len(padding) < padding_len:
        byte = os.urandom(1)[0]
        if byte != 0:
            padding.append(byte)
    
    # Format: 0x00 0x02 [random padding] 0x00 [message]
    padded = bytes([0x00, 0x02]) + bytes(padding) + bytes([0x00]) + message_bytes
    
    return padded

def pkcs1_v15_unpad(padded_bytes):
    """Remove PKCS#1 v1.5 padding"""
    if padded_bytes[0] != 0x00 or padded_bytes[1] != 0x02:
        raise ValueError(f"Invalid padding: first bytes are {padded_bytes[0]:02x} {padded_bytes[1]:02x}")
    
    # Find the 0x00 separator
    separator_index = padded_bytes.find(b'\x00', 2)
    
    if separator_index == -1:
        raise ValueError("No padding separator found")
    
    return padded_bytes[separator_index + 1:]

def test_key_pair():
    """Test if the key pair works correctly"""
    print("="*70)
    print("STEP 1: KEY PAIR VALIDATION")
    print("="*70)
    
    N = FIXED_KEYS["N"]
    e = FIXED_KEYS["e"]
    d = FIXED_KEYS["d"]
    
    print(f"\nN: {N.bit_length()} bits")
    print(f"e: {e}")
    print(f"d: {d.bit_length()} bits")
    
    # Simple test
    test_msg = 12345
    encrypted = pow(test_msg, e, N)
    decrypted = pow(encrypted, d, N)
    
    if decrypted == test_msg:
        print(f"\n[✓] Key pair is mathematically valid!")
        print(f"[✓] Test: {test_msg} -> encrypt -> {encrypted} -> decrypt -> {decrypted}")
    else:
        print(f"\n[✗] Key pair is INVALID!")
        return False
    
    return True

def test_with_message():
    """Test full encryption/decryption with padding"""
    print("\n" + "="*70)
    print("STEP 2: TEST WITH REAL MESSAGE")
    print("="*70)
    
    N = FIXED_KEYS["N"]
    e = FIXED_KEYS["e"]
    d = FIXED_KEYS["d"]
    
    # Test message
    test_message = "flag{Hochschule_Schmalkalden_Timing_Attack_2026}"
    print(f"\n[*] Original message: {test_message}")
    
    # Convert to bytes
    message_bytes = test_message.encode('utf-8')
    print(f"[*] Message bytes: {message_bytes.hex()}")
    
    # Add PKCS#1 v1.5 padding
    key_size_bytes = (N.bit_length() + 7) // 8
    padded = pkcs1_v15_pad(message_bytes, key_size_bytes)
    print(f"[*] Padded length: {len(padded)} bytes")
    print(f"[*] First 40 bytes: {padded[:40].hex()}")
    
    # Convert to integer
    padded_int = int.from_bytes(padded, 'big')
    
    # Encrypt
    ciphertext = pow(padded_int, e, N)
    print(f"\n[*] Encrypted ciphertext:")
    print(f"    {ciphertext}")
    
    # Decrypt
    decrypted_int = pow(ciphertext, d, N)
    decrypted_bytes = decrypted_int.to_bytes(key_size_bytes, 'big')
    
    print(f"\n[*] Decrypted bytes (first 40): {decrypted_bytes[:40].hex()}")
    
    # Remove padding
    try:
        unpadded = pkcs1_v15_unpad(decrypted_bytes)
        decrypted_message = unpadded.decode('utf-8')
        
        print(f"[✓] Unpadded message: {decrypted_message}")
        
        if decrypted_message == test_message:
            print(f"\n[✓✓✓] FULL CYCLE WORKS PERFECTLY!")
            return True
        else:
            print(f"\n[✗] Message mismatch!")
            return False
            
    except Exception as e:
        print(f"\n[✗] Unpadding failed: {e}")
        return False

def test_actual_ciphertext():
    """Test with your actual ciphertext"""
    print("\n" + "="*70)
    print("STEP 3: TEST WITH YOUR ACTUAL CIPHERTEXT")
    print("="*70)
    
    N = FIXED_KEYS["N"]
    d = FIXED_KEYS["d"]
    
    # Your actual ciphertext from ciphertext.txt
    ciphertext = 72998219023597207703030436340605223403752765541785129770668414973770091308228914968816310736481377209356377497302658434904471685057246749767445645127601109622757477211455888363331354198056546249907330923983999165664234120857348416585920511359350130398045595880819269625369672117176456359975134952494042562164768366581741383325574623463599265547507120857579252482922363508842263049724415779946039338245027407254970627677168446608278050395825468489720132118041777932853659021449165890149057173223602858935337489108006569328143656593745779665279168959648712086977434442863319208916202184463864142878382369463989186330703821603011251954873959182562484955673034203761174865905209119773209298118492140297434940045762812069700124260168608869756395959569941892257888722347902124636236084461706259211775917136239944837130055439103270848567047912726512188492407597588573757747454353986231261985443978973851433233431208340667123398031606953477361154131565028121709892357118507073283109303214589660943092039061353631737267490860285324958144072835488922301987004294789119967962944240165182655601016133520862298780234495104936
    
    print(f"\n[*] Ciphertext length: {len(str(ciphertext))} digits")
    print(f"[*] First 60 chars: {str(ciphertext)[:60]}...")
    
    # Decrypt
    decrypted_int = pow(ciphertext, d, N)
    
    key_size_bytes = (N.bit_length() + 7) // 8
    decrypted_bytes = decrypted_int.to_bytes(key_size_bytes, 'big')
    
    print(f"\n[*] Decrypted bytes (first 40): {decrypted_bytes[:40].hex()}")
    print(f"[*] First byte: 0x{decrypted_bytes[0]:02x} (should be 0x00)")
    print(f"[*] Second byte: 0x{decrypted_bytes[1]:02x} (should be 0x02 for PKCS#1)")
    
    # Try to unpad
    try:
        unpadded = pkcs1_v15_unpad(decrypted_bytes)
        print(f"\n[✓] Successfully removed padding!")
        print(f"[*] Message length: {len(unpadded)} bytes")
        print(f"[*] Message hex: {unpadded.hex()}")
        
        # Try to decode
        try:
            message = unpadded.decode('utf-8')
            print(f"\n[✓✓✓] DECRYPTED MESSAGE:")
            print(f"\n    {message}\n")
            return True
        except:
            try:
                message = unpadded.decode('ascii', errors='replace')
                print(f"\n[✓] DECRYPTED MESSAGE (ASCII):")
                print(f"\n    {message}\n")
                return True
            except:
                print(f"\n[!] Could not decode as text, showing hex:")
                print(f"    {unpadded.hex()}\n")
                return False
                
    except ValueError as e:
        print(f"\n[✗] Unpadding failed: {e}")
        print(f"\n[!] DIAGNOSIS:")
        print(f"    The ciphertext was NOT encrypted with these keys!")
        print(f"    Possible reasons:")
        print(f"    1. Wrong ciphertext file")
        print(f"    2. Ciphertext was encrypted with different server/keys")
        print(f"    3. Ciphertext is corrupted")
        print(f"\n[!] SOLUTION:")
        print(f"    Generate fresh ciphertext with your current server:")
        print(f"    1. Start server: python3 server.py")
        print(f"    2. Send message and capture ciphertext")
        print(f"    3. Use that ciphertext for decryption")
        return False

def main():
    print("\n" + "="*70)
    print("🔐 RSA KEY AND CIPHERTEXT DIAGNOSTIC")
    print("   Hochschule Schmalkalden - Seminar Project")
    print("="*70 + "\n")
    
    # Step 1: Validate key pair
    if not test_key_pair():
        print("\n[FATAL] Key pair validation failed!")
        return
    
    # Step 2: Test with known message
    if not test_with_message():
        print("\n[WARNING] Test encryption failed!")
        return
    
    # Step 3: Try actual ciphertext
    test_actual_ciphertext()
    
    print("="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
