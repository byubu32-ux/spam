#!/usr/bin/env python3
# main.py - AXKA-OTP Spammer (FINAL - RAPIH + COWSAY + TANPA SOUND + PHISING)

import sys
import time
import platform
import os
import tty
import termios
import math
import random
import threading
import shutil
import re
import subprocess
import json
import hashlib
import secrets
import requests
import socket
import uuid
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from collections import deque

# 🔥 IMPORT DARI main_engine
from main_engine import run_single_round, run_infinite_loop, TARGETS

# 🔥 IMPORT DARI main_engine2
from main_engine2 import (
    run_spam_tele, run_spam_ngl, run_spam_report_tele,
    check_all_bots, get_user_id_from_username,
    run_react_wa, get_vip_token_from_firebase, save_vip_token_to_firebase,
    get_react_limit
)

init(autoreset=True)

VERSION = "1.0.0"
TOOLS_NAME = "AXKA-OTP"

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
        print(f"\033[93m⚠️  Menginstall package: {', '.join(missing)}\033[0m")
        for package in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"\033[92m✓ {package} berhasil diinstall\033[0m")
            except:
                print(f"\033[91m✗ Gagal install {package}\033[0m")
                return False
        return True
    return True

check_and_install_dependencies()

# ==================== SECURITY CONFIG ====================
MAX_ATTEMPTS = 5
BLOCK_DURATION = 300
RATE_LIMIT_WINDOW = 60
MAX_REQUESTS_PER_WINDOW = 30

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
    
    def update(self, path, data):
        return self.patch(path, data)

firebase = FirebaseDB()

# ==================== CEK KONEKSI ====================

def quick_check_firebase():
    try:
        url = firebase._get_url()
        response = requests.get(url, timeout=3)
        return response.status_code == 200
    except:
        return False

FIREBASE_AVAILABLE = quick_check_firebase()

if not FIREBASE_AVAILABLE:
    print(f"\033[91m❌ Firebase tidak terhubung!\033[0m")
    print(f"\033[93mCek koneksi internet atau firewall\033[0m")
    sys.exit(1)

# ==================== SECURITY SYSTEM ====================

class SecurityManager:
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_until = {}
        self.request_history = {}
        self.session_token = None
        self.last_activity = time.time()
        self.session_timeout = 1800
        
    def generate_session_token(self):
        self.session_token = secrets.token_hex(32)
        return self.session_token
    
    def validate_session(self):
        if not self.session_token:
            return False
        if time.time() - self.last_activity > self.session_timeout:
            return False
        return True
    
    def update_activity(self):
        self.last_activity = time.time()
    
    def check_rate_limit(self, user_id):
        now = time.time()
        if user_id not in self.request_history:
            self.request_history[user_id] = deque()
        while self.request_history[user_id] and self.request_history[user_id][0] < now - RATE_LIMIT_WINDOW:
            self.request_history[user_id].popleft()
        if len(self.request_history[user_id]) >= MAX_REQUESTS_PER_WINDOW:
            return False, "Rate limit exceeded. Please wait."
        self.request_history[user_id].append(now)
        return True, "OK"
    
    def record_failed_attempt(self, user_id):
        now = time.time()
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = []
        self.failed_attempts[user_id].append(now)
        self.failed_attempts[user_id] = [t for t in self.failed_attempts[user_id] if t > now - 3600]
        if len(self.failed_attempts[user_id]) >= MAX_ATTEMPTS:
            self.blocked_until[user_id] = now + BLOCK_DURATION
            return True, f"Blocked for {BLOCK_DURATION//60} minutes."
        return False, f"Attempt {len(self.failed_attempts[user_id])}/{MAX_ATTEMPTS}"
    
    def is_blocked(self, user_id):
        if user_id in self.blocked_until:
            if time.time() < self.blocked_until[user_id]:
                remaining = int(self.blocked_until[user_id] - time.time())
                return True, f"Blocked for {remaining//60}m {remaining%60}s"
            else:
                del self.blocked_until[user_id]
                if user_id in self.failed_attempts:
                    self.failed_attempts[user_id] = []
        return False, "OK"
    
    def reset_failed_attempts(self, user_id):
        if user_id in self.failed_attempts:
            self.failed_attempts[user_id] = []
        if user_id in self.blocked_until:
            del self.blocked_until[user_id]

security = SecurityManager()

# ==================== FIREBASE LIMIT SYSTEM ====================

def get_user_limit_data(username):
    try:
        user_limits = firebase.get('user_limits') or {}
        return user_limits.get(username, {})
    except:
        return {}

def save_user_limit_data(username, data):
    try:
        user_limits = firebase.get('user_limits') or {}
        user_limits[username] = data
        firebase.put('user_limits', user_limits)
        return True
    except:
        return False

def check_and_reset_firebase_limit(username, max_limit):
    data = get_user_limit_data(username)
    now = time.time()
    sent_count = data.get('sent_count', 0)
    limit_start = data.get('limit_start', now)
    
    if now - limit_start >= 1800:
        data['sent_count'] = 0
        data['limit_start'] = now
        data['last_used'] = now
        save_user_limit_data(username, data)
        return True, "Limit telah direset otomatis", data
    
    if sent_count >= max_limit:
        remaining_time = 1800 - (now - limit_start)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        return False, f"Limit habis! Reset dalam {minutes}m {seconds}s", data
    
    return True, f"Sisa {max_limit - sent_count}", data

def use_limit_firebase(username, max_limit):
    data = get_user_limit_data(username)
    now = time.time()
    sent_count = data.get('sent_count', 0)
    limit_start = data.get('limit_start', now)
    
    if now - limit_start >= 1800:
        sent_count = 0
        limit_start = now
        data['limit_start'] = limit_start
        data['sent_count'] = 0
    
    if sent_count >= max_limit:
        return False, "Limit habis!", data
    
    sent_count += 1
    data['sent_count'] = sent_count
    data['limit_start'] = limit_start
    data['last_used'] = now
    
    save_user_limit_data(username, data)
    return True, f"Limit tersisa {max_limit - sent_count}", data

# ==================== LIMIT REACT ====================

def use_react_limit(username):
    try:
        _, role = check_user_access()
        max_limit = get_react_limit(role if role else 'TRIAL')
        
        if role == 'TRIAL':
            max_limit = 1
        
        react_data = firebase.get(f'react_usage/{username}') or {}
        now = time.time()
        count = react_data.get('count', 0)
        last_reset = react_data.get('last_reset', now)
        
        if now - last_reset >= 1800:
            count = 0
            last_reset = now
        
        if count >= max_limit:
            remaining = 1800 - (now - last_reset)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return False, f"Limit React habis! Reset dalam {minutes}m {seconds}s"
        
        count += 1
        react_data['count'] = count
        react_data['last_reset'] = last_reset
        firebase.put(f'react_usage/{username}', react_data)
        return True, f"React tersisa {max_limit - count}"
    except Exception as e:
        return False, f"Error: {e}"

def get_react_remaining():
    try:
        username = get_whoami()
        _, role = check_user_access()
        max_limit = get_react_limit(role if role else 'TRIAL')
        
        if role == 'TRIAL':
            max_limit = 1
        
        react_data = firebase.get(f'react_usage/{username}') or {}
        now = time.time()
        count = react_data.get('count', 0)
        last_reset = react_data.get('last_reset', now)
        
        if now - last_reset >= 1800:
            return max_limit, "Reset tersedia"
        
        remaining = max(0, max_limit - count)
        remaining_time = max(0, 1800 - (now - last_reset))
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        return remaining, f"Reset {minutes}m {seconds}s"
    except:
        return 0, "Error"

# ==================== MATRIX LOADING ====================

class MatrixBackground:
    def __init__(self):
        try:
            self.width = shutil.get_terminal_size().columns
            self.height = shutil.get_terminal_size().lines
        except:
            self.width = 80
            self.height = 24
        self.width = max(60, self.width)
        self.height = max(15, self.height)
        self.columns = []
        self.chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
        self.init_columns()
    
    def init_columns(self):
        self.columns = []
        for x in range(self.width):
            length = random.randint(8, 20)
            col = {
                'x': x,
                'y': random.randint(-self.height, 0),
                'speed': random.uniform(0.5, 1.5),
                'length': length,
                'chars': [random.choice(self.chars) for _ in range(length)],
                'bright_pos': random.randint(0, length-1)
            }
            self.columns.append(col)
    
    def update(self):
        for col in self.columns:
            col['y'] += col['speed'] * 0.8
            if col['y'] > self.height + col['length']:
                col['y'] = random.randint(-self.height, 0)
                col['length'] = random.randint(8, 20)
                col['chars'] = [random.choice(self.chars) for _ in range(col['length'])]
                col['speed'] = random.uniform(0.5, 1.5)
                col['bright_pos'] = random.randint(0, col['length']-1)
            if random.random() < 0.03:
                for i in range(len(col['chars'])):
                    if random.random() < 0.3:
                        col['chars'][i] = random.choice(self.chars)
    
    def render(self, overlay_lines=None):
        sys.stdout.write('\033[?25l')
        sys.stdout.write('\033[H')
        screen = []
        for y in range(self.height):
            screen.append([' ' for _ in range(self.width)])
        for col in self.columns:
            x = col['x']
            start_y = int(col['y'])
            for i in range(col['length']):
                y = start_y + i
                if 0 <= y < self.height and 0 <= x < self.width:
                    char = col['chars'][i % len(col['chars'])]
                    if i == col['bright_pos']:
                        color = Fore.GREEN + Style.BRIGHT
                    elif i < col['bright_pos'] + 3 and i > col['bright_pos'] - 2:
                        color = Fore.GREEN
                    else:
                        color = Fore.GREEN + Style.DIM
                    screen[y][x] = color + char + Style.RESET_ALL
        for y in range(self.height):
            print(''.join(screen[y]))
        if overlay_lines:
            filtered = [line for line in overlay_lines if line.strip()]
            overlay_height = len(filtered)
            start_y = (self.height - overlay_height) // 2
            for i, line in enumerate(filtered):
                if line.strip():
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    x_pos = (self.width - len(clean_line)) // 2
                    if x_pos < 0:
                        x_pos = 0
                    sys.stdout.write(f'\033[{start_y + i};{x_pos}H')
                    print(line, end='')
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

