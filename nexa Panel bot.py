import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import time
import threading
import os
import uuid
import html
import re

# --- Telegram Latest Feature Check (CopyTextButton) ---
try:
    from telebot.types import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# --- কনফিগারেশন (Configuration) ---
TOKEN = "8111731612:AAHY9MNVLN_VHrO0sQLw1wxxgMAZrAp5p-s"
ADMIN_ID = YOUR_TELEGRAM_ID
BASE_URL = "http://185.190.142.81"
NEXA_API_KEY = "nxa_908f09625e23ca12bee17e46b4bf07208dd03122"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "dxa_bot_premium_data_v2.json"

active_polls = {}
user_states = {}
data_lock = threading.Lock()

# --- Auto Country ISO Codes ---
COUNTRY_CODES = {
    "bangladesh": "BD", "india": "IN", "pakistan": "PK", "cameroon": "CM",
    "vietnam": "VN", "indonesia": "ID", "united states": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB", "russia": "RU", "brazil": "BR",
    "nigeria": "NG", "philippines": "PH", "egypt": "EG", "turkey": "TR",
    "thailand": "TH", "myanmar": "MM", "south africa": "ZA", "colombia": "CO",
    "kenya": "KE", "argentina": "AR", "algeria": "DZ", "sudan": "SD",
    "ukraine": "UA", "iraq": "IQ", "morocco": "MA", "peru": "PE",
    "malaysia": "MY", "uzbekistan": "UZ", "saudi arabia": "SA", "yemen": "YE",
    "ghana": "GH", "mozambique": "MZ", "nepal": "NP", "madagascar": "MG",
    "venezuela": "VE", "cote d'ivoire": "CI", "ivory coast": "CI",
    "australia": "AU", "taiwan": "TW", "sri lanka": "LK", "burkina faso": "BF",
    "mali": "ML", "romania": "RO", "chile": "CL", "kazakhstan": "KZ",
    "zambia": "ZM", "guatemala": "GT", "ecuador": "EC", "syria": "SY",
    "senegal": "SN", "cambodia": "KH", "chad": "TD", "somalia": "SO",
    "zimbabwe": "ZW", "guinea": "GN", "rwanda": "RW", "benin": "BJ",
    "tunisia": "TN", "bolivia": "BO", "belgium": "BE", "haiti": "HT",
    "cuba": "CU", "south sudan": "SS", "dominican republic": "DO",
    "czechia": "CZ", "greece": "GR", "jordan": "JO", "portugal": "PT",
    "azerbaijan": "AZ", "sweden": "SE", "honduras": "HN", "uae": "AE",
    "united arab emirates": "AE", "tajikistan": "TJ", "serbia": "RS",
    "switzerland": "CH", "togo": "TG", "sierra leone": "SL", "laos": "LA",
    "paraguay": "PY", "bulgaria": "BG", "libya": "LY", "lebanon": "LB",
    "nicaragua": "NI", "kyrgyzstan": "KG", "el salvador": "SV",
    "singapore": "SG", "denmark": "DK", "finland": "FI", "slovakia": "SK",
    "norway": "NO", "ireland": "IE", "croatia": "HR", "moldova": "MD",
    "georgia": "GE", "armenia": "AM", "lithuania": "LT", "albania": "AL",
    "jamaica": "JM", "mongolia": "MN", "cyprus": "CY", "universal": "UN",
    "poland": "PL", "germany": "DE", "japan": "JP", "belarus": "BY",
    "spain": "ES", "italy": "IT", "france": "FR", "canada": "CA", "mexico": "MX"
}

# --- Service Short Forms ---
SERVICE_SHORTS = {
    "facebook": "FB", "whatsapp": "WA", "whatsapp businesses": "WB",
    "telegram": "TG", "instagram": "IG", "twitter": "TW", "x": "X",
    "google": "GO", "gmail": "GM", "youtube": "YT", "apple": "AP",
    "microsoft": "MS", "tiktok": "TT", "snapchat": "SC", "binance": "BN",
    "melbet": "MB", "bkash": "BK", "rocket": "RK", "nagad": "NG",
    "imo": "IMO", "messenger": "MS", "custom search": "CS"
}

