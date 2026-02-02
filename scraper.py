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
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        configs = []
        for msg in messages:
            # استخراج دقیق لینک‌هایی که با پروتکل‌ها شروع می‌شوند
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', msg.get_text())
            configs.extend(found)
        return configs
    except: return []

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
    all_raw.extend(get_live_configs(ch))

# حذف موارد تکراری و لینک‌های ناقص
all_raw = list(set([c for c in all_raw if len(c) > 10]))

categorized = {
    'all': all_raw,
    'vless': [c for c in all_raw if c.startswith('vless')],
    'vmess': [c for c in all_raw if c.startswith('vmess')],
    'trojan': [c for c in all_raw if c.startswith('trojan')],
    'ss': [c for c in all_raw if c.startswith('ss')]
}

for key, value in categorized.items():
    content = "\n".join(value)
    
    # فایل اول: مخصوص برنامه (Base64) - این فایل با vless شروع نمی شود و طبیعی است
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f: f.write(encoded)
    
    # فایل دوم: مخصوص مشاهده انسان (Raw) - این فایل دقیقاً با vless شروع می شود
    with open(f'{key}_raw.txt', 'w') as f: f.write(content)

stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w') as f: json.dump(stats, f)
