#!/usr/bin/env python3
# create.py - ARLEN -OTP Account Management System (FINAL - ADMIN AMAN + VIP TOKEN)

import os
import sys
import time
import json
import subprocess
import platform
import math
import re
import requests
import socket
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# ==================== CEK DEPENDENSI ====================

def check_and_install_dependencies():
    required = {
        'requests': 'requests',
        'colorama': 'colorama'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"\033[93m⚠️  Menginstall package yang diperlukan: {', '.join(missing)}\033[0m")
        for package in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"\033[92m✓ {package} berhasil diinstall\033[0m")
            except:
                print(f"\033[91m✗ Gagal install {package}\033[0m")
                return False
        return True
    return True

# Install dependensi jika belum
check_and_install_dependencies()

# Inisialisasi colorama
init(autoreset=True)

# ==================== FUNGSI DASAR ====================

def get_whoami():
    try:
        if platform.system() == 'Windows':
            return os.environ.get('USERNAME', 'unknown')
        else:
            result = subprocess.run(['whoami'], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except:
        return 'unknown'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def rgb_color(tick, offset=0):
    r = int((math.sin(tick * 0.5 + offset) + 1) * 127)
    g = int((math.sin(tick * 0.5 + offset + 2) + 1) * 127)
    b = int((math.sin(tick * 0.5 + offset + 4) + 1) * 127)
    return f"\033[38;2;{r};{g};{b}m"

def gradient_text(text, tick, offset=0):
    result = ""
    for i, char in enumerate(text):
        color = rgb_color(tick, offset + i * 0.1)
        result += f"{color}{char}{Style.RESET_ALL}"
    return result

# ==================== FIREBASE CONFIG ====================

FIREBASE_CONFIG = {
    "databaseURL": "https://otpaxka-default-rtdb.asia-southeast1.firebasedatabase.app",
}

# ==================== FIREBASE REST API ====================

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
    
    # 🔥 TAMBAHKAN METHOD DELETE
    def delete(self, path):
        try:
            url = self._get_url(path)
            response = requests.delete(url, timeout=5)
            return response.status_code in [200, 201, 204]
        except:
            return False

firebase = FirebaseDB()

# ==================== TEST KONEKSI ====================

def test_firebase_connection():
    print(f"{Fore.CYAN}🔍 Mengecek koneksi ke Firebase...{Style.RESET_ALL}")
    try:
        hostname = FIREBASE_CONFIG['databaseURL'].replace('https://', '').split('/')[0]
        print(f"{Fore.CYAN}📡 DNS: {hostname}{Style.RESET_ALL}")
        try:
            ip = socket.gethostbyname(hostname)
            print(f"{Fore.GREEN}✅ DNS Resolve: {ip}{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}❌ Gagal resolve DNS!{Style.RESET_ALL}")
            return False
        
        test_url = firebase._get_url()
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ Firebase terhubung!{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Error {response.status_code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        return False

FIREBASE_AVAILABLE = test_firebase_connection()

if not FIREBASE_AVAILABLE:
    print(f"\n{Fore.RED}❌ Firebase tidak terhubung!{Style.RESET_ALL}")
    sys.exit(1)

# ==================== VIP TOKEN FUNCTIONS ====================

def get_vip_token_from_firebase():
    """Ambil VIP token dari Firebase"""
    try:
        url = "https://otpaxka-default-rtdb.asia-southeast1.firebasedatabase.app/vip_token.json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, str) and data.startswith('VIP-'):
                return data
        return None
    except:
        return None

def save_vip_token_to_firebase(token):
    """Simpan VIP token ke Firebase"""
    try:
        url = "https://otpaxka-default-rtdb.asia-southeast1.firebasedatabase.app/vip_token.json"
        resp = requests.put(url, json=token, timeout=5)
        return resp.status_code in [200, 201]
    except:
        return False

# ==================== ACCOUNT MANAGER ====================

# 🔥 DAFTAR ADMIN - TIDAK BISA DIBLOKIR / DIHAPUS
ADMIN_LIST = ['root', 'admin']  # Tambahkan username admin di sini

class AccountManager:
    def __init__(self):
        self.current_user = get_whoami()
        self.blocked_ids = []
        self.reports = []
        self.server_maintenance = False
        self.vip_token = None
        self.load_data()
        
    def load_data(self):
        try:
            data = firebase.get()
            if data:
                self.blocked_ids = data.get('blocked_ids', [])
                self.reports = data.get('reports', [])
                self.server_maintenance = data.get('maintenance', False)
                self.vip_token = data.get('vip_token', None)
        except:
            pass
    
    def save_data(self):
        try:
            data = {
                'blocked_ids': self.blocked_ids,
                'reports': self.reports,
                'maintenance': self.server_maintenance,
                'vip_token': self.vip_token
            }
            firebase.patch('', data)
        except:
            pass
    
    def create_account(self, username, role='PREMIUM', duration='7d'):
        try:
            duration_map = {
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '14d': timedelta(days=14),
                '30d': timedelta(days=30),
                '60d': timedelta(days=60),
                '90d': timedelta(days=90)
            }
            
            if duration not in duration_map:
                return False, "Durasi tidak valid"
            
            expiry = datetime.now() + duration_map[duration]
            
            account_data = {
                'username': username,
                'role': role,
                'created_at': datetime.now().isoformat(),
                'expiry': expiry.isoformat(),
                'status': 'ACTIVE'
            }
            
            success = firebase.put(f'accounts/{username}', account_data)
            
            if success:
                return True, f"Akun {role} untuk {username} berhasil dibuat (expiry: {expiry.strftime('%Y-%m-%d %H:%M')})"
            else:
                return False, "Gagal menyimpan ke Firebase"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def delete_account(self, username):
        """🔥 HAPUS AKUN dari Firebase - ADMIN TIDAK BISA DIHAPUS!"""
        # 🔥 CEK APAKAH USER ADALAH ADMIN
        if username in ADMIN_LIST:
            return False, f"⚠️ {username} adalah ADMIN, tidak bisa dihapus!"
        
        # Cek apakah user terdaftar
        accounts = self.get_accounts()
        if username not in accounts:
            return False, f"User {username} tidak ditemukan!"
        
        # 🔥 HAPUS DARI ACCOUNTS
        success = firebase.delete(f'accounts/{username}')
        
        if success:
            # 🔥 HAPUS JUGA DARI BLOCKED_IDS JIKA ADA
            if username in self.blocked_ids:
                self.blocked_ids.remove(username)
                self.save_data()
            
            # 🔥 HAPUS JUGA DARI TRIALS JIKA ADA
            try:
                firebase.delete(f'trials/{username}')
            except:
                pass
            
            # 🔥 HAPUS DARI USER_LIMITS JIKA ADA
            try:
                firebase.delete(f'user_limits/{username}')
            except:
                pass
            
            return True, f"✅ Akun {username} berhasil dihapus dari Firebase!"
        else:
            return False, "❌ Gagal menghapus akun!"
    
    def block_user(self, username):
        """Block user - ADMIN TIDAK BISA DIBLOKIR!"""
        if username in ADMIN_LIST:
            return False, f"⚠️ {username} adalah ADMIN, tidak bisa diblokir!"
        
        if username not in self.blocked_ids:
            self.blocked_ids.append(username)
            self.save_data()
            return True, f"✅ User {username} berhasil diblokir"
        return False, "User sudah diblokir"
    
    def unblock_user(self, username):
        """Unblock user"""
        if username in self.blocked_ids:
            self.blocked_ids.remove(username)
            self.save_data()
            return True, f"✅ User {username} berhasil dibuka blokirnya"
        return False, "User tidak terblokir"
    
    def get_accounts(self):
        try:
            data = firebase.get('accounts')
            return data or {}
        except:
            return {}
    
    def get_reports(self, limit=50):
        try:
            data = firebase.get('reports')
            reports = data or []
            return sorted(reports, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        except:
            return []
    
    def is_user_registered(self, username):
        accounts = self.get_accounts()
        return username in accounts
    
    def check_access(self):
        if self.current_user in ADMIN_LIST:
            return True, "OWNER"
        
        if self.server_maintenance:
            return False, "MAINTENANCE"
        
        if self.current_user in self.blocked_ids:
            return False, "BLOCKED"
        
        if not self.is_user_registered(self.current_user):
            return False, "NOT_REGISTERED"
        
        accounts = self.get_accounts()
        user_data = accounts.get(self.current_user)
        if user_data and user_data.get('expiry'):
            try:
                expiry = datetime.fromisoformat(user_data['expiry'])
                if datetime.now() > expiry:
                    return False, "EXPIRED"
            except:
                pass
        
        return True, user_data.get('role', 'PREMIUM') if user_data else 'PREMIUM'

# ==================== UI FUNCTIONS ====================

def print_header(manager):
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}🔧 ARLEN -OTP ADMIN PANEL{Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 60}╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Admin: {Fore.YELLOW}{manager.current_user}{Style.RESET_ALL}{' ' * (60 - 9 - len(manager.current_user))}{Fore.CYAN}║{Style.RESET_ALL}")
    
    # 🔥 TAMPILKAN VIP TOKEN DI HEADER (SEMBUNYIKAN)
    vip_token = manager.vip_token or get_vip_token_from_firebase()
    if vip_token:
        token_display = vip_token[:15] + '...' if len(vip_token) > 15 else vip_token
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}VIP Token: {Fore.YELLOW}{token_display}{Style.RESET_ALL}{' ' * (60 - 13 - len(token_display))}{Fore.CYAN}║{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}VIP Token: {Fore.RED}BELUM DISET{Style.RESET_ALL}{' ' * 31}{Fore.CYAN}║{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")

def print_menu(selected=0, tick=0):
    color = rgb_color(tick)
    items = [
        ("📝 Create Akun", "Buat akun baru", Fore.GREEN),
        ("📋 List Akun", "Lihat semua akun", Fore.CYAN),
        ("🗑️ Hapus Akun", "Hapus akun dari Firebase", Fore.RED),
        ("🔑 VIP Token", "Set/Update token VIP", Fore.MAGENTA),
        ("🔧 Maintenance", "Atur mode maintenance", Fore.YELLOW),
        ("🚫 Block ID", "Blokir/buka blokir user", Fore.RED),
        ("📊 List Laporan", "Lihat laporan user", Fore.MAGENTA),
        ("🚪 Exit", "Keluar dari menu", Fore.WHITE)
    ]
    print()
    print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {color}📋 MENU ADMINISTRATOR{Style.RESET_ALL}{' ' * 35}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
    print()
    for i, (label, desc, fg) in enumerate(items):
        if i == selected:
            print(f"  {Fore.CYAN}▶ {fg}{label}{Style.RESET_ALL}  ─ {desc}")
        else:
            grad_label = gradient_text(label, tick, i * 2)
            print(f"     {grad_label}  ─ {desc}")
    print()
    print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {color}↑/↓{Style.RESET_ALL}  : Navigasi  {color}ENTER{Style.RESET_ALL}  : Pilih  {color}Q{Style.RESET_ALL}  : Keluar  {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")

def get_key():
    try:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except:
        try:
            import msvcrt
            return msvcrt.getch().decode()
        except:
            return None

# ==================== MENU FUNCTIONS ====================

def create_account_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}📝 CREATE NEW ACCOUNT{Style.RESET_ALL}{' ' * 34}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}Masukkan username (whoami) yang akan dibuatkan akun:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  Contoh: root, user_a, admin, dll{Style.RESET_ALL}")
    print()
    username = input(f"{Fore.WHITE}└─ Username: {Style.RESET_ALL}").strip()
    if not username:
        print(f"\n{Fore.RED}✗ Username tidak boleh kosong!{Style.RESET_ALL}")
        time.sleep(1)
        return
    if manager.is_user_registered(username):
        print(f"\n{Fore.YELLOW}⚠️  User {username} sudah terdaftar!{Style.RESET_ALL}")
        time.sleep(1)
        return
    print()
    print(f"{Fore.CYAN}Pilih Role:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[1] PREMIUM (10x limit){Style.RESET_ALL}")
    print(f"  {Fore.CYAN}[2] VIP (20x limit){Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}[3] OWNER (unlimited){Style.RESET_ALL}")
    print()
    role_choice = input(f"{Fore.WHITE}Pilih (1/2/3): {Style.RESET_ALL}").strip()
    roles = {'1': 'PREMIUM', '2': 'VIP', '3': 'OWNER'}
    role = roles.get(role_choice, 'PREMIUM')
    print()
    print(f"{Fore.CYAN}Pilih Durasi:{Style.RESET_ALL}")
    print(f"  [1] 24 jam")
    print(f"  [2] 7 hari")
    print(f"  [3] 14 hari")
    print(f"  [4] 30 hari")
    print(f"  [5] 60 hari")
    print(f"  [6] 90 hari")
    print()
    dur_choice = input(f"{Fore.WHITE}Pilih (1-6): {Style.RESET_ALL}").strip()
    durations = {'1': '24h', '2': '7d', '3': '14d', '4': '30d', '5': '60d', '6': '90d'}
    duration = durations.get(dur_choice, '7d')
    print()
    confirm = input(f"{Fore.YELLOW}Buat akun {role} untuk {username} dengan durasi {duration}? (y/n): {Style.RESET_ALL}").strip().lower()
    if confirm == 'y':
        success, msg = manager.create_account(username, role, duration)
        if success:
            print(f"\n{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ {msg}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    input()

def list_accounts_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}📋 LIST AKUN TERDAFTAR{Style.RESET_ALL}{' ' * 32}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    accounts = manager.get_accounts()
    if not accounts:
        print(f"{Fore.YELLOW}⚠️  Belum ada akun terdaftar{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}Total: {len(accounts)} akun{Style.RESET_ALL}")
        print(f"{Fore.CYAN}─{'─' * 58}{Style.RESET_ALL}")
        print()
        for username, data in accounts.items():
            role = data.get('role', 'UNKNOWN')
            expiry = data.get('expiry', '-')
            status = data.get('status', 'UNKNOWN')
            try:
                if expiry != '-':
                    exp_date = datetime.fromisoformat(expiry)
                    if datetime.now() > exp_date:
                        status = 'EXPIRED'
            except:
                pass
            is_admin = username in ADMIN_LIST
            is_blocked = username in manager.blocked_ids
            
            status_color = Fore.GREEN if status == 'ACTIVE' else Fore.RED
            block_status = "🔴 BLOCKED" if is_blocked else "🟢 ACTIVE"
            block_color = Fore.RED if is_blocked else Fore.GREEN
            expiry_short = expiry[:16] if expiry != '-' else '-'
            admin_label = " 👑 ADMIN" if is_admin else ""
            
            print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Username: {Fore.YELLOW}{username}{admin_label}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Role    : {Fore.CYAN}{role}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Status  : {status_color}{status}{Style.RESET_ALL}")
            if is_admin:
                print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Block   : {Fore.YELLOW}🛡️ ADMIN (TIDAK BISA DIBLOKIR){Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Block   : {block_color}{block_status}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Expiry  : {Fore.YELLOW}{expiry_short}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
            print()
    print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    input()

# 🔥 FITUR BARU: HAPUS AKUN
def delete_account_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}🗑️ HAPUS AKUN DARI FIREBASE{Style.RESET_ALL}{' ' * 27}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    
    accounts = manager.get_accounts()
    if not accounts:
        print(f"{Fore.YELLOW}⚠️  Belum ada akun terdaftar{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return
    
    # 🔥 FILTER ADMIN - TIDAK BISA DIHAPUS
    user_list = [u for u in accounts.keys() if u not in ADMIN_LIST]
    
    if not user_list:
        print(f"{Fore.YELLOW}⚠️  Tidak ada user non-admin yang bisa dihapus{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return
    
    selected = 0
    
    while True:
        clear_screen()
        print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}🗑️ HAPUS AKUN DARI FIREBASE{Style.RESET_ALL}{' ' * 27}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        print()
        
        print(f"{Fore.CYAN}Pilih user yang akan dihapus (↑/↓ navigasi, ENTER pilih, Q kembali):{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Admin tidak bisa dihapus{Style.RESET_ALL}")
        print()
        
        for i, username in enumerate(user_list):
            is_blocked = username in manager.blocked_ids
            status_color = Fore.RED if is_blocked else Fore.GREEN
            status_text = "🔴 BLOCKED" if is_blocked else "🟢 ACTIVE"
            
            if i == selected:
                print(f"  {Fore.CYAN}▶ {username} → {status_color}{status_text}{Style.RESET_ALL}")
            else:
                print(f"     {username} → {status_color}{status_text}{Style.RESET_ALL}")
        
        print()
        print(f"{Fore.CYAN}↑/↓: Navigasi | ENTER: Pilih | Q: Kembali{Style.RESET_ALL}")
        
        key = get_key()
        
        if key == '\x1b[A':
            selected = (selected - 1) % len(user_list)
        elif key == '\x1b[B':
            selected = (selected + 1) % len(user_list)
        elif key in ['\r', '\n']:
            username = user_list[selected]
            
            # 🔥 TAMPILKAN KONFIRMASI
            print()
            print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}⚠️  PERINGATAN!{Style.RESET_ALL}{' ' * 37}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Anda akan menghapus akun: {Fore.YELLOW}{username}{Style.RESET_ALL}{' ' * (50 - len(username) - 28)}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}⚠️  Data AKAN HILANG PERMANEN!{Style.RESET_ALL}{' ' * 16}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * 50}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Yang akan dihapus:{Style.RESET_ALL}{' ' * 34}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}• Akun dari 'accounts'{Style.RESET_ALL}{' ' * 31}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}• Data dari 'user_limits'{Style.RESET_ALL}{' ' * 29}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}• Data dari 'trials'{Style.RESET_ALL}{' ' * 33}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}• ID dari 'blocked_ids'{Style.RESET_ALL}{' ' * 26}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
            print()
            
            confirm = input(f"{Fore.RED}⚠️  Yakin ingin menghapus {username}? (y/n): {Style.RESET_ALL}").strip().lower()
            if confirm == 'y':
                confirm2 = input(f"{Fore.RED}⚠️  KETIK 'yes' untuk konfirmasi: {Style.RESET_ALL}").strip().lower()
                if confirm2 == 'yes':
                    success, msg = manager.delete_account(username)
                    if success:
                        print(f"\n{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.RED}✗ {msg}{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.YELLOW}⚠️  Konfirmasi gagal, dibatalkan{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
            
            time.sleep(1.5)
        elif key in ['q', 'Q']:
            break

# 🔥 FITUR BARU: VIP TOKEN MENU
def vip_token_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.MAGENTA}🔑 VIP TOKEN MANAGEMENT{Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    
    # 🔥 AMBIL TOKEN SAAT INI
    current_token = manager.vip_token or get_vip_token_from_firebase()
    
    print(f"{Fore.CYAN}📌 Token VIP Saat Ini:{Style.RESET_ALL}")
    if current_token:
        print(f"{Fore.GREEN}  {current_token}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  (disimpan di Firebase){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}  ❌ BELUM ADA TOKEN VIP!{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}─{'─' * 58}{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}📝 Masukkan token VIP baru:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Format: VIP-XXXX-XXXX-XXXX-XXXX{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Contoh: VIP-7948-2B65-EB9E-7D6D{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}  (Kosongkan untuk menghapus token){Style.RESET_ALL}")
    print()
    
    new_token = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
    
    if new_token == "":
        # 🔥 HAPUS TOKEN
        confirm = input(f"\n{Fore.RED}⚠️  Hapus token VIP? (y/n): {Style.RESET_ALL}").strip().lower()
        if confirm == 'y':
            success = save_vip_token_to_firebase(None)
            if success:
                manager.vip_token = None
                manager.save_data()
                print(f"\n{Fore.GREEN}✅ Token VIP berhasil dihapus!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}❌ Gagal menghapus token!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
    else:
        # 🔥 VALIDASI TOKEN
        if not new_token.startswith('VIP-'):
            print(f"\n{Fore.RED}❌ Token tidak valid! Harus dimulai dengan 'VIP-'{Style.RESET_ALL}")
            time.sleep(1.5)
            print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
            input()
            return
        
        # 🔥 SIMPAN TOKEN
        confirm = input(f"\n{Fore.YELLOW}Simpan token VIP? (y/n): {Style.RESET_ALL}").strip().lower()
        if confirm == 'y':
            success = save_vip_token_to_firebase(new_token)
            if success:
                manager.vip_token = new_token
                manager.save_data()
                print(f"\n{Fore.GREEN}✅ Token VIP berhasil disimpan!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📌 Token: {new_token}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}❌ Gagal menyimpan token!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    input()

def maintenance_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.YELLOW}🔧 MAINTENANCE SERVER{Style.RESET_ALL}{' ' * 33}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    current = "ON" if manager.server_maintenance else "OFF"
    color = Fore.RED if manager.server_maintenance else Fore.GREEN
    print(f"{Fore.WHITE}Status saat ini: {color}{current}{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}[1] Turn ON (Aktifkan maintenance){Style.RESET_ALL}")
    print(f"{Fore.CYAN}[2] Turn OFF (Nonaktifkan maintenance){Style.RESET_ALL}")
    print(f"{Fore.CYAN}[3] Kembali{Style.RESET_ALL}")
    print()
    choice = input(f"{Fore.WHITE}Pilih (1/2/3): {Style.RESET_ALL}").strip()
    if choice == '1':
        manager.server_maintenance = True
        manager.save_data()
        print(f"\n{Fore.RED}⚠️  Maintenance diaktifkan!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Semua user akan dikeluarkan dari server{Style.RESET_ALL}")
    elif choice == '2':
        manager.server_maintenance = False
        manager.save_data()
        print(f"\n{Fore.GREEN}✓ Maintenance dinonaktifkan{Style.RESET_ALL}")
        print(f"{Fore.GREEN}User bisa login kembali{Style.RESET_ALL}")
    else:
        return
    print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    input()

def block_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}🚫 BLOCK / UNBLOCK USER{Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    
    accounts = manager.get_accounts()
    if not accounts:
        print(f"{Fore.YELLOW}⚠️  Belum ada akun terdaftar{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return
    
    # 🔥 FILTER ADMIN - TIDAK BISA DIPILIH UNTUK DIBLOKIR
    user_list = [u for u in accounts.keys() if u not in ADMIN_LIST]
    
    if not user_list:
        print(f"{Fore.YELLOW}⚠️  Tidak ada user non-admin yang bisa diblokir{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return
    
    selected = 0
    
    while True:
        clear_screen()
        print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}🚫 BLOCK / UNBLOCK USER{Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        print()
        
        print(f"{Fore.CYAN}Pilih user (↑/↓ navigasi, ENTER pilih, Q kembali):{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Admin tidak bisa diblokir{Style.RESET_ALL}")
        print()
        
        for i, username in enumerate(user_list):
            is_blocked = username in manager.blocked_ids
            status_color = Fore.RED if is_blocked else Fore.GREEN
            status_text = "🔴 BLOCKED" if is_blocked else "🟢 ACTIVE"
            
            if i == selected:
                print(f"  {Fore.CYAN}▶ {username} → {status_color}{status_text}{Style.RESET_ALL}")
            else:
                print(f"     {username} → {status_color}{status_text}{Style.RESET_ALL}")
        
        print()
        print(f"{Fore.CYAN}↑/↓: Navigasi | ENTER: Pilih | Q: Kembali{Style.RESET_ALL}")
        
        key = get_key()
        
        if key == '\x1b[A':
            selected = (selected - 1) % len(user_list)
        elif key == '\x1b[B':
            selected = (selected + 1) % len(user_list)
        elif key in ['\r', '\n']:
            username = user_list[selected]
            is_blocked = username in manager.blocked_ids
            
            if is_blocked:
                confirm = input(f"\n{Fore.YELLOW}Buka blokir {username}? (y/n): {Style.RESET_ALL}").strip().lower()
                if confirm == 'y':
                    success, msg = manager.unblock_user(username)
                    print(f"\n{Fore.GREEN if success else Fore.RED}{'✓' if success else '✗'} {msg}{Style.RESET_ALL}")
            else:
                confirm = input(f"\n{Fore.RED}⚠️  Blokir {username}? (y/n): {Style.RESET_ALL}").strip().lower()
                if confirm == 'y':
                    success, msg = manager.block_user(username)
                    print(f"\n{Fore.GREEN if success else Fore.RED}{'✓' if success else '✗'} {msg}{Style.RESET_ALL}")
            
            time.sleep(1)
        elif key in ['q', 'Q']:
            break

def reports_menu(manager):
    clear_screen()
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.MAGENTA}📊 LIST LAPORAN{Style.RESET_ALL}{' ' * 36}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    
    reports = manager.get_reports()
    
    if not reports:
        print(f"{Fore.YELLOW}⚠️  Belum ada laporan{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}Total: {len(reports)} laporan{Style.RESET_ALL}")
        print(f"{Fore.CYAN}─{'─' * 58}{Style.RESET_ALL}")
        print()
        
        for i, report in enumerate(reports[:20]):
            username = report.get('username', 'unknown')
            timestamp = report.get('timestamp', '')
            message = report.get('message', '')[:80]
            status = report.get('status', 'PENDING')
            
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = timestamp[:16]
            
            status_color = Fore.GREEN if status == 'RESOLVED' else Fore.YELLOW
            
            print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}#{i+1}  ID: {Fore.YELLOW}{username}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Waktu: {Fore.CYAN}{time_str}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Pesan: {Fore.WHITE}{message}{'...' if len(message) >= 80 else ''}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}Status: {status_color}{status}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
            print()
    
    print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    input()

# ==================== MAIN ====================

def main():
    try:
        is_termux = os.path.exists("/data/data/com.termux/files/usr")
        
        manager = AccountManager()
        selected = 0
        items = ["create", "list", "delete", "vip", "maintenance", "block", "reports", "exit"]
        tick = 0
        
        clear_screen()
        print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}🔧 ARLEN -OTP ADMIN PANEL{Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 60}╣{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Admin: {Fore.YELLOW}{manager.current_user}{Style.RESET_ALL}{' ' * (60 - 9 - len(manager.current_user))}{Fore.CYAN}║{Style.RESET_ALL}")
        
        # 🔥 TAMPILKAN VIP TOKEN
        vip_token = manager.vip_token or get_vip_token_from_firebase()
        if vip_token:
            token_display = vip_token[:15] + '...' if len(vip_token) > 15 else vip_token
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}VIP Token: {Fore.YELLOW}{token_display}{Style.RESET_ALL}{' ' * (60 - 13 - len(token_display))}{Fore.CYAN}║{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}VIP Token: {Fore.RED}BELUM DISET{Style.RESET_ALL}{' ' * 31}{Fore.CYAN}║{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        print()
        
        print(f"{Fore.GREEN}✅ Firebase terhubung!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📱 Database: {FIREBASE_CONFIG['databaseURL']}{Style.RESET_ALL}")
        print()
        
        # Cek akses admin
        status, role = manager.check_access()
        if not status:
            if role == "MAINTENANCE":
                print(f"{Fore.YELLOW}⚠️  Server dalam maintenance mode{Style.RESET_ALL}")
                time.sleep(2)
            elif role == "BLOCKED":
                print(f"{Fore.RED}🚫 Admin ID diblokir!{Style.RESET_ALL}")
                time.sleep(2)
                sys.exit(0)
            elif role == "NOT_REGISTERED":
                print(f"{Fore.RED}❌ Admin belum terdaftar!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Silakan daftar dulu di menu Create Akun{Style.RESET_ALL}")
                time.sleep(2)
            elif role == "EXPIRED":
                print(f"{Fore.RED}⏰ Admin expired!{Style.RESET_ALL}")
                time.sleep(2)
        
        if is_termux:
            print(f"{Fore.GREEN}✓ Mode Termux terdeteksi{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  Gunakan tombol ↑/↓ untuk navigasi{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  ENTER untuk memilih, Q untuk keluar{Style.RESET_ALL}")
            print()
            time.sleep(1)
        
        while True:
            try:
                clear_screen()
                tick += 0.05
                print_header(manager)
                print_menu(selected, tick)
                
                key = get_key()
                
                if key == '\x1b[A':
                    selected = (selected - 1) % len(items)
                elif key == '\x1b[B':
                    selected = (selected + 1) % len(items)
                elif key in ['\r', '\n', '\x1b[C']:
                    choice = items[selected]
                    if choice == "create":
                        create_account_menu(manager)
                    elif choice == "list":
                        list_accounts_menu(manager)
                    elif choice == "delete":
                        delete_account_menu(manager)
                    elif choice == "vip":
                        vip_token_menu(manager)  # 🔥 FITUR BARU
                    elif choice == "maintenance":
                        maintenance_menu(manager)
                    elif choice == "block":
                        block_menu(manager)
                    elif choice == "reports":
                        reports_menu(manager)
                    elif choice == "exit":
                        print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                        time.sleep(0.5)
                        print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                        sys.exit(0)
                elif key in ['q', 'Q']:
                    print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                    time.sleep(0.5)
                    print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                    sys.exit(0)
                    
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                time.sleep(0.5)
                sys.exit(0)
            except Exception as e:
                print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
        time.sleep(0.5)
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()