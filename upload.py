import requests
import base64
import os
import json

# ===== KONFIGURASI =====
TOKEN = "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"  # Token Anda
REPO = "AXKADEV/OtpSpamer"
BRANCH = "main"
# =======================

def upload_file(file_path):
    """Upload file ke GitHub"""
    
    # Cek file
    if not os.path.exists(file_path):
        print(f"❌ File '{file_path}' tidak ditemukan!")
        return False
    
    # Baca dan encode file
    with open(file_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    
    file_name = os.path.basename(file_path)
    
    # URL API
    url = f"https://api.github.com/repos/{REPO}/contents/{file_name}"
    
    # Header
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Cek apakah file sudah ada
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Update file yang sudah ada
        sha = response.json()["sha"]
        data = {
            "message": f"Update {file_name}",
            "content": content,
            "sha": sha,
            "branch": BRANCH
        }
        print(f"📝 File '{file_name}' sudah ada, mengupdate...")
        response = requests.put(url, headers=headers, json=data)
    else:
        # Upload file baru
        data = {
            "message": f"Upload {file_name}",
            "content": content,
            "branch": BRANCH
        }
        print(f"📤 Upload file '{file_name}'...")
        response = requests.put(url, headers=headers, json=data)
    
    # Cek hasil
    if response.status_code in [200, 201]:
        print(f"✅ BERHASIL! File '{file_name}' terupload!")
        print(f"🔗 https://github.com/{REPO}/blob/{BRANCH}/{file_name}")
        return True
    else:
        print(f"❌ GAGAL: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return False

def upload_multiple_files(file_list):
    """Upload banyak file sekaligus"""
    success = 0
    failed = 0
    
    for file_path in file_list:
        if upload_file(file_path):
            success += 1
        else:
            failed += 1
        print("-" * 40)
    
    print(f"\n📊 Selesai! Berhasil: {success}, Gagal: {failed}")

# ===== CARA PAKAI =====

if __name__ == "__main__":
    print("🚀 GITHUB UPLOAD TOOL")
    print("=" * 40)
    
    # Cara 1: Upload satu file
    # upload_file("script.py")
    
    # Cara 2: Upload banyak file
    # upload_multiple_files(["file1.py", "file2.txt", "file3.json"])
    
    # Cara 3: Input dari user
    file_path = input("📁 Masukkan nama file: ")
    upload_file(file_path)