# --- All Premium App & Core Emojis ---
APP_EMOJIS = {
    # Services
    "facebook": {"emoji": "🚫", "id": "5334807341109908955"},
    "whatsapp": {"emoji": "🚫", "id": "5334759662677957452"},
    "telegram": {"emoji": "🚫", "id": "5337010556253543833"},
    "imo": {"emoji": "🚫", "id": "5337155807752524558"},
    "instagram": {"emoji": "🚫", "id": "5334868205091459431"},
    "apple": {"emoji": "🚫", "id": "5334637951894722661"},
    "youtube": {"emoji": "🚫", "id": "5334769042886533147"},
    "google": {"emoji": "🚫", "id": "5335010201005231986"},
    "microsoft": {"emoji": "🖥", "id": "5334880948259427772"},
    "melbet": {"emoji": "🌟", "id": "5337102391244263212"},
    "tiktok": {"emoji": "🚫", "id": "5339213256001102461"},
    "bkash": {"emoji": "💸", "id": "5348469219761626211"},
    "rocket": {"emoji": "💸", "id": "5346042941196507141"},
    "binance": {"emoji": "💸", "id": "5348212415077064131"},
    "gmail": {"emoji": "🐁", "id": "5348494358205207761"},
    "messenger": {"emoji": "🧻", "id": "5348486915026884464"},
    
    # UI Icons & Core
    "dxa": {"emoji": "😒", "id": "5334763399299506604"},
    "done": {"emoji": "✅", "id": "5352694861990501856"},
    "cross": {"emoji": "❌", "id": "5420130255174145507"},
    "warning": {"emoji": "⚠️", "id": "5336944168944047463"},
    "time": {"emoji": "🕓", "id": "5336983442125001376"},
    "waiting": {"emoji": "⌛", "id": "5337172996211648018"},
    "message": {"emoji": "💬", "id": "5337302974806922068"},
    "otp": {"emoji": "🔐", "id": "5337255927735163754"},
    "number": {"emoji": "🍏", "id": "5337132498965010628"},
    "world": {"emoji": "🌐", "id": "5336972142066047577"},
    "user": {"emoji": "👤", "id": "5352861489541714456"},
    "admin": {"emoji": "📊", "id": "5353032893096567467"},
    "file": {"emoji": "📁", "id": "5352721946054268944"},
    "1": {"emoji": "1️⃣", "id": "5352651766288652742"},
    "link": {"emoji": "🔗", "id": "5420517437885943844"},
    "fire": {"emoji": "🔥", "id": "5337267511261960341"},
    "phone": {"emoji": "📱", "id": "5355208818017999139"},
    "gear": {"emoji": "⚙️", "id": "5420155432272438703"},
    "plus": {"emoji": "➕", "id": "5420323438508155202"},
    "hi": {"emoji": "👋", "id": "5353027129250453493"},
    "pin": {"emoji": "📍", "id": "5352922460897452503"},
    "diamond": {"emoji": "💎", "id": "5352838545826420397"},
    "note": {"emoji": "✏️", "id": "5395444784611480792"},
    "service_icon": {"emoji": "🖥", "id": "5336879280578138635"},
    "inbox": {"emoji": "📩", "id": "5352597830089347330"},
    "live": {"emoji": "🎙", "id": "5355102594886833928"},
    "megaphone": {"emoji": "📣", "id": "5352980533150259581"},
    "rocket": {"emoji": "🚀", "id": "5352597830089347330"}
}

# --- ডাটাবেস ফাংশন ---
def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "users": [], 
            "services_data": {}, 
            "forward_groups": [], 
            "main_otp_link": "https://t.me/",
            "flags": {}, 
            "watermark": "DXA UNIVERSE",
            "force_join_enabled": False, 
            "force_join_channel": "" 
        }
        save_data(default_data)
        return default_data
    try:
        with open(DATA_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
            if "force_join_enabled" not in data:
                data["force_join_enabled"] = False
                data["force_join_channel"] = ""
            return data
    except:
        return {"users": [], "services_data": {}, "forward_groups": [], "main_otp_link": "https://t.me/", "flags": {}, "watermark": "DXA UNIVERSE", "force_join_enabled": False, "force_join_channel": ""}

def save_data(data):
    with data_lock:
        with open(DATA_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

def add_user(user_id):
    data = load_data()
    if user_id not in data.get("users", []):
        data.setdefault("users", []).append(user_id)
        save_data(data)

def get_total_ranges():
    data = load_data()
    count = 0
    for srv in data.get("services_data", {}).values():
        for cnt in srv.get("countries", {}).values():
            count += len(cnt.get("ranges", {}))
    return count

# --- Helpers ---
def emo(keyword, default_emo=""):
    keyword = str(keyword).lower().strip()
    data = load_data()
    flags = data.get("flags", {})
    if keyword in flags:
        return f"<tg-emoji emoji-id='{flags[keyword]['id']}'>{flags[keyword]['emoji']}</tg-emoji>"
    for key, val in APP_EMOJIS.items():
        if key in keyword:
            return f"<tg-emoji emoji-id='{val['id']}'>{val['emoji']}</tg-emoji>"
    if "custom" in keyword or "unknown" in keyword:
        return f"<tg-emoji emoji-id='{APP_EMOJIS['world']['id']}'>{APP_EMOJIS['world']['emoji']}</tg-emoji>"
    return default_emo

def get_iso_code(country_name):
    name = str(country_name).lower().strip()
    return COUNTRY_CODES.get(name, name[:2].upper() if len(name) >= 2 else "UN")

def get_short_service(service_name):
    name = str(service_name).lower().strip()
    return SERVICE_SHORTS.get(name, name[:2].upper() if len(name) >= 2 else "SV")

def format_url(url):
    url = url.strip()
    if url and not url.startswith(('http://', 'https://', 'tg://')): return 'https://' + url
    return url

# Extract Username from link to check membership
def extract_channel_username(url):
    if "t.me/" in url:
        parts = url.split("t.me/")
        if len(parts) > 1:
            username = parts[1].split("/")[0].split("?")[0]
            if not username.startswith("@"):
                username = "@" + username
            return username
    return ""

def mask_number(phone):
    phone_str = str(phone).replace('+', '')
    if len(phone_str) > 7: return f"{phone_str[:3]}DXA{phone_str[-4:]}"
    return phone_str

def clean_input(message):
    if message.chat.type == 'private':
        try: bot.delete_message(message.chat.id, message.message_id)
        except: pass

def safe_send(chat_id, text, reply_markup=None, message_id=None):
    try:
        if message_id:
            msg = bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=reply_markup)
            return msg
        else:
            msg = bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=reply_markup)
            return msg
    except Exception as e:
        error_msg = str(e).lower()
        if "custom emoji" in error_msg or "entities" in error_msg or "can't parse" in error_msg:
            clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
            try:
                if message_id: return bot.edit_message_text(clean_text, chat_id, message_id, parse_mode="HTML", reply_markup=reply_markup)
                else: return bot.send_message(chat_id, clean_text, parse_mode="HTML", reply_markup=reply_markup)
            except: pass