def matrix_loading(duration=2.0):
    matrix = MatrixBackground()
    ascii_arlen = [
        " █████╗ ██╗  ██╗██╗  ██╗ █████╗",
        " ██╔══██╗╚██╗██╔╝╚██╗██╔╝██╔══██╗",
        " ███████║ ╚███╔╝  ╚███╔╝ ███████║",
        " ██╔══██║ ██╔██╗  ██╔██╗ ██╔══██║",
        " ██║  ██║██╔╝ ██╗██╔╝ ██╗██║  ██║",
        " ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝"
    ]
    start_time = time.time()
    tick = 0
    
    sys.stdout.write('\033[s')
    
    while time.time() - start_time < duration:
        tick += 0.15
        matrix.update()
        colored_ascii = []
        for line in ascii_arlen:
            colored_line = ""
            for i, char in enumerate(line):
                if char != ' ':
                    color = rgb_color(tick, i * 0.1)
                    colored_line += f"{color}{char}{Style.RESET_ALL}"
                else:
                    colored_line += " "
            colored_ascii.append(colored_line)
        progress = (time.time() - start_time) / duration
        dots = "." * (int((time.time() - start_time) * 4) % 4)
        loading_text = f"LOADING{dots}"
        loading_color = rgb_color(tick, 2)
        bar_length = min(30, matrix.width - 20)
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        bar_color = rgb_color(tick, 3)
        status_color = rgb_color(tick, 4)
        status_text = "INITIALIZING" if progress < 0.3 else "LOADING" if progress < 0.6 else "PREPARING" if progress < 0.8 else "READY"
        overlay = [
            "",
            *colored_ascii,
            "",
            f"{loading_color}{loading_text}{Style.RESET_ALL}",
            "",
            f"{bar_color}[{bar}] {int(progress * 100)}%{Style.RESET_ALL}",
            "",
            f"{status_color}{'─' * 18}{Style.RESET_ALL}",
            f"{status_color}  {status_text}  {Style.RESET_ALL}",
            f"{status_color}{'─' * 18}{Style.RESET_ALL}",
        ]
        matrix.render(overlay)
        time.sleep(0.015)
    
    sys.stdout.write('\033[u')
    sys.stdout.write('\033[J')
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()
    
    clear_screen()
    
# ==================== SISTEM TRIAL ====================

def check_trial_eligibility(username):
    try:
        trials = firebase.get('trials') or {}
        if username in trials:
            return False, "Already claimed trial"
        return True, "Eligible"
    except:
        return True, "Eligible"

def claim_trial(username):
    try:
        trials = firebase.get('trials') or {}
        now = datetime.now().isoformat()
        expiry = (datetime.now() + timedelta(hours=1)).isoformat()
        
        trials[username] = {
            'claimed_at': now,
            'expiry': expiry,
            'role': 'TRIAL',
            'limit': 1,
            'status': 'ACTIVE'
        }
        firebase.put('trials', trials)
        
        accounts = firebase.get('accounts') or {}
        accounts[username] = {
            'role': 'TRIAL',
            'limit': 1,
            'expiry': expiry,
            'status': 'ACTIVE',
            'trial': True
        }
        firebase.put('accounts', accounts)
        return True, expiry
    except:
        return False, None

def is_trial_expired(username):
    try:
        accounts = firebase.get('accounts') or {}
        if username in accounts:
            user_data = accounts[username]
            if user_data.get('trial') and user_data.get('expiry'):
                expiry = datetime.fromisoformat(user_data['expiry'])
                if datetime.now() > expiry:
                    return True
        return False
    except:
        return False

# ==================== SETTING PESAN SPAM NGL ====================

SPAM_NGL_MESSAGE = "Spam By AXKA 🔥"

