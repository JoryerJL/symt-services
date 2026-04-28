import asyncio
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from decouple import config
import ftplib

FTP_HOST = config('FTP_HOST')
FTP_USER = config('FTP_USER')
FTP_PASS = config('FTP_PASS')
FTP_PATH = config('FTP_PATH')


def createMsg(service):
    message = (
        f"⚠️ -- ID Servicio {service.service_number}-- ⚠️\n\n"
        f"👤 Cliente: {service.client}\n"
        f"💬 Descripción del servicio: {service.description}\n"
        f"🛠️ Empleado: {service.employee}\n"
        f"🔍 Estado del servicio: {service.get_status_display()}\n"
    )
    return message


async def send_msg(message, chat_id, service_id):
    async def main():
        bot = telegram.Bot(config("TOKEN_BOT"))
        keyboard = [[InlineKeyboardButton("Confirmar", callback_data=f'confirm_{service_id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        async with bot:
            await bot.send_message(text=message, chat_id=chat_id, reply_markup=reply_markup)

    await main()

def createMsgFromJson(service_json):
    message = (
        f"⚠️ -- ID Servicio {service_json['service_number']}-- ⚠️\n\n"
        f"👤 Cliente: {service_json['client']['first_name']}\n"
        f"💬 Descripción del servicio: {service_json['description']}\n"
        f"🛠️ Empleado: {service_json['employee']['first_name']}\n"
        f"🔍 Estado del servicio: {service_json['status_name']}\n"
    )
    return message

async def send_confirm_msg(message, chat_id):
    async def main():
        bot = telegram.Bot(config("TOKEN_BOT"))
        async with bot:
            await bot.send_message(text=message, chat_id=chat_id)

    await main()


def list_images_from_ftp(service):
    ftp_host = config("FTP_HOST")
    ftp_user = config("FTP_USER")
    ftp_pass = config("FTP_PASS")
    ftp_path = f"{config('FTP_PATH')}/{service.service_number}-{service.client.first_name}-{service.created_at.strftime('%Y-%m-%d')}"

    images = []

    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_path)

        images = ftp.nlst()  # Obtiene la lista de archivos

        ftp.quit()
    except ftplib.all_errors as e:
        print(f"Error al acceder al FTP: {e}")

    return images
