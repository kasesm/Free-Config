import requests
from bs4 import BeautifulSoup
import re
import base64

def clean_config(config):
    # حذف تگ‌های تبلیغاتی انتهای کانفیگ
    cleaned = re.split(r'[#\s]', config)[0]
    return cleaned

def get_live_configs(channel_username):
    url = f"https://t.me/s/{channel_username.replace('@', '')}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        configs = []
        for msg in messages:
            raw_text = msg.get_text()
            found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', raw_text)
            for f in found:
                cleaned = clean_config(f)
                if len(cleaned) > 20:
                    configs.append(cleaned)
        return configs
    except:
        return []

# لیست کانال‌های هدف را اینجا اضافه کنید
channels = ['v2rayng_org', 'v2ray_alpha', 'VlessConfig', 'FreeVlessConfig']

all_configs = []
for ch in channels:
    all_configs.extend(get_live_configs(ch))

# حذف تکراری‌ها
unique_configs = list(set(all_configs))
final_text = "\n".join(unique_configs)

# ۱. ذخیره به صورت متن ساده (Plain Text)
with open('configs.txt', 'w', encoding='utf-8') as f:
    f.write(final_text)

# ۲. ذخیره به صورت Base64 (برای سابلینک استاندارد)
with open('sub_link.txt', 'w', encoding='utf-8') as f:
    encoded_configs = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    f.write(encoded_configs)

print(f"Done! Found {len(unique_configs)} configs.")