def set_ngl_message():
    global SPAM_NGL_MESSAGE
    clear_screen()
    print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.YELLOW}✏️  SETTING PESAN SPAM NGL{Style.RESET_ALL}{' ' * 28}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}📝 Pesan saat ini:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   \"{SPAM_NGL_MESSAGE}\"{Style.RESET_ALL}")
    print()
    print(f"{Fore.WHITE}Masukkan pesan baru (kosongkan untuk reset ke default):{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   (Tekan ENTER tanpa mengetik apa pun untuk reset){Style.RESET_ALL}")
    print()
    new_message = input(f"{Fore.GREEN}└─> {Style.RESET_ALL}").strip()
    
    if new_message == "":
        SPAM_NGL_MESSAGE = "Spam By AXKA 🔥"
        print(f"\n{Fore.GREEN}✓ Pesan direset ke default!{Style.RESET_ALL}")
    else:
        SPAM_NGL_MESSAGE = new_message
        print(f"\n{Fore.GREEN}✓ Pesan berhasil diupdate!{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}📝 Pesan sekarang: \"{SPAM_NGL_MESSAGE}\"{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    input()

# ==================== ANIMASI ====================

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

# ==================== AUTHENTICATION SYSTEM ====================

user_session = {
    'role': None,
    'limit': 0,
    'sent_count': 0,
    'max_limit': 0,
    'is_infinite': False,
    'last_reset': None,
    'reset_time': None,
    'limit_start_time': None,
    'is_limited': False,
    'authenticated': False,
    'limit_used': False
}

def get_whoami():
    try:
        if platform.system() == 'Windows':
            return os.environ.get('USERNAME', 'unknown')
        else:
            result = subprocess.run(['whoami'], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except:
        return 'unknown'

def get_device_id():
    try:
        identifiers = [get_whoami()]
        try:
            import socket
            identifiers.append(socket.gethostname())
        except:
            pass
        try:
            import uuid
            identifiers.append(str(uuid.getnode()))
        except:
            pass
        salt = "ARLEN_OTP_SECURE_SALT_2026"
        combined = '|'.join(identifiers) + salt
        return hashlib.sha512(combined.encode()).hexdigest()[:32]
    except:
        return hashlib.sha512(get_whoami().encode()).hexdigest()[:32]

def check_user_access():
    try:
        username = get_whoami()
        device_id = get_device_id()
        
        if not FIREBASE_AVAILABLE:
            return False, "FIREBASE_NOT_CONNECTED"
        
        rate_ok, rate_msg = security.check_rate_limit(username)
        if not rate_ok:
            return False, f"RATE_LIMIT:{rate_msg}"
        
        blocked, block_msg = security.is_blocked(username)
        if blocked:
            return False, f"TEMP_BLOCKED:{block_msg}"
        
        try:
            maintenance = firebase.get('maintenance')
            if maintenance is None:
                maintenance = False
        except:
            maintenance = False
        
        if maintenance:
            return False, "MAINTENANCE"
        
        try:
            blocked_ids = firebase.get('blocked_ids')
            if blocked_ids is None:
                blocked_ids = []
        except:
            blocked_ids = []
        
        if username in blocked_ids or device_id in blocked_ids:
            return False, "BLOCKED"
        
        try:
            accounts = firebase.get('accounts')
            if accounts is None:
                accounts = {}
        except:
            accounts = {}
        
        user_data = None
        user_key = None
        
        if username in accounts:
            user_data = accounts[username]
            user_key = username
        elif device_id in accounts:
            user_data = accounts[device_id]
            user_key = device_id
        
        if not user_data:
            security.record_failed_attempt(username)
            return False, "NOT_REGISTERED"
        
        security.reset_failed_attempts(username)
        
        if user_data.get('trial') and user_data.get('expiry'):
            try:
                expiry = datetime.fromisoformat(user_data['expiry'])
                if datetime.now() > expiry:
                    if user_key in accounts:
                        accounts[user_key]['status'] = 'EXPIRED'
                        firebase.put('accounts', accounts)
                    return False, "TRIAL_EXPIRED"
            except:
                pass
        
        if user_data.get('expiry'):
            try:
                expiry = datetime.fromisoformat(user_data['expiry'])
                if datetime.now() > expiry:
                    if user_key in accounts:
                        del accounts[user_key]
                        firebase.put('accounts', accounts)
                    return False, "EXPIRED"
            except:
                pass
        
        if user_data.get('status') == 'EXPIRED':
            return False, "EXPIRED"
        
        role = user_data.get('role', 'PREMIUM')
        user_session['authenticated'] = True
        return True, role
        
    except Exception as e:
        return False, "SYSTEM_ERROR"

def get_user_info():
    try:
        username = get_whoami()
        accounts = firebase.get('accounts') or {}
        if username in accounts:
            return accounts[username]
        return None
    except:
        return None

def get_role_limit(role):
    limits = {'PREMIUM': 10, 'VIP': 20, 'OWNER': float('inf'), 'TRIAL': 1}
    return limits.get(role, 0)

def get_user_role():
    try:
        status, role = check_user_access()
        if status and role not in ['MAINTENANCE', 'BLOCKED', 'NOT_REGISTERED', 'EXPIRED', 'FIREBASE_NOT_CONNECTED', 'SYSTEM_ERROR', 'TRIAL_EXPIRED']:
            user_session['role'] = role
            user_session['limit'] = get_role_limit(role)
            user_session['max_limit'] = user_session['limit']
            return role
        user_session['authenticated'] = False
        return None
    except:
        user_session['authenticated'] = False
        return None

def check_and_reset_limit():
    if not user_session.get('authenticated', False):
        return False, "Not authenticated"
    
    username = get_whoami()
    max_limit = user_session.get('limit', 1)
    
    status, msg, data = check_and_reset_firebase_limit(username, max_limit)
    
    if status:
        user_session['sent_count'] = data.get('sent_count', 0)
        user_session['limit_start_time'] = data.get('limit_start', time.time())
        return True, msg
    else:
        user_session['sent_count'] = data.get('sent_count', 0)
        user_session['limit_start_time'] = data.get('limit_start', time.time())
        user_session['is_limited'] = True
        return False, msg

def get_remaining_limit():
    if not user_session.get('authenticated', False):
        return 0, "Not authenticated"
    
    username = get_whoami()
    max_limit = user_session.get('limit', 1)
    
    data = get_user_limit_data(username)
    sent_count = data.get('sent_count', 0)
    limit_start = data.get('limit_start', time.time())
    
    now = time.time()
    
    if now - limit_start >= 1800:
        return max_limit, "Reset tersedia"
    
    if max_limit == float('inf'):
        return float('inf'), None
    
    remaining = max(0, max_limit - sent_count)
    remaining_time = max(0, 1800 - (now - limit_start))
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    reset_info = f"Reset dalam {minutes}m {seconds}s"
    
    return remaining, reset_info

def is_limit_reached():
    if not user_session.get('authenticated', False):
        return True
    
    username = get_whoami()
    max_limit = user_session.get('limit', 1)
    
    if max_limit == float('inf'):
        return False
    
    data = get_user_limit_data(username)
    sent_count = data.get('sent_count', 0)
    limit_start = data.get('limit_start', time.time())
    
    if time.time() - limit_start >= 1800:
        return False
    
    return sent_count >= max_limit

def get_limit_info():
    if not user_session.get('authenticated', False):
        return "🔴 TIDAK TERDAFTAR", None
    
    username = get_whoami()
    max_limit = user_session.get('limit', 1)
    
    if max_limit == float('inf'):
        return "∞ UNLIMITED", None
    
    data = get_user_limit_data(username)
    sent_count = data.get('sent_count', 0)
    limit_start = data.get('limit_start', time.time())
    
    now = time.time()
    
    if now - limit_start >= 1800:
        sent_count = 0
        data['sent_count'] = 0
        data['limit_start'] = now
        save_user_limit_data(username, data)
        return f"🟢 0/{max_limit} (sisa {max_limit})", "⏰ Reset: tersedia"
    
    remaining = max(0, max_limit - sent_count)
    remaining_time = max(0, 1800 - (now - limit_start))
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    reset_info = f"⏰ Reset: {minutes}m {seconds}s"
    
    if remaining <= 0:
        return f"🔴 {sent_count}/{max_limit} (HABIS!)", reset_info
    elif remaining <= 3:
        return f"🟡 {sent_count}/{max_limit} (sisa {int(remaining)})", reset_info
    else:
        return f"🟢 {sent_count}/{max_limit} (sisa {int(remaining)})", reset_info

def use_limit_session():
    if not user_session.get('authenticated', False):
        return False, "Not authenticated"
    
    if user_session.get('limit_used', False):
        return True, "Limit sudah digunakan"
    
    username = get_whoami()
    max_limit = user_session.get('limit', 1)
    
    if max_limit == float('inf'):
        user_session['limit_used'] = True
        return True, "Unlimited"
    
    success, msg, data = use_limit_firebase(username, max_limit)
    if success:
        user_session['sent_count'] = data.get('sent_count', 0)
        user_session['limit_used'] = True
    return success, msg

def reset_limit_flag():
    user_session['limit_used'] = False

def reset_session_counter():
    pass

# ==================== REPORT SYSTEM ====================

def send_report(username, message):
    try:
        if not FIREBASE_AVAILABLE:
            return False, "Firebase tidak tersedia"
        if not message or len(message) < 10:
            return False, "Pesan minimal 10 karakter"
        if len(message) > 500:
            return False, "Pesan maksimal 500 karakter"
        dangerous_chars = ['<', '>', '{', '}', '[', ']', ';', '`']
        for char in dangerous_chars:
            if char in message:
                return False, f"Karakter '{char}' tidak diizinkan"
        
        today = datetime.now().date().isoformat()
        reports = firebase.get('reports') or []
        
        for report in reports:
            if report.get('username') == username:
                report_date = report.get('date', '')
                if report_date == today:
                    return False, "Anda sudah melapor hari ini"
        
        report_data = {
            'username': username,
            'device_id': get_device_id(),
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'date': today,
            'status': 'PENDING'
        }
        
        reports.append(report_data)
        firebase.put('reports', reports)
        
        seven_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        reports = [r for r in reports if r.get('date', '') >= seven_days_ago]
        firebase.put('reports', reports)
        
        return True, "Laporan berhasil dikirim"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_maintenance():
    try:
        if FIREBASE_AVAILABLE:
            return firebase.get('maintenance') or False
    except:
        pass
    return False

# ==================== UI COMPONENTS ====================

exec_data = {
    'target': '',
    'threads': 5,
    'total_api': len(TARGETS) if 'TARGETS' in dir() else 41,
    'status': 'Initializing...',
    'progress': 0,
    'sent': 0,
    'success': 0,
    'failed': 0,
    'last_log': 'Starting...'
}

# ==================== COWSAY BANNER ====================

def print_cowsay_banner():
    """Tampilkan banner dengan cowsay"""
    clear_screen()
    print()
    
    cowsay_path = shutil.which('cowsay')
    
    if cowsay_path:
        try:
            process = subprocess.Popen(
                ['cowsay', '-f', 'eyes', 'AXKA OTP'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            output, _ = process.communicate()
            
            if process.returncode == 0 and output:
                lines = output.decode('utf-8', errors='ignore').split('\n')
                colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
                for i, line in enumerate(lines):
                    if line.strip():
                        color = colors[i % len(colors)]
                        print(f"{color}{line}{Style.RESET_ALL}")
                    else:
                        print(line)
                return
        except:
            pass
    
    # FALLBACK
    print(f"""
{Fore.CYAN}  ╔══════════════════════════════════════════════════╗
  ║                                                      ║
  ║     {Fore.RED} █████╗ ██╗  ██╗██╗  ██╗ █████╗ {Fore.CYAN}║
  ║     {Fore.YELLOW}██╔══██╗╚██╗██╔╝╚██╗██╔╝██╔══██╗{Fore.CYAN}║
  ║     {Fore.GREEN}███████║ ╚███╔╝  ╚███╔╝ ███████║{Fore.CYAN}║
  ║     {Fore.BLUE}██╔══██║ ██╔██╗  ██╔██╗ ██╔══██║{Fore.CYAN}║
  ║     {Fore.MAGENTA}██║  ██║██╔╝ ██╗██╔╝ ██╗██║  ██║{Fore.CYAN}║
  ║     {Fore.RED}╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝{Fore.CYAN}║
  ║                                                      ║
  ╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

# ==================== USER INFORMATION ====================

def print_user_info(tick=0):
    color = rgb_color(tick)
    username = get_whoami()
    status, role = check_user_access()
    
    # STATUS
    if status:
        if role == "MAINTENANCE":
            status_text, status_color = "🔧 MAINTENANCE", Fore.YELLOW
        elif role == "BLOCKED":
            status_text, status_color = "🚫 DIBLOKIR", Fore.RED
        elif role == "EXPIRED":
            status_text, status_color = "⏰ EXPIRED", Fore.RED
        elif role in ['PREMIUM', 'VIP', 'OWNER']:
            status_text, status_color = f"✅ {role}", Fore.GREEN
        elif role == 'TRIAL':
            status_text, status_color = "🆓 TRIAL", Fore.CYAN
        else:
            status_text, status_color = "✅ AKTIF", Fore.GREEN
    else:
        if "FIREBASE_NOT_CONNECTED" in role:
            status_text, status_color = "❌ FIREBASE ERROR", Fore.RED
        elif "MAINTENANCE" in role:
            status_text, status_color = "🔧 MAINTENANCE", Fore.YELLOW
        elif "BLOCKED" in role or "TEMP_BLOCKED" in role:
            status_text, status_color = "🚫 DIBLOKIR", Fore.RED
        elif "EXPIRED" in role or "TRIAL_EXPIRED" in role:
            status_text, status_color = "⏰ EXPIRED", Fore.RED
        elif "RATE_LIMIT" in role:
            status_text, status_color = "⏳ RATE LIMIT", Fore.YELLOW
        elif "SYSTEM_ERROR" in role:
            status_text, status_color = "⚠️ SYSTEM ERROR", Fore.RED
        else:
            status_text, status_color = "❌ TIDAK TERDAFTAR", Fore.RED
    
    # EXPIRY
    expiry_text = "-"
    user_info = get_user_info()
    if user_info and user_info.get('expiry'):
        try:
            expiry = datetime.fromisoformat(user_info['expiry'])
            expiry_text = expiry.strftime('%Y-%m-%d %H:%M')
        except:
            pass
    
    # LIMIT OTP
    limit_info, reset_info = get_limit_info()
    
    # LIMIT REACT
    react_remaining, react_info = get_react_remaining()
    if react_remaining == float('inf'):
        react_text = "∞"
    else:
        react_text = f"{int(react_remaining)}"
    
    # BOX LEBAR 58
    W = 58
    
    print(f"{Fore.CYAN}┌{'─' * W}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}{' ' * 18}{color}👤 USER INFORMATION{Style.RESET_ALL}{' ' * 21}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}├{'─' * W}┤{Style.RESET_ALL}")
    
    # BARIS 1
    left1 = f"  {Fore.GREEN}ID     :{Style.RESET_ALL} {Fore.YELLOW}{username}{Style.RESET_ALL}"
    right1 = f"{Fore.GREEN}Status :{Style.RESET_ALL} {status_color}{status_text}{Style.RESET_ALL}"
    pad1 = W - len(left1) - len(right1) - 2
    pad1 = max(pad1, 4)
    print(f"{Fore.CYAN}│{Style.RESET_ALL}{left1}{' ' * pad1}{right1}{' ' * 2}{Fore.CYAN}│{Style.RESET_ALL}")
    
    # BARIS 2
    left2 = f"  {Fore.GREEN}Role   :{Style.RESET_ALL} {Fore.YELLOW}{role if status else '-'}{Style.RESET_ALL}"
    right2 = f"{Fore.GREEN}Limit  :{Style.RESET_ALL} {Fore.CYAN}{limit_info}{Style.RESET_ALL}"
    pad2 = W - len(left2) - len(right2) - 2
    pad2 = max(pad2, 4)
    print(f"{Fore.CYAN}│{Style.RESET_ALL}{left2}{' ' * pad2}{right2}{' ' * 2}{Fore.CYAN}│{Style.RESET_ALL}")
    
    # BARIS 3
    left3 = f"  {Fore.GREEN}Reset  :{Style.RESET_ALL} {Fore.YELLOW}{reset_info if reset_info else '-'}{Style.RESET_ALL}"
    right3 = f"{Fore.GREEN}React  :{Style.RESET_ALL} {Fore.MAGENTA}{react_text}{Style.RESET_ALL}"
    pad3 = W - len(left3) - len(right3) - 2
    pad3 = max(pad3, 4)
    print(f"{Fore.CYAN}│{Style.RESET_ALL}{left3}{' ' * pad3}{right3}{' ' * 2}{Fore.CYAN}│{Style.RESET_ALL}")
    
    # BARIS 4
    left4 = f"  {Fore.GREEN}Expiry :{Style.RESET_ALL} {Fore.YELLOW}{expiry_text}{Style.RESET_ALL}"
    right4 = f"{Fore.GREEN}Info   :{Style.RESET_ALL} {Fore.CYAN}{react_info}{Style.RESET_ALL}"
    pad4 = W - len(left4) - len(right4) - 2
    pad4 = max(pad4, 4)
    print(f"{Fore.CYAN}│{Style.RESET_ALL}{left4}{' ' * pad4}{right4}{' ' * 2}{Fore.CYAN}│{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}└{'─' * W}┘{Style.RESET_ALL}")

# ==================== BANNER ====================

def print_banner(tick=0):
    color = rgb_color(tick, 0)
    is_maintenance = check_maintenance()
    
    clear_screen()
    
    # COWSAY
    print_cowsay_banner()
    
    # INFO BAR
    print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {color}API{Style.RESET_ALL}  : {len(TARGETS)}{' ' * 8}{color}Version{Style.RESET_ALL}  : 1.0.0{' ' * 8}{color}Dev{Style.RESET_ALL}  : AXKA     {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
    
    # USER INFO
    print_user_info(tick)
    
    if is_maintenance:
        print(f"\n{Fore.RED}╔{'═' * 58}╗{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⚠️  SERVER DALAM MAINTENANCE - TIDAK DAPAT DIGUNAKAN{Style.RESET_ALL}  {Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}╚{'═' * 58}╝{Style.RESET_ALL}")

# ==================== MENU ====================

def print_menu(selected=0, tick=0):
    color = rgb_color(tick, 0)
    color1 = rgb_color(tick, 0)
    color2 = rgb_color(tick, 1)
    color3 = rgb_color(tick, 2)
    color4 = rgb_color(tick, 3)
    color5 = rgb_color(tick, 4)
    color6 = rgb_color(tick, 5)
    status, role = check_user_access()
    remaining, reset_info = get_remaining_limit()
    
    if remaining == float('inf'):
        limit_display = "∞"
    else:
        limit_display = str(int(remaining))
    
    if not status or role in ['NOT_REGISTERED', 'EXPIRED', 'BLOCKED', 'MAINTENANCE', 'TRIAL_EXPIRED']:
        items = [
            ("🔑 Beli Akses", "Hubungi admin untuk daftar", color3),
            ("🆓 Uji Coba", "Claim trial 1 jam (limit 1)", color4),
            ("✕ Keluar", "Tutup aplikasi", color3)
        ]
    else:
        items = [
            ("▶ Single Round", f"Sekali kirim ke semua API {limit_display}", color1),
            ("⟳ Infinite Loop", f"Kirim berulang dengan jeda {limit_display}", color2),
            ("📱 Spam Tele", f"Spam OTP via Telegram Bot {limit_display}", color4),
            ("💬 Spam NGL", f"Spam pesan ke NGL {limit_display}", color4),
            ("🚫 Spam Report Tele", f"Spam laporan ke Telegram {limit_display}", color3),
            ("❤️ React WA", f"React ke postingan WhatsApp Channel", color6),
            ("✏️ Setting NGL", f"Ubah pesan Spam NGL", color5),
            ("🤖 Cek Bot", "Cek status bot Telegram", color3),
            ("🎯 Phising", "Jalankan Phising Engine", color3),
            ("📊 Laporan Bug", "Kirim laporan ke admin", color3),
            ("✕ Keluar", "Tutup aplikasi", color3)
        ]
    
    print(f"\n{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {color}📋 MENU UTAMA{Style.RESET_ALL}{' ' * 44}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
    print()
    
    for i, (label, desc, color_item) in enumerate(items):
        if i == selected:
            print(f"  {Fore.CYAN}┌{'─' * 54}┐{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}│{Style.RESET_ALL}  {color_item}▶ {Style.RESET_ALL}{label:<18}─ {desc}{' ' * (54 - len(label) - len(desc) - 6)}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}└{'─' * 54}┘{Style.RESET_ALL}")
        else:
            grad_label = gradient_text(label, tick, i * 2)
            print(f"     {grad_label:<20}─ {desc}")
    
    if is_limit_reached() and reset_info:
        print(f"\n  {Fore.YELLOW}⏳ {reset_info}{Style.RESET_ALL}")
    
    print()
    print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {color1}↑/↓{Style.RESET_ALL}  : Navigasi  {color1}ENTER{Style.RESET_ALL}  : Pilih  {color1}Q{Style.RESET_ALL}  : Keluar  {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")

# ==================== RUN FUNCTIONS ====================

def update_exec_data(name, status, detail=""):
    global exec_data
    exec_data['last_log'] = f"{name}: {status} {detail}"
    
    if status == "SUCCESS":
        exec_data['success'] += 1
        exec_data['sent'] += 1
    elif status == "FAIL" or status == "ERROR" or status == "TIMEOUT":
        exec_data['failed'] += 1
        exec_data['sent'] += 1
    
    total = exec_data.get('total_api', len(TARGETS))
    sent = exec_data.get('sent', 0)
    exec_data['progress'] = int((sent / total) * 100)
    if exec_data['progress'] > 100:
        exec_data['progress'] = 100
    
    if is_limit_reached():
        exec_data['status'] = '⚠️ LIMIT HABIS - Tunggu Reset'

def show_execution_table(data, tick=0):
    clear_screen()
    color = rgb_color(tick)
    remaining, reset_info = get_remaining_limit()
    limit = user_session.get('limit', 1)
    sent = data.get('sent', 0)
    
    if remaining == float('inf'):
        limit_text = "∞ UNLIMITED"
        limit_color = Fore.GREEN
    elif remaining > 5:
        limit_text = f"{sent}/{limit} (sisa {int(remaining)})"
        limit_color = Fore.GREEN
    elif remaining > 0:
        limit_text = f"{sent}/{limit} (sisa {int(remaining)})"
        limit_color = Fore.YELLOW
    else:
        limit_text = f"🔴 {sent}/{limit} (HABIS!)"
        limit_color = Fore.RED
    
    W = 58
    
    print(f"{Fore.CYAN}┌{'─' * W}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {color}⚡ EKSEKUSI OTP SPAMMER{Style.RESET_ALL}{' ' * (W - 22 - len('⚡ EKSEKUSI OTP SPAMMER'))}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}├{'─' * W}┤{Style.RESET_ALL}")
    
    target_text = str(data.get('target', 'N/A'))
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Target    :{Style.RESET_ALL} {Fore.YELLOW}{target_text}{' ' * (W - 12 - len(target_text))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    thread_text = str(data.get('threads', 5))
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Thread    :{Style.RESET_ALL} {Fore.YELLOW}{thread_text}{' ' * (W - 12 - len(thread_text))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    api_text = str(data.get('total_api', len(TARGETS)))
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}API Total :{Style.RESET_ALL} {Fore.YELLOW}{api_text}{' ' * (W - 12 - len(api_text))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    status_text = str(data.get('status', 'Running...'))
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Status    :{Style.RESET_ALL} {color}{status_text}{' ' * (W - 12 - len(status_text))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Limit     :{Style.RESET_ALL} {limit_color}{limit_text}{' ' * (W - 12 - len(limit_text))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    if reset_info and is_limit_reached():
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Reset     :{Style.RESET_ALL} {Fore.YELLOW}{reset_info}{' ' * (W - 12 - len(reset_info))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    progress = data.get('progress', 0)
    bar_length = 30
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    progress_text = f"{progress}%"
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Progress  :{Style.RESET_ALL} {color}[{bar}] {progress_text}{' ' * (W - 14 - len(f'[{bar}] {progress_text}'))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}├{'─' * W}┤{Style.RESET_ALL}")
    
    sent_text = f"{data.get('sent', 0):>4}"
    success_text = f"{data.get('success', 0):>4}"
    failed_text = f"{data.get('failed', 0):>4}"
    
    line = f"  {Fore.GREEN}Sent    :{Style.RESET_ALL} {Fore.YELLOW}{sent_text}{Style.RESET_ALL}  "
    line += f"{Fore.GREEN}Success :{Style.RESET_ALL} {Fore.GREEN}{success_text}{Style.RESET_ALL}  "
    line += f"{Fore.GREEN}Failed  :{Style.RESET_ALL} {Fore.RED}{failed_text}{Style.RESET_ALL}  "
    
    padding = W - len(line) + 6
    if padding < 0:
        padding = 0
    print(f"{Fore.CYAN}│{Style.RESET_ALL}{line}{' ' * padding}{Fore.CYAN}│{Style.RESET_ALL}")
    
    last_log = str(data.get('last_log', ''))[:45]
    if last_log:
        log_color = Fore.WHITE
        if 'success' in last_log.lower():
            log_color = Fore.GREEN
        elif 'fail' in last_log.lower() or 'error' in last_log.lower():
            log_color = Fore.RED
        elif 'limit' in last_log.lower() or 'block' in last_log.lower():
            log_color = Fore.YELLOW
        
        log_text = f"{log_color}{last_log}{Style.RESET_ALL}"
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}Last Log :{Style.RESET_ALL} {log_text}{' ' * (W - 12 - len(last_log))}{Fore.CYAN}│{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}└{'─' * W}┘{Style.RESET_ALL}")

def run_with_ui(engine_func, target, threads=5, input_type="phone", message=None):
    global exec_data
    reset_session_counter()
    
    if engine_func.__name__ == 'run_react_wa':
        try:
            if message is not None:
                return engine_func(
                    target=target,
                    callback=update_exec_data,
                    limit_check=is_limit_reached,
                    limit_use=use_limit_session,
                    message=message
                )
            else:
                return engine_func(
                    target=target,
                    callback=update_exec_data,
                    limit_check=is_limit_reached,
                    limit_use=use_limit_session
                )
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            return False
    
    user_session['limit_used'] = False
    user_session['sent_count'] = 0
    
    exec_data['target'] = target
    exec_data['threads'] = threads
    exec_data['total_api'] = len(TARGETS)
    exec_data['status'] = 'Running...'
    exec_data['progress'] = 0
    exec_data['sent'] = 0
    exec_data['success'] = 0
    exec_data['failed'] = 0
    exec_data['last_log'] = 'Initializing...'
    stop_update = False
    
    def update_ui():
        tick = 0
        while not stop_update:
            tick += 0.1
            if is_limit_reached():
                exec_data['status'] = '⚠️ LIMIT HABIS - Tunggu Reset'
            show_execution_table(exec_data, tick)
            time.sleep(0.1)
    
    update_thread = threading.Thread(target=update_ui, daemon=True)
    update_thread.start()
    
    stopped_by_user = False
    result = False
    
    try:
        if message is not None:
            result = engine_func(
                threads=threads,
                target=target,
                callback=update_exec_data,
                limit_check=is_limit_reached,
                limit_use=use_limit_session,
                message=message
            )
        else:
            result = engine_func(
                threads=threads,
                target=target,
                callback=update_exec_data,
                limit_check=is_limit_reached,
                limit_use=use_limit_session
            )
        
    except KeyboardInterrupt:
        stopped_by_user = True
        print(f"\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    finally:
        if stopped_by_user:
            exec_data['status'] = 'Stopped'
        else:
            exec_data['status'] = 'Completed' if result else 'Failed'
        exec_data['progress'] = 100
        
        stop_update = True
        time.sleep(0.3)
        
        show_execution_table(exec_data, 0)
        
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")
        try:
            input()
        except KeyboardInterrupt:
            pass
        except:
            pass
    
    return result

# ==================== LOADING VERIFIKASI ====================

def loading_verify_id():
    """Loading verifikasi dengan ● ● ● ● ●"""
    dots = ['●', '●', '●', '●', '●']
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.MAGENTA]
    width = 60
    
    print()
    for _ in range(3):
        for start in range(len(dots)):
            sys.stdout.write('\r' + ' ' * width + '\r')
            line = ""
            for i in range(len(dots)):
                pos = (start + i) % len(dots)
                line += f"{colors[pos]}{dots[pos]}{Style.RESET_ALL} "
            sys.stdout.write(f"\r{Fore.CYAN}🔍 Memverifikasi ID... {line}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
    
    sys.stdout.write('\r' + ' ' * width + '\r')
    print(f"{Fore.GREEN}✅ Verifikasi ID selesai!{Style.RESET_ALL}")

# ==================== NAVIGASI ====================

_cached_status = None
_cached_role = None
_cache_time = 0
_CACHE_DURATION = 2

def get_cached_access():
    global _cached_status, _cached_role, _cache_time
    now = time.time()
    if now - _cache_time < _CACHE_DURATION and _cached_status is not None:
        return _cached_status, _cached_role
    status, role = check_user_access()
    _cached_status = status
    _cached_role = role
    _cache_time = now
    return status, role

def print_access_denied(role_info=""):
    clear_screen()
    print(f"{Fore.RED}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.RED}║{' ' * 20}🚫 AKSES DITOLAK 🚫{' ' * 20}║{Style.RESET_ALL}")
    print(f"{Fore.RED}╠{'═' * 60}╣{Style.RESET_ALL}")
    
    if "TEMP_BLOCKED" in role_info:
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⏳ Terlalu banyak percobaan gagal{Style.RESET_ALL}{' ' * 21}{Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}{role_info.replace('TEMP_BLOCKED:', '')}{' ' * 30}{Fore.RED}║{Style.RESET_ALL}")
    elif "RATE_LIMIT" in role_info:
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⏳ Rate limit exceeded{Style.RESET_ALL}{' ' * 31}{Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Mohon tunggu beberapa saat{Style.RESET_ALL}{' ' * 25}{Fore.RED}║{Style.RESET_ALL}")
    elif "FIREBASE_NOT_CONNECTED" in role_info:
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⚠️  Firebase tidak terhubung{Style.RESET_ALL}{' ' * 25}{Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Periksa koneksi internet Anda{Style.RESET_ALL}{' ' * 23}{Fore.RED}║{Style.RESET_ALL}")
    elif "SYSTEM_ERROR" in role_info:
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⚠️  System error terjadi{Style.RESET_ALL}{' ' * 28}{Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Hubungi admin untuk bantuan{Style.RESET_ALL}{' ' * 23}{Fore.RED}║{Style.RESET_ALL}")
    elif "TRIAL_EXPIRED" in role_info:
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⏰ Masa trial telah berakhir{Style.RESET_ALL}{' ' * 25}{Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Silakan beli akses untuk melanjutkan{Style.RESET_ALL}{' ' * 14}{Fore.RED}║{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⚠️  ID Anda tidak terdaftar atau expired{Style.RESET_ALL}{' ' * 14}{Fore.RED}║{Style.RESET_ALL}")
        print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Silakan hubungi admin untuk mendapatkan akses{Style.RESET_ALL}{' ' * 9}{Fore.RED}║{Style.RESET_ALL}")
    
    print(f"{Fore.RED}║{Style.RESET_ALL}{' ' * 60}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.CYAN}📱 Kontak Admin: 082320884089{Style.RESET_ALL}{' ' * 24}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}╠{'═' * 60}╣{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.CYAN}[1] Beli Akses{Style.RESET_ALL}{' ' * 46}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.CYAN}[2] Uji Coba (TRIAL){Style.RESET_ALL}{' ' * 40}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.CYAN}[3] Exit{Style.RESET_ALL}{' ' * 52}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}╚{'═' * 60}╝{Style.RESET_ALL}")
    print()
    
    choice = input(f"{Fore.WHITE}Pilih (1/2/3): {Style.RESET_ALL}").strip()
    
    if choice == '1':
        print()
        print(f"{Fore.GREEN}📤 Kirim pesan ke admin:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Nomor: 082320884089{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Pesan: Saya {get_whoami()} ingin beli akses OTP Spammer{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⚠️  Tunggu admin menambahkan ID Anda{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False
    elif choice == '2':
        return handle_trial_claim()
    else:
        return True

def handle_trial_claim():
    username = get_whoami()
    
    eligible, msg = check_trial_eligibility(username)
    if not eligible:
        print(f"\n{Fore.RED}❌ Anda sudah pernah claim trial sebelumnya!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Hanya bisa claim 1x per ID{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False
    
    print(f"\n{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🆓 UJI COBA (TRIAL){Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}📋 Detail Trial:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}• Durasi  : 1 Jam{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}• Limit OTP : 1 kali spam{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}• Limit React: 1 kali{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}• Hanya  : 1x per ID{Style.RESET_ALL}")
    print()
    
    confirm = input(f"{Fore.WHITE}Claim trial sekarang? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if confirm != 'y':
        print(f"\n{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False
    
    print(f"\n{Fore.CYAN}⏳ Memproses claim trial...{Style.RESET_ALL}")
    time.sleep(1)
    
    success, expiry = claim_trial(username)
    
    if success:
        print(f"\n{Fore.GREEN}✅ Trial berhasil di-claim!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📅 Expiry: {expiry}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Anda akan otomatis keluar setelah 1 jam{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk masuk ke menu...{Style.RESET_ALL}")
        input()
        return True
    else:
        print(f"\n{Fore.RED}❌ Gagal claim trial!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False

def print_report_menu():
    clear_screen()
    print(f"{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.MAGENTA}📊 LAPORAN BUG / MASALAH{Style.RESET_ALL}{' ' * 29}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}⚠️  Laporkan bug atau masalah yang Anda temui{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Setiap ID hanya bisa laporan 1x per hari{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Maksimal 500 karakter, minimal 10 karakter{Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}📝 Tulis pesan laporan Anda:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   (Ketik 'batal' untuk membatalkan){Style.RESET_ALL}")
    print()
    
    message = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
    
    if message.lower() == 'batal':
        return False
    if not message:
        print(f"\n{Fore.RED}✗ Pesan tidak boleh kosong!{Style.RESET_ALL}")
        time.sleep(0.5)
        return False
    if len(message) < 10:
        print(f"\n{Fore.RED}✗ Pesan minimal 10 karakter!{Style.RESET_ALL}")
        time.sleep(0.5)
        return False
    if len(message) > 500:
        print(f"\n{Fore.RED}✗ Pesan maksimal 500 karakter!{Style.RESET_ALL}")
        time.sleep(0.5)
        return False
    
    dangerous_chars = ['<', '>', '{', '}', '[', ']', ';', '`']
    for char in dangerous_chars:
        if char in message:
            print(f"\n{Fore.RED}✗ Karakter '{char}' tidak diizinkan!{Style.RESET_ALL}")
            time.sleep(0.5)
            return False
    
    print()
    print(f"{Fore.YELLOW}Konfirmasi laporan:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  {message[:100]}{'...' if len(message) > 100 else ''}{Style.RESET_ALL}")
    print()
    confirm = input(f"{Fore.WHITE}Kirim laporan? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if confirm == 'y':
        username = get_whoami()
        success, msg = send_report(username, message)
        if success:
            print(f"\n{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ {msg}{Style.RESET_ALL}")
        time.sleep(0.5)
        return True
    else:
        print(f"\n{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
        time.sleep(0.5)
        return False

def input_with_animation(prompt, duration=0.3, input_type="phone"):
    chars = ['█', '▓', '▒', '░']
    tick = 0
    start = time.time()
    
    if input_type == "phone":
        title = "📱 MASUKKAN NOMOR TARGET"
        example = "Contoh: 08123456789"
    elif input_type == "telegram":
        title = "🤖 MASUKKAN TARGET TELEGRAM"
        example = "Contoh: @username atau 123456789"
    elif input_type == "ngl":
        title = "💬 MASUKKAN USERNAME NGL"
        example = "Contoh: username_ngl"
    elif input_type == "report":
        title = "🚫 MASUKKAN TARGET REPORT"
        example = "Contoh: @username atau 123456789"
    else:
        title = "📱 MASUKKAN TARGET"
        example = "Masukkan target..."
    
    print(f"\n{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}💡 {example}{Style.RESET_ALL}")
    print()
    
    while time.time() - start < duration:
        tick += 0.1
        color = rgb_color(tick)
        idx = int((time.time() - start) * 4) % 4
        sys.stdout.write(f'\r{Fore.GREEN}  ┌──{Fore.YELLOW} {prompt} {color}{chars[idx]}{Style.RESET_ALL}')
        sys.stdout.flush()
        time.sleep(0.02)
    print("\r" + " " * 60 + "\r", end='')
    print(f"{Fore.GREEN}  └──{Fore.WHITE} ➜ {Style.RESET_ALL}", end='')
    target = input()
    return target.strip()

def print_loading_animation(message="Processing", duration=0.3):
    chars = ['◐', '◓', '◑', '◒']
    tick = 0
    start = time.time()
    while time.time() - start < duration:
        tick += 0.1
        color = rgb_color(tick)
        idx = int((time.time() - start) * 8) % 4
        sys.stdout.write(f'\r{color}{chars[idx]} {message}...{Style.RESET_ALL}')
        sys.stdout.flush()
        time.sleep(0.02)
    print('\r' + ' ' * 50 + '\r', end='')

def get_key():
    try:
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

def print_maintenance_banner():
    clear_screen()
    print(f"{Fore.RED}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.RED}║{' ' * 20}🔧 MAINTENANCE MODE 🔧{' ' * 19}║{Style.RESET_ALL}")
    print(f"{Fore.RED}╠{'═' * 60}╣{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.YELLOW}⚠️  Server sedang dalam pemeliharaan{Style.RESET_ALL}{' ' * 26}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Mohon tunggu hingga server kembali aktif{Style.RESET_ALL}{' ' * 15}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}  {Fore.WHITE}Estimasi waktu: beberapa menit{Style.RESET_ALL}{' ' * 26}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}╠{'═' * 60}╣{Style.RESET_ALL}")
    print(f"{Fore.RED}║{Style.RESET_ALL}{' ' * 20}{Fore.RED}🔴 STATUS: OFFLINE{Style.RESET_ALL}{' ' * 20}{Fore.RED}║{Style.RESET_ALL}")
    print(f"{Fore.RED}╚{'═' * 60}╝{Style.RESET_ALL}")
    time.sleep(0.5)

# ==================== MENU NAVIGATION ====================

def menu_navigation():
    global selected
    selected = 0
    tick = 0
    
    global _cache_time
    _cache_time = 0
    
    while True:
        try:
            if check_maintenance():
                print_maintenance_banner()
                sys.exit(0)
            
            status, role = get_cached_access()
            
            if not status:
                if role == "MAINTENANCE":
                    print_maintenance_banner()
                    sys.exit(0)
                elif "BLOCKED" in role:
                    print(f"\n{Fore.RED}🚫 ID Anda diblokir oleh admin!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Hubungi admin untuk informasi lebih lanjut{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}📱 Kontak Admin: 082320884089{Style.RESET_ALL}")
                    time.sleep(1)
                    sys.exit(0)
                elif "TEMP_BLOCKED" in role:
                    if print_access_denied(role):
                        sys.exit(0)
                    else:
                        continue
                elif "RATE_LIMIT" in role:
                    if print_access_denied(role):
                        sys.exit(0)
                    else:
                        continue
                elif role in ["NOT_REGISTERED", "EXPIRED", "FIREBASE_NOT_CONNECTED", "SYSTEM_ERROR", "TRIAL_EXPIRED"]:
                    if print_access_denied(role):
                        sys.exit(0)
                    else:
                        continue
                else:
                    if print_access_denied():
                        sys.exit(0)
                    else:
                        continue
            
            clear_screen()
            tick += 0.08
            print_banner(tick)
            print_menu(selected, tick)
            
            is_termux = os.path.exists("/data/data/com.termux/files/usr")
            
            if is_termux:
                key = get_key()
                
                if key == '\x1b[A':
                    if status and role not in ['NOT_REGISTERED', 'EXPIRED', 'BLOCKED', 'MAINTENANCE']:
                        selected = (selected - 1) % 11
                    else:
                        selected = (selected - 1) % 3
                    continue
                    
                elif key == '\x1b[B':
                    if status and role not in ['NOT_REGISTERED', 'EXPIRED', 'BLOCKED', 'MAINTENANCE']:
                        selected = (selected + 1) % 11
                    else:
                        selected = (selected + 1) % 3
                    continue
                    
                elif key in ['\r', '\n', '\x1b[C']:
                    if not status or role in ['NOT_REGISTERED', 'EXPIRED', 'BLOCKED', 'MAINTENANCE', 'TRIAL_EXPIRED']:
                        if selected == 0:
                            print()
                            print(f"{Fore.GREEN}📤 Kirim pesan ke admin:{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Nomor: 082320884089{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Pesan: Saya {get_whoami()} ingin beli akses OTP Spammer{Style.RESET_ALL}")
                            print()
                            print(f"{Fore.YELLOW}⚠️  Tunggu admin menambahkan ID Anda{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                            input()
                            _cache_time = 0
                        elif selected == 1:
                            if handle_trial_claim():
                                _cache_time = 0
                                continue
                            else:
                                continue
                        else:
                            print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                            time.sleep(0.3)
                            print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                            sys.exit(0)
                    else:
                        choices = ["single", "infinite", "spamtele", "spamngl", "spamreport", "reactwa", "settingngl", "cekbot", "phising", "report", "exit"]
                        choice = choices[selected]
                        
                        # ========== SINGLE ROUND ==========
                        if choice == "single":
                            if is_limit_reached():
                                remaining, reset_info = get_remaining_limit()
                                print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            clear_screen()
                            target = input_with_animation("Masukkan nomor target", 0.2, "phone")
                            if not target:
                                print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            if not re.match(r'^08\d{8,12}$', target) and not re.match(r'^\+?62\d{8,12}$', target):
                                print(f"\n{Fore.RED}✗ Nomor tidak valid! Harus 08xx atau +62xx{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            print_loading_animation("Memulai Single Round", 0.2)
                            clear_screen()
                            limit_info, reset_info = get_limit_info()
                            print(f"\n{Fore.YELLOW}⚠️  Menjalankan Single Round...{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Tekan {Fore.RED}CTRL+C{Fore.CYAN} untuk berhenti{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Limit: {limit_info}{Style.RESET_ALL}")
                            if reset_info:
                                print(f"{Fore.CYAN}   {reset_info}{Style.RESET_ALL}")
                            print()
                            time.sleep(0.1)
                            try:
                                run_with_ui(run_single_round, target, threads=5)
                            except KeyboardInterrupt:
                                print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                            print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                            print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                            input()
                            _cache_time = 0
                            
                        # ========== INFINITE LOOP ==========
                        elif choice == "infinite":
                            if is_limit_reached():
                                remaining, reset_info = get_remaining_limit()
                                print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            clear_screen()
                            target = input_with_animation("Masukkan nomor target", 0.2, "phone")
                            if not target:
                                print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            if not re.match(r'^08\d{8,12}$', target) and not re.match(r'^\+?62\d{8,12}$', target):
                                print(f"\n{Fore.RED}✗ Nomor tidak valid! Harus 08xx atau +62xx{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            print_loading_animation("Memulai Infinite Loop", 0.2)
                            clear_screen()
                            limit_info, reset_info = get_limit_info()
                            print(f"\n{Fore.YELLOW}⚠️  Mode Infinite Loop akan berjalan terus menerus{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}   Tekan {Fore.RED}CTRL+C{Fore.YELLOW} untuk berhenti{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Limit: {limit_info}{Style.RESET_ALL}")
                            if reset_info:
                                print(f"{Fore.CYAN}   {reset_info}{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   ⚠️  Akan berhenti otomatis jika limit habis{Style.RESET_ALL}")
                            print()
                            time.sleep(0.2)
                            try:
                                run_with_ui(run_infinite_loop, target, threads=5)
                            except KeyboardInterrupt:
                                print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                            print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                            print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                            input()
                            _cache_time = 0
                            
                        # ========== SPAM TELE ==========
                        elif choice == "spamtele":
                            if is_limit_reached():
                                remaining, reset_info = get_remaining_limit()
                                print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            clear_screen()
                            target = input_with_animation("Masukkan username atau ID Telegram", 0.2, "telegram")
                            if not target:
                                print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            print_loading_animation("Memulai Spam Telegram", 0.2)
                            clear_screen()
                            limit_info, reset_info = get_limit_info()
                            print(f"\n{Fore.YELLOW}⚠️  Menjalankan Spam Telegram...{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Tekan {Fore.RED}CTRL+C{Fore.CYAN} untuk berhenti{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Limit: {limit_info}{Style.RESET_ALL}")
                            if reset_info:
                                print(f"{Fore.CYAN}   {reset_info}{Style.RESET_ALL}")
                            print()
                            time.sleep(0.1)
                            try:
                                run_with_ui(run_spam_tele, target, threads=5)
                            except KeyboardInterrupt:
                                print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                            print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                            print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                            input()
                            _cache_time = 0
                            
                        # ========== SPAM NGL ==========
                        elif choice == "spamngl":
                            if is_limit_reached():
                                remaining, reset_info = get_remaining_limit()
                                print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            clear_screen()
                            print(f"\n{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}💬 SPAM NGL{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")
                            print(f"{Fore.YELLOW}💡 Masukkan {Fore.CYAN}username NGL{Fore.YELLOW} target{Style.RESET_ALL}")
                            print(f"{Fore.WHITE}   Contoh: username_ngl{Style.RESET_ALL}")
                            print()
                            target = input(f"{Fore.GREEN}└──{Fore.WHITE} ➜ {Style.RESET_ALL}").strip()
                            
                            if not target:
                                print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            
                            print()
                            print(f"{Fore.CYAN}📝 Pesan default: {Fore.YELLOW}\"{SPAM_NGL_MESSAGE}\"{Style.RESET_ALL}")
                            print(f"{Fore.WHITE}Masukkan pesan baru (kosongkan untuk pakai default):{Style.RESET_ALL}")
                            print()
                            msg_input = input(f"{Fore.GREEN}└──{Fore.WHITE} ➜ {Style.RESET_ALL}").strip()
                            
                            if msg_input:
                                msg_to_send = msg_input
                            else:
                                msg_to_send = SPAM_NGL_MESSAGE
                                print(f"{Fore.YELLOW}💡 Menggunakan pesan default{Style.RESET_ALL}")
                            
                            print(f"{Fore.CYAN}📝 Pesan akan dikirim: {Fore.YELLOW}\"{msg_to_send}\"{Style.RESET_ALL}")
                            time.sleep(0.5)
                            
                            print_loading_animation("Memulai Spam NGL", 0.2)
                            clear_screen()
                            limit_info, reset_info = get_limit_info()
                            print(f"\n{Fore.YELLOW}⚠️  Menjalankan Spam NGL...{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Tekan {Fore.RED}CTRL+C{Fore.CYAN} untuk berhenti{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Limit: {limit_info}{Style.RESET_ALL}")
                            if reset_info:
                                print(f"{Fore.CYAN}   {reset_info}{Style.RESET_ALL}")
                            print()
                            time.sleep(0.1)
                            try:
                                run_with_ui(run_spam_ngl, target, threads=5, message=msg_to_send)
                            except KeyboardInterrupt:
                                print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                            print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                            print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                            input()
                            _cache_time = 0
                            
                        # ========== SPAM REPORT TELE ==========
                        elif choice == "spamreport":
                            if is_limit_reached():
                                remaining, reset_info = get_remaining_limit()
                                print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            clear_screen()
                            target = input_with_animation("Masukkan username atau ID Telegram", 0.2, "report")
                            if not target:
                                print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            print_loading_animation("Memulai Spam Report Telegram", 0.2)
                            clear_screen()
                            limit_info, reset_info = get_limit_info()
                            print(f"\n{Fore.YELLOW}⚠️  Menjalankan Spam Report Telegram...{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Tekan {Fore.RED}CTRL+C{Fore.CYAN} untuk berhenti{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}   Limit: {limit_info}{Style.RESET_ALL}")
                            if reset_info:
                                print(f"{Fore.CYAN}   {reset_info}{Style.RESET_ALL}")
                            print()
                            time.sleep(0.1)
                            try:
                                run_with_ui(run_spam_report_tele, target, threads=5)
                            except KeyboardInterrupt:
                                print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                            print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                            print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                            input()
                            _cache_time = 0
                            
                        # ========== REACT WA ==========
                        elif choice == "reactwa":
                            if is_limit_reached():
                                remaining, reset_info = get_remaining_limit()
                                print(f"\n{Fore.RED}✗ Limit OTP habis! {reset_info}{Style.RESET_ALL}")
                                time.sleep(0.5)
                                continue
                            
                            username = get_whoami()
                            success, msg = use_react_limit(username)
                            if not success:
                                print(f"\n{Fore.RED}✗ {msg}{Style.RESET_ALL}")
                                time.sleep(1)
                                continue
                            print(f"\n{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")
                            print()
                            
                            clear_screen()
                            try:
                                run_react_wa(
                                    target="",
                                    callback=update_exec_data,
                                    limit_check=is_limit_reached,
                                    limit_use=use_limit_session
                                )
                            except KeyboardInterrupt:
                                print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                            _cache_time = 0
                            
                        # ========== SETTING NGL ==========
                        elif choice == "settingngl":
                            set_ngl_message()
                            _cache_time = 0
                            
                        # ========== CEK BOT ==========
                        elif choice == "cekbot":
                            clear_screen()
                            check_all_bots()
                            _cache_time = 0
                            
                        # ========== PHISING ==========
                        elif choice == "phising":
                            try:
                                from main_phis import phising_menu
                                phising_menu()
                            except ImportError:
                                print(f"\n{Fore.RED}❌ File main_phis.py tidak ditemukan!{Style.RESET_ALL}")
                                time.sleep(2)
                            _cache_time = 0
                            
                        # ========== LAPORAN BUG ==========
                        elif choice == "report":
                            if print_report_menu():
                                continue
                            continue
                            
                        # ========== EXIT ==========
                        elif choice == "exit":
                            print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                            time.sleep(0.3)
                            print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                            sys.exit(0)
                            
                elif key in ['q', 'Q']:
                    print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                    time.sleep(0.3)
                    print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                    sys.exit(0)
            else:
                # ========== MODE NON-TERMUX ==========
                if not status or role in ['NOT_REGISTERED', 'EXPIRED', 'BLOCKED', 'MAINTENANCE', 'TRIAL_EXPIRED']:
                    print(f"\n{Fore.YELLOW}ℹ️  ID Anda tidak terdaftar!{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [1] Beli Akses{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [2] Uji Coba (TRIAL){Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [3] Keluar{Style.RESET_ALL}")
                    choice = input(f"\n{Fore.WHITE}Pilih (1/2/3): {Style.RESET_ALL}").strip()
                    if choice == "1":
                        print()
                        print(f"{Fore.GREEN}📤 Kirim pesan ke admin:{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Nomor: 082320884089{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Pesan: Saya {get_whoami()} ingin beli akses OTP Spammer{Style.RESET_ALL}")
                        print()
                        input(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                    elif choice == "2":
                        if handle_trial_claim():
                            continue
                    else:
                        print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                        time.sleep(0.3)
                        print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                        sys.exit(0)
                else:
                    print(f"\n{Fore.YELLOW}ℹ️  Mode keyboard tidak tersedia, gunakan input angka{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [1] Single Round{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [2] Infinite Loop{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [3] Spam Tele{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [4] Spam NGL{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [5] Spam Report Tele{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [6] React WA{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [7] Setting NGL{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [8] Cek Bot{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [9] Phising{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [10] Laporan Bug{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}   [11] Keluar{Style.RESET_ALL}")
                    choice = input(f"\n{Fore.WHITE}Pilih (1-11): {Style.RESET_ALL}").strip()
                    
                    if choice == "1":
                        if is_limit_reached():
                            remaining, reset_info = get_remaining_limit()
                            print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        clear_screen()
                        target = input(f"{Fore.WHITE}Nomor target (08xx): {Style.RESET_ALL}").strip()
                        if not target:
                            print(f"\n{Fore.RED}✗ Nomor tidak boleh kosong!{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        if not re.match(r'^08\d{8,12}$', target):
                            print(f"\n{Fore.RED}✗ Nomor tidak valid! Harus dimulai 08{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        try:
                            run_with_ui(run_single_round, target, threads=5)
                        except KeyboardInterrupt:
                            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                        print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                        input()
                    elif choice == "2":
                        if is_limit_reached():
                            remaining, reset_info = get_remaining_limit()
                            print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        clear_screen()
                        target = input(f"{Fore.WHITE}Nomor target (08xx): {Style.RESET_ALL}").strip()
                        if not target:
                            print(f"\n{Fore.RED}✗ Nomor tidak boleh kosong!{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        if not re.match(r'^08\d{8,12}$', target):
                            print(f"\n{Fore.RED}✗ Nomor tidak valid! Harus dimulai 08{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        print(f"\n{Fore.YELLOW}⚠️  Mode Infinite Loop akan berjalan terus menerus{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}   Tekan {Fore.RED}CTRL+C{Fore.YELLOW} untuk berhenti{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}   ⚠️  Akan berhenti otomatis jika limit habis{Style.RESET_ALL}")
                        print()
                        time.sleep(0.3)
                        try:
                            run_with_ui(run_infinite_loop, target, threads=5)
                        except KeyboardInterrupt:
                            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                        print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                        input()
                    elif choice == "3":
                        if is_limit_reached():
                            remaining, reset_info = get_remaining_limit()
                            print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        clear_screen()
                        target = input(f"{Fore.WHITE}Username atau ID Telegram: {Style.RESET_ALL}").strip()
                        if not target:
                            print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        try:
                            run_with_ui(run_spam_tele, target, threads=5)
                        except KeyboardInterrupt:
                            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                        print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                        input()
                    elif choice == "4":
                        if is_limit_reached():
                            remaining, reset_info = get_remaining_limit()
                            print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        clear_screen()
                        print(f"\n{Fore.CYAN}💬 SPAM NGL{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Masukkan username NGL target:{Style.RESET_ALL}")
                        target = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
                        if not target:
                            print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        print()
                        print(f"{Fore.CYAN}📝 Pesan default: {Fore.YELLOW}\"{SPAM_NGL_MESSAGE}\"{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}Masukkan pesan baru (kosongkan untuk pakai default):{Style.RESET_ALL}")
                        msg_input = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
                        if msg_input:
                            msg_to_send = msg_input
                        else:
                            msg_to_send = SPAM_NGL_MESSAGE
                            print(f"{Fore.YELLOW}💡 Menggunakan pesan default{Style.RESET_ALL}")
                        try:
                            run_with_ui(run_spam_ngl, target, threads=5, message=msg_to_send)
                        except KeyboardInterrupt:
                            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                        print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                        input()
                    elif choice == "5":
                        if is_limit_reached():
                            remaining, reset_info = get_remaining_limit()
                            print(f"\n{Fore.RED}✗ Limit habis! {reset_info}{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        clear_screen()
                        target = input(f"{Fore.WHITE}Username atau ID Telegram: {Style.RESET_ALL}").strip()
                        if not target:
                            print(f"\n{Fore.RED}✗ Target tidak boleh kosong!{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        try:
                            run_with_ui(run_spam_report_tele, target, threads=5)
                        except KeyboardInterrupt:
                            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                        print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                        input()
                    elif choice == "6":
                        if is_limit_reached():
                            remaining, reset_info = get_remaining_limit()
                            print(f"\n{Fore.RED}✗ Limit OTP habis! {reset_info}{Style.RESET_ALL}")
                            time.sleep(0.5)
                            continue
                        
                        username = get_whoami()
                        success, msg = use_react_limit(username)
                        if not success:
                            print(f"\n{Fore.RED}✗ {msg}{Style.RESET_ALL}")
                            time.sleep(1)
                            continue
                        print(f"\n{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")
                        print()
                        
                        clear_screen()
                        print(f"{Fore.CYAN}❤️ REACT WHATSAPP CHANNEL{Style.RESET_ALL}")
                        print()
                        try:
                            run_react_wa(
                                target="",
                                callback=update_exec_data,
                                limit_check=is_limit_reached,
                                limit_use=use_limit_session
                            )
                        except KeyboardInterrupt:
                            print(f"\n\n{Fore.YELLOW}⚠️ Proses dihentikan oleh user{Style.RESET_ALL}")
                        print(f"\n{Fore.GREEN}✓ Proses selesai!{Style.RESET_ALL}")
                        print(f"\n{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
                        input()
                    elif choice == "7":
                        set_ngl_message()
                    elif choice == "8":
                        clear_screen()
                        check_all_bots()
                    elif choice == "9":
                        try:
                            from main_phis import phising_menu
                            phising_menu()
                        except ImportError:
                            print(f"\n{Fore.RED}❌ File main_phis.py tidak ditemukan!{Style.RESET_ALL}")
                            time.sleep(2)
                    elif choice == "10":
                        print_report_menu()
                        continue
                    elif choice == "11":
                        print(f"\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
                        time.sleep(0.3)
                        print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
                        sys.exit(0)
                        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
            time.sleep(0.3)
            print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
            time.sleep(0.5)
            continue

# ==================== MAIN ====================

def main():
    try:
        is_termux = os.path.exists("/data/data/com.termux/files/usr")
        
        clear_screen()
        
        # BANNER & VERIFIKASI
        print_cowsay_banner()
        print()
        loading_verify_id()
        print()
        
        matrix_loading(2.0)
        
        status, role = check_user_access()
        
        if not status:
            if "BLOCKED" in role:
                print(f"\n{Fore.RED}🚫 ID Anda diblokir oleh admin!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Hubungi admin untuk informasi lebih lanjut{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📱 Kontak Admin: 082320884089{Style.RESET_ALL}")
                time.sleep(2)
                sys.exit(0)
            elif role == "MAINTENANCE":
                print_maintenance_banner()
                sys.exit(0)
            elif "TEMP_BLOCKED" in role:
                print(f"\n{Fore.RED}⏳ Terlalu banyak percobaan gagal!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{role.replace('TEMP_BLOCKED:', '')}{Style.RESET_ALL}")
                time.sleep(2)
                sys.exit(0)
            elif "RATE_LIMIT" in role:
                print(f"\n{Fore.RED}⏳ Rate limit exceeded!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Mohon tunggu beberapa saat{Style.RESET_ALL}")
                time.sleep(2)
                sys.exit(0)
            elif role in ["NOT_REGISTERED", "EXPIRED", "FIREBASE_NOT_CONNECTED", "SYSTEM_ERROR", "TRIAL_EXPIRED"]:
                print_access_denied(role)
                sys.exit(0)
            else:
                print_access_denied(role)
                sys.exit(0)
        
        get_user_role()
        
        if check_maintenance():
            print_maintenance_banner()
            sys.exit(0)
        
        if is_termux:
            print(f"{Fore.GREEN}✓ Mode Termux terdeteksi{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  Gunakan tombol ↑/↓ untuk navigasi{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  ENTER untuk memilih, Q untuk keluar{Style.RESET_ALL}")
            print()
            time.sleep(0.2)
        
        menu_navigation()
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}● {Fore.WHITE}Keluar...{Style.RESET_ALL}")
        time.sleep(0.3)
        print(f"{Fore.GREEN}✓ Sampai jumpa! 👋{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()