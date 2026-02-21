import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import datetime
import time

# تابع کمکی برای استخراج کانفیگ از هر متنی
def extract_configs(text):
    if not text: return []
    return re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"]+', text)

# تابع هوشمند برای تغییر نام کانفیگ‌ها
def rename_config(config, index):
    new_name = f"@smartconfigs_{index}"
    try:
        if config.startswith('vmess://'):
            # استخراج بخش Base64
            b64_part = config[8:]
            # اصلاح پدینگ
            missing_padding = len(b64_part) % 4
            if missing_padding: b64_part += '=' * (4 - missing_padding)
            
            data = json.loads(base64.b64decode(b64_part).decode('utf-8'))
            data['ps'] = new_name
            return 'vmess://' + base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        else:
            # برای پروتکل‌های VLESS, Trojan, SS
            if '#' in config:
                base = config.split('#')[0]
                return f"{base}#{new_name}"
            return f"{config}#{new_name}"
    except:
        return config

def get_live_configs(channel_username):
    username = channel_username.replace('@', '').strip()
    url = f"https://t.me/s/{username}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    found_in_channel = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        for msg in messages:
            text = msg.get_text()
            # ۱. استخراج مستقیم از متن پیام
            found_in_channel.extend(extract_configs(text))
            
            # ۲. بررسی لینک‌های موجود (برای فایل txt یا سابلینک)
            links = re.findall(r'https?://[^\s<>"]+', text)
            for link in links:
                if link.endswith('.txt') or 'sub' in link or 'githubusercontent' in link:
                    try:
                        res = requests.get(link, timeout=10)
                        if res.status_code == 200:
                            content = res.text
                            # بررسی اگر محتوا Base64 بود (سابلینک‌های معمولی)
                            try:
                                decoded = base64.b64decode(content).decode('utf-8')
                                found_in_channel.extend(extract_configs(decoded))
                            except:
                                # اگر متن خام بود
                                found_in_channel.extend(extract_configs(content))
                    except: continue
        return found_in_channel
    except:
        return []

# لیست کانال‌های هدف
channels = [
    'Azadnet', 'AR14N24B', 'aristapnel', 'arshia_mod_fun', 'canfing_vpn', 
    'capoit', 'configfa', 'configraygan', 'fg_link', 'freenet_vt', 
    'hamedvpns', 'iphone02016vpn', 'irancpi_vpn', 'marambashi', 'merlinvpn', 
    'myporoxy', 'netaccount', 'persianvpnhub', 'pewezavpn', 'proxydaemi', 
    'proxyskull', 'rahgozar94725_ip', 'sinavm', 'soskeynet', 'tikvpnir', 
    'v2freehub', 'wiki_tajrobe', 'xsfilternet', 'yebekhe' , 'Cygag' , 'DailyV2RY' ,
    'v2ray_configs_pools' , 'v2rayvpnchannel' , 'Galax_vpn' , 'v2makers' , 'FREE_V2RAYS' ,
    'isubvpn' , 'AchaVPN', 'v2ray_free_conf', 'vpnbuying', 'v2rayfori', 'v_ngfree', 'ehsawn8', 
    'V2Shop_Com' , 'oneclickvpnkeys', 'NETMelliAnti', 'V2rayngSeven', 'proxy_Shadowsocks', 
    'FreeConfigV2ray_1', 'v2rayfresh', 'v2ray_youtube_group/10', 'v2rayfreedaily', 'outlineOpenKey',
    'PrivateVPNs', 'VlessConfig', 'vmessiraan', 'vmesskhodam', 'vmessh', 'config_ss','config_v2ray_daily',
    'prrofile_purple', 'v2_mod_shop', 'anty_filter', 'YamYamProxy', 'ettehad_vpn', 'DarkTeam_VPN', 
    'filter_breaker', 'iran_v2ray1'
]


all_extracted = []
print(f"{'Channel Name':<20} | {'Count':<10}") # یک سرتیتر زیبا برای لاگ گیت‌هاب
print("-" * 35)

for ch in channels:
    configs = get_live_configs(ch)
    count = len(configs)
    
    # چاپ گزارش در بخش Actions
    print(f"{ch:<20} | {count:<10} ✅")
    
    all_extracted.extend([rename_config(c, i + len(all_extracted), f"VIP_{ch}" if ch in vip_channels else "Normal") 
                          for i, c in enumerate(configs, 1)])
    time.sleep(0.1)

print("-" * 35)
print(f"Total Configs Found: {len(all_extracted)}")



# ۱. حذف تکراری‌ها و فیلتر کردن کانفیگ‌های خیلی کوتاه (خراب)
unique_raw = list(set([c for c in all_extracted if len(c) > 30]))

# ۲. تغییر نام همه‌ی کانفیگ‌ها با شماره ردیف
final_configs = []
for i, conf in enumerate(unique_raw, 1):
    final_configs.append(rename_config(conf, i))

# دسته‌بندی برای خروجی
categorized = {
    'all': final_configs,
    'vless': [c for c in final_configs if c.startswith('vless')],
    'vmess': [c for c in final_configs if c.startswith('vmess')],
    'trojan': [c for c in final_configs if c.startswith('trojan')],
    'ss': [c for c in final_configs if c.startswith('ss')]
}

# ذخیره سازی در فایل‌ها
for key, value in categorized.items():
    content = "\n".join(value)
    # خروجی خام
    with open(f'{key}_raw.txt', 'w', encoding='utf-8') as f: f.write(content)
    # خروجی Base64 برای سابلینک
    with open(f'{key}_sub.txt', 'w', encoding='utf-8') as f:
        f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))

# به‌روزرسانی آمار در info.json
stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)

print(f"Done! Total unique configs: {len(final_configs)}")
