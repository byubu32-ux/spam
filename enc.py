#!/usr/bin/env python3
# encrypt_fix.py - Super Obfuscation SUPPORT IMPORT

import os
import sys
import base64
import zlib
import random
import string
import shutil

FILES_TO_ENCRYPT = [
    "main_engine.py",
    "main_engine2.py",
    "handlers.py",
    "useragents.py",
    "targets.py",
    "utils.py",
    "main.py",
    "telegram_tokens.py"
]

BACKUP_DIR = "backup_original"
ENCRYPTED_DIR = "encrypted_fix"

def obfuscate_code(code):
    compressed = zlib.compress(code.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    return encoded

def generate_random_vars(count=10):
    vars_list = []
    for _ in range(count):
        var = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 12)))
        vars_list.append(var)
    return vars_list

def encrypt_single_file(input_file, output_file):
    """Enkripsi file dengan SUPPORT IMPORT"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        encoded = obfuscate_code(original_code)
        vars_list = generate_random_vars(10)
        v1, v2, v3, v4, v5, v6, v7, v8, v9, v10 = vars_list
        
        # 🔥 WRAPPER YANG FULL SUPPORT IMPORT
        wrapper = f'''#!/usr/bin/env python3
# Obfuscated - {os.path.basename(input_file)}

import base64
import zlib
import sys
import os

# ===== DATA TERENKRIPSI =====
{v1} = "{encoded}"

# ===== DEKRIPSI =====
def {v2}():
    try:
        {v3} = zlib.decompress(base64.b64decode({v1}.encode()))
        {v4} = {v3}.decode()
        return {v4}
    except Exception as {v5}:
        return None

# ===== EKSEKUSI & EXPOSE FUNGSI =====
{v6} = {v2}()

if {v6}:
    # Eksekusi kode dengan globals() agar fungsi bisa di-import
    exec({v6}, globals())
    
    # EXPOSE semua fungsi, class, variabel ke __all__
    __all__ = []
    for {v7} in dir():
        if not {v7}.startswith("_"):
            __all__.append({v7})
    
    # TAMBAHKAN fungsi yang dibutuhkan main.py
    # (run_single_round, run_infinite_loop, TARGETS, dll)
    for {v8} in ['run_single_round', 'run_infinite_loop', 'TARGETS', 
                 'start_spam', 'send_message', 'get_targets']:
        if {v8} in globals():
            __all__.append({v8})
else:
    print(f"Failed to decrypt {{__file__}}")
    sys.exit(1)

# Auto-execute if main
if __name__ == "__main__":
    {v9} = None
    for {v10} in __all__:
        if {v10} == "main" or {v10}.endswith("_main"):
            {v9} = globals().get({v10})
            break
    if {v9}:
        {v9}()
'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(wrapper)
        
        os.chmod(output_file, 0o755)
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  🔐 SUPER OBFUSCATOR - FIX IMPORT                        ║
╠════════════════════════════════════════════════════════════╣
║  Support: import run_single_round, run_infinite_loop,    ║
║           TARGETS, dan semua fungsi lain                 ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(ENCRYPTED_DIR, exist_ok=True)
    
    print("📦 Backup files...")
    for f in FILES_TO_ENCRYPT:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join(BACKUP_DIR, f))
            print(f"   ✅ {f}")
    
    print("\n🔐 Encrypting files...")
    for f in FILES_TO_ENCRYPT:
        if not os.path.exists(f):
            continue
        output = os.path.join(ENCRYPTED_DIR, f)
        if encrypt_single_file(f, output):
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f}")

    print("\n" + "="*60)
    print("✅ DONE!")
    print(f"📂 Hasil: {ENCRYPTED_DIR}/")
    print(f"📂 Backup: {BACKUP_DIR}/")
    print("\n🚀 Jalankan:")
    print(f"   cd {ENCRYPTED_DIR}")
    print("   python3 main.py")
    print("="*60)

if __name__ == "__main__":
    main()