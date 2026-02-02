import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def clean_config(config):
    # حذف هر چیزی که بعد از کاراکترهایی مثل # یا فضای خالی بیاید
    # این کار باعث حذف تگ‌های تبلیغاتی انتهای کانفیگ می‌شود
    cleaned = re.split(r'[#\s]', config)[0]
    return cleaned

def get_live_configs(channel_username):
    url = f"https://t.me/s/{channel_username.replace('@', '')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        messages = soup.find_all('div', class_='tgme_widget_message')
        configs = []

        for msg in messages:
            # بررسی زمان پیام (اختیاری - برای فیلتر کردن قدیمی‌ها)
            time_element = msg.find('time', class_='time')
            if time_element:
                post_time = time_element.get('datetime')
                # اینجا می‌توانید شرط بگذارید که اگر خیلی قدیمی بود نادیده بگیرد

            text_area = msg.find('div', class_='tgme_widget_message_text')
            if text_area:
                raw_text = text_area.get_text()
                # پیدا کردن کانفیگ‌ها
                found = re.findall(r'(vless|vmess|ss|trojan)://[^\s<>"]+', raw_text)
                for f in found:
                    cleaned = clean_config(f)
                    if len(cleaned) > 15: # جلوگیری از ذخیره لینک‌های ناقص
                        configs.append(cleaned)
        return configs
    except Exception as e:
        print(f"Error in {channel_username}: {e}")
        return []

# لیست کانال‌های هدف (می‌توانید هر تعداد که بخواهید اضافه کنید)
target_channels = ['v2rayng_org', 'v2ray_alpha', 'v2ray_free_conf']

final_list = []
for channel in target_channels:
    print(f"Processing {channel}...")
    final_list.extend(get_live_configs(channel))

# حذف موارد تکراری
final_list = list(set(final_list))

# ذخیره نهایی
with open('configs.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(final_list))

print(f"Total active configs found: {len(final_list)}")
