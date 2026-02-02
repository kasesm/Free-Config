import requests
from bs4 import BeautifulSoup
import re
import base64

def clean_and_rename(config, my_brand="MyFreeNet"):
    # جدا کردن بخش اصلی کانفیگ از اسم (بعد از #)
    if '#' in config:
        base_config = config.split('#')[0]
        return f"{base_config}#{my_brand}"
    return f"{config}#{my_brand}"

def extract_host(config):
    # استخراج آدرس سرور برای شناسایی تکراری‌ها
    try:
        host_part = config.split('@')[1].split(':')[0]
        return host_part
    except:
        return config

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
            # پیدا کردن تمام پروتکل‌ها
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', raw_text)
            configs.extend(found)
        return configs
    except:
        return []

# --- تنظیمات ---
channels = ['v2rayng_org', 'v2ray_alpha', 'VlessConfig', 'FreeVlessConfig']
my_name = "Gemini_Configs" # نامی که می‌خواهید روی کانفیگ‌ها باشد

all_raw_configs = []
for ch in channels:
    print(f"Fetching from {ch}...")
    all_raw_configs.extend(get_live_configs(ch))

# --- فیلتر و تمیزکاری ---
seen_hosts = set()
unique_configs = []

for conf in all_raw_configs:
    host = extract_host(conf)
    if host not in seen_hosts:
        seen_hosts.add(host)
        unique_configs.append(clean_and_rename(conf, my_name))

# --- ذخیره‌سازی ---
final_text = "\n".join(unique_configs)

# ۱. فایل متنی
with open('configs.txt', 'w', encoding='utf-8') as f:
    f.write(final_text)

# ۲. فایل Base64 (سابلینک)
with open('sub_link.txt', 'w', encoding='utf-8') as f:
    encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    f.write(encoded)

print(f"Finished! {len(unique_configs)} clean configs saved.")
