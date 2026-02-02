import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import socket
import datetime
import time

def check_connection(config):
    # یک تست ساده برای اطمینان از فرمت صحیح و زنده بودن تقریبی
    try:
        if 'vmess://' in config: return True 
        if '@' not in config: return False
        parts = config.split('@')[1].split('#')[0]
        if ':' not in parts: return False
        host = parts.split(':')[0]
        port_part = parts.split(':')[1].split('?')[0]
        port = int(''.join(filter(str.isdigit, port_part)))
        
        # تست پورت (اختیاری - اگر سرعت خیلی کم شد این بخش را حذف کنید)
        with socket.create_connection((host, port), timeout=1):
            return True
    except: return False

def get_live_configs(channel_username):
    # حذف @ از ابتدای نام کانال در صورت وجود
    username = channel_username.replace('@', '').strip()
    url = f"https://t.me/s/{username}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200: return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # گشتن در تمام متن پیام‌ها
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        configs = []
        for msg in messages:
            # پیدا کردن پروتکل‌ها با Regex دقیق‌تر
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', msg.get_text())
            configs.extend(found)
        return configs
    except Exception as e:
        print(f"Error scraping {username}: {e}")
        return []

# لیست کانال‌های شما
channels = [
    'Azadnet', 'AR1N24B', 'aristapnel', 'arshia_mod_fun', 'canfing_vpn', 
    'capoit', 'configfa', 'configraygan', 'fg_link', 'freenet_vt', 
    'hamedvpns', 'iphone02016vpn', 'irancpi_vpn', 'marambashi', 'merlinvpn', 
    'myporoxy', 'netaccount', 'persianvpnhub', 'pewezavpn', 'proxydaemi', 
    'proxyskull', 'rahgozar94725_ip', 'sinavm', 'soskeynet', 'tikvpnir', 
    'v2freehub', 'wiki_tajrobe', 'xsfilternet', 'yebekhe'
]

all_raw = []
for ch in channels:
    print(f"در حال استخراج از: {ch}...")
    configs = get_live_configs(ch)
    print(f"پیدا شد: {len(configs)}")
    all_raw.extend(configs)
    time.sleep(1) # وقفه کوتاه برای جلوگیری از مسدود شدن توسط تلگرام

all_raw = list(set(all_raw)) # حذف تکراری‌ها

# تست اتصال (در صورت نیاز به سرعت بالاتر، این خط را با valid_configs = all_raw جایگزین کنید)
print(f"تعداد کل یافت شده: {len(all_raw)}. در حال تست اتصال...")
valid_configs = [c for c in all_raw if check_connection(c)]

if not valid_configs:
    print("هشدار: هیچ کانفیگ سالمی پیدا نشد. جهت اطمینان از لیست خام استفاده می‌شود.")
    valid_configs = all_raw[:100] # حداقل ۱۰۰ مورد اول را نگه می‌دارد

categorized = {
    'all': valid_configs,
    'vless': [c for c in valid_configs if c.startswith('vless')],
    'vmess': [c for c in valid_configs if c.startswith('vmess')],
    'trojan': [c for c in valid_configs if c.startswith('trojan')],
    'ss': [c for c in valid_configs if c.startswith('ss')]
}

# ذخیره سازی
for key, value in categorized.items():
    content = "\n".join(value)
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f: f.write(encoded)

stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w') as f: json.dump(stats, f)

print("عملیات با موفقیت پایان یافت.")
