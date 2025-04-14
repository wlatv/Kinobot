import os
import json
from telethon import Button
from telethon.errors import UserNotParticipantError, ChannelPrivateError
from telethon.tl.functions.channels import GetParticipantRequest

# Fayl nomlari
START_FILE = "start_message.json"
FORCE_SUB_FILE = "force_subs.json"
EDIT_FORCE_SUB_FILE = "edit_force_state.txt"
LIST_FILE = "list.json"
USERS_FILE = "users.json"
ADMINS_FILE = "admins.json"

# ✅ Adminlar
def load_admins():
    try:
        with open(ADMINS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

ADMIN_IDS = load_admins()

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ✅ JSON faylni yuklash (universal funksiya)
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} if filename.endswith(".json") and "list" not in filename else []
    return {} if filename.endswith(".json") and "list" not in filename else []

# ✅ JSON faylni saqlash (universal funksiya)
def save_data(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# ✅ Start xabari
def load_start():
    if os.path.exists(START_FILE):
        with open(START_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return {"text": "👋 Salom {first_name}!", "photo": None}

def save_start(text=None, photo=None):
    data = load_start()
    if text:
        data["text"] = text
    if photo:
        data["photo"] = photo
    with open(START_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ✅ Kino ro‘yxati
def load_list():
    if not os.path.exists(LIST_FILE):
        with open(LIST_FILE, "w") as f:
            json.dump([], f)
    with open(LIST_FILE, "r") as f:
        return json.load(f)

def save_list(data):
    with open(LIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ✅ Foydalanuvchilar
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# ✅ Majburiy obuna (force sub)
if not os.path.exists(FORCE_SUB_FILE):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump([], f)

def load_forced_subs():
    with open(FORCE_SUB_FILE, "r") as f:
        return json.load(f)

def save_forced_subs(channels):
    with open(FORCE_SUB_FILE, "w") as f:
        json.dump(channels, f, indent=4)

# ✅ Obuna tekshirish
async def is_subscribed(bot, user_id):
    if is_admin(user_id):
        return True

    channels = load_forced_subs()
    for ch in channels:
        try:
            channel = ch.lstrip("@")
            channel_entity = await bot.get_input_entity(channel)
            user_entity = await bot.get_input_entity(user_id)

            await bot(GetParticipantRequest(
                channel=channel_entity,
                participant=user_entity
            ))
        except UserNotParticipantError:
            return False
        except ChannelPrivateError:
            continue
        except Exception:
            return False
    return True

# ✅ Obuna haqida xabar yuborish
async def send_force_sub_message(bot, user_id):
    channels = load_forced_subs()
    unsubscribed = []

    for ch in channels:
        try:
            channel = ch.lstrip("@")
            channel_entity = await bot.get_input_entity(channel)
            user_entity = await bot.get_input_entity(user_id)

            await bot(GetParticipantRequest(
                channel=channel_entity,
                participant=user_entity
            ))
        except UserNotParticipantError:
            unsubscribed.append(channel)
        except ChannelPrivateError:
            print(f"Bot kanalga kira olmaydi: {ch}")
        except Exception as e:
            print(f"[ERROR send_force_sub_message] Kanal: {ch}, Xatolik: {e}")

    if not unsubscribed:
        return

    buttons = [[Button.url(f"📢 {ch}", f"https://t.me/{ch}")] for ch in unsubscribed]
    buttons.append([Button.inline("🔄 Tekshirish", b"check_sub")])

    await bot.send_message(
        user_id,
        "❌ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
        buttons=buttons
    )