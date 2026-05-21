from machine import Pin, PWM, I2C
import network
import dht
import time
import math
import urequests
import struct
import gc

# CONFIGURACION WIFI
WIFI_SSID = "VALENTINA2.4"
WIFI_PASSWORD = "Valentina1526"

# SERVIDOR PC
PC_IP = "192.168.0.6"
PC_PORT = 5000

# TELEGRAM
BOT_TOKEN = "8893106710:AAFwLqo_3TzZ1pkKnhwleG0JpUxLHAJ6d0o"
CHAT_ID = "8283465180"

# UMBRALES
TEMP_MIN = 35
TEMP_MAX = 38

HUM_MIN = 40
HUM_MAX = 60

# PINES
DHT_PIN = 4
BUZZER_PIN = 18
PANIC_PIN = 19
SDA_PIN = 21
SCL_PIN = 22

# HARDWARE
sensor = dht.DHT22(
    Pin(DHT_PIN)
)

i2c = I2C(
    0,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=100000
)

buzzer = PWM(
    Pin(BUZZER_PIN)
)

buzzer.duty(0)

panic_button = Pin(
    PANIC_PIN,
    Pin.IN,
    Pin.PULL_UP
)

# WIFI
wifi = network.WLAN(
    network.STA_IF
)

wifi.active(True)


def connect_wifi():

    if wifi.isconnected():
        return True

    print("\nConectando WiFi...")

    try:
        wifi.disconnect()
    except:
        pass

    time.sleep(1)

    wifi.connect(
        WIFI_SSID,
        WIFI_PASSWORD
    )

    timeout = 20

    while (
        not wifi.isconnected()
        and timeout > 0
    ):

        print(".", end="")

        time.sleep(1)

        timeout -= 1

    if wifi.isconnected():

        print("\nWiFi conectado")
        print(wifi.ifconfig())

        return True

    print(
        "\nNo fue posible conectar WiFi"
    )

    return False

# MPU6050
MPU_ADDR = 0x68

try:

    i2c.writeto_mem(
        MPU_ADDR,
        0x6B,
        b'\x00'
    )

    print(
        "MPU6050 conectado"
    )

except Exception as e:

    print(
        "Error MPU6050:",
        e
    )


def read_word(reg):

    data = i2c.readfrom_mem(
        MPU_ADDR,
        reg,
        2
    )

    return struct.unpack(
        ">h",
        data
    )[0]


def get_acceleration():

    try:

        ax = (
            read_word(0x3B)
            / 16384
        )

        ay = (
            read_word(0x3D)
            / 16384
        )

        az = (
            read_word(0x3F)
            / 16384
        )

        magnitude = math.sqrt(
            ax**2 +
            ay**2 +
            az**2
        )

        return magnitude

    except Exception as e:

        print(
            "Error MPU:",
            e
        )

        return 1.0


def detect_movement():

    a = get_acceleration()

    if 0.95 <= a <= 1.05:
        return "REPOSO", 1

    elif a <= 1.30:
        return (
            "MOVIMIENTO LEVE",
            2
        )

    elif a <= 2.2:
        return (
            "MOVIMIENTO MODERADO",
            3
        )

    else:
        return (
            "MOVIMIENTO BRUSCO",
            4
        )

# BUZZER
def beep(freq, duration):

    buzzer.freq(freq)

    buzzer.duty(512)

    time.sleep(duration)

    buzzer.duty(0)


def alarm_temp():

    beep(1000, 0.15)

    time.sleep(0.08)

    beep(1000, 0.15)


def alarm_humidity():

    for _ in range(3):

        beep(700, 0.08)

        time.sleep(0.08)


def alarm_fall():

    for _ in range(6):

        beep(1500, 0.08)

        time.sleep(0.04)


def alarm_panic():

    for _ in range(10):

        beep(2000, 0.07)

        time.sleep(0.03)

# TELEGRAM
def send_telegram(message):

    if not wifi.isconnected():
        return

    response = None

    try:

        url = (
            "https://api.telegram.org/bot"
            + BOT_TOKEN
            + "/sendMessage"
        )

        payload = (
            "chat_id="
            + str(CHAT_ID)
            + "&text="
            + str(message)
        )

        headers = {
            "Content-Type":
            "application/x-www-form-urlencoded"
        }

        response = (
            urequests.post(
                url,
                data=payload,
                headers=headers
            )
        )

        print(
            "Telegram:",
            response.status_code
        )

        response.close()

    except Exception as e:

        print(
            "ERROR TELEGRAM:"
        )

        print(e)

    gc.collect()

