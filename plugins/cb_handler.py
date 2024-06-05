import asyncio
import os
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyromod.types import ListenerTypes
from pyromod.listen import Client

from helpers import database
from helpers.utils import UserSettings
from bot import (
    LOGGER,
    UPLOAD_AS_DOC,
    UPLOAD_TO_DRIVE,
    delete_all,
    formatDB,
    gDict,
    queueDB,
    showQueue,
)
from plugins.mergeVideo import mergeNow
from plugins.mergeVideoAudio import mergeAudio
from plugins.mergeVideoSub import mergeSub
from plugins.streams_extractor import streamsExtractor
from plugins.usettings import userSettings


@Client.on_callback_query()
async def callback_handler(c: Client, cb: CallbackQuery):
    #     await cb_handler.cb_handler(c, cb)
    # async def cb_handler(c: Client, cb: CallbackQuery):
    if cb.data == "merge":
        await cb.message.edit(
            text="𝖶𝗁𝖾𝗋𝖾 𝖣𝗈 𝖸𝗈𝗎 𝖶𝖺𝗇𝗍 𝖳𝗈 𝖴𝗉𝗅𝗈𝖺𝖽 ?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📤 𝖳𝗈 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆", callback_data="to_telegram"
                        ),
                        InlineKeyboardButton("🌫️ 𝖳𝗈 𝖣𝗋𝗂𝗏𝖾", callback_data="to_drive"),
                    ],
                    [InlineKeyboardButton("❌ 𝖢𝖺𝗇𝖼𝖾𝗅 ❌", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "to_drive":
        try:
            urc = await database.getUserRcloneConfig(cb.from_user.id)
            await c.download_media(
                message=urc, file_name=f"userdata/{cb.from_user.id}/rclone.conf"
            )
        except Exception:
            await cb.message.reply_text("𝖱𝖼𝗅𝗈𝗇𝖾 𝗇𝗈𝗍 𝖥𝗈𝗎𝗇𝖽, 𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝗎𝗉𝗅𝗈𝖺𝖽 𝗍𝗈 𝖽𝗋𝗂𝗏𝖾")
        if os.path.exists(f"userdata/{cb.from_user.id}/rclone.conf") is False:
            await cb.message.delete()
            await delete_all(root=f"downloads/{cb.from_user.id}/")
            queueDB.update(
                {cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}}
            )
            formatDB.update({cb.from_user.id: None})
            return
        UPLOAD_TO_DRIVE.update({f"{cb.from_user.id}": True})
        await cb.message.edit(
            text="𝖮𝗄𝖺𝗒 𝖨'𝗅𝗅 𝗎𝗉𝗅𝗈𝖺𝖽 𝗍𝗈 𝖽𝗋𝗂𝗏𝖾.\n𝖣𝗈 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗋𝖾𝗇𝖺𝗆𝖾? 𝖣𝖾𝖿𝖺𝗎𝗅𝗍 𝖿𝗂𝗅𝖾 𝗇𝖺𝗆𝖾 𝗂𝗌 **[@Movies_Zone_Media]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 𝖣𝖾𝖿𝖺𝗎𝗅𝗍", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ 𝖱𝖾𝗇𝖺𝗆𝖾", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("❌ 𝖢𝖺𝗇𝖼𝖾𝗅 ❌", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "to_telegram":
        UPLOAD_TO_DRIVE.update({f"{cb.from_user.id}": False})
        await cb.message.edit(
            text="𝖧𝗈𝗐 𝖽𝗈 𝗒𝗈 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗎𝗉𝗅𝗈𝖺𝖽 𝖿𝗂𝗅𝖾 ?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎞️ 𝖵𝗂𝖽𝖾𝗈", callback_data="video"),
                        InlineKeyboardButton("📁 𝖥𝗂𝗅𝖾", callback_data="document"),
                    ],
                    [InlineKeyboardButton("❌ 𝖢𝖺𝗇𝖼𝖾𝗅 ❌", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "document":
        UPLOAD_AS_DOC.update({f"{cb.from_user.id}": True})
        await cb.message.edit(
            text="𝖣𝗈 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗋𝖾𝗇𝖺𝗆𝖾? 𝖣𝖾𝖿𝖺𝗎𝗅𝗍 𝖿𝗂𝗅𝖾 𝗇𝖺𝗆𝖾 𝗂𝗌 **[@Movies_Zone_Media]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 𝖣𝖾𝖿𝖺𝗎𝗅𝗍", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ 𝖱𝖾𝗇𝖺𝗆𝖾", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("❌ 𝖢𝖺𝗇𝖼𝖾𝗅 ❌", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "video":
        UPLOAD_AS_DOC.update({f"{cb.from_user.id}": False})
        await cb.message.edit(
            text="𝖣𝗈 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗋𝖾𝗇𝖺𝗆𝖾? 𝖣𝖾𝖿𝖺𝗎𝗅𝗍 𝖿𝗂𝗅𝖾 𝗇𝖺𝗆𝖾 𝗂𝗌 **[@Movies_Zone_Media]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 𝖣𝖾𝖿𝖺𝗎𝗅𝗍", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ 𝖱𝖾𝗇𝖺𝗆𝖾", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("❌ 𝖢𝖺𝗇𝖼𝖾𝗅 ❌", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data.startswith("rclone_"):
        if "save" in cb.data:
            message_id = cb.message.reply_to_message.document.file_id
            LOGGER.info(message_id)
            await c.download_media(
                message=cb.message.reply_to_message,
                file_name=f"./userdata/{cb.from_user.id}/rclone.conf",
            )
            await database.addUserRcloneConfig(cb, message_id)
        else:
            await cb.message.delete()
        return

    elif cb.data.startswith("rename_"):
        user = UserSettings(cb.from_user.id, cb.from_user.first_name)
        if "YES" in cb.data:
            await cb.message.edit(
                "𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖿𝗂𝗅𝖾𝗇𝖺𝗆𝖾: **[@Movies_Zone_Media]_merged.mkv**\n\n𝖲𝖾𝗇𝖽 𝗆𝖾 𝗇𝖾𝗐 𝖿𝗂𝗅𝖾 𝗇𝖺𝗆𝖾 𝗐𝗂𝗍𝗁𝗈𝗎𝗍 𝖾𝗑𝗍𝖾𝗇𝗌𝗂𝗈𝗇: 𝖸𝗈𝗎 𝗁𝖺𝗏𝖾 1 𝗆𝗂𝗇𝗎𝗍𝖾"
            )
            res: Message = await c.listen(chat_id=cb.message.chat.id, filters=filters.text, listener_type=ListenerTypes.MESSAGE, timeout=120, user_id=cb.from_user.id)
            if res.text:
                new_file_name = f"downloads/{str(cb.from_user.id)}/{res.text}.mkv"
                await res.delete(True)
            if user.merge_mode == 1:
                await mergeNow(c, cb, new_file_name)
            elif user.merge_mode == 2:
                await mergeAudio(c, cb, new_file_name)
            elif user.merge_mode == 3:
                await mergeSub(c, cb, new_file_name)
            return

        if "NO" in cb.data:
            new_file_name = (
                f"downloads/{str(cb.from_user.id)}/[@Movies_Zone_Media]_merged.mkv"
            )
            if user.merge_mode == 1:
                await mergeNow(c, cb, new_file_name)
            elif user.merge_mode == 2:
                await mergeAudio(c, cb, new_file_name)
            elif user.merge_mode == 3:
                await mergeSub(c, cb, new_file_name)

    elif cb.data == "cancel":
        await delete_all(root=f"downloads/{cb.from_user.id}/")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("𝖲𝗎𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖢𝖺𝗇𝖼𝖾𝗅𝗅𝖾𝖽")
        await asyncio.sleep(5)
        await cb.message.delete(True)
        return

    elif cb.data.startswith("gUPcancel"):
        cmf = cb.data.split("/")
        chat_id, mes_id, from_usr = cmf[1], cmf[2], cmf[3]
        if int(cb.from_user.id) == int(from_usr):
            await c.answer_callback_query(
                cb.id, text="𝖦𝗈𝗂𝗇𝗀 𝗍𝗈 𝖢𝖺𝗇𝖼𝖾𝗅 . . . 🛠", show_alert=False
            )
            gDict[int(chat_id)].append(int(mes_id))
        else:
            await c.answer_callback_query(
                callback_query_id=cb.id,
                text="⚠️ 𝖮𝗉𝗉𝗌 ⚠️ \n 𝖨 𝖦𝗈𝗍 𝖺 𝖥𝖺𝗅𝗌𝖾 𝖵𝗂𝗌𝗂𝗍𝗈𝗋 🚸 !! \n\n 📛 𝖲𝗍𝖺𝗒 𝖠𝗍 𝖸𝗈𝗎𝗋 𝖫𝗂𝗆𝗂𝗍𝗌 !!📛",
                show_alert=True,
                cache_time=0,
            )
        await delete_all(root=f"downloads/{cb.from_user.id}/")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return

    elif cb.data == "close":
        await cb.message.delete(True)
        try:
            await cb.message.reply_to_message.delete(True)
        except Exception as err:
            pass

    elif cb.data.startswith("showFileName_"):
        message_id = int(cb.data.rsplit("_", 1)[-1])
        LOGGER.info(queueDB.get(cb.from_user.id)["videos"])
        LOGGER.info(queueDB.get(cb.from_user.id)["subtitles"])
        sIndex = queueDB.get(cb.from_user.id)["videos"].index(message_id)
        m = await c.get_messages(chat_id=cb.message.chat.id, message_ids=message_id)
        if queueDB.get(cb.from_user.id)["subtitles"][sIndex] is None:
            try:
                await cb.message.edit(
                    text=f"𝖥𝗂𝗅𝖾 𝖭𝖺𝗆𝖾: {m.video.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ 𝖱𝖾𝗆𝗈𝗏𝖾",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "📜 𝖠𝖽𝖽 𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾",
                                    callback_data=f"addSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 𝖡𝖺𝖼𝗄", callback_data="back")],
                        ]
                    ),
                )
            except Exception:
                await cb.message.edit(
                    text=f"𝖥𝗂𝗅𝖾 𝖭𝖺𝗆𝖾: {m.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ 𝖱𝖾𝗆𝗈𝗏𝖾",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "📜 𝖠𝖽𝖽 𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾",
                                    callback_data=f"addSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 𝖡𝖺𝖼𝗄", callback_data="back")],
                        ]
                    ),
                )
            return
        else:
            sMessId = queueDB.get(cb.from_user.id)["subtitles"][sIndex]
            s = await c.get_messages(chat_id=cb.message.chat.id, message_ids=sMessId)
            try:
                await cb.message.edit(
                    text=f"𝖥𝗂𝗅𝖾 𝖭𝖺𝗆𝖾: {m.video.file_name}\n\n𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾: {s.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖥𝗂𝗅𝖾",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "❌ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾",
                                    callback_data=f"removeSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 𝖡𝖺𝖼𝗄", callback_data="back")],
                        ]
                    ),
                )
            except Exception:
                await cb.message.edit(
                    text=f"𝖥𝗂𝗅𝖾 𝖭𝖺𝗆𝖾: {m.video.file_name}\n\n𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾: {s.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖥𝗂𝗅𝖾",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "❌ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾",
                                    callback_data=f"removeSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 𝖡𝖺𝖼𝗄", callback_data="back")],
                        ]
                    ),
                )
            return

    elif cb.data.startswith("addSub_"):
        sIndex = int(cb.data.split(sep="_")[1])
        vMessId = queueDB.get(cb.from_user.id)["videos"][sIndex]
        rmess = await cb.message.edit(
            text=f"𝖲𝖾𝗇𝖽 𝗆𝖾 𝖺 𝗌𝗎𝖻𝗍𝗂𝗍𝗅𝖾 𝖿𝗂𝗅𝖾, 𝗒𝗈𝗎 𝗁𝖺𝗏𝖾 1 𝗆𝗂𝗇𝗎𝗍𝖾",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 𝖡𝖺𝖼𝗄", callback_data=f"showFileName_{vMessId}"
                        )
                    ]
                ]
            ),
        )
        subs: Message = await c.listen(
            chat_id=cb.message.chat.id, filters=filters.document, listener_type=ListenerTypes.MESSAGE, timeout=120, user_id=cb.from_user.id
        )
        if subs is not None:
            media = subs.document or subs.video
            if media.file_name.rsplit(".")[-1] not in "srt":
                await subs.reply_text(
                    text=f"𝖯𝗅𝖾𝖺𝗌𝖾 𝗀𝗈 𝖻𝖺𝖼𝗄 𝖿𝗂𝗋𝗌𝗍",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔙 𝖡𝖺𝖼𝗄", callback_data=f"showFileName_{vMessId}"
                                )
                            ]
                        ]
                    ),
                    quote=True,
                )
                return
            queueDB.get(cb.from_user.id)["subtitles"][sIndex] = subs.id
            await subs.reply_text(
                f"Added {subs.document.file_name}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 𝖡𝖺𝖼𝗄", callback_data=f"showFileName_{vMessId}"
                            )
                        ]
                    ]
                ),
                quote=True,
            )
            await rmess.delete(True)
            LOGGER.info("𝖠𝖽𝖽𝖾𝖽 𝗌𝗎𝖻 𝗍𝗈 𝗅𝗂𝗌𝗍")
        return

    elif cb.data.startswith("removeSub_"):
        sIndex = int(cb.data.rsplit("_")[-1])
        vMessId = queueDB.get(cb.from_user.id)["videos"][sIndex]
        queueDB.get(cb.from_user.id)["subtitles"][sIndex] = None
        await cb.message.edit(
            text=f"𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾 𝖱𝖾𝗆𝗈𝗏𝖾𝖽 𝖭𝗈𝗐 𝗀𝗈 𝖻𝖺𝖼𝗄 𝗈𝗋 𝗌𝖾𝗇𝖽 𝗇𝖾𝗑𝗍 𝗏𝗂𝖽𝖾𝗈",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 𝖡𝖺𝖼𝗄", callback_data=f"showFileName_{vMessId}"
                        )
                    ]
                ]
            ),
        )
        LOGGER.info("𝖲𝗎𝖻 𝗋𝖾𝗆𝗈𝗏𝖾𝖽 𝖿𝗋𝗈𝗆 𝗅𝗂𝗌𝗍")
        return

    elif cb.data == "back":
        await showQueue(c, cb)
        return

    elif cb.data.startswith("removeFile_"):
        sIndex = queueDB.get(cb.from_user.id)["videos"].index(
            int(cb.data.split("_", 1)[-1])
        )
        queueDB.get(cb.from_user.id)["videos"].remove(int(cb.data.split("_", 1)[-1]))
        await showQueue(c, cb)
        return

    elif cb.data.startswith("ch@ng3M0de_"):
        uid = cb.data.split("_")[1]
        user = UserSettings(int(uid), cb.from_user.first_name)
        mode = int(cb.data.split("_")[2])
        user.merge_mode = mode
        user.set()
        await userSettings(
            cb.message, int(uid), cb.from_user.first_name, cb.from_user.last_name, user
        )
        return

    elif cb.data == "tryotherbutton":
        await cb.answer(text="𝖳𝗋𝗒 𝗈𝗍𝗁𝖾𝗋 𝖻𝗎𝗍𝗍𝗈𝗇 → ☛")
        return

    elif cb.data.startswith("toggleEdit_"):
        uid = int(cb.data.split("_")[1])
        user = UserSettings(uid, cb.from_user.first_name)
        user.edit_metadata = False if user.edit_metadata else True
        user.set()
        await userSettings(
            cb.message, uid, cb.from_user.first_name, cb.from_user.last_name, user
        )
        return

    elif cb.data.startswith('extract'):
        edata = cb.data.split('_')[1]
        media_mid = int(cb.data.split('_')[2])
        try:
            if edata == 'audio':
                LOGGER.info('audio')
                await streamsExtractor(c, cb, media_mid, exAudios=True)
            elif edata == 'subtitle':
                await streamsExtractor(c, cb, media_mid, exSubs=True)
            elif edata == 'all':
                await streamsExtractor(c, cb, media_mid, exAudios=True, exSubs=True)
        except Exception as e:
            LOGGER.error(e)
