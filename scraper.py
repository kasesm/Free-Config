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

def rename_config(config, index, prefix="smart", is_special=False):
    suffix = "_(ویژه)" if is_special else ""
    new_name = f"@{prefix}_{index}{suffix}"
    try:
        if config.startswith('vmess://'):
            b64_part = config[8:]
            missing_padding = len(b64_part) % 4
            if missing_padding: b64_part += '=' * (4 - missing_padding)
            data = json.loads(base64.b64decode(b64_part).decode('utf-8'))
            data['ps'] = new_name
            return 'vmess://' + base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
        else:
            base = config.split('#')[0]
            return f"{base}#{new_name}"
    except: return config

def get_live_configs(channel_username):
    username = channel_username.replace('@', '').strip()
    url = f"https://t.me/s/{username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        return [conf for msg in messages for conf in extract_configs(msg.get_text())]
    except: return []

# ۱. تفکیک منابع
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
    'prrofile_purple', 'v2_mod_shop', 'anty_filter', 'YamYamProxy', 'ettehad_vpn', 'DarkTeam_VPN', 'iran_v2ray1'
]

# --- استخراج منبع پرحجم (HV) ---
hv_configs = get_live_configs(high_volume_channel)
hv_unique = list(set([c for c in hv_configs if len(c) > 30]))
hv_final = [rename_config(c, i, "HV_Breaker") for i, c in enumerate(hv_unique, 1)]

# --- استخراج سایر منابع ---
normal_all_raw = []
# منبع ویژه
for conf in list(set(get_live_configs(special_channel))):
    if len(conf) > 30: normal_all_raw.append(rename_config(conf, len(normal_all_raw)+1, "Smart", True))

# منابع عادی
for ch in normal_channels:
    for conf in list(set(get_live_configs(ch))):
        if len(conf) > 30: normal_all_raw.append(rename_config(conf, len(normal_all_raw)+1, "Smart", False))
    time.sleep(0.1)

# دسته‌بندی و ذخیره
normal_final = list(dict.fromkeys(normal_all_raw))
categorized = {
    'all': normal_final,
    'vless': [c for c in normal_final if c.startswith('vless')],
    'vmess': [c for c in normal_final if c.startswith('vmess')],
    'trojan': [c for c in normal_final if c.startswith('trojan')],
    'ss': [c for c in normal_final if c.startswith('ss')]
}

# ذخیره فایل‌های عادی
for key, value in categorized.items():
    with open(f'{key}_raw.txt', 'w', encoding='utf-8') as f: f.write("\n".join(value))

# ذخیره فایل پرحجم (این خط بسیار مهم است)
with open('high_volume_raw.txt', 'w', encoding='utf-8') as f: f.write("\n".join(hv_final))

# بروزرسانی info.json (این بخش برای نمایش عدد در سایت حیاتی است)
stats = {k: len(v) for k, v in categorized.items()}
stats['hv_count'] = len(hv_final) # اضافه کردن آمار حجیم
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

with open('info.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)

print(f"Update Successful! HV: {len(hv_final)}, Normal: {len(normal_final)}")