# --- Smart Force Join Checker (Link Only) ---
def check_force_join(user_id):
    if user_id == ADMIN_ID: return True 
    data = load_data()
    if not data.get("force_join_enabled"): return True
    channel_link = data.get("force_join_channel", "")
    if not channel_link: return True 
    
    chat_username = extract_channel_username(channel_link)
    if not chat_username: return True 
    
    try:
        member = bot.get_chat_member(chat_username, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Force Join Check Error: {e}")
        return True 

def show_force_join_message(chat_id, message_id=None):
    data = load_data()
    channel_link = data.get("force_join_channel", "https://t.me/")
    
    text = (
        f"{emo('warning')} <b>Access Denied!</b> {emo('warning')}\n"
        f"━━━━━━━━━━━\n"
        f"You must join our official channel to use this bot.\n\n"
        f"{emo('megaphone')} Please join via the button below and then click <b>'Joined'</b>."
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="📢 Join Channel", url=channel_link))
    markup.add(InlineKeyboardButton(text="✅ Joined", callback_data="check_join"))
    
    safe_send(chat_id, text, markup, message_id)

# --- কীবোর্ড মেনু ---
def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(f"📱 Get Number"))
    if user_id == ADMIN_ID:
        markup.add(KeyboardButton(f"⚙️ Admin Panel"))
    return markup

def get_admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛠️ Manage Services & Ranges", callback_data="admin_manage_service"),
        InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"),
        InlineKeyboardButton("⚙️ Group Forward Settings", callback_data="admin_group_settings"),
        InlineKeyboardButton("📣 Force Join Settings", callback_data="admin_force_join"),
        InlineKeyboardButton("🎌 Manage Premium Flags", callback_data="admin_manage_flags"),
        InlineKeyboardButton("🏷️ Set Watermark", callback_data="admin_set_watermark")
    )
    return markup

def get_force_join_menu():
    data = load_data()
    is_enabled = data.get("force_join_enabled", False)
    channel_link = data.get("force_join_channel", "")
    
    status_text = "🟢 Enabled" if is_enabled else "🔴 Disabled"
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(f"Toggle Status: {status_text}", callback_data="toggle_force_join"))
    
    if channel_link:
        markup.add(InlineKeyboardButton(f"❌ Remove: {channel_link}", callback_data="delete_force_join"))
    else:
        markup.add(InlineKeyboardButton("➕ Add Channel Link", callback_data="set_force_join_channel"))
        
    markup.add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    return markup

def get_flags_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📤 Upload Flag File (.txt)", callback_data="upload_flags"),
        InlineKeyboardButton("🗑️ Delete All Flags", callback_data="delete_all_flags"),
        InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin")
    )
    return markup

def get_group_settings_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔗 Set UI 'OTP Group' Link", callback_data="set_main_otp_link"),
        InlineKeyboardButton("➕ Add Forward Group", callback_data="add_fwd_group"),
        InlineKeyboardButton("🗑️ Remove Forward Group", callback_data="del_fwd_group"),
        InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin")
    )
    return markup

