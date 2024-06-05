import time
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery

from pyrogram.errors import MessageNotModified
from pyrogram.errors.rpc_error import UnknownError
import asyncio
from __init__ import LOGGER, gDict, queueDB
import os
from bot import delete_all
from helpers.display_progress import Progress
from helpers.ffmpeg_helper import extractAudios, extractSubtitles
from helpers.uploader import uploadFiles

async def streamsExtractor(c: Client, cb:CallbackQuery ,media_mid, exAudios=False, exSubs=False):
    if not os.path.exists(f"downloads/{str(cb.from_user.id)}/"):
        os.makedirs(f"downloads/{str(cb.from_user.id)}/")
    _hold = await cb.message.edit(text="𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍")
    omess:Message = await c.get_messages(chat_id=cb.from_user.id, message_ids=media_mid)
    try:
        if (omess.video or omess.document):
            media = omess.video or omess.document
            LOGGER.info(f'𝖲𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽: {media.file_name}')
    except Exception as e:
        LOGGER.error(f"𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝖿𝖺𝗂𝗅𝖾𝖽: 𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗆𝖾𝖽𝗂𝖺 {e}")
        return
    c.stream_media(media,)
    try:
        c_time = time.time()
        prog = Progress(cb.from_user.id, c, cb.message)
        progress=f"🚀 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀: `{media.file_name}`"
        file_dl_path = await c.download_media(
            message=media,
            file_name=f"downloads/{str(cb.from_user.id)}/{str(omess.id)}/vid.mkv",  # fix for filename with single quote(') in name
            progress=prog.progress_for_pyrogram,
            progress_args=(progress, c_time),
        )
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
        await cb.message.edit("𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 𝖤𝗋𝗋𝗈𝗋")
        await asyncio.sleep(4)
    await _hold.edit_text("𝖥𝖾𝗍𝖼𝗁𝗂𝗇𝗀 𝖽𝖺𝗍𝖺")
    await asyncio.sleep(3)
    if exAudios:
        await _hold.edit_text("𝖤𝗑𝗍𝗋𝖺𝖼𝗍𝗂𝗇𝗀 𝖠𝗎𝖽𝗂𝗈𝗌")
        extract_dir = await extractAudios(file_dl_path,cb.from_user.id)
    if exSubs:
        await _hold.edit_text("𝖤𝗑𝗍𝗋𝖺𝖼𝗍𝗂𝗇𝗀 𝖲𝗎𝖻𝗍𝗂𝗍𝗅𝖾𝗌")
        extract_dir = await extractSubtitles(file_dl_path, cb.from_user.id)

    if extract_dir is None:
        await cb.message.edit("❌ 𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖤𝗑𝗍𝗋𝖺𝖼𝗍 𝖲𝗍𝗋𝖾𝖺𝗆𝗌 !")
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        return

    for dirpath, dirnames, filenames in os.walk(extract_dir):
        no_of_files = len(filenames)
        cf=1
        for f in filenames:
            await asyncio.sleep(5)
            up_path = os.path.join(dirpath,f)
            await uploadFiles(
                c=c,
                cb=cb,
                up_path=up_path,
                n=cf,
                all=no_of_files,
            )
            cf+=1
            LOGGER.info(f"𝖴𝗉𝗅𝗈𝖺𝖽𝖾𝖽: {up_path}")
    await cb.message.delete()
    await delete_all(root=f"downloads/{str(cb.from_user.id)}")
    queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
    
    return
