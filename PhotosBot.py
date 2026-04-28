import logging
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings before any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BotPhotosSYMT.settings')

import django
django.setup()

import pytz
import requests
from decouple import config
import ftplib
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

from service.models import Service, ServiceImage
from service.utils import createMsgFromJson, send_confirm_msg

# Configuración del Bot
TOKEN = config('TOKEN_BOT')
API_URL = config("API_URL")
GROUP_CHAT_ID = config("GROUP_CHAT_ID")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Definiendo zona horaria local
local_tz = pytz.timezone('America/Mexico_City')

# obteniendo la hora actual en UTC y conviértela a la zona horaria local
utc_now = datetime.datetime.now(pytz.utc)
local_now = utc_now.astimezone(local_tz)

# Configuración del FTP
FTP_HOST = config('FTP_HOST')
FTP_USER = config('FTP_USER')
FTP_PASS = config('FTP_PASS')
FTP_PATH = config('FTP_PATH')

# Diccionario para rastrear el servicio activo de cada usuario
active_service = {}

# Diccionario para rastrear usuarios esperando enviar resumen
waiting_for_summary = {}

# Estados de conversación
WAITING_SUMMARY = 1


# Función para conectar al FTP
def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp


# Función para verificar o crear una carpeta en FTP
def create_ftp_folder(create_folder):
    ftp = connect_ftp()
    ftp.cwd(FTP_PATH)  # Ir a la ruta base
    try:
        ftp.cwd(create_folder)  # Intentar entrar a la carpeta
    except ftplib.error_perm:
        ftp.mkd(create_folder)  # Si no existe, crearla
    ftp.quit()


# Función para subir archivos a la NAS usando FTP
def upload_a_ftp(local_name, remote_folder, remote_name):
    ftp = connect_ftp()
    ftp.cwd(f"{FTP_PATH}/{remote_folder}")  # Entrar a la carpeta específica
    with open(local_name, "rb") as file:
        ftp.storbinary(f"STOR {remote_name}", file)
    ftp.quit()


