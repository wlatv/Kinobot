from telethon import events, Button
from config import ADMIN_IDS, STORAGE_CHANNEL_MULTI
from utils import is_admin
import os
import json

MULTI_LIST_FILE = "multi_list.json"
MULTI_STATE_FILE = "multi_state.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_data(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def register_multi_handlers(bot):

    @bot.on(events.NewMessage(pattern="^multi$"))
    async def start_multi(event):
        # faqat userlar uchun (adminlar faqat video yuboradi)
        save_data({"active": True, "user_id": event.sender_id}, MULTI_STATE_FILE)

        await event.respond(
            "🎞 <b>Multfilm rejimi yoqildi!</b>\n"
            "Endi 000 bilan boshlanuvchi kod kiriting.\n\n"
            "Masalan: <code>00042</code>",
            buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]],
            parse_mode="html"
        )

    @bot.on(events.NewMessage(pattern=r"^0{3}\d{1,3}$"))
    async def handle_code_input(event):
        if not os.path.exists(MULTI_STATE_FILE):
            return

        state = load_data(MULTI_STATE_FILE)
        if not state.get("active") or event.sender_id != state.get("user_id"):
            return

        code = int(event.raw_text.strip())
        state["code"] = code
        save_data(state, MULTI_STATE_FILE)

        await event.reply(
            f"✅ Kod <code>{code}</code> belgilandi.\nEndi admin multfilm yuboradi.",
            buttons=[[Button.inline("❌ Chiqish", b"exit_multi")]],
            parse_mode="html"
        )

    @bot.on(events.NewMessage(func=lambda e: e.video or (e.document and e.document.mime_type.startswith("video/"))))
    async def upload_multifilm(event):
        if not is_admin(event.sender_id):
            return  # faqat adminlar yuklaydi

        if not os.path.exists(MULTI_STATE_FILE):
            return

        state = load_data(MULTI_STATE_FILE)
        if not state.get("active") or "code" not in state:
            return  # kod berilmagan bo‘lsa

        code = state["code"]
        multi_list = load_data(MULTI_LIST_FILE)

        if str(code) in multi_list:
            await event.reply("⚠️ Bu kod allaqachon ishlatilgan!")
            return

        try:
            forwarded = await bot.forward_messages(
                entity=STORAGE_CHANNEL_MULTI,
                messages=event.id,
                from_peer=event.chat_id
            )
            msg_id = forwarded.id
            multi_list[str(code)] = msg_id
            save_data(multi_list, MULTI_LIST_FILE)

            await event.reply(
                f"✅ Multfilm yuklandi!\n🔢 Kod: <code>{code}</code>",
                parse_mode="html"
            )

            os.remove(MULTI_STATE_FILE)

        except Exception as e:
            await event.reply(f"❌ Xatolik: {str(e)}")

    @bot.on(events.NewMessage(pattern="^0{3}\d{1,3}$"))
    async def get_multifilm(event):
        if os.path.exists(MULTI_STATE_FILE):
            state = load_data(MULTI_STATE_FILE)
            if state.get("active") and event.sender_id == state.get("user_id"):
                return  # aktiv rejimda bo‘lsa, yuqoridagi handler ishlaydi

        code = event.raw_text.strip()
        multi_list = load_data(MULTI_LIST_FILE)

        if code in multi_list:
            try:
                msg_id = multi_list[code]
                msg = await bot.get_messages(STORAGE_CHANNEL_MULTI, ids=msg_id)
                if msg:
                    await bot.send_file(
                        event.chat_id,
                        msg.media,
                        caption="🍿 Multfilm topildi!"
                    )
                else:
                    await event.reply("⚠️ Multfilm topilmadi!")
            except Exception as e:
                await event.reply(f"❌ Xatolik: {str(e)}")
        else:
            await event.reply("❌ Bunday kodli multfilm yo‘q!")

    @bot.on(events.CallbackQuery(data=b"exit_multi"))
    async def exit_multi(event):
        if os.path.exists(MULTI_STATE_FILE):
            os.remove(MULTI_STATE_FILE)
        await event.edit("❌ Multfilm rejimidan chiqildi.", buttons=None)
print("🍿Multi ishladi")