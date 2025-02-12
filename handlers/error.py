from aiogram import Router, Bot
from aiogram.types import FSInputFile
from aiogram.types import ErrorEvent

from config_data.config import Config, load_config

import traceback
import logging

logger = logging.getLogger(__name__)
router = Router()
config: Config = load_config()


@router.error()
async def error_handler(event: ErrorEvent, bot: Bot):
    logger.critical("Критическая ошибка: %s", event.exception, exc_info=True)
    formatted_lines = traceback.format_exc()
    text_file = open('error.txt', 'w')
    text_file.write(str(formatted_lines))
    text_file.close()
    for support in config.tg_bot.support_ids.split(','):
        try:
            await bot.send_message(chat_id=support,
                                   text=f'{event.exception}')
            await bot.send_document(chat_id=support,
                                    document=FSInputFile('error.txt'))
        except:
            pass