# Comando para asignar el número de servicio y crear la carpeta en FTP
async def confirmButton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('confirm_'):
        service_id = query.data.split('_')[1]
        context.user_data['service_id'] = service_id
        try:
            response = requests.get(f"{API_URL}/service/{service_id}/", timeout=10)
            response.raise_for_status()
            service = response.json()
            service['status'] = 1
            data = {
                "status": 1,
            }
            service_response = requests.patch(f"{API_URL}/service/{service['id']}/", data)
            service_response.raise_for_status()
            service = service_response.json()
            print(service)
            messageConfirm = createMsgFromJson(service)
            await send_confirm_msg(messageConfirm, GROUP_CHAT_ID)
            await set_service(update, context, service)
        except requests.exceptions.Timeout:
            logging.error("Request timed out")
            await query.message.reply_text("La solicitud a la API ha expirado. Inténtalo de nuevo más tarde.")
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP error occurred: {err}")
            if err.response.status_code == 404:
                await query.message.reply_text("No se encontró el servicio.")
            else:
                await query.message.reply_text("Ocurrió un error al consultar la API.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            await query.message.reply_text("Ocurrió un error inesperado.")

async def set_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service):
    chat_id = update.callback_query.message.chat_id
    service_number = service['service_number']
    client_name = service['client']['first_name']
    created_data = service['created_at'].split('T')[0]

    folder_name = f"{service_number}-{client_name}-{created_data}"
    print(folder_name)
    active_service[chat_id] = folder_name
    # Crear la carpeta en el FTP si no existe
    create_ftp_folder(folder_name)

    # Botón de finalizar servicio
    keyboard = [[InlineKeyboardButton("✅ Finalizar Servicio", callback_data=f"finalizar_{folder_name}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Enviar mensaje de confirmación
    await update.callback_query.message.reply_text(
        f"📂 Carpeta creada y servicio asignado: {folder_name}\nAhora puedes enviar fotos.",
        reply_markup=reply_markup
    )




# Manejo de fotos
async def manage_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in active_service:
        await update.message.reply_text("❌ No tienes un servicio activo.")
        return

    service_folder = active_service[chat_id]
    service_number = service_folder.split("-")[0]
    archive = await update.message.photo[-1].get_file()

    # Crear el directorio file_temp si no existe
    file_temp_dir = "file_temp"
    if not os.path.exists(file_temp_dir):
        os.makedirs(file_temp_dir)

    # Nombre del archivo
    image_filename = f"{update.message.message_id}.jpg"
    local_name = f"/tmp/{update.message.message_id}.jpg"
    remote_name = f"{update.message.message_id}.jpg"
    project_local_path = os.path.join(file_temp_dir, image_filename)

    try:
        # Descargar la imagen localmente
        await archive.download_to_drive(local_name)
        await archive.download_to_drive(project_local_path)
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        await update.message.reply_text(f"❌ Ocurrió un error al descargar la imagen {e}")
        return

    from django.core.files import File
    from asgiref.sync import sync_to_async

    try:
        service = await sync_to_async(Service.objects.get)(pk=service_number)

        with open(project_local_path, "rb") as f:
            django_file = File(f)
            # Crear ServiceImage de forma asíncrona
            service_image = await sync_to_async(ServiceImage.objects.create)(
                service=service,
                nas_url=f"{FTP_PATH}/{service_folder}"
            )
            # Guardar el archivo en el campo ImageField de forma asíncrona
            await sync_to_async(service_image.image.save)(image_filename, django_file)
            await sync_to_async(service_image.save)()
            os.remove(project_local_path)

    except Service.DoesNotExist:
        await update.message.reply_text("❌ No se encontró el servicio.")
        return
    except Exception as e:
        logging.error(f"Error saving image to database: {e}")
        await update.message.reply_text("❌ Ocurrió un error al guardar la imagen.")
        return


    # Subir a la carpeta del servicio en FTP
    try:
        upload_a_ftp(local_name, service_folder, remote_name)
        os.remove(local_name)
    except Exception as e:
        logging.error(f"Error uploading image to FTP: {e}")
        await update.message.reply_text(f"❌ Ocurrió un error al subir la imagen al servidor. {e}")
        return

    # Eliminar el archivo local después de subirlo

    keyboard = [[InlineKeyboardButton("✅ Finalizar Servicio", callback_data=f"finalizar_{service_number}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📸 Imagen guardada en /Telegram/Bot/{service_number}",
        reply_markup=reply_markup
    )


# Solicitar resumen antes de finalizar servicio
async def request_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    service_data = query.data.split("_")[1]
    folder_name = service_data
    service_number = service_data.split("-")[0]

    # Verificar que el usuario tenga el servicio asignado
    if chat_id not in active_service or active_service[chat_id].split("-")[0] != service_number:
        await query.message.reply_text("❌ No tienes este servicio asignado.")
        return

    # Guardar la información del servicio para cuando envíe el resumen
    waiting_for_summary[chat_id] = {
        'folder_name': folder_name,
        'service_number': service_number
    }

    await query.message.reply_text("📝 Envía el resumen del servicio:")

# Manejar el resumen del servicio
async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id

    # Verificar si el usuario está esperando enviar un resumen
    if chat_id not in waiting_for_summary:
        return  # No hacer nada si no está esperando resumen

    summary_text = update.message.text
    service_info = waiting_for_summary[chat_id]
    folder_name = service_info['folder_name']
    service_number = service_info['service_number']

    # Remover de la lista de espera
    del waiting_for_summary[chat_id]

    try:
        response = requests.get(f"{API_URL}/service/{service_number}")
        response.raise_for_status()
        service = response.json()

        if chat_id in active_service and active_service[chat_id].split("-")[0] == service_number:
            del active_service[chat_id]
            service['status'] = 2
            service['end_date'] = datetime.datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S.%f')
            data = {
                "status": 2,
                "end_date": service['end_date'],
                "summary": summary_text
            }
            service_response = requests.patch(f"{API_URL}/service/{service['id']}/", data)
            service_response.raise_for_status()
            service = service_response.json()
            print(service)
            messageConfirm = createMsgFromJson(service)
            await send_confirm_msg(messageConfirm, GROUP_CHAT_ID)
            await update.message.reply_text(f"✅ Servicio {folder_name} finalizado con resumen.")
        else:
            await update.message.reply_text("❌ No tienes este servicio asignado.")
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        await update.message.reply_text("Ocurrió un error al finalizar el servicio. Inténtalo de nuevo más tarde.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception: {e}")
        await update.message.reply_text("Ocurrió un error al comunicarse con la API. Inténtalo de nuevo más tarde.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text("Ocurrió un error inesperado. Inténtalo de nuevo más tarde.")

# Finalizar servicio (función original renombrada para mantener compatibilidad)
async def end_service_old(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    service_number = query.data.split("_")[1]
    folder_name = service_number
    service_number = service_number.split("-")[0]


    try:
        response = requests.get(f"{API_URL}/service/{service_number}")
        response.raise_for_status()
        service = response.json()

        if chat_id in active_service and active_service[chat_id].split("-")[0] == service_number:
            del active_service[chat_id]
            service['status'] = 2
            service['end_date'] = datetime.datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S.%f')
            data = {
                "status": 2,
                "end_date": service['end_date']
            }
            service_response = requests.patch(f"{API_URL}/service/{service['id']}/", data)
            service_response.raise_for_status()
            service = service_response.json()
            print(service)
            messageConfirm = createMsgFromJson(service)
            await send_confirm_msg(messageConfirm, GROUP_CHAT_ID)
            await query.message.reply_text(f"✅ Servicio {folder_name} finalizado.")
        else:
            await query.message.reply_text("❌ No tienes este servicio asignado.")
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        await query.message.reply_text("Ocurrió un error al finalizar el servicio. Inténtalo de nuevo más tarde.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception: {e}")
        await query.message.reply_text("Ocurrió un error al comunicarse con la API. Inténtalo de nuevo más tarde.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await query.message.reply_text("Ocurrió un error inesperado. Inténtalo de nuevo más tarde.")


# Comando de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        response = requests.get(f"{API_URL}/employee/?chat_id={chat_id}", timeout=10)
        response.raise_for_status()
        employee = response.json()
        await update.message.reply_text(f"Bienvenido de nuevo, {employee['first_name']}")
    except requests.exceptions.Timeout:
        logging.error("Request timed out")
        await update.message.reply_text("La solicitud a la API ha expirado. Inténtalo de nuevo más tarde.")
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            keyboard = [[KeyboardButton("Compartir número de teléfono", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text("Comparte tu número de teléfono", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Ocurrió un error al consultar la API.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await update.message.reply_text("Ocurrió un error inesperado.")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone_number = contact.phone_number[-10:]
    chat_id = update.effective_chat.id

    try:
        response = requests.get(f"{API_URL}/employee/?phone_number={phone_number}", timeout=10)
        response.raise_for_status()
        employee = response.json()
        employee['chat_id'] = chat_id
        update_response = requests.put(f"{API_URL}/employee/{employee['id']}/", json=employee, timeout=10)
        update_response.raise_for_status()
        await update.message.reply_text(f"Número de teléfono recibido, Bienvenido {employee['first_name']}")
    except requests.exceptions.Timeout:
        logging.error("Request timed out")
        await update.message.reply_text("La solicitud a la API ha expirado. Inténtalo de nuevo más tarde.")
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404:
            await update.message.reply_text("No se encontró persona autorizada con ese número de teléfono.")
        else:
            await update.message.reply_text("Ocurrió un error al consultar la API.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await update.message.reply_text("Ocurrió un error inesperado.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la cancelación de la conversación"""
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END


# Configurar el bot
def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(CallbackQueryHandler(confirmButton, pattern="confirm_.*"))
    app.add_handler(MessageHandler(filters.PHOTO, manage_photos))
    app.add_handler(CallbackQueryHandler(request_summary, pattern="finalizar_.*"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_summary))

    # Iniciar el bot
    print("🤖 Bot Iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
