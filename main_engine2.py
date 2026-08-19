#!/usr/bin/env python3
# main_engine2.py - Telegram Spam Engine + React WA (LENGKAP)

import time
import random
import threading
import requests
import re
import sys
import uuid
import signal
from colorama import Fore, Style, init
from datetime import datetime, timedelta

from telegram_tokens import TOKENS, get_all_tokens, count_tokens, get_vip_token, set_vip_token

init(autoreset=True)

stop_flag = False
global_callback = None
global_limit_check = None

# ==================== LIMIT REACT ====================

# 🔥 LIMIT REACT BERDASARKAN ROLE
REACT_LIMITS = {
    'PREMIUM': 10,
    'VIP': 20,
    'OWNER': 30,
    'TRIAL': 1
}

def get_react_limit(role):
    """Ambil limit react berdasarkan role"""
    return REACT_LIMITS.get(role, 1)

def log_target_tele(idx, total, name, status, detail=""):
    with threading.Lock():
        if status == "SUCCESS":
            sym, col = "+", Fore.GREEN
        elif status == "ERROR":
            sym, col = "x", Fore.RED
        elif status == "LIMITED":
            sym, col = "!", Fore.YELLOW
        else:
            sym, col = "-", Fore.RED
        print(f"{col}[{sym}]{Style.RESET_ALL} ({idx:>2}/{total}) {name:<20}: {status}" + (f" - {detail}" if detail else ""))

# ==================== FUNGSI BOT TELEGRAM ====================

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        return resp
    except:
        return None

def get_user_id_from_username(token, username):
    if not username:
        return None
    username = username.strip()
    if not username.startswith('@'):
        username = '@' + username
    
    url = f"https://api.telegram.org/bot{token}/getChat"
    payload = {"chat_id": username}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok'):
                return data['result']['id']
        return None
    except:
        return None

