#!/usr/bin/env python3
# telegram_tokens.py - Token Bot Telegram + VIP Token

# 🔥 DAFTAR TOKEN BOT TELEGRAM (10 TOKEN)
TOKENS = [
    "8338187636:AAFEpGPVCuKDq5JciJyb2wSX7A4D_0GJ96M",
    "8928480699:AAFfgQ8-Z9gBZyYZcgkYlekfruoBUThcndA",
    "8861113859:AAHcNH0dol2Cst6puMxqkNJFGmoWywc-q04",
    "8673832825:AAGCtSMiSggiWBmGnckCrXDYu8fx-A07jmA",
    "8331281574:AAHgI36wDWcVBi5hOLqnDu0u1x-Wj7tSzlw",
    "7991918859:AAEia1Cuh1TrLAM2MCPqexxq2-G5WsBgoiQ",
    "8496191432:AAEf0TbEjfiWLjHmNSaL0lMR27FTJGCc6Vs",
    "8176976604:AAFmi8gaQCMxTAz05Bcu95gCBvzQuluFV_Y",
    "8218789724:AAFRZsWKpMx3XLw_D218ABYCVc1nGp_OwYo",
    "8044898619:AAEJDIRl5T5QD_qfxtZkGC87Tr8qirioLJM",
]

# 🔥 TOKEN VIP REACT WA (DEFAULT - AKAN DI OVERRIDE OLEH FIREBASE)
VIP_TOKEN = "VIP-7948-2B65-EB9E-7D6D"

# 🔥 FUNGSI
def get_token(index):
    """Ambil token berdasarkan index"""
    if 0 <= index < len(TOKENS):
        return TOKENS[index]
    return None

def get_all_tokens():
    """Ambil semua token"""
    return TOKENS

def count_tokens():
    """Jumlah token"""
    return len(TOKENS)

def get_vip_token():
    """Ambil VIP token default"""
    return VIP_TOKEN

def set_vip_token(new_token):
    """Set VIP token (hanya untuk fallback)"""
    global VIP_TOKEN
    VIP_TOKEN = new_token