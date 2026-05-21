from flask import Flask, request, jsonify, send_file
import telebot
import threading
import time

# ==========================
# CONFIG TELEGRAM
# ==========================

BOT_TOKEN = "8893106710:AAFwLqo_3TzZ1pkKnhwleG0JpUxLHAJ6d0o"

bot = telebot.TeleBot("8893106710:AAFwLqo_3TzZ1pkKnhwleG0JpUxLHAJ6d0o")

# ==========================
# FLASK
# ==========================

app = Flask(__name__)

sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "movement": "Esperando datos",
    "movement_level": 0,
    "alarm": "NORMAL",
    "wifi": "DESCONECTADO",
    "temp_min": 35,
    "temp_max": 38,
    "hum_min": 40,
    "hum_max": 60
}

# ==========================
# WEB DASHBOARD
# ==========================

@app.route("/")
def home():
    return send_file("index.html")


@app.route("/api/data")
def api_data():
    return jsonify(sensor_data)


@app.route("/update", methods=["POST"])
def update():

    global sensor_data

    sensor_data = request.json

    print("\nDatos recibidos:")
    print(sensor_data)

    return jsonify({
        "status": "ok"
    })


# ==========================
# COMANDOS TELEGRAM
# ==========================

@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        "🤖 Bot Monitor IoT Paciente\n\n"
        "Comandos disponibles:\n"
        "/temp\n"
        "/humedad\n"
        "/movimiento\n"
        "/umbrales\n"
        "/alarma\n"
        "/estado\n"
        "/wifi\n"
        "/help"
    )


@bot.message_handler(commands=['help'])
def help_command(message):

    bot.reply_to(
        message,
        "📌 Comandos disponibles:\n\n"
        "🌡 /temp\n"
        "💧 /humedad\n"
        "🧍 /movimiento\n"
        "⚙ /umbrales\n"
        "🚨 /alarma\n"
        "📶 /wifi\n"
        "📊 /estado"
    )


@bot.message_handler(commands=['temp'])
def temperature(message):

    bot.reply_to(
        message,
        f"🌡 Temperatura actual\n\n"
        f"La temperatura es "
        f"{sensor_data['temperature']} °C"
    )


@bot.message_handler(commands=['humedad'])
def humidity(message):

    bot.reply_to(
        message,
        f"💧 Humedad actual\n\n"
        f"La humedad es "
        f"{sensor_data['humidity']} %"
    )


@bot.message_handler(commands=['movimiento'])
def movement(message):

    bot.reply_to(
        message,
        f"🧍 Estado del paciente\n\n"
        f"{sensor_data['movement']}"
    )


@bot.message_handler(commands=['umbrales'])
def thresholds(message):

    bot.reply_to(
        message,
        f"⚙ Umbrales configurados\n\n"
        f"🌡 Temperatura:\n"
        f"Mín: {sensor_data['temp_min']}°C\n"
        f"Máx: {sensor_data['temp_max']}°C\n\n"
        f"💧 Humedad:\n"
        f"Mín: {sensor_data['hum_min']}%\n"
        f"Máx: {sensor_data['hum_max']}%"
    )


@bot.message_handler(commands=['alarma'])
def alarm(message):

    bot.reply_to(
        message,
        f"🚨 Estado de alarma\n\n"
        f"{sensor_data['alarm']}"
    )


@bot.message_handler(commands=['wifi'])
def wifi(message):

    bot.reply_to(
        message,
        f"📶 Estado WiFi\n\n"
        f"{sensor_data['wifi']}"
    )


@bot.message_handler(commands=['estado'])
def estado(message):

    bot.reply_to(
        message,
        f"📊 ESTADO GENERAL DEL PACIENTE\n\n"
        f"🌡 Temperatura: "
        f"{sensor_data['temperature']} °C\n"
        f"💧 Humedad: "
        f"{sensor_data['humidity']} %\n"
        f"🧍 Movimiento: "
        f"{sensor_data['movement']}\n"
        f"🚨 Alarma: "
        f"{sensor_data['alarm']}\n"
        f"📶 WiFi: "
        f"{sensor_data['wifi']}"
    )


# ==========================
# TELEGRAM THREAD
# ==========================

def run_bot():

    print("Bot Telegram iniciado...")
    bot.infinity_polling()


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    telegram_thread = threading.Thread(
        target=run_bot
    )

    telegram_thread.daemon = True
    telegram_thread.start()

    print("Servidor Flask iniciado...")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )