import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import datetime
import time

# تابع کمکی برای استخراج کانفیگ از متن
def extract_configs(text):
    if not text: return []
    return re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>"]+', text)

# تابع تغییر نام کانفیگ‌ها
def rename_config(config, index):
    new_name = f"@smartconfigs_{index}"
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    found_in_channel = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        for msg in messages:
            text = msg.get_text()
            found_in_channel.extend(extract_configs(text))
            
            # بررسی لینک‌های داخلی برای استخراج از سابلینک‌ها یا فایل‌های متنی
            links = re.findall(r'https?://[^\s<>"]+', text)
            for link in links:
                if any(x in link for x in ['.txt', 'sub', 'githubusercontent']):
                    try:
                        res = requests.get(link, timeout=10)
                        if res.status_code == 200:
                            content = res.text
                            try:
                                decoded = base64.b64decode(content).decode('utf-8')
                                found_in_channel.extend(extract_configs(decoded))
                            except:
                                found_in_channel.extend(extract_configs(content))
                    except: continue
        return found_in_channel
    except: return []

# لیست کامل کانال‌های شما
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

all_extracted_raw = []

# بخش گزارش‌دهی در GitHub Actions
print(f"{'Channel Name':<25} | {'Count':<10}")
print("-" * 40)

for ch in channels:
    configs = get_live_configs(ch)
    count = len(configs)
    
    # نمایش وضعیت در کنسول اکشنز
    print(f"{ch:<25} | {count:<10} {'✅' if count > 0 else '❌'}")
    
    all_extracted_raw.extend(configs)
    time.sleep(0.1)

print("-" * 40)

# حذف تکراری‌ها و موارد نامعتبر
unique_configs = list(set([c for c in all_extracted_raw if len(c) > 30]))

# اعمال تغییر نام نهایی
final_configs = [rename_config(conf, i) for i, conf in enumerate(unique_configs, 1)]

# دسته‌بندی برای فایل‌ها
categorized = {
    'all': final_configs,
    'vless': [c for c in final_configs if c.startswith('vless')],
    'vmess': [c for c in final_configs if c.startswith('vmess')],
    'trojan': [c for c in final_configs if c.startswith('trojan')],
    'ss': [c for c in final_configs if c.startswith('ss')]
}

# ذخیره فایل‌ها
for key, value in categorized.items():
    content = "\n".join(value)
    with open(f'{key}_raw.txt', 'w', encoding='utf-8') as f: f.write(content)
    with open(f'{key}_sub.txt', 'w', encoding='utf-8') as f:
        f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))

# بروزرسانی آمار
stats = {k: len(v) for k, v in categorized.items()}
stats['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
with open('info.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=4)

print(f"Success! Total Unique Configs: {len(final_configs)}")