# SERVIDOR FLASK
def send_to_server(data):

    if not wifi.isconnected():
        return

    response = None

    try:

        url = (
            "http://"
            + PC_IP
            + ":"
            + str(PC_PORT)
            + "/update"
        )

        response = (
            urequests.post(
                url,
                json=data
            )
        )

        response.close()

    except Exception as e:

        print(
            "Servidor desconectado:",
            e
        )

    gc.collect()

# INICIO
connect_wifi()

if wifi.isconnected():

    ip_esp32 = (
        wifi.ifconfig()[0]
    )

    send_telegram(
        "✅ ESP32 conectado\nIP: "
        + ip_esp32
    )

print("\nSistema iniciado")

# VARIABLES
last_alert = ""

last_dht_read = 0

temperature = 0
humidity = 0

# LOOP PRINCIPAL
while True:

    try:

        # WIFI RECONNECT
        if not wifi.isconnected():

            print(
                "\nWiFi perdido"
            )

            connect_wifi()

        # DHT22
        current_time = (
            time.time()
        )

        if (
            current_time
            - last_dht_read
            >= 2
        ):

            try:

                sensor.measure()

                temperature = (
                    sensor.temperature()
                )

                humidity = (
                    sensor.humidity()
                )

                last_dht_read = (
                    current_time
                )

            except Exception as e:

                print(
                    "Error DHT:",
                    e
                )

        # MOVIMIENTO
        movement, movement_level = (
            detect_movement()
        )

        wifi_state = (
            "CONECTADO"
            if wifi.isconnected()
            else "DESCONECTADO"
        )

        alarm = "NORMAL"

        # TEMPERATURA
        if temperature > TEMP_MAX:

            alarm = "PELIGRO"

            if (
                last_alert
                != "temp_high"
            ):

                alarm_temp()

                send_telegram(
                    "🌡️ TEMPERATURA ALTA\n"
                    + str(temperature)
                    + " °C"
                )

                last_alert = (
                    "temp_high"
                )

        elif temperature < TEMP_MIN:

            alarm = "PELIGRO"

            if (
                last_alert
                != "temp_low"
            ):

                alarm_temp()

                send_telegram(
                    "🥶 TEMPERATURA BAJA\n"
                    + str(temperature)
                    + " °C"
                )

                last_alert = (
                    "temp_low"
                )

        # HUMEDAD
        if (
            humidity > HUM_MAX
            or humidity < HUM_MIN
        ):

            alarm = "PELIGRO"

            if (
                last_alert
                != "humidity"
            ):

                alarm_humidity()

                send_telegram(
                    "💧 ALERTA HUMEDAD\n"
                    + str(humidity)
                    + "%"
                )

                last_alert = (
                    "humidity"
                )

        # POSIBLE CAIDA
        if (
            movement
            == "MOVIMIENTO BRUSCO"
        ):

            alarm = "CRITICO"

            if (
                last_alert
                != "fall"
            ):

                alarm_fall()

                send_telegram(
                    "🚨 POSIBLE CAÍDA DETECTADA"
                )

                last_alert = (
                    "fall"
                )

        # BOTON PANICO

        if (
            panic_button.value()
            == 0
        ):

            alarm = "CRITICO"

            if (
                last_alert
                != "panic"
            ):

                alarm_panic()

                send_telegram(
                    "🆘 BOTÓN DE PÁNICO ACTIVADO"
                )

                last_alert = (
                    "panic"
                )

        # RESET ALERTAS
        if alarm == "NORMAL":

            last_alert = ""

        # DASHBOARD
        payload = {

            "temperature":
            temperature,

            "humidity":
            humidity,

            "movement":
            movement,

            "movement_level":
            movement_level,

            "alarm":
            alarm,

            "wifi":
            wifi_state,

            "temp_min":
            TEMP_MIN,

            "temp_max":
            TEMP_MAX,

            "hum_min":
            HUM_MIN,

            "hum_max":
            HUM_MAX
        }

        send_to_server(
            payload
        )

        print(payload)

    except Exception as e:

        print(
            "ERROR GENERAL:"
        )

        print(e)

    gc.collect()

    # VELOCIDAD
    time.sleep(0.25)