# --- কমান্ড হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)
    
    clean_input(message)
    try:
        m = bot.send_message(message.chat.id, "🔄 Refreshing...", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.delete_message(message.chat.id, m.message_id)
    except: pass
    
    if not check_force_join(user_id):
        show_force_join_message(message.chat.id)
        return
        
    show_main_menu(message.chat.id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)

    if "Get Number" in text:
        clean_input(message)
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_user_services(message.chat.id)
    elif "Admin Panel" in text:
        clean_input(message)
        if user_id == ADMIN_ID:
            show_admin_panel(message.chat.id)
        else:
            bot.send_message(message.chat.id, f"{emo('warning')} <b>Access Denied:</b> You are not authorized.", parse_mode="HTML")
    else:
        clean_input(message)

# --- 1. USER UI ---
def show_main_menu(chat_id, message_id=None):
    data = load_data()
    watermark = data.get("watermark", "DXA UNIVERSE")
    
    text = (
        f"{emo('fire')} <b>NUMBER BOT</b> {emo('fire')}\n"
        f"━━━━━━━━━━━\n"
        f"{emo('hi')} Hello! Welcome To {html.escape(watermark)}.\n\n"
        f"{emo('pin')} Tap Get Number to start!\n"
        f"━━━━━━━━━━━\n"
        f"{emo('dxa')} POWERED BY {html.escape(watermark)}"
    )
    safe_send(chat_id, text, get_main_menu(chat_id), message_id)

def show_user_services(chat_id, message_id=None):
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for srv_id, srv in data.get("services_data", {}).items():
        has_ranges = any(len(cnt.get("ranges", {})) > 0 for cnt in srv.get("countries", {}).values())
        if has_ranges:
            buttons.append(InlineKeyboardButton(text=f"📌 {srv['name']}", callback_data=f"usr_s|{srv_id}"))
            
    if buttons: markup.add(*buttons)
    markup.add(InlineKeyboardButton(text="🔍 Find Number (Custom)", callback_data="find_number"))
    
    text = (
        f"{emo('number')} <b>AVAILABLE SERVICES</b> {emo('number')}\n"
        f"━━━━━━━━━━━━━━\n"
        f"{emo('diamond')} <i>Select a service or find custom number :</i>"
    )
    safe_send(chat_id, text, markup, message_id)

def show_user_countries(chat_id, srv_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    if not srv_data: return
    
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for cnt_id, cnt in srv_data.get("countries", {}).items():
        if len(cnt.get("ranges", {})) > 0:
            buttons.append(InlineKeyboardButton(text=f"🌍 {cnt['name']}", callback_data=f"usr_c|{srv_id}|{cnt_id}"))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
    
    text = (
        f"{emo('world')} <b>SELECT COUNTRY</b> {emo('world')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('service_icon')} <b>Service:</b> <code>{html.escape(srv_data['name'])}</code>\n\n"
        f"{emo('diamond')} <i>Select a country from below:</i>"
    )
    safe_send(chat_id, text, markup, message_id)

def show_user_ranges(chat_id, srv_id, cnt_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    cnt_data = srv_data.get("countries", {}).get(cnt_id) if srv_data else None
    if not cnt_data: return
    
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=f"🔢 {rng_val}", callback_data=f"usr_r|{srv_id}|{cnt_id}|{rng_id}") for rng_id, rng_val in cnt_data.get("ranges", {}).items()]
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🔙 Back to Countries", callback_data=f"usr_s|{srv_id}"))
    
    text = (
        f"{emo('number')} <b>SELECT NUMBER RANGE</b> {emo('number')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('service_icon')} <b>Service:</b> <code>{html.escape(srv_data['name'])}</code>\n"
        f"{emo('world')} <b>Country:</b> <code>{html.escape(cnt_data['name'])}</code>\n\n"
        f"{emo('diamond')} <i>Select your preferred number range:</i>"
    )
    safe_send(chat_id, text, markup, message_id)

# --- 2. ADMIN UI ---
def show_admin_panel(chat_id, message_id=None):
    data = load_data()
    text = (
        f"{emo('admin')} <b>ADMIN CONTROL PANEL</b> {emo('admin')}\n"
        f"━━━━━━━━━━━━\n\n"
        f"{emo('admin')} <b>DATABASE OVERVIEW</b>\n"
        f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
        f"{emo('user')} <b>Users:</b> »  <code>{len(data.get('users', []))}</code>\n"
        f"{emo('number')} <b>Ranges:</b> »  <code>{get_total_ranges()}</code>\n"
        f"{emo('message')} <b>Fwd Groups:</b> »  <code>{len(data.get('forward_groups', []))}</code>\n"
        f"{emo('file')} <b>Saved Flags:</b> »  <code>{len(data.get('flags', {}))}</code>\n\n"
        f"━━━━━━━━━━━━"
    )
    safe_send(chat_id, text, get_admin_menu(), message_id)

def show_admin_services(chat_id, message_id=None):
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=2)
    for srv_id, srv in data.get("services_data", {}).items():
        markup.add(InlineKeyboardButton(text=f"📁 {srv['name']}", callback_data=f"adm_s|{srv_id}"))
    markup.add(InlineKeyboardButton("➕ Add New Service", callback_data="add_srv"))
    markup.add(InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin"))
    safe_send(chat_id, f"{emo('gear')} <b>Manage Services</b>\nSelect a service to view countries:", markup, message_id)

def show_admin_countries(chat_id, srv_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    if not srv_data: return
    markup = InlineKeyboardMarkup(row_width=2)
    for cnt_id, cnt in srv_data.get("countries", {}).items():
        markup.add(InlineKeyboardButton(text=f"🌍 {cnt['name']}", callback_data=f"adm_c|{srv_id}|{cnt_id}"))
    markup.add(InlineKeyboardButton("➕ Add Country", callback_data=f"add_cnt|{srv_id}"))
    markup.add(InlineKeyboardButton(f"🗑️ Delete Service ({srv_data['name']})", callback_data=f"del_srv|{srv_id}"))
    markup.add(InlineKeyboardButton("🔙 Back to Services", callback_data="admin_manage_service"))
    safe_send(chat_id, f"{emo('world')} <b>Manage Countries for {html.escape(srv_data['name'])}</b>\nSelect a country to view ranges:", markup, message_id)

def show_admin_ranges(chat_id, srv_id, cnt_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    cnt_data = srv_data.get("countries", {}).get(cnt_id) if srv_data else None
    if not cnt_data: return
    markup = InlineKeyboardMarkup(row_width=1)
    for rng_id, rng_val in cnt_data.get("ranges", {}).items():
        markup.add(InlineKeyboardButton(text=f"❌ Delete Range: {rng_val}", callback_data=f"del_rng|{srv_id}|{cnt_id}|{rng_id}"))
    markup.add(InlineKeyboardButton("➕ Add New Range", callback_data=f"add_rng|{srv_id}|{cnt_id}"))
    markup.add(InlineKeyboardButton(f"🗑️ Delete Country ({cnt_data['name']})", callback_data=f"del_cnt|{srv_id}|{cnt_id}"))
    markup.add(InlineKeyboardButton("🔙 Back to Countries", callback_data=f"adm_s|{srv_id}"))
    safe_send(chat_id, f"{emo('number')} <b>Manage Ranges for {html.escape(srv_data['name'])} -> {html.escape(cnt_data['name'])}</b>\nTap a range to delete it:", markup, message_id)

# --- Callback Handler ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    
    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = load_data()
    api_key = NEXA_API_KEY
    
    # Check Force Join for User Actions
    if call.data in ["main_get_number", "back_to_user_services", "find_number"] or call.data.startswith("usr_s|") or call.data.startswith("usr_c|") or call.data.startswith("chgc|") or call.data.startswith("chg_r|"):
        if not check_force_join(user_id):
            show_force_join_message(chat_id, msg_id)
            return
            
    if call.data == "check_join":
        if check_force_join(user_id):
            bot.answer_callback_query(call.id, "✅ Thank you for joining!", show_alert=True)
            show_main_menu(chat_id, msg_id)
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined the channel yet. Please join first.", show_alert=True)
        return
    
    if call.data.startswith("adm_") or call.data.startswith("add_") or call.data.startswith("del_") or call.data in ["admin_broadcast", "admin_group_settings", "admin_manage_flags", "admin_set_watermark", "upload_flags", "admin_force_join", "toggle_force_join", "set_force_join_channel", "delete_force_join"]:
        if user_id != ADMIN_ID: return safe_send(chat_id, f"{emo('warning')} <b>You are not authorized.</b>", None, msg_id)

    # --- ROUTING ---
    if call.data == "back_to_main":
        show_main_menu(chat_id, msg_id)
    elif call.data == "main_get_number":
        show_user_services(chat_id, msg_id)
    elif call.data == "main_admin_panel":
        show_admin_panel(chat_id, msg_id)
    elif call.data == "back_to_admin":
        show_admin_panel(chat_id, msg_id)
    elif call.data == "back_to_user_services":
        if str(chat_id) in active_polls: active_polls[str(chat_id)] = False 
        show_user_services(chat_id, msg_id)
    elif call.data.startswith("usr_s|"):
        show_user_countries(chat_id, call.data.split("|")[1], msg_id)
    elif call.data.startswith("usr_c|"):
        _, srv_id, cnt_id = call.data.split("|")
        show_user_ranges(chat_id, srv_id, cnt_id, msg_id)
        
    elif call.data == "find_number":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="back_to_user_services"))
        safe_send(chat_id, f"{emo('note')} <b>Enter Number Range:</b>\n<i>Example: 99298XXX or 8801</i>\n\n(Send /cancel to stop)", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_custom_range, msg_id)

    # Core Fetching
    elif call.data.startswith("chgc|") or call.data.startswith("usr_r|") or call.data.startswith("chg_r|"):
        is_custom = call.data.startswith("chgc|")
        if is_custom:
            custom_range = call.data.split("|")[1]
            service_info = {'id': f"custom_{custom_range}", 'service_name': 'Custom Search', 'country_name': 'Universal', 'range': custom_range, 'srv_id': None, 'cnt_id': None}
        else:
            _, srv_id, cnt_id, rng_id = call.data.split("|")
            srv_data = data.get("services_data", {}).get(srv_id)
            cnt_data = srv_data.get("countries", {}).get(cnt_id) if srv_data else None
            rng_val = cnt_data.get("ranges", {}).get(rng_id) if cnt_data else None
            if not rng_val: return
            service_info = {'id': rng_id, 'srv_id': srv_id, 'cnt_id': cnt_id, 'service_name': srv_data['name'], 'country_name': cnt_data['name'], 'range': rng_val}

        if str(chat_id) in active_polls: active_polls[str(chat_id)] = False 
        
        msg_obj = safe_send(chat_id, f"{emo('waiting')} <b>Extracting number for</b> <code>{html.escape(service_info['service_name'])}</code>...", None, msg_id)
        if msg_obj: fetch_number(chat_id, service_info, api_key, msg_obj.message_id, is_custom)

    elif call.data.startswith("cp_"):
        bot.answer_callback_query(call.id, f"OTP: {call.data.split('_')[1]}\n(Update app for direct copy)", show_alert=True)

    # Admin Routing (Smart Force Join)
    elif call.data == "admin_force_join":
        safe_send(chat_id, f"{emo('megaphone')} <b>Force Join Settings</b>\nManage channel requirements here.", get_force_join_menu(), msg_id)
    elif call.data == "toggle_force_join":
        data["force_join_enabled"] = not data.get("force_join_enabled", False)
        save_data(data)
        safe_send(chat_id, f"{emo('megaphone')} <b>Force Join Settings</b>\nManage channel requirements here.", get_force_join_menu(), msg_id)
    elif call.data == "set_force_join_channel":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_force_join"))
        safe_send(chat_id, f"{emo('rocket')} <b>Send Channel Link:</b>\n(Example: https://t.me/yourchannel)\n\n<i>Note: Make sure to add the bot as an admin in this channel!</i>", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_set_force_join_link, msg_id)
    elif call.data == "delete_force_join":
        data["force_join_channel"] = ""
        save_data(data)
        safe_send(chat_id, f"{emo('megaphone')} <b>Force Join Settings</b>\nManage channel requirements here.", get_force_join_menu(), msg_id)

    elif call.data == "admin_manage_flags":
        safe_send(chat_id, f"{emo('file')} <b>Manage Premium Flags</b>\nUpload your <code>All Flag.txt</code> to update country emojis.", get_flags_menu(), msg_id)
    elif call.data == "upload_flags":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_manage_flags"))
        safe_send(chat_id, f"{emo('file')} Please send the <b>All Flag.txt</b> file:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_flag_file, msg_id)
    elif call.data == "delete_all_flags":
        data["flags"] = {}
        save_data(data)
        show_admin_panel(chat_id, msg_id)
    elif call.data == "admin_manage_service":
        show_admin_services(chat_id, msg_id)
    elif call.data == "add_srv":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_manage_service"))
        safe_send(chat_id, f"{emo('message')} <b>Send New Service Name</b> (e.g. WhatsApp):", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_add_srv, msg_id)
    elif call.data.startswith("adm_s|"):
        show_admin_countries(chat_id, call.data.split("|")[1], msg_id)
    elif call.data.startswith("add_cnt|"):
        srv_id = call.data.split("|")[1]
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data=f"adm_s|{srv_id}"))
        safe_send(chat_id, f"{emo('world')} <b>Send Country Name:</b>", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_add_cnt, srv_id, msg_id)
    elif call.data.startswith("adm_c|"):
        _, srv_id, cnt_id = call.data.split("|")
        show_admin_ranges(chat_id, srv_id, cnt_id, msg_id)
    elif call.data.startswith("add_rng|"):
        _, srv_id, cnt_id = call.data.split("|")
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data=f"adm_c|{srv_id}|{cnt_id}"))
        safe_send(chat_id, f"{emo('number')} <b>Send Range</b> (e.g. 8801):", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_add_rng, srv_id, cnt_id, msg_id)
    elif call.data.startswith("del_srv|"):
        srv_id = call.data.split("|")[1]
        if srv_id in data.get("services_data", {}):
            del data["services_data"][srv_id]
            save_data(data)
        show_admin_services(chat_id, msg_id)
    elif call.data.startswith("del_cnt|"):
        _, srv_id, cnt_id = call.data.split("|")
        if srv_id in data["services_data"] and cnt_id in data["services_data"][srv_id]["countries"]:
            del data["services_data"][srv_id]["countries"][cnt_id]
            save_data(data)
        show_admin_countries(chat_id, srv_id, msg_id)
    elif call.data.startswith("del_rng|"):
        _, srv_id, cnt_id, rng_id = call.data.split("|")
        if srv_id in data["services_data"] and cnt_id in data["services_data"][srv_id]["countries"] and rng_id in data["services_data"][srv_id]["countries"][cnt_id]["ranges"]:
            del data["services_data"][srv_id]["countries"][cnt_id]["ranges"][rng_id]
            save_data(data)
        show_admin_ranges(chat_id, srv_id, cnt_id, msg_id)
    elif call.data == "admin_group_settings":
        safe_send(chat_id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)
    elif call.data == "set_main_otp_link":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_group_settings"))
        safe_send(chat_id, "🔗 Send the URL for UI 'OTP Group' button:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_main_otp_link, msg_id)
    elif call.data == "add_fwd_group":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_group_settings"))
        safe_send(chat_id, f"{emo('plus')} Send the <b>Group Chat ID</b> (e.g., -100123):", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, step1_fwd_group_id, msg_id)
    elif call.data == "del_fwd_group":
        groups = data.get("forward_groups", [])
        if not groups: return
        markup = InlineKeyboardMarkup(row_width=1)
        for g in groups: markup.add(InlineKeyboardButton(f"❌ {g['chat_id']}", callback_data=f"delfwd_{g['chat_id']}"))
        markup.add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_group_settings"))
        safe_send(chat_id, "Select a group to remove:", markup, msg_id)
    elif call.data.startswith("delfwd_"):
        data["forward_groups"] = [g for g in data.get("forward_groups", []) if str(g['chat_id']) != call.data.split("_")[1]]
        save_data(data)
        show_admin_panel(chat_id, msg_id)
    elif call.data == "admin_set_watermark":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="back_to_admin"))
        safe_send(chat_id, f"✍️ <b>Send new Watermark text:</b>\n(Current: {data.get('watermark', 'DXA UNIVERSE')})", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_set_watermark, msg_id)
    elif call.data == "admin_broadcast":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="back_to_admin"))
        safe_send(chat_id, f"{emo('message')} <b>Send any message (Text, Photo, Sticker) to broadcast:</b>", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_broadcast, msg_id)