def check_bot_status(token):
    if not token or token.startswith('YOUR_TOKEN') or token == "7581234567:AAHabcdefghijklmnopqrstuvwxyz123456":
        return False, None
    
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        resp = requests.post(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok'):
                return True, data['result']['username']
        return False, None
    except:
        return False, None

def get_chat_info(token, chat_id):
    url = f"https://api.telegram.org/bot{token}/getChat"
    payload = {"chat_id": chat_id}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok'):
                return data['result']
        return None
    except:
        return None

# ==================== SPAM TELE (OTP) ====================

def run_spam_tele(target, threads=5, callback=None, limit_check=None, limit_use=None):
    global stop_flag, global_callback, global_limit_check
    stop_flag = False
    global_callback = callback
    global_limit_check = limit_check
    
    tokens = get_all_tokens()
    total_tokens = len(tokens)
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📱 SPAM TELEGRAM (∞ LOOP){Style.RESET_ALL}{' ' * 25}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Total Bot: {Fore.WHITE}{total_tokens}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Target: {Fore.WHITE}{target}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  Delay antar bot: {Fore.CYAN}2 detik{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  Tekan {Fore.RED}CTRL+C{Fore.YELLOW} untuk berhenti{Style.RESET_ALL}")
    print()
    
    if limit_use:
        used, msg = limit_use()
        if not used:
            print(f"{Fore.RED}[LIMIT]{Style.RESET_ALL} {msg}")
            return False
        print(f"{Fore.GREEN}[LIMIT]{Style.RESET_ALL} {msg}")
    
    valid_tokens = []
    for token in tokens:
        status, username = check_bot_status(token)
        if status:
            valid_tokens.append(token)
            print(f"{Fore.GREEN}✅ Bot @{username} AKTIF{Style.RESET_ALL}")
        else:
            if token and not token.startswith('7581234567'):
                print(f"{Fore.RED}❌ Bot dengan token {token[:15]}... TIDAK VALID{Style.RESET_ALL}")
    
    if not valid_tokens:
        print()
        print(f"{Fore.RED}❌ TIDAK ADA BOT YANG AKTIF!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Pastikan token di telegram_tokens.py sudah diganti dengan token asli{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        try:
            input()
        except:
            pass
        return False
    
    # ==================== 🔥 KONVERSI USERNAME KE ID ====================
    chat_id = None
    target_info = None
    target_clean = target.strip()
    
    print(f"{Fore.CYAN}🔍 Mencari target...{Style.RESET_ALL}")
    
    # 🔥 CEK APAKAH TARGET ADALAH ID (ANGKA)
    if target_clean.isdigit():
        chat_id = int(target_clean)
        print(f"{Fore.CYAN}📌 Target ID: {Fore.WHITE}{chat_id}{Style.RESET_ALL}")
        
        # Coba dapatkan info target
        for token in valid_tokens[:3]:
            info = get_chat_info(token, chat_id)
            if info:
                target_info = info
                break
        if target_info:
            username_display = target_info.get('username', '')
            first_name = target_info.get('first_name', '')
            print(f"{Fore.GREEN}✅ Target ditemukan: {first_name} (@{username_display}){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Tidak bisa mendapatkan info target, tapi ID valid{Style.RESET_ALL}")
    else:
        # 🔥 TARGET ADALAH USERNAME
        print(f"{Fore.CYAN}🔍 Mencari username: {Fore.WHITE}{target_clean}{Style.RESET_ALL}")
        
        # Bersihkan username
        target_username = target_clean
        if not target_username.startswith('@'):
            target_username = '@' + target_username
        
        found = False
        for token in valid_tokens:
            user_id = get_user_id_from_username(token, target_username)
            if user_id:
                chat_id = user_id
                found = True
                info = get_chat_info(token, chat_id)
                if info:
                    target_info = info
                break
        
        # Jika tidak ditemukan, coba tanpa @
        if not found:
            target_username2 = target_clean.replace('@', '')
            for token in valid_tokens:
                user_id = get_user_id_from_username(token, target_username2)
                if user_id:
                    chat_id = user_id
                    found = True
                    info = get_chat_info(token, chat_id)
                    if info:
                        target_info = info
                    break
        
        if not chat_id:
            print(f"{Fore.RED}❌ Username {target} tidak ditemukan!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Pastikan username benar dan bot sudah di-start oleh target{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Atau gunakan ID Telegram langsung (contoh: 123456789){Style.RESET_ALL}")
            print()
            print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
            try:
                input()
            except:
                pass
            return False
        
        # 🔥 TAMPILKAN HASIL KONVERSI
        if target_info:
            username_display = target_info.get('username', '')
            first_name = target_info.get('first_name', '')
            print(f"{Fore.GREEN}✅ Target ditemukan: {first_name} (@{username_display}) -> ID: {chat_id}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Target ditemukan! Chat ID: {chat_id}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}📊 Menggunakan {Fore.WHITE}{len(valid_tokens)}{Fore.CYAN} bot aktif{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔄 Mode INFINITE LOOP - akan berulang terus{Style.RESET_ALL}")
    print()
    
    success_count_round = 0
    total_targets = len(valid_tokens)
    round_count = 0
    total_success = 0
    total_fail = 0
    
    # 🔥 SIGNAL HANDLER UNTUK CTRL+C
    def signal_handler(sig, frame):
        global stop_flag
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}⚠️ Menghentikan proses...{Style.RESET_ALL}")
    
    original_handler = signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while not stop_flag:
            if limit_check and limit_check():
                print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan...")
                break
            
            round_count += 1
            print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🔄 ROUND {round_count}{Style.RESET_ALL}{' ' * (39 - len(str(round_count)))}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
            
            success_count_round = 0
            idx = 0
            
            for token in valid_tokens:
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Berhenti...")
                    stop_flag = True
                    break
                
                idx += 1
                otp = ''.join(random.choices('0123456789', k=random.randint(4, 6)))
                message = f"🔐 Kode verifikasi Anda: <b>{otp}</b>\n\nJangan berikan kode ini kepada siapa pun!"
                
                try:
                    resp = send_telegram_message(token, chat_id, message)
                    if resp and resp.status_code == 200:
                        status_text = "SUCCESS"
                        detail = f"OTP {otp} sent"
                        success_count_round += 1
                        total_success += 1
                    else:
                        status_text = "ERROR"
                        detail = f"Failed ({resp.status_code if resp else 'No response'})"
                        total_fail += 1
                except Exception as e:
                    status_text = "ERROR"
                    detail = str(e)[:30]
                    total_fail += 1
                
                log_target_tele(idx, total_targets, f"Bot {idx}", status_text, detail)
                
                if global_callback:
                    try:
                        global_callback(f"Bot {idx}", status_text, detail)
                    except:
                        pass
                
                if not stop_flag and idx < total_targets:
                    for _ in range(2):
                        if stop_flag:
                            break
                        time.sleep(1)
            
            if stop_flag:
                break
            
            print(f"{Fore.CYAN}📊 Round {round_count}: {Fore.GREEN}✅ {success_count_round}/{total_targets}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Total: {Fore.GREEN}✅ {total_success}{Style.RESET_ALL} | {Fore.RED}❌ {total_fail}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏳ Menunggu 60 detik...{Style.RESET_ALL}")
            
            for i in range(60):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan...")
                    stop_flag = True
                    break
                if i % 15 == 0 and i > 0:
                    print(f"{Fore.CYAN}⏳ Sisa {60 - i} detik...{Style.RESET_ALL}")
                time.sleep(1)
            
            if not stop_flag:
                print()
                    
    except KeyboardInterrupt:
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}⚠️ Proses dihentikan oleh user (CTRL+C){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    finally:
        signal.signal(signal.SIGINT, original_handler)
        signal.signal(signal.SIGTERM, original_handler)
        global_callback = None
        global_limit_check = None
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📊 HASIL AKHIR{Style.RESET_ALL}{' ' * 35}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}Total Round : {Fore.WHITE}{round_count}{Style.RESET_ALL}{' ' * (30 - len(str(round_count)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}Total Success : {Fore.WHITE}{total_success}{Style.RESET_ALL}{' ' * (25 - len(str(total_success)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}Total Fail    : {Fore.WHITE}{total_fail}{Style.RESET_ALL}{' ' * (26 - len(str(total_fail)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    
    return total_success > 0

# ==================== SPAM NGL ====================

def run_spam_ngl(target, threads=5, callback=None, limit_check=None, limit_use=None, message=None):
    global stop_flag, global_callback, global_limit_check
    stop_flag = False
    global_callback = callback
    global_limit_check = limit_check
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}💬 SPAM NGL (∞ LOOP){Style.RESET_ALL}{' ' * 32}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Target: {Fore.WHITE}{target}{Style.RESET_ALL}")
    print()
    
    if message is None:
        print(f"{Fore.YELLOW}📝 Masukkan pesan yang ingin dikirim:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   (Kosongkan untuk menggunakan pesan default){Style.RESET_ALL}")
        print()
        msg_input = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
        if msg_input:
            message = msg_input
        else:
            message = "Spam By AXKA 🔥"
            print(f"{Fore.YELLOW}💡 Menggunakan pesan default: {message}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}📝 Pesan: {Fore.CYAN}{message}{Style.RESET_ALL}")
    
    print()
    print(f"{Fore.YELLOW}⚠️  Tekan {Fore.RED}CTRL+C{Fore.YELLOW} untuk berhenti{Style.RESET_ALL}")
    print()
    
    if limit_use:
        used, msg = limit_use()
        if not used:
            print(f"{Fore.RED}[LIMIT]{Style.RESET_ALL} {msg}")
            return False
        print(f"{Fore.GREEN}[LIMIT]{Style.RESET_ALL} {msg}")
    
    success_count = 0
    total_targets = 20
    round_count = 0
    total_success = 0
    total_fail = 0
    
    # 🔥 SIGNAL HANDLER UNTUK CTRL+C
    def signal_handler(sig, frame):
        global stop_flag
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}⚠️ Menghentikan proses...{Style.RESET_ALL}")
    
    original_handler = signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while not stop_flag:
            if limit_check and limit_check():
                print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan...")
                break
            
            round_count += 1
            print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🔄 ROUND {round_count}{Style.RESET_ALL}{' ' * (39 - len(str(round_count)))}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
            
            success_count = 0
            
            for i in range(total_targets):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Berhenti...")
                    stop_flag = True
                    break
                
                url = "https://ngl.link/api/submit"
                payload = {
                    "username": target,
                    "question": message,
                    "deviceId": str(uuid.uuid4()),
                    "gameSlug": "",
                    "referrer": ""
                }
                headers = {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
                    "Content-Type": "application/json",
                    "Origin": "https://ngl.link",
                    "Referer": f"https://ngl.link/{target}"
                }
                
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=15)
                    if resp.status_code == 200:
                        status_text = "SUCCESS"
                        detail = f"Pesan {i+1} sent"
                        success_count += 1
                        total_success += 1
                    else:
                        status_text = "ERROR"
                        detail = f"({resp.status_code})"
                        total_fail += 1
                except Exception as e:
                    status_text = "ERROR"
                    detail = str(e)[:30]
                    total_fail += 1
                
                log_target_tele(i+1, total_targets, f"Pesan {i+1}", status_text, detail)
                
                if global_callback:
                    try:
                        global_callback(f"Pesan {i+1}", status_text, detail)
                    except:
                        pass
                
                if not stop_flag:
                    time.sleep(1)
            
            if stop_flag:
                break
            
            print(f"{Fore.CYAN}📊 Round {round_count}: {Fore.GREEN}✅ {success_count}/{total_targets}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Total: {Fore.GREEN}✅ {total_success}{Style.RESET_ALL} | {Fore.RED}❌ {total_fail}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏳ Menunggu 60 detik...{Style.RESET_ALL}")
            
            for i in range(60):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan...")
                    stop_flag = True
                    break
                if i % 15 == 0 and i > 0:
                    print(f"{Fore.CYAN}⏳ Sisa {60 - i} detik...{Style.RESET_ALL}")
                time.sleep(1)
            
            if not stop_flag:
                print()
                
    except KeyboardInterrupt:
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}⚠️ Proses dihentikan oleh user (CTRL+C){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    finally:
        signal.signal(signal.SIGINT, original_handler)
        signal.signal(signal.SIGTERM, original_handler)
        global_callback = None
        global_limit_check = None
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📊 HASIL AKHIR{Style.RESET_ALL}{' ' * 35}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}Total Round : {Fore.WHITE}{round_count}{Style.RESET_ALL}{' ' * (30 - len(str(round_count)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}Total Success : {Fore.WHITE}{total_success}{Style.RESET_ALL}{' ' * (25 - len(str(total_success)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}Total Fail    : {Fore.WHITE}{total_fail}{Style.RESET_ALL}{' ' * (26 - len(str(total_fail)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    
    return total_success > 0

# ==================== SPAM REPORT TELEGRAM ====================

def run_spam_report_tele(target, threads=5, callback=None, limit_check=None, limit_use=None):
    global stop_flag, global_callback, global_limit_check
    stop_flag = False
    global_callback = callback
    global_limit_check = limit_check
    
    tokens = get_all_tokens()
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🚫 SPAM REPORT TELEGRAM (∞ LOOP){Style.RESET_ALL}{' ' * 15}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Target: {Fore.WHITE}{target}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  Tekan {Fore.RED}CTRL+C{Fore.YELLOW} untuk berhenti{Style.RESET_ALL}")
    print()
    
    if limit_use:
        used, msg = limit_use()
        if not used:
            print(f"{Fore.RED}[LIMIT]{Style.RESET_ALL} {msg}")
            return False
        print(f"{Fore.GREEN}[LIMIT]{Style.RESET_ALL} {msg}")
    
    valid_tokens = []
    for token in tokens:
        status, username = check_bot_status(token)
        if status:
            valid_tokens.append(token)
    
    if not valid_tokens:
        print(f"{Fore.RED}❌ TIDAK ADA BOT YANG AKTIF!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Pastikan token di telegram_tokens.py sudah diganti{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        try:
            input()
        except:
            pass
        return False
    
    # ==================== 🔥 KONVERSI USERNAME KE ID ====================
    chat_id = None
    target_info = None
    target_clean = target.strip()
    
    print(f"{Fore.CYAN}🔍 Mencari target...{Style.RESET_ALL}")
    
    # 🔥 CEK APAKAH TARGET ADALAH ID (ANGKA)
    if target_clean.isdigit():
        chat_id = int(target_clean)
        print(f"{Fore.CYAN}📌 Target ID: {Fore.WHITE}{chat_id}{Style.RESET_ALL}")
        
        # Coba dapatkan info target
        for token in valid_tokens[:3]:
            info = get_chat_info(token, chat_id)
            if info:
                target_info = info
                break
        if target_info:
            username_display = target_info.get('username', '')
            first_name = target_info.get('first_name', '')
            print(f"{Fore.GREEN}✅ Target ditemukan: {first_name} (@{username_display}){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Tidak bisa mendapatkan info target, tapi ID valid{Style.RESET_ALL}")
    else:
        # 🔥 TARGET ADALAH USERNAME
        print(f"{Fore.CYAN}🔍 Mencari username: {Fore.WHITE}{target_clean}{Style.RESET_ALL}")
        
        # Bersihkan username
        target_username = target_clean
        if not target_username.startswith('@'):
            target_username = '@' + target_username
        
        found = False
        for token in valid_tokens:
            user_id = get_user_id_from_username(token, target_username)
            if user_id:
                chat_id = user_id
                found = True
                info = get_chat_info(token, chat_id)
                if info:
                    target_info = info
                break
        
        # Jika tidak ditemukan, coba tanpa @
        if not found:
            target_username2 = target_clean.replace('@', '')
            for token in valid_tokens:
                user_id = get_user_id_from_username(token, target_username2)
                if user_id:
                    chat_id = user_id
                    found = True
                    info = get_chat_info(token, chat_id)
                    if info:
                        target_info = info
                    break
        
        if not chat_id:
            print(f"{Fore.RED}❌ Username {target} tidak ditemukan!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Pastikan username benar dan bot sudah di-start oleh target{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Atau gunakan ID Telegram langsung (contoh: 123456789){Style.RESET_ALL}")
            print()
            print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
            try:
                input()
            except:
                pass
            return False
        
        # 🔥 TAMPILKAN HASIL KONVERSI
        if target_info:
            username_display = target_info.get('username', '')
            first_name = target_info.get('first_name', '')
            print(f"{Fore.GREEN}✅ Target ditemukan: {first_name} (@{username_display}) -> ID: {chat_id}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Target ditemukan! Chat ID: {chat_id}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}📊 Menggunakan {Fore.WHITE}{len(valid_tokens)}{Fore.CYAN} bot aktif{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔄 Mode INFINITE LOOP - akan berulang terus{Style.RESET_ALL}")
    print()
    
    round_count = 0
    total_success = 0
    total_fail = 0
    total_targets = 30
    
    messages = [
        "🚨 LAPORAN PENIPUAN! Akun ini melakukan penipuan. Tolong segera di-block!",
        "⚠️ AKUN PENIPUAN! Saya menjadi korban penipuan dari akun ini. Mohon tindakan tegas!",
        "🔴 PERINGATAN! Akun ini terindikasi penipuan. Jangan percaya dengan akun ini!",
        "❗ LAPORAN! Akun ini menipu banyak orang. Segera lakukan tindakan!",
        "💢 PENIPU! Akun ini adalah penipu. Sudah banyak korban yang melapor!",
        "🚫 AKUN PALSU! Ini adalah akun penipuan yang harus segera ditutup!",
        "⚡ LAPORAN! Saya melaporkan akun ini karena melakukan penipuan dan pencurian!",
        "🔥 AKUN BERBAHAYA! Jangan percaya dengan akun ini, ini adalah penipuan!",
        "⚠️ PENIPUAN MASSAL! Akun ini menipu banyak orang. Tolong segera di-block!",
        "🚨 DARURAT! Akun ini adalah penipu yang sudah merugikan banyak orang!"
    ]
    
    # 🔥 SIGNAL HANDLER UNTUK CTRL+C
    def signal_handler(sig, frame):
        global stop_flag
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}⚠️ Menghentikan proses...{Style.RESET_ALL}")
    
    original_handler = signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while not stop_flag:
            if limit_check and limit_check():
                print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan...")
                break
            
            round_count += 1
            print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🔄 ROUND {round_count}{Style.RESET_ALL}{' ' * (39 - len(str(round_count)))}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
            
            success_count = 0
            
            for i in range(total_targets):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Berhenti...")
                    stop_flag = True
                    break
                
                msg = random.choice(messages)
                token = random.choice(valid_tokens)
                
                try:
                    resp = send_telegram_message(token, chat_id, msg)
                    if resp and resp.status_code == 200:
                        status_text = "SUCCESS"
                        detail = f"Report {i+1} sent"
                        success_count += 1
                        total_success += 1
                    else:
                        status_text = "ERROR"
                        detail = f"({resp.status_code if resp else 'No response'})"
                        total_fail += 1
                except Exception as e:
                    status_text = "ERROR"
                    detail = str(e)[:30]
                    total_fail += 1
                
                log_target_tele(i+1, total_targets, f"Report {i+1}", status_text, detail)
                
                if global_callback:
                    try:
                        global_callback(f"Report {i+1}", status_text, detail)
                    except:
                        pass
                
                if not stop_flag and i < total_targets - 1:
                    for _ in range(2):
                        if stop_flag:
                            break
                        time.sleep(1)
            
            if stop_flag:
                break
            
            print(f"{Fore.CYAN}📊 Round {round_count}: {Fore.GREEN}✅ {success_count}/{total_targets}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}📊 Total: {Fore.GREEN}✅ {total_success}{Style.RESET_ALL} | {Fore.RED}❌ {total_fail}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}⏳ Menunggu 60 detik...{Style.RESET_ALL}")
            
            for i in range(60):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan...")
                    stop_flag = True
                    break
                if i % 15 == 0 and i > 0:
                    print(f"{Fore.CYAN}⏳ Sisa {60 - i} detik...{Style.RESET_ALL}")
                time.sleep(1)
            
            if not stop_flag:
                print()
                
    except KeyboardInterrupt:
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}⚠️ Proses dihentikan oleh user (CTRL+C){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
    
    finally:
        signal.signal(signal.SIGINT, original_handler)
        signal.signal(signal.SIGTERM, original_handler)
        global_callback = None
        global_limit_check = None
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📊 HASIL AKHIR{Style.RESET_ALL}{' ' * 35}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.CYAN}Total Round : {Fore.WHITE}{round_count}{Style.RESET_ALL}{' ' * (30 - len(str(round_count)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}Total Success : {Fore.WHITE}{total_success}{Style.RESET_ALL}{' ' * (25 - len(str(total_success)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}Total Fail    : {Fore.WHITE}{total_fail}{Style.RESET_ALL}{' ' * (26 - len(str(total_fail)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    
    return total_success > 0

# ==================== REACT WA ====================

def run_react_wa(target, threads=5, callback=None, limit_check=None, limit_use=None):
    """React WA - React ke postingan WhatsApp Channel"""
    global stop_flag, global_callback, global_limit_check
    stop_flag = False
    global_callback = callback
    global_limit_check = limit_check
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}❤️ REACT WHATSAPP CHANNEL{Style.RESET_ALL}{' ' * 19}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    print()
    
    # 🔥 JANGAN PAKAI LIMIT DI SINI - SUDAH DIPAKAI DI MAIN.PY
    
    # 🔥 INPUT LINK SALURAN
    print(f"{Fore.YELLOW}📎 Masukkan link postingan WhatsApp Channel:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Contoh: https://whatsapp.com/channel/0029VbDFJJoElagrDWebCB47/311{Style.RESET_ALL}")
    print(f"{Fore.RED}   ⚠️  WAJIB ada ID postingan di akhir (contoh: /311){Style.RESET_ALL}")
    print()
    channel_url = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
    
    if not channel_url:
        print(f"\n{Fore.RED}❌ Link tidak boleh kosong!{Style.RESET_ALL}")
        time.sleep(1)
        return False
    
    # 🔥 VALIDASI LINK - HARUS ADA ID POSTINGAN
    if not re.search(r'/channel/[^/]+/\d+$', channel_url):
        print(f"\n{Fore.RED}❌ Link tidak valid! Harus ada ID postingan di akhir!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Contoh: https://whatsapp.com/channel/0029VbDFJJoElagrDWebCB47/311{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False
    
    # 🔥 INPUT EMOJI
    print()
    print(f"{Fore.YELLOW}😊 Masukkan emoji yang ingin digunakan (maksimal 3):{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Contoh: 👍, 👎, ☠, ❤️, 🔥, 😍{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Pisahkan dengan koma jika lebih dari 1{Style.RESET_ALL}")
    print()
    emoji_input = input(f"{Fore.WHITE}└─> {Style.RESET_ALL}").strip()
    
    if not emoji_input:
        print(f"\n{Fore.RED}❌ Emoji tidak boleh kosong!{Style.RESET_ALL}")
        time.sleep(1)
        return False
    
    # 🔥 PARSING EMOJI
    emojis = [e.strip() for e in emoji_input.split(',') if e.strip()]
    if len(emojis) > 3:
        print(f"\n{Fore.RED}❌ Maksimal 3 emoji!{Style.RESET_ALL}")
        time.sleep(1)
        return False
    
    emoji_codes = ','.join(emojis)
    print(f"\n{Fore.GREEN}✅ Emoji yang akan digunakan: {emoji_codes}{Style.RESET_ALL}")
    
    # 🔥 AMBIL TOKEN VIP DARI FIREBASE (SEMBUNYIKAN)
    vip_token = get_vip_token_from_firebase()
    if not vip_token:
        vip_token = get_vip_token()
    
    # 🔥 KIRIM REQUEST (SEMBUNYIKAN DETAIL)
    print(f"\n{Fore.CYAN}⏳ Mengirim request...{Style.RESET_ALL}")
    
    url = "https://auto-reaction.zxcoderid.web.id/api/vip/open-api/react"
    params = {
        "api_key": vip_token,
        "url": channel_url,
        "reaction": emoji_codes
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        if data.get('success'):
            print(f"\n{Fore.GREEN}✅ {data.get('message', 'Sukses!')}{Style.RESET_ALL}")
            
            # Tampilkan detail hasil
            task = data.get('task', {})
            vip_info = data.get('vip', {})
            
            print(f"\n{Fore.CYAN}📊 Hasil:{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}Status: {Fore.GREEN}{task.get('status', 'success')}{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}Reaction: {Fore.MAGENTA}{task.get('reaction_code', emoji_codes)}{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}Point: {Fore.GREEN}{vip_info.get('pointRemaining', '?')}{Style.RESET_ALL}")
            
            print()
            print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
            input()
            return True
        else:
            error = data.get('error', {})
            error_type = error.get('type', 'UNKNOWN')
            error_msg = error.get('message', 'Unknown error')
            
            print(f"\n{Fore.RED}❌ Gagal!{Style.RESET_ALL}")
            print(f"  {Fore.RED}Error: {error_msg}{Style.RESET_ALL}")
            
            if error_type == 'MISSING_POST_ID':
                print(f"\n{Fore.YELLOW}💡 Pastikan link adalah URL postingan, bukan URL channel{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   Contoh: https://whatsapp.com/channel/0029VbDFJJoElagrDWebCB47/311{Style.RESET_ALL}")
            elif 'INVALID_API_KEY' in error_type or 'API_KEY_NOT_FOUND' in error_type:
                print(f"\n{Fore.YELLOW}💡 Token VIP mungkin kadaluarsa!{Style.RESET_ALL}")
            
            print()
            print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
            input()
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n{Fore.RED}❌ Timeout! Server tidak merespon{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}❌ Connection Error! Cek koneksi internet{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        return False

# ==================== FUNGSI VIP TOKEN DARI FIREBASE ====================

def get_vip_token_from_firebase():
    """Ambil VIP token dari Firebase"""
    try:
        import requests
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
        import requests
        url = "https://otpaxka-default-rtdb.asia-southeast1.firebasedatabase.app/vip_token.json"
        resp = requests.put(url, json=token, timeout=5)
        return resp.status_code in [200, 201]
    except:
        return False

# ==================== CEK STATUS BOT ====================

def check_all_bots():
    tokens = get_all_tokens()
    print()
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🤖 STATUS BOT TELEGRAM{Style.RESET_ALL}{' ' * 25}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}")
    
    active = 0
    for i, token in enumerate(tokens):
        if not token or token.startswith('YOUR_TOKEN') or token == "7581234567:AAHabcdefghijklmnopqrstuvwxyz123456":
            print(f"{Fore.YELLOW}⚠️  Bot {i+1}: TOKEN CONTOH - GANTI DENGAN ASLI!{Style.RESET_ALL}")
            continue
            
        status, username = check_bot_status(token)
        if status:
            print(f"{Fore.GREEN}✅ Bot {i+1}: @{username} - AKTIF{Style.RESET_ALL}")
            active += 1
        else:
            print(f"{Fore.RED}❌ Bot {i+1}: TOKEN TIDAK VALID{Style.RESET_ALL}")
    
    print()
    print(f"{Fore.CYAN}📊 Total: {Fore.WHITE}{active}/{len(tokens)} bot aktif{Style.RESET_ALL}")
    
    # 🔥 TAMPILKAN VIP TOKEN (SEMBUNYIKAN)
    vip_token = get_vip_token_from_firebase()
    if not vip_token:
        vip_token = get_vip_token()
    if vip_token:
        print(f"{Fore.CYAN}🔑 VIP Token: {Fore.YELLOW}{vip_token[:15]}...{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}🔑 VIP Token: TIDAK DITEMUKAN{Style.RESET_ALL}")
    
    if active == 0:
        print(f"{Fore.YELLOW}💡 Pastikan token di telegram_tokens.py sudah diganti dengan token asli dari @BotFather{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
    try:
        input()
    except KeyboardInterrupt:
        pass
    return active