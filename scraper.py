import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import datetime
import time

def extract_configs(text):
    if not text: return []
    return re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"]+', text)

def rename_config(config, index, is_special=False):
    # نام پایه طبق خواسته شما
    new_name = "@smartconfigs"
    # اگر از کانال ویژه بود، تگ ویژه اضافه شود
    if is_special:
        new_name += "_(ویژه)"
    
    try:
        if config.startswith('vmess://'):
            b64_part = config[8:]
            # رفع مشکل Padding در Base64
            missing_padding = len(b64_part) % 4
            if missing_padding: b64_part += '=' * (4 - missing_padding)
            
            data = json.loads(base64.b64decode(b64_part).decode('utf-8'))
            data['ps'] = new_name # تغییر نام در vmess
            return 'vmess://' + base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        else:
            # برای vless, trojan, ss (تغییر نام بعد از هشتگ)
            base = config.split('#')[0]
            return f"{base}#{new_name}"
    except: 
        return config

def get_live_configs(channel_username):
    username = channel_username.replace('@', '').strip()
    url = f"https://t.me/s/{username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    found_configs = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        for msg in messages:
            text = msg.get_text()
            # ۱. استخراج مستقیم از متن
            found_configs.extend(extract_configs(text))
            
            # ۲. استخراج از لینک‌های سابلینک یا فایل txt داخل پیام
            links = re.findall(r'https?://[^\s<>"]+', text)
            for link in links:
                if any(x in link.lower() for x in ['.txt', 'sub', 'githubusercontent', 'raw']):
                    try:
                        res = requests.get(link, timeout=10)
                        if res.status_code == 200:
                            content = res.text
                            # بررسی اگر محتوا Base64 بود
                            try:
                                decoded = base64.b64decode(content).decode('utf-8')
                                found_configs.extend(extract_configs(decoded))
                            except:
                                found_configs.extend(extract_configs(content))
                    except: continue
        return found_configs
    except: return []

# لیست کانال‌ها
high_volume_channel = 'filter_breaker'
special_channel = 'isubvpn'
normal_channels = [
    'Azadnet', 'AR14N24B', 'aristapnel', 'arshia_mod_fun', 'canfing_vpn', 
    'capoit', 'configfa', 'configraygan', 'fg_link', 'freenet_vt', 
    'hamedvpns', 'iphone02016vpn', 'irancpi_vpn', 'marambashi', 'merlinvpn', 
    'myporoxy', 'netaccount', 'persianvpnhub', 'pewezavpn', 'proxydaemi', 
    'proxyskull', 'rahgozar94725_ip', 'sinavm', 'soskeynet', 'tikvpnir', 
    'v2freehub', 'wiki_tajrobe', 'xsfilternet', 'yebekhe' , 'Cygag' , 'DailyV2RY' ,
    'v2ray_configs_pools' , 'v2rayvpnchannel' , 'Galax_vpn' , 'v2makers' , 'FREE_V2RAYS' ,
    'AchaVPN', 'v2ray_free_conf', 'vpnbuying', 'v2rayfori', 'v_ngfree', 'ehsawn8', 
    'V2Shop_Com' , 'oneclickvpnkeys', 'NETMelliAnti', 'V2rayngSeven', 'proxy_Shadowsocks', 
    'FreeConfigV2ray_1', 'v2rayfresh', 'v2ray_youtube_group/10', 'v2rayfreedaily', 'outlineOpenKey',
    'PrivateVPNs', 'VlessConfig', 'vmessiraan', 'vmesskhodam', 'vmessh', 'config_ss','config_v2ray_daily',
    'prrofile_purple', 'v2_mod_shop', 'anty_filter', 'YamYamProxy', 'ettehad_vpn', 'DarkTeam_VPN', 'iran_v2ray1',
    'samiotech', 'Hope_Net',
]

print(f"{'Channel Name':<25} | {'Count':<10}")
print("-" * 40)

# ۱. پردازش منبع پرحجم
hv_raw = get_live_configs(high_volume_channel)
hv_unique = list(set([c for c in hv_raw if len(c) > 30]))
hv_final = [rename_config(c, i, is_special=False) for i, c in enumerate(hv_unique, 1)]
print(f"{high_volume_channel:<25} | {len(hv_final):<10} 🔥")

# ۲. پردازش منبع ویژه
special_raw = get_live_configs(special_channel)
special_final = [rename_config(c, i, is_special=True) for i, c in enumerate(list(set(special_raw)), 1) if len(c) > 30]
print(f"{special_channel:<25} | {len(special_final):<10} ⭐")

# ۳. پردازش سایر کانال‌ها
normal_all_raw = []
normal_all_raw.extend(special_final) # اضافه کردن ویژه ها به لیست کل

for ch in normal_channels:
    configs = get_live_configs(ch)
    print(f"{ch:<25} | {len(configs):<10} ✅")
    for conf in list(set(configs)):
        if len(conf) > 30:
            normal_all_raw.append(rename_config(conf, len(normal_all_raw)+1, is_special=False))
    time.sleep(0.1)

# ذخیره سازی
normal_final = list(dict.fromkeys(normal_all_raw))
categorized = {
    'all': normal_final,
    'vless': [c for c in normal_final if c.startswith('vless')],
    'vmess': [c for c in normal_final if c.startswith('vmess')],
    'trojan': [c for c in normal_final if c.startswith('trojan')],
    'ss': [c for c in normal_final if c.startswith('ss')]
}

for key, value in categorized.items():
    with open(f'{key}_raw.txt', 'w', encoding='utf-8') as f: f.write("\n".join(value))

with open('high_volume_raw.txt', 'w', encoding='utf-8') as f: f.write("\n".join(hv_final))

# بروزرسانی آمار
stats = {k: len(v) for k, v in categorized.items()}
stats['hv_count'] = len(hv_final)
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

with open('info.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)

print("-" * 40)
print("عملیات با موفقیت انجام شد و تمام نام‌ها به @smartconfigs تغییر یافت.")
