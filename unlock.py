#!/usr/bin/env python3
# unlock.py - Unlock Blocked ID

import os
import sys
import time
import requests
import socket
from colorama import Fore, Style, init

init(autoreset=True)

# ==================== FIREBASE CONFIG ====================
FIREBASE_CONFIG = {
    "databaseURL": "https://otpaxka-default-rtdb.asia-southeast1.firebasedatabase.app",
}

class FirebaseDB:
    def __init__(self):
        self.db_url = FIREBASE_CONFIG['databaseURL'].rstrip('/')
        
    def _get_url(self, path=""):
        path = path.strip('/')
        if path:
            return f"{self.db_url}/{path}.json"
        return f"{self.db_url}/.json"
    
    def get(self, path=""):
        try:
            url = self._get_url(path)
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def put(self, path, data):
        try:
            url = self._get_url(path)
            response = requests.put(url, json=data, timeout=5)
            return response.status_code in [200, 201]
        except:
            return False
    
    def patch(self, path, data):
        try:
            url = self._get_url(path)
            response = requests.patch(url, json=data, timeout=5)
            return response.status_code in [200, 201]
        except:
            return False

firebase = FirebaseDB()

# ==================== CEK KONEKSI ====================

def check_connection():
    try:
        url = firebase._get_url()
        response = requests.get(url, timeout=3)
        return response.status_code == 200
    except:
        return False

# ==================== FUNGSI UNLOCK ====================

def get_blocked_list():
    """Dapatkan daftar ID yang diblokir"""
    data = firebase.get('blocked_ids')
    return data or []

def save_blocked_list(blocked_list):
    """Simpan daftar block terbaru"""
    return firebase.put('blocked_ids', blocked_list)

def unlock_user(username):
    """Buka blokir user"""
    blocked = get_blocked_list()
    
    if username not in blocked:
        return False, f"❌ {username} tidak terblokir"
    
    blocked.remove(username)
    save_blocked_list(blocked)
    return True, f"✅ {username} berhasil dibuka blokirnya!"

def list_blocked():
    """Lihat semua yang diblokir"""
    blocked = get_blocked_list()
    return blocked

# ==================== MAIN ====================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}🔓 UNLOCK BLOCKED ID{Style.RESET_ALL}{' ' * 28}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print()
    
    # Cek koneksi
    if not check_connection():
        print(f"{Fore.RED}❌ Firebase tidak terhubung!{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.GREEN}✅ Firebase terhubung!{Style.RESET_ALL}")
    print()
    
    # List blocked
    blocked = list_blocked()
    
    if not blocked:
        print(f"{Fore.GREEN}✅ Tidak ada ID yang diblokir!{Style.RESET_ALL}")
        sys.exit(0)
    
    print(f"{Fore.YELLOW}📋 Daftar ID yang diblokir:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}─{'─' * 48}{Style.RESET_ALL}")
    for i, user in enumerate(blocked, 1):
        print(f"  {Fore.RED}[{i}]{Style.RESET_ALL} {Fore.YELLOW}{user}{Style.RESET_ALL}")
    print()
    
    print(f"{Fore.CYAN}[1] Buka semua{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[2] Buka satu ID{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[3] Keluar{Style.RESET_ALL}")
    print()
    
    choice = input(f"{Fore.WHITE}Pilih (1/2/3): {Style.RESET_ALL}").strip()
    
    if choice == '1':
        # Buka semua
        confirm = input(f"{Fore.RED}⚠️  Buka semua blokir? (y/n): {Style.RESET_ALL}").strip().lower()
        if confirm == 'y':
            save_blocked_list([])
            print(f"\n{Fore.GREEN}✅ Semua ID berhasil dibuka blokirnya!{Style.RESET_ALL}")
    
    elif choice == '2':
        # Buka satu
        print()
        for i, user in enumerate(blocked, 1):
            print(f"  {Fore.RED}[{i}]{Style.RESET_ALL} {Fore.YELLOW}{user}{Style.RESET_ALL}")
        
        print()
        idx = input(f"{Fore.WHITE}Pilih nomor: {Style.RESET_ALL}").strip()
        
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(blocked):
                username = blocked[idx]
                confirm = input(f"{Fore.YELLOW}Buka blokir {username}? (y/n): {Style.RESET_ALL}").strip().lower()
                if confirm == 'y':
                    success, msg = unlock_user(username)
                    print(f"\n{Fore.GREEN if success else Fore.RED}{msg}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Nomor tidak valid!{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}❌ Input tidak valid!{Style.RESET_ALL}")
    
    elif choice == '3':
        print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
