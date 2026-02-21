import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import datetime
import time

# تابع استخراج کانفیگ
def extract_configs(text):
    if not text: return []
    return re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"]+', text)

# تابع تغییر نام کانفیگ‌ها با قابلیت تشخیص منبع ویژه
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
            found_configs.extend(extract_configs(msg.get_text()))
        return found_configs
    except:
        return []

# ۱. تفکیک کانال‌های خاص
high_volume_channel = 'filter_breaker'
special_channel = 'isubvpn' # کانال مورد نظر شما برای تگ ویژه

# ۲. لیست سایر کانال‌ها
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

# --- استخراج منبع پرحجم (جداگانه) ---
hv_raw = get_live_configs(high_volume_channel)
hv_unique = list(set([c for c in hv_raw if len(c) > 30]))
hv_final = [rename_config(c, i, "HV_Breaker") for i, c in enumerate(hv_unique, 1)]

# --- استخراج سایر کانال‌ها ---
print(f"{'Channel Name':<25} | {'Count':<10}")
print("-" * 40)
normal_all_raw = []

# اول پردازش کانال ویژه isubvpn
special_raw = get_live_configs(special_channel)
print(f"{special_channel:<25} | {len(special_raw):<10} ⭐ (ویژه)")
for i, conf in enumerate(list(set(special_raw)), 1):
    if len(conf) > 30:
        normal_all_raw.append(rename_config(conf, i, "Smart", is_special=True))

# سپس بقیه کانال‌ها
for ch in normal_channels:
    configs = get_live_configs(ch)
    count = len(configs)
    print(f"{ch:<25} | {count:<10} {'✅' if count > 0 else '❌'}")
    for i, conf in enumerate(list(set(configs)), 1):
        if len(conf) > 30:
            normal_all_raw.append(rename_config(conf, i, "Smart", is_special=False))
    time.sleep(0.1)

# حذف تکراری‌های نهایی و ذخیره‌سازی
normal_final = list(dict.fromkeys(normal_all_raw)) # حفظ ترتیب و حذف تکراری

# دسته‌بندی و ذخیره فایل‌ها
categorized = {
    'all': normal_final,
    'vless': [c for c in normal_final if c.startswith('vless')],
    'vmess': [c for c in normal_final if c.startswith('vmess')],
    'trojan': [c for c in normal_final if c.startswith('trojan')],
    'ss': [c for c in normal_final if c.startswith('ss')]
}

for key, value in categorized.items():
    content = "\n".join(value)
    with open(f'{key}_raw.txt', 'w', encoding='utf-8') as f: f.write(content)
    with open(f'{key}_sub.txt', 'w', encoding='utf-8') as f:
        f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))

# ذخیره HV
hv_content = "\n".join(hv_final)
with open('high_volume_raw.txt', 'w', encoding='utf-8') as f: f.write(hv_content)

# به‌روزرسانی آمار
stats = {k: len(v) for k, v in categorized.items()}
stats['hv_count'] = len(hv_final)
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)
