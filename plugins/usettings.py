import time
from pyrogram import filters, Client as mergeApp
from pyrogram.types import Message, InlineKeyboardMarkup
from helpers.msg_utils import MakeButtons
from helpers.utils import UserSettings


@mergeApp.on_message(filters.command(["settings"]))
async def f1(c: mergeApp, m: Message):
    # setUserMergeMode(uid=m.from_user.id,mode=1)
    replay = await m.reply(text="Please wait", quote=True)
    usettings = UserSettings(m.from_user.id, m.from_user.first_name)
    await userSettings(
        replay, m.from_user.id, m.from_user.first_name, m.from_user.last_name, usettings
    )


async def userSettings(
    editable: Message,
    uid: int,
    fname,
    lname,
    usettings: UserSettings,
):
    b = MakeButtons()
    if usettings.user_id:
        if usettings.merge_mode == 1:
            userMergeModeId = 1
            userMergeModeStr = "𝖵𝗂𝖽𝖾𝗈 🎥 + 𝖵𝗂𝖽𝖾𝗈 🎥"
        elif usettings.merge_mode == 2:
            userMergeModeId = 2
            userMergeModeStr = "𝖵𝗂𝖽𝖾𝗈 🎥 + 𝖠𝗎𝖽𝗂𝗈 🎵"
        elif usettings.merge_mode == 3:
            userMergeModeId = 3
            userMergeModeStr = "𝖵𝗂𝖽𝖾𝗈 🎥 + 𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾 📜"
        elif usettings.merge_mode == 4:
            userMergeModeId = 4
            userMergeModeStr = "𝖤𝗑𝗍𝗋𝖺𝖼𝗍" 
        if usettings.edit_metadata:
            editMetadataStr = "✅"
        else:
            editMetadataStr = "❌"
        uSettingsMessage = f"""
<b><u>𝖬𝖾𝗋𝗀𝖾 𝖡𝗈𝗍 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖿𝗈𝗋 <a href='tg://user?id={uid}'>{fname} {lname}</a></u></b>
╭──────────────────────
┣**🎭 𝖨𝖣: <u>{usettings.user_id}</u>**
┣**{'❌' if usettings.banned else '🪺'} 𝖡𝖺𝗇 𝖲𝗍𝖺𝗍𝗎𝗌: <u>{usettings.banned}</u>**
┣**{'🌦️' if usettings.allowed else '🌦️'} 𝖠𝗅𝗅𝗈𝗐𝖾𝖽: <u>{usettings.allowed}</u>**
┣**{'🏜️' if usettings.edit_metadata else '❌'} 𝖤𝖽𝗂𝗍 𝖬𝖾𝗍𝖺𝖽𝖺𝗍𝖺: <u>{usettings.edit_metadata}</u>**
┣**🚏 𝖬𝖾𝗋𝗀𝖾 𝗆𝗈𝖽𝖾: <u>{userMergeModeStr}</u>**
╰──────────────────────
"""
        markup = b.makebuttons(
            [
                "𝖬𝖾𝗋𝗀𝖾 𝗆𝗈𝖽𝖾",
                userMergeModeStr,
                "𝖤𝖽𝗂𝗍 𝖬𝖾𝗍𝖺𝖽𝖺𝗍𝖺",
                editMetadataStr,
                "Close",
            ],
            [
                "tryotherbutton",
                f"ch@ng3M0de_{uid}_{(userMergeModeId%4)+1}",
                "tryotherbutton",
                f"toggleEdit_{uid}",
                "close",
            ],
            rows=2,
        )
        res = await editable.edit(
            text=uSettingsMessage, reply_markup=InlineKeyboardMarkup(markup)
        )
    else:
        usettings.name = fname
        usettings.merge_mode = 1
        usettings.allowed = False
        usettings.edit_metadata = False
        usettings.thumbnail = None
        await userSettings(editable, uid, fname, lname, usettings)
    # await asyncio.sleep(10)
    # await c.delete_messages(chat_id=editable.chat.id, message_ids=[res.id-1,res.id])
    return
