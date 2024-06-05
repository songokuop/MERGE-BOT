import asyncio
import os
import time

from bot import (LOGGER, UPLOAD_AS_DOC, UPLOAD_TO_DRIVE, delete_all, formatDB,
                 gDict, queueDB)
from config import Config
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helpers.display_progress import Progress
from helpers.ffmpeg_helper import MergeSub, MergeVideo, take_screen_shot
from helpers.rclone_upload import rclone_driver, rclone_upload
from helpers.uploader import uploadVideo
from helpers.utils import UserSettings
from PIL import Image
from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.errors.rpc_error import UnknownError
from pyrogram.types import CallbackQuery


async def mergeNow(c: Client, cb: CallbackQuery, new_file_name: str):
    omess = cb.message.reply_to_message
    # LOGGER.info(omess.id)
    vid_list = list()
    sub_list = list()
    sIndex = 0
    await cb.message.edit("⭕ 𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀...")
    duration = 0
    list_message_ids = queueDB.get(cb.from_user.id)["videos"]
    list_message_ids.sort()
    list_subtitle_ids = queueDB.get(cb.from_user.id)["subtitles"]
    # list_subtitle_ids.sort()
    LOGGER.info(Config.IS_PREMIUM)
    LOGGER.info(f"Videos: {list_message_ids}")
    LOGGER.info(f"Subs: {list_subtitle_ids}")
    if list_message_ids is None:
        await cb.answer("𝖰𝗎𝖾𝗎𝖾 𝖤𝗆𝗉𝗍𝗒", show_alert=True)
        await cb.message.delete(True)
        return
    if not os.path.exists(f"downloads/{str(cb.from_user.id)}/"):
        os.makedirs(f"downloads/{str(cb.from_user.id)}/")
    input_ = f"downloads/{str(cb.from_user.id)}/input.txt"
    all = len(list_message_ids)
    n=1
    for i in await c.get_messages(
chat_id=cb.from_user.id, message_ids=list_message_ids ):
        media = i.video or i.document
        await cb.message.edit(f"📥 𝖲𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗈𝖿 ... `{media.file_name}`")
        LOGGER.info(f"📥 𝖲𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝗈𝖿 ... {media.file_name}")
        await asyncio.sleep(5)
        file_dl_path = None
        sub_dl_path = None
        try:
            c_time = time.time()
            prog = Progress(cb.from_user.id, c, cb.message)
            file_dl_path = await c.download_media(
                message=media,
                file_name=f"downloads/{str(cb.from_user.id)}/{str(i.id)}/vid.mkv",  # fix for filename with single quote(') in name
                progress=prog.progress_for_pyrogram,
                progress_args=(f"🚀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀: `{media.file_name}`", c_time, f"\n**𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀: {n}/{all}**"),
            )
            n+=1
            if gDict[cb.message.chat.id] and cb.message.id in gDict[cb.message.chat.id]:
                return
            await cb.message.edit(f"𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝖽 𝖲𝗎𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 ... `{media.file_name}`")
            LOGGER.info(f"𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝖾𝖽 𝖲𝗎𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 ... {media.file_name}")
            await asyncio.sleep(5)
        except UnknownError as e:
            LOGGER.info(e)
            pass
        except Exception as downloadErr:
            LOGGER.info(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖽𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝖤𝗋𝗋𝗈𝗋: {downloadErr}")
            queueDB.get(cb.from_user.id)["video"].remove(i.id)
            await cb.message.edit("❗𝖥𝗂𝗅𝖾 𝖲𝗄𝗂𝗉𝗉𝖾𝖽!")
            await asyncio.sleep(4)
            continue

        if list_subtitle_ids[sIndex] is not None:
            a = await c.get_messages(
                chat_id=cb.from_user.id, message_ids=list_subtitle_ids[sIndex]
            )
            sub_dl_path = await c.download_media(
                message=a,
                file_name=f"downloads/{str(cb.from_user.id)}/{str(a.id)}/",
            )
            LOGGER.info("Got sub: ", a.document.file_name)
            file_dl_path = await MergeSub(file_dl_path, sub_dl_path, cb.from_user.id)
            LOGGER.info("𝖠𝖽𝖽𝖾𝖽 𝗌𝗎𝖻𝗌")
        sIndex += 1

        metadata = extractMetadata(createParser(file_dl_path))
        try:
            if metadata.has("duration"):
                duration += metadata.get("duration").seconds
            vid_list.append(f"file '{file_dl_path}'")
        except:
            await delete_all(root=f"downloads/{str(cb.from_user.id)}")
            queueDB.update(
                {cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}}
            )
            formatDB.update({cb.from_user.id: None})
            await cb.message.edit("⚠️ 𝖵𝗂𝖽𝖾𝗈 𝗂𝗌 𝖼𝗈𝗋𝗋𝗎𝗉𝗍𝖾𝖽")
            return

    _cache = list()
    for i in range(len(vid_list)):
        if vid_list[i] not in _cache:
            _cache.append(vid_list[i])
    vid_list = _cache
    LOGGER.info(f"𝖳𝗋𝗒𝗂𝗇𝗀 𝗍𝗈 𝗆𝖾𝗋𝗀𝖾 𝗏𝗂𝖽𝖾𝗈𝗌 user {cb.from_user.id}")
    await cb.message.edit(f"🔀 𝖳𝗋𝗒𝗂𝗇𝗀 𝗍𝗈 𝗆𝖾𝗋𝗀𝖾 𝗏𝗂𝖽𝖾𝗈𝗌 ...")
    with open(input_, "w") as _list:
        _list.write("\n".join(vid_list))
    merged_video_path = await MergeVideo(
        input_file=input_, user_id=cb.from_user.id, message=cb.message, format_="mkv"
    )
    if merged_video_path is None:
        await cb.message.edit("❌ 𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝗆𝖾𝗋𝗀𝖾 𝗏𝗂𝖽𝖾𝗈 !")
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    try:
        await cb.message.edit("✅ 𝖲𝗎𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖬𝖾𝗋𝗀𝖾𝖽 𝖵𝗂𝖽𝖾𝗈 !")
    except MessageNotModified:
        await cb.message.edit("𝖲𝗎𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖬𝖾𝗋𝗀𝖾𝖽 𝖵𝗂𝖽𝖾𝗈 ! ✅")
    LOGGER.info(f"𝖵𝗂𝖽𝖾𝗈 𝗆𝖾𝗋𝗀𝖾𝖽 𝖿𝗈𝗋: {cb.from_user.first_name} ")
    await asyncio.sleep(3)
    file_size = os.path.getsize(merged_video_path)
    os.rename(merged_video_path, new_file_name)
    await cb.message.edit(
        f"🔄 𝖱𝖾𝗇𝖺𝗆𝖾𝖽 𝖬𝖾𝗋𝗀𝖾𝖽 𝖵𝗂𝖽𝖾𝗈 𝗍𝗈\n **{new_file_name.rsplit('/',1)[-1]}**"
    )
    await asyncio.sleep(3)
    merged_video_path = new_file_name
    if UPLOAD_TO_DRIVE[f"{cb.from_user.id}"]:
        await rclone_driver(omess, cb, merged_video_path)
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    if file_size > 2044723200 and Config.IS_PREMIUM == False:
        await cb.message.edit(
            f"𝖵𝗂𝖽𝖾𝗈 𝗂𝗌 𝖫𝖺𝗋𝗀𝖾𝗋 𝗍𝗁𝖺𝗇 2𝖦𝖡 𝖢𝖺𝗇'𝗍 𝖴𝗉𝗅𝗈𝖺𝖽,\n\n Tell {Config.OWNER_USERNAME} 𝗍𝗈 𝖺𝖽𝖽 𝗉𝗋𝖾𝗆𝗂𝗎𝗆 𝖺𝖼𝖼𝗈𝗎𝗇𝗍 𝗍𝗈 𝗀𝖾𝗍 4𝖦𝖡 𝖳𝖦 𝗎𝗉𝗅𝗈𝖺𝖽𝗌"
        )
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    if Config.IS_PREMIUM and file_size > 4241280205:
        await cb.message.edit(
            f"𝖵𝗂𝖽𝖾𝗈 𝗂𝗌 𝖫𝖺𝗋𝗀𝖾𝗋 𝗍𝗁𝖺𝗇 4𝖦𝖡 𝖢𝖺𝗇'𝗍 𝖴𝗉𝗅𝗈𝖺𝖽,\n\n Tell {Config.OWNER_USERNAME} 𝗍𝗈 𝖽𝗂𝖾 𝗐𝗂𝗍𝗁 𝗉𝗋𝖾𝗆𝗂𝗎𝗆 𝖺𝖼𝖼𝗈𝗎𝗇𝗍"
        )
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    await cb.message.edit("🎥 𝖤𝗑𝗍𝗋𝖺𝖼𝗍𝗂𝗇𝗀 𝖵𝗂𝖽𝖾𝗈 𝖣𝖺𝗍𝖺 ...")
    duration = 1
    try:
        metadata = extractMetadata(createParser(merged_video_path))
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
    except Exception as er:
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("⭕ 𝖬𝖾𝗋𝗀𝖾𝖽 𝖵𝗂𝖽𝖾𝗈 𝗂𝗌 𝖼𝗈𝗋𝗋𝗎𝗉𝗍𝖾𝖽")
        return
    try:
        user = UserSettings(cb.from_user.id, cb.from_user.first_name)
        thumb_id = user.thumbnail
        if thumb_id is None:
            raise Exception
        # thumb_id = await database.getThumb(cb.from_user.id)
        video_thumbnail = f"downloads/{str(cb.from_user.id)}_thumb.jpg"
        await c.download_media(message=str(thumb_id), file_name=video_thumbnail)
    except Exception as err:
        LOGGER.info("Generating thumb")
        video_thumbnail = await take_screen_shot(
            merged_video_path, f"downloads/{str(cb.from_user.id)}", (duration / 2)
        )
    width = 1280
    height = 720
    try:
        thumb = extractMetadata(createParser(video_thumbnail))
        height = thumb.get("height")
        width = thumb.get("width")
        img = Image.open(video_thumbnail)
        if width > height:
            img.resize((320, height))
        elif height > width:
            img.resize((width, 320))
        img.save(video_thumbnail)
        Image.open(video_thumbnail).convert("RGB").save(video_thumbnail, "JPEG")
    except:
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("⭕ 𝖬𝖾𝗋𝗀𝖾𝖽 𝖵𝗂𝖽𝖾𝗈 𝗂𝗌 𝖼𝗈𝗋𝗋𝗎𝗉𝗍𝖾𝖽")
        return
    await uploadVideo(
        c=c,
        cb=cb,
        merged_video_path=merged_video_path,
        width=width,
        height=height,
        duration=duration,
        video_thumbnail=video_thumbnail,
        file_size=os.path.getsize(merged_video_path),
        upload_mode=UPLOAD_AS_DOC[f"{cb.from_user.id}"],
    )
    await cb.message.delete(True)
    await delete_all(root=f"downloads/{str(cb.from_user.id)}")
    queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
    formatDB.update({cb.from_user.id: None})
    return
