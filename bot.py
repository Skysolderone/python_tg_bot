
import logging
import asyncio
from telegram import ForceReply, Update,Bot,BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from dotenv import load_dotenv
import os
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE)->None:
    user=update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update:Update,context:ContextTypes.DEFAULT_TYPE)->None:
    await update.message.reply_text("help!")
async def echo(update:Update,context:ContextTypes.DEFAULT_TYPE)->None:
    await update.message.reply_text(update.message.text)



async def main():
    load_dotenv()
    token=os.getenv('bot_api')
    # bot=Bot(token)
    Commands=[BotCommand('action','start the bot'),BotCommand('start','start the bot'),BotCommand('test','get the help')]
    # async with bot:
    #     await bot.set_my_commands(Commands)
    appliction=Application.builder().token(token).build()
    await appliction.bot.set_my_commands(Commands)
  
    appliction.add_handler(CommandHandler('start',start))
    appliction.add_handler(CommandHandler('help',help_command))
    appliction.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,echo))
    appliction.run_polling(allowed_updates=Update.ALL_TYPES)
    



if __name__=='__main__':
    asyncio.run(main())
    # main()