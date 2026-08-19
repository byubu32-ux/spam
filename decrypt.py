#!/usr/bin/env python3
# decrypt.py - Decrypt Super Obfuscation

import os
import sys
import re
import base64
import zlib

def extract_encoded(file_path):
    """Ekstrak encoded string dari file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cari pattern: VARIABLE = "BASE64_STRING"
        match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(2)
        
        # Cari pattern: VARIABLE = 'BASE64_STRING'
        match = re.search(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*'([^']+)'", content)
        if match:
            return match.group(2)
        
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def decrypt_file(input_file, output_file):
    try:
        # Ekstrak encoded
        encoded = extract_encoded(input_file)
        if not encoded:
            print("❌ Gagal ekstrak encoded data!")
            return False
        
        print("🔍 Data ditemukan, mendekode...")
        
        # Decode base64 + decompress
        try:
            decoded = base64.b64decode(encoded.encode())
            decompressed = zlib.decompress(decoded)
            original_code = decompressed.decode('utf-8')
        except Exception as e:
            print(f"❌ Gagal decode: {e}")
            return False
        
        # Tulis file asli
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(original_code)
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  🔓 SUPER DECRYPTOR                                      ║
╠════════════════════════════════════════════════════════════╣
║  Kembalikan file obfuscated ke kode asli                ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Cara pakai:")
        print(f"  python3 {sys.argv[0]} <file_enc.py>")
        print()
        print("Contoh:")
        print(f"  python3 {sys.argv[0]} main_enc.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ File tidak ditemukan: {input_file}")
        sys.exit(1)
    
    output_file = input_file.replace("_enc.py", "_dec.py")
    if output_file == input_file:
        output_file = os.path.splitext(input_file)[0] + "_dec.py"
    
    print(f"📁 Input:  {input_file}")
    print(f"📁 Output: {output_file}")
    print()
    
    print("🔄 Mendekripsi...")
    if decrypt_file(input_file, output_file):
        print(f"✅ Berhasil! File asli: {output_file}")
        print(f"📌 Jalankan: python3 {output_file}")
    else:
        print("❌ Gagal mendekripsi!")

if __name__ == "__main__":
    main()