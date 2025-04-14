from telethon import events
from config import ADMIN_IDS, STORAGE_CHANNEL, STORAGE_CHANNEL_MULTI, MOVIE_CHANNEL
from utils import is_admin, load_data, save_data
import os
import json

MOVIE_LIST_FILE = "movie_list.json"
MULTI_LIST_FILE = "multi_list.json"
MULTI_STATE_FILE = "multi_state.json"


def register_movie_handlers(bot):

    @bot.on(events.NewMessage(func=lambda e: e.video or (e.document and e.document.mime_type.startswith("video/"))))
    async def upload_video(event):
        if not is_admin(event.sender_id):
            await event.delete()
            await event.respond("❌ Siz video yubora olmaysiz!")
            return

        # Multi rejim tekshiriladi
        is_multi = False
        if os.path.exists(MULTI_STATE_FILE):
            data = load_data(MULTI_STATE_FILE)
            is_multi = isinstance(data, dict) and data.get("active")

        target_channel = STORAGE_CHANNEL_MULTI if is_multi else STORAGE_CHANNEL
        list_file = MULTI_LIST_FILE if is_multi else MOVIE_LIST_FILE
        media_type = "Multfilm" if is_multi else "Kino"

        try:
            forwarded = await bot.forward_messages(
                entity=target_channel,
                messages=event.id,
                from_peer=event.chat_id
            )

            msg_id = forwarded.id
            saved_list = load_data(list_file)
            if msg_id not in saved_list:
                saved_list.append(msg_id)
                save_data(saved_list, list_file)

            await event.reply(
                f"✅ {media_type} yuklandi!\n🔢 Kod: <code>{msg_id}</code>",
                parse_mode="html"
            )
        except Exception as e:
            await event.reply(f"❌ Xatolik: {str(e)}")

    # Foydalanuvchi kino kodi yuborganida
    @bot.on(events.NewMessage(pattern=r"^\d+$"))
    async def user_request_movie(event):
        if os.path.exists(MULTI_STATE_FILE):
            state = load_data(MULTI_STATE_FILE)
            if isinstance(state, dict) and state.get("active"):
                return  # Multi rejimda oddiy kino yuborilmaydi

        code = int(event.raw_text.strip())
        movie_list = load_data(MOVIE_LIST_FILE)

        if code in movie_list:
            try:
                msg = await bot.get_messages(MOVIE_CHANNEL, ids=code)
                if msg.video or (msg.document and msg.document.mime_type.startswith("video/")):
                    await bot.send_file(
                        event.chat_id,
                        msg.media,
                        caption="🎬 Siz so‘ragan kino topildi!\n@Archive_channel1"
                    )
                else:
                    await event.reply("❌ Bu kino emas!")
            except Exception as e:
                await event.reply(f"❌ Xatolik: {str(e)}")
        else:
            await event.reply("❌ Bunday kino kodi mavjud emas.")