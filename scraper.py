import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import socket
import datetime

def check_connection(config):
    try:
        if 'vmess://' in config: return True 
        parts = config.split('@')[1].split('#')[0]
        host, port = parts.split(':')[0], int(parts.split(':')[1].split('?')[0])
        with socket.create_connection((host, port), timeout=2):
            return True
    except: return False

def get_live_configs(channel_username):
    url = f"https://t.me/s/{channel_username.replace('@', '')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        configs = []
        for msg in messages:
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', msg.get_text())
            configs.extend(found)
        return configs
    except: return []

# لیست کامل کانال‌های ارسالی شما
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
    print(f"Scraping {ch}...")
    all_raw.extend(get_live_configs(ch))

all_raw = list(set(all_raw))
print(f"Total found: {len(all_raw)}. Testing connections...")
valid_configs = [c for c in all_raw if check_connection(c)]

categorized = {
    'all': valid_configs,
    'vless': [c for c in valid_configs if c.startswith('vless')],
    'vmess': [c for c in valid_configs if c.startswith('vmess')],
    'trojan': [c for c in valid_configs if c.startswith('trojan')],
    'ss': [c for c in valid_configs if c.startswith('ss')]
}

for key, value in categorized.items():
    content = "\n".join(value)
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f: f.write(encoded)

stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w') as f: json.dump(stats, f)
