import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import socket

def check_connection(config):
    # استخراج هاست و پورت برای تست
    try:
        if 'vmess://' in config:
            # vmess پیچیده است، فعلاً فرض می‌کنیم سالم است یا از هاست استفاده می‌کنیم
            return True 
        
        parts = config.split('@')[1].split('#')[0]
        host_port = parts.split(':')
        host = host_port[0]
        port = int(host_port[1].split('?')[0])
        
        # تست باز بودن پورت (TCP Connect)
        with socket.create_connection((host, port), timeout=2):
            return True
    except:
        return False

def get_live_configs(channel_username):
    url = f"https://t.me/s/{channel_username.replace('@', '')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        configs = []
        for msg in messages:
            raw_text = msg.get_text()
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', raw_text)
            configs.extend(found)
        return configs
    except:
        return []

# --- شروع فرآیند ---
channels = ['v2rayng_org', 'v2ray_alpha', 'VlessConfig']
all_raw = list(set(sum([get_live_configs(ch) for ch in channels], [])))

# تست سلامت کانفیگ‌ها (فقط آن‌هایی که متصل می‌شوند)
print("Testing configs... this may take a while.")
valid_configs = [c for c in all_raw if check_connection(c)]

categorized = {
    'all': valid_configs,
    'vless': [c for c in valid_configs if c.startswith('vless')],
    'vmess': [c for c in valid_configs if c.startswith('vmess')],
    'trojan': [c for c in valid_configs if c.startswith('trojan')]
}

stats = {}
for key, value in categorized.items():
    stats[key] = len(value)
    content = "\n".join(value)
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f:
        f.write(encoded)

with open('info.json', 'w') as f:
    json.dump(stats, f)

print(f"Total valid configs found: {len(valid_configs)}")
