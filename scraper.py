import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import datetime
import time

def get_live_configs(channel_username):
    username = channel_username.replace('@', '').strip()
    url = f"https://t.me/s/{username}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج تمام متن پیام‌ها
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        configs = []
        
        for msg in messages:
            # این الگو کل لینک کانفیگ را تا رسیدن به فاصله یا کاراکتر غیرمجاز برمی‌دارد
            found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"]+', msg.get_text())
            configs.extend(found)
            
        return configs
    except:
        return []

# لیست کانال‌های شما
channels = [
    'Azadnet', 'AR1N24B', 'aristapnel', 'arshia_mod_fun', 'canfing_vpn', 
    'capoit', 'configfa', 'configraygan', 'fg_link', 'freenet_vt', 
    'hamedvpns', 'iphone02016vpn', 'irancpi_vpn', 'marambashi', 'merlinvpn', 
    'myporoxy', 'netaccount', 'persianvpnhub', 'pewezavpn', 'proxydaemi', 
    'proxyskull', 'rahgozar94725_ip', 'sinavm', 'soskeynet', 'tikvpnir', 
    'v2freehub', 'wiki_tajrobe', 'xsfilternet', 'yebekhe' , 'Cygag' , 'DailyV2RY' ,
    'v2ray_configs_pools' , 'v2rayvpnchannel' , 'Galax_vpn' , 'v2makers' ,
]

all_raw = []
for ch in channels:
    print(f"در حال دریافت از: {ch}")
    res = get_live_configs(ch)
    print(f"تعداد یافته شده: {len(res)}")
    all_raw.extend(res)
    time.sleep(0.5)

# حذف تکراری‌ها و موارد ناقص
all_raw = list(set([c for c in all_raw if len(c) > 20]))

# دسته‌بندی
categorized = {
    'all': all_raw,
    'vless': [c for c in all_raw if c.startswith('vless')],
    'vmess': [c for c in all_raw if c.startswith('vmess')],
    'trojan': [c for c in all_raw if c.startswith('trojan')],
    'ss': [c for c in all_raw if c.startswith('ss')]
}

# ذخیره سازی
for key, value in categorized.items():
    content = "\n".join(value)
    # نسخه Base64 برای سابلینک کلاینت
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f: f.write(encoded)
    # نسخه Raw برای تست چشمی شما
    with open(f'{key}_raw.txt', 'w') as f: f.write(content)

# آمار
stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w') as f: json.dump(stats, f)

print(f"عملیات تمام شد. مجموع کانفیگ‌ها: {len(all_raw)}")
