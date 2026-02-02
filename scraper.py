import requests
from bs4 import BeautifulSoup
import re
import base64
import json

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

channels = ['v2rayng_org', 'v2ray_alpha', 'VlessConfig']
all_configs = list(set(sum([get_live_configs(ch) for ch in channels], [])))

categorized = {
    'all': all_configs,
    'vless': [c for c in all_configs if c.startswith('vless')],
    'vmess': [c for c in all_configs if c.startswith('vmess')],
    'trojan': [c for c in all_configs if c.startswith('trojan')]
}

# ذخیره تعداد کانفیگ‌ها برای نمایش در سایت
stats = {}
for key, value in categorized.items():
    stats[key] = len(value)
    content = "\n".join(value)
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f:
        f.write(encoded)

with open('info.json', 'w') as f:
    json.dump(stats, f)