# --- Input Handlers ---
def process_set_force_join_link(message, msg_id):
    clean_input(message)
    if message.text == '/cancel':
        safe_send(message.chat.id, f"{emo('megaphone')} <b>Force Join Settings</b>", get_force_join_menu(), msg_id)
        return
    data = load_data()
    data["force_join_channel"] = format_url(message.text.strip())
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} Force Join Channel Linked Successfully!", None, msg_id)
    time.sleep(1)
    safe_send(message.chat.id, f"{emo('megaphone')} <b>Force Join Settings</b>\nManage channel requirements here.", get_force_join_menu(), msg_id)


def process_add_srv(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_services(message.chat.id, msg_id)
    data = load_data()
    srv_id = "s_" + str(uuid.uuid4())[:8]
    data.setdefault("services_data", {})[srv_id] = {"name": message.text.strip(), "countries": {}}
    save_data(data)
    show_admin_services(message.chat.id, msg_id)

def process_add_cnt(message, srv_id, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_countries(message.chat.id, srv_id, msg_id)
    data = load_data()
    cnt_id = "c_" + str(uuid.uuid4())[:8]
    if srv_id in data.get("services_data", {}):
        data["services_data"][srv_id]["countries"][cnt_id] = {"name": message.text.strip(), "ranges": {}}
        save_data(data)
    show_admin_countries(message.chat.id, srv_id, msg_id)

def process_add_rng(message, srv_id, cnt_id, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_ranges(message.chat.id, srv_id, cnt_id, msg_id)
    data = load_data()
    rng_id = "r_" + str(uuid.uuid4())[:8]
    try:
        data["services_data"][srv_id]["countries"][cnt_id]["ranges"][rng_id] = message.text.strip()
        save_data(data)
    except: pass
    show_admin_ranges(message.chat.id, srv_id, cnt_id, msg_id)

def process_flag_file(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    if not message.document: return safe_send(message.chat.id, f"{emo('cross')} Please upload a .txt document.", None, msg_id)
    try:
        file_info = bot.get_file(message.document.file_id)
        content = bot.download_file(file_info.file_path).decode('utf-8')
        data = load_data()
        for line in content.split('\n'):
            if not line or '{' not in line: continue
            parts = line.split('{', 1)
            words = parts[0].strip().split(' ')
            clean_name = (' '.join(words[1:]) if len(words) > 1 else words[0]).lower().strip()
            try: data.setdefault("flags", {})[clean_name] = json.loads('{' + parts[1])
            except: pass
        save_data(data)
        show_admin_panel(message.chat.id, msg_id)
    except Exception as e: safe_send(message.chat.id, f"{emo('cross')} <b>Error:</b> {str(e)}", None, msg_id)

def process_custom_range(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_user_services(message.chat.id, msg_id)
    custom_range = message.text.strip()
    service_info = {'id': f"custom_{custom_range}", 'service_name': 'Custom Search', 'country_name': 'Universal', 'range': custom_range, 'srv_id': None, 'cnt_id': None}
    if str(message.chat.id) in active_polls: active_polls[str(message.chat.id)] = False
    
    safe_send(message.chat.id, f"{emo('waiting')} <b>Searching custom range</b> <code>{html.escape(custom_range)}</code>...", None, msg_id)
    fetch_number(message.chat.id, service_info, NEXA_API_KEY, msg_id, is_custom=True)

def step1_fwd_group_id(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    user_states[message.chat.id] = {'chat_id': message.text.strip()}
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_group_settings"))
    safe_send(message.chat.id, f"{emo('message')} Send the <b>Button Name</b>:\n(Type <code>/skip</code> to add without button)", markup, msg_id)
    bot.register_next_step_handler_by_chat_id(message.chat.id, step2_fwd_group_btn_name, msg_id)

def step2_fwd_group_btn_name(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    if message.text.strip() == '/skip':
        state = user_states.get(message.chat.id, {})
        data = load_data()
        data.setdefault("forward_groups", []).append({"chat_id": state.get('chat_id'), "btn_name": "", "btn_url": ""})
        save_data(data)
        safe_send(message.chat.id, f"{emo('done')} <b>Forward Group configured without button!</b>", None, msg_id)
        time.sleep(1)
        show_admin_panel(message.chat.id, msg_id)
        return
    user_states[message.chat.id]['btn_name'] = message.text.strip()
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel & Go Back", callback_data="admin_group_settings"))
    safe_send(message.chat.id, f"{emo('link')} Send the <b>Button URL</b>:", markup, msg_id)
    bot.register_next_step_handler_by_chat_id(message.chat.id, step3_fwd_group_url, msg_id)

def step3_fwd_group_url(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    state = user_states.get(message.chat.id, {})
    data = load_data()
    data.setdefault("forward_groups", []).append({"chat_id": state.get('chat_id'), "btn_name": state.get('btn_name'), "btn_url": format_url(message.text.strip())})
    save_data(data)
    show_admin_panel(message.chat.id, msg_id)

def process_main_otp_link(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    data = load_data()
    data["main_otp_link"] = format_url(message.text.strip())
    save_data(data)
    show_admin_panel(message.chat.id, msg_id)

def process_set_watermark(message, msg_id):
    clean_input(message)
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    data = load_data()
    data["watermark"] = message.text.strip()
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} Watermark Successfully Updated!", None, msg_id)
    time.sleep(1)
    show_admin_panel(message.chat.id, msg_id)

def run_broadcast(chat_id, original_message, msg_id):
    data = load_data()
    users = data.get("users", [])
    success = 0
    failed = 0
    
    for u in users:
        try:
            bot.copy_message(chat_id=u, from_chat_id=chat_id, message_id=original_message.message_id)
            success += 1
            time.sleep(0.05)
        except:
            failed += 1
            
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    report_msg = (
        f"📢 <b>Broadcast Completed!</b>\n\n"
        f"✅ <b>Delivered:</b> {success} users\n"
        f"❌ <b>Failed:</b> {failed} users"
    )
    safe_send(chat_id, report_msg, markup, msg_id)

def process_broadcast(message, msg_id):
    if message.text == '/cancel': 
        clean_input(message)
        return show_admin_panel(message.chat.id, msg_id)
        
    data = load_data()
    safe_send(message.chat.id, f"{emo('waiting')} Broadcasting...", None, msg_id)
    threading.Thread(target=run_broadcast, args=(message.chat.id, message, msg_id)).start()
    clean_input(message)

# --- Core API Logic ---
def fetch_number(chat_id, service_info, api_key, msg_id, is_custom=False):
    headers = {'X-API-Key': api_key}
    payload = {"range": service_info['range'], "format": "normal"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/numbers/get", json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if res_data.get("success"):
            number = res_data.get("number")
            number_id = res_data.get("number_id")
            data = load_data()
            watermark = data.get("watermark", "DXA UNIVERSE")
            
            text = (
                f"━━━━━━━━━━━\n"
                f"《 {emo('done')} <b>NUMBERS ALLOCATED</b> 》\n"
                f"━━━━━━━━━━━\n"
                f"<blockquote>[Service {emo(service_info['service_name'])} {html.escape(service_info['service_name'])}]\n"
                f"[Country {emo(service_info['country_name'])} {html.escape(service_info['country_name'])}]</blockquote>\n"
                f"━━━━━━━━━━━\n"
                f"{emo('1')} <code>{number}</code>\n"
                f"━━━━━━━━━━━\n"
                f"{emo('fire')} <b>POWERED BY {html.escape(watermark)}</b> {emo('fire')}\n"
                f"━━━━━━━━━━━"
            )
            
            main_link = format_url(data.get("main_otp_link", "https://t.me/"))
            markup = InlineKeyboardMarkup(row_width=2)
            
            if is_custom:
                markup.add(InlineKeyboardButton("🔄 Change Number", callback_data=f"chgc|{service_info['range']}"), InlineKeyboardButton("📨 OTP Group", url=main_link))
                markup.add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
            else:
                markup.add(InlineKeyboardButton("🔄 Change Number", callback_data=f"chg_r|{service_info['srv_id']}|{service_info['cnt_id']}|{service_info['id']}"), InlineKeyboardButton("📨 OTP Group", url=main_link))
                markup.add(InlineKeyboardButton("🔙 Back to Ranges", callback_data=f"usr_c|{service_info['srv_id']}|{service_info['cnt_id']}"))
            
            safe_send(chat_id, text, markup, msg_id)
            active_polls[str(chat_id)] = True
            
            threading.Thread(target=poll_otp, args=(chat_id, number_id, number, service_info, api_key, msg_id, is_custom)).start()
        else:
            api_err = res_data.get("message", "Number is currently out of stock.")
            if "balance" in api_err.lower():
                api_err = "Number is out of stock for this range."
            
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
            safe_send(chat_id, f"{emo('cross')} <b>{api_err}</b>", markup, msg_id)
            
    except Exception as e: 
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
        safe_send(chat_id, f"{emo('warning')} <b>API Connection Error. Please try again.</b>", markup, msg_id)

def poll_otp(chat_id, number_id, phone_number, service_info, api_key, msg_id, is_custom):
    headers = {'X-API-Key': api_key}
    timeout = 600
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not active_polls.get(str(chat_id), True): return 
        
        try:
            res = requests.get(f"{BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=15)
            s_data = res.json()
            
            if s_data.get("success") and s_data.get("otp"):
                otp_code = s_data.get("otp")
                
                # --- 1. EDIT OLD MESSAGE TO SHOW COMPLETED ---
                success_edit_text = (
                    f"━━━━━━━━━━━\n"
                    f"《 {emo('done')} <b>COMPLETED</b> 》\n"
                    f"━━━━━━━━━━━\n"
                    f"<blockquote>[Service {emo(service_info['service_name'])} {html.escape(service_info['service_name'])}]\n"
                    f"[Country {emo(service_info['country_name'])} {html.escape(service_info['country_name'])}]</blockquote>\n"
                    f"━━━━━━━━━━━\n"
                    f"{emo('1')} <code>+{str(phone_number).replace('+', '')}</code>\n"
                    f"━━━━━━━━━━━\n"
                    f"{emo('live')} <i>OTP has been received and sent below!</i>"
                )
                markup = InlineKeyboardMarkup()
                if is_custom:
                    markup.add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
                else:
                    markup.add(InlineKeyboardButton("🔙 Back to Ranges", callback_data=f"usr_c|{service_info['srv_id']}|{service_info['cnt_id']}"))
                
                safe_send(chat_id, success_edit_text, markup, msg_id) 
                
                # --- 2. USER INBOX MESSAGE (NEW MESSAGE, LIFETIME SAVED) ---
                disp_num = f"+{str(phone_number).replace('+', '')}"
                
                user_msg = (
                    f"━━━━━━━━━━━\n"
                    f"[{emo('message')}] <b>New Message Received!</b>\n"
                    f"━━━━━━━━━━━\n"
                    f"[{emo('number')}] <b>Number:</b> <code>{disp_num}</code>\n"
                    f"━━━━━━━━━━━\n"
                    f"[{emo('otp')}] <b>OTP:</b> <code>{otp_code}</code>\n"
                    f"━━━━━━━━━━━"
                )
                
                safe_send(chat_id, user_msg)
                
                # --- 3. GROUP MESSAGE WITH SHORT FORMS ---
                masked_num = mask_number(phone_number)
                srv_short = get_short_service(service_info['service_name'])
                cc = get_iso_code(service_info['country_name'])
                
                group_msg = (
                    f"╭────────────────────────╮\n"
                    f"│{emo(service_info['service_name'])} #{srv_short} {emo(service_info['country_name'])} #{cc} {masked_num}\n"
                    f"╰────────────────────────╯"
                )
                
                data = load_data()
                for grp in data.get("forward_groups", []):
                    try:
                        grp_markup = InlineKeyboardMarkup(row_width=1)
                        if HAS_COPY_BTN:
                            grp_markup.add(InlineKeyboardButton(text=f"📋 {otp_code}", copy_text=CopyTextButton(text=str(otp_code))))
                        else:
                            grp_markup.add(InlineKeyboardButton(text=f"📋 {otp_code}", callback_data=f"cp_{otp_code}"))
                            
                        btn_name = grp.get('btn_name', '').strip()
                        btn_url = format_url(grp.get('btn_url', ''))
                        if btn_name and btn_url:
                            grp_markup.add(InlineKeyboardButton(text=btn_name, url=btn_url))
                            
                        safe_send(grp['chat_id'], group_msg, grp_markup)
                    except: pass
                        
                active_polls[str(chat_id)] = False 
                return 
        except: pass 
        time.sleep(3) 
        
    if active_polls.get(str(chat_id), False):
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
        safe_send(chat_id, f"{emo('time')} <b>Timeout!</b> No OTP received for <code>{phone_number}</code>.", markup, msg_id)
        active_polls[str(chat_id)] = False

if __name__ == "__main__":
    print("DXA NexaOTP Premium Bot (Smart Force Join Added) is running...")
    bot.infinity_polling()
