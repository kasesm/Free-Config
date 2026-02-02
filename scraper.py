import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import datetime
import time
import random

def get_live_configs(channel_username):
    username = channel_username.replace('@', '').strip()
    # استفاده از لینک مستقیم نسخه وب تلگرام
    url = f"https://t.me/s/{username}"
    
    # لیست یوزر ایجنت‌ها برای دور زدن محدودیت تلگرام
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    
    headers = {'User-Agent': random.choice(user_agents)}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Status Code {response.status_code} for {username}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # تمام باکس‌های پیام را پیدا می‌کند
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        configs = []
        for msg in messages:
            text = msg.get_text()
            # پیدا کردن کانفیگ‌ها با Regex
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', text)
            configs.extend(found)
        return configs
    except Exception as e:
        print(f"Error for {username}: {e}")
        return []

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
    configs = get_live_configs(ch)
    print(f"Found: {len(configs)}") # این عدد باید اینجا چاپ شود
    all_raw.extend(configs)
    time.sleep(random.uniform(1.5, 3)) # وقفه تصادفی برای شک نکردن تلگرام

all_raw = list(set(all_raw))

# بقیه کد ذخیره سازی طبق روال قبل...
categorized = {
    'all': all_raw,
    'vless': [c for c in all_raw if c.startswith('vless')],
    'vmess': [c for c in all_raw if c.startswith('vmess')],
    'trojan': [c for c in all_raw if c.startswith('trojan')],
    'ss': [c for c in all_raw if c.startswith('ss')]
}

for key, value in categorized.items():
    content = "\n".join(value)
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    with open(f'{key}_sub.txt', 'w') as f: f.write(encoded)
    with open(f'{key}_raw.txt', 'w') as f: f.write(content)

stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w') as f: json.dump(stats, f)
