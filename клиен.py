import sys
import os
import colorsys
import socket
import threading
from pathlib import Path
from PIL import Image
import customtkinter as ctk

# --- НАЛАШТУВАННЯ ШЛЯХІВ ДО TKINTER/TCL ---
# Фікс для того, щоб графічна бібліотека Tkinter коректно знаходила системні файли на різних комп'ютерах
base_python = Path(sys.base_prefix)
os.environ["TCL_LIBRARY"] = str(base_python / "tcl" / "tcl8.6")
os.environ["TK_LIBRARY"] = str(base_python / "tcl" / "tk8.6")


# =========================================================================
# ВІКНО АВТОРИЗАЦІЇ (ВХОДУ)
# =========================================================================
auth_app = ctk.CTk()
auth_app.geometry("400x380")
auth_app.title("LogiTalk — Підключення")
ctk.set_appearance_mode("Dark") # Встановлюємо темну тему оформлення

# Поле введення IP-адреси сервера
ctk.CTkLabel(auth_app, text="IP сервера:", font=("Arial", 14, "bold")).pack(pady=(15, 5))
server_entry = ctk.CTkEntry(auth_app, width=280, height=35, fg_color="#2b2b2b", text_color="#ffffff")
server_entry.insert(0, "127.0.0.1") # Значення за замовчуванням (локальний комп'ютер)
server_entry.pack()

# Поле введення порту сервера
ctk.CTkLabel(auth_app, text="Порт сервера:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
port_entry = ctk.CTkEntry(auth_app, width=280, height=35, fg_color="#2b2b2b", text_color="#ffffff")
port_entry.insert(0, "5000") # Стандартний порт для підключення
port_entry.pack()

# Поле введення імені водія
ctk.CTkLabel(auth_app, text="Ім'я або ID водія:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
user_entry = ctk.CTkEntry(auth_app, width=280, height=35, fg_color="#2b2b2b", text_color="#ffffff")
user_entry.pack()

config_data = {}

def start_app():
    """Зберігає введені дані та закриває вікно авторизації, якщо ім'я заповнене"""
    config_data["ip"] = server_entry.get()
    config_data["port"] = int(port_entry.get())
    config_data["name"] = user_entry.get()
    if config_data["name"]:
        auth_app.destroy()

# Кнопка запуску підключення
ctk.CTkButton(auth_app, width=160, height=40, text="Підключитися", fg_color="#cc0000", hover_color="#ff1a1a", command=start_app).pack(pady=20)
auth_app.mainloop()

# Якщо користувач не ввів ім'я і просто закрив вікно — зупиняємо програму
if not config_data.get("name"):
    sys.exit()


# =========================================================================
# МЕРЕЖЕВЕ ПІДКЛЮЧЕННЯ (SOCKETS)
# =========================================================================
driver_name = config_data["name"]
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Намагаємося підключитися до сервера за вказаними IP та портом
    client_socket.connect((config_data["ip"], config_data["port"]))
except Exception as e:
    print(f"Помилка підключення: {e}")


# =========================================================================
# ГОЛОВНЕ ВІКНО ДОДАТКУ (ГАРАЖ / ЧАТ)
# =========================================================================
app = ctk.CTk()
app.geometry("750x600")
app.title(f"LogiTalk — Гараж (Водій: {driver_name})")
ctk.set_appearance_mode("Dark")

rainbow_running = False
hue = 0.0

def load_avatar(filename):
    """Функція для безпечного завантаження зображення аватарки"""
    if os.path.exists(filename):
        return ctk.CTkImage(Image.open(filename), size=(45, 45))
    return None

# Завантажуємо іконки машини та мотоцикла
car_img = load_avatar("car.png")
moto_img = load_avatar("moto.png")
selected_avatar = "car" # Аватар за замовчуванням

def animate_rainbow():
    """Створює ефект переливання кольорів для режиму 'Діагностика' (кольори веселки)"""
    global hue, rainbow_running
    if rainbow_running:
        hue = (hue + 0.01) % 1.0
        r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        btn.configure(fg_color=hex_color, hover_color=hex_color)
        app.after(50, animate_rainbow) # Повторювати кожні 50 мілісекунд

def set_mode(mode):
    """Змінює режими авто ('Спорт', 'Еко', 'Діагностика') та налаштовує інтерфейс"""
    global rainbow_running
    if mode == "Спорт":
        rainbow_running = False
        btn.configure(fg_color="#cc0000", hover_color="#ff1a1a")
        add_system_msg("Система: Активовано режим — Спорт 🏎️")
    elif mode == "Еко":
        rainbow_running = False
        btn.configure(fg_color="#00aa44", hover_color="#00cc55")
        add_system_msg("Система: Активовано режим — Еко 🏙️")
    elif mode == "Діагностика":
        if not rainbow_running:
            rainbow_running = True
            animate_rainbow()
        add_system_msg("Система: Активовано режим — Діагностика 🔧")


# =========================================================================
# БОКОВА ПАНЕЛЬ (SIDEBAR)
# =========================================================================
sidebar = ctk.CTkFrame(app, width=180, fg_color="#1f1f1f")
sidebar.pack(side="left", fill="y", padx=0, pady=0)

# Кнопки вибору режимів
ctk.CTkLabel(sidebar, text="Режими авто", font=("Arial", 14, "bold"), text_color="#ffffff").pack(pady=(20, 10))
ctk.CTkButton(sidebar, text="🏎️ Спорт", width=140, fg_color="#333333", hover_color="#cc0000", command=lambda: set_mode("Спорт")).pack(pady=5)
ctk.CTkButton(sidebar, text="🏙️ Еко", width=140, fg_color="#333333", hover_color="#00aa44", command=lambda: set_mode("Еко")).pack(pady=5)
ctk.CTkButton(sidebar, text="🔧 Діагностика", width=140, fg_color="#333333", hover_color="#8800cc", command=lambda: set_mode("Діагностика")).pack(pady=5)

ctk.CTkLabel(sidebar, text="Вибір аватарки", font=("Arial", 14, "bold"), text_color="#ffffff").pack(pady=(20, 10))

def select_avatar(av_type):
    """Зберігає обраний тип аватара (машина чи мотоцикл)"""
    global selected_avatar
    selected_avatar = av_type
    add_system_msg(f"Система: Вибрано аватарку — {av_type.upper()}")

# Кнопки вибору аватарок
ctk.CTkButton(sidebar, text="🏎️ Машина", width=140, fg_color="#2b2b2b", hover_color="#555555", command=lambda: select_avatar("car")).pack(pady=5)
ctk.CTkButton(sidebar, text="🏍️ Мотоцикл", width=140, fg_color="#2b2b2b", hover_color="#555555", command=lambda: select_avatar("moto")).pack(pady=5)


# =========================================================================
# ОБЛАСТЬ ЧАТУ ТА ПОВІДОМЛЕНЬ
# =========================================================================
chat_frame = ctk.CTkFrame(app, fg_color="transparent")
chat_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

# Скрол-контейнер для повідомлень (щоб можна було гортати історію)
messages_frame = ctk.CTkScrollableFrame(chat_frame, fg_color="#1a1a1a", width=520, height=450)
messages_frame.pack(pady=5, fill="both", expand=True)

def add_system_msg(text):
    """Виводить системні повідомлення (наприклад, про зміну режиму)"""
    msg_card = ctk.CTkFrame(messages_frame, fg_color="#262626", corner_radius=10)
    msg_card.pack(fill="x", pady=4, padx=5)
    ctk.CTkLabel(msg_card, text=text, font=("Arial", 12), text_color="#00ffcc", justify="left", wraplength=450).pack(side="left", padx=10, pady=5)

def add_msg(sender, text, avatar_type="car"):
    """Формує та виводить картку звичайного повідомлення від користувача в чаті"""
    msg_card = ctk.CTkFrame(
        messages_frame,
        fg_color="#222222",
        corner_radius=12,
        border_width=2,
        border_color="#ff1a1a" if avatar_type == "car" else "#00ffcc" # Колір рамки залежить від обраного транспортного засобу
    )
    msg_card.pack(fill="x", pady=5, padx=5)

    img = car_img if avatar_type == "car" else moto_img
    icon_text = "🏎️" if avatar_type == "car" else "🏍️"

    # Фрейм для аватарки
    avatar_frame = ctk.CTkFrame(msg_card, width=50, height=50, corner_radius=25, fg_color="#1a1a1a")
    avatar_frame.pack(side="left", padx=8, pady=8)
    avatar_frame.pack_propagate(False)

    if img:
        ctk.CTkLabel(avatar_frame, image=img, text="").pack(expand=True)
    else:
        ctk.CTkLabel(avatar_frame, text=icon_text, font=("Arial", 20)).pack(expand=True)

    # Текстова частина повідомлення (відправник + текст)
    content_frame = ctk.CTkFrame(msg_card, fg_color="transparent")
    content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    ctk.CTkLabel(content_frame, text=sender, font=("Arial", 11, "bold"), text_color="#888888", anchor="w").pack(fill="x")
    ctk.CTkLabel(content_frame, text=text, font=("Arial", 13), text_color="#ffffff", anchor="w", justify="left", wraplength=380).pack(fill="x")

# Вітальне системне повідомлення при вході
add_system_msg(f"Система: Водій {driver_name} підключений до мережі.")

def receive_messages():
    """Фонова функція (потік), яка постійно слухає сервер і приймає повідомлення від інших користувачів"""
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if data:
                if ":" in data:
                    sender, msg = data.split(":", 1)
                    add_msg(sender.strip(), msg.strip())
                else:
                    add_system_msg(data)
            else:
                break
        except:
            break

# Запускаємо прийом повідомлень у фоновому потоці, щоб не зависав інтерфейс
threading.Thread(target=receive_messages, daemon=True).start()


# =========================================================================
# НИЖНЯ ПАНЕЛЬ (ВВЕДЕННЯ ТА ВІДПРАВКА ПОВІДОМЛЕНЬ)
# =========================================================================
bottom_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
bottom_frame.pack(fill="x", pady=5)

# Поле введення повідомлення
entry = ctk.CTkEntry(bottom_frame, width=380, height=40, placeholder_text="Введіть команду або повідомлення...", fg_color="#2b2b2b", text_color="#ffffff")
entry.pack(side="left", padx=5)

def send():
    """Відправляє введений текст на сервер та додає його у свій локальний чат"""
    msg = entry.get()
    if msg:
        add_msg(driver_name, msg, selected_avatar)
        try:
            client_socket.send(f"{driver_name}: {msg}".encode("utf-8"))
        except:
            add_system_msg("Система: Помилка надсилання на сервер!")
        entry.delete(0, "end") # Очищуємо поле введення

# Кнопка надсилання
btn = ctk.CTkButton(bottom_frame, width=120, height=40, text="🏎️ Надіслати", fg_color="#cc0000", hover_color="#ff1a1a", text_color="#ffffff", font=("Arial", 13, "bold"), command=send)
btn.pack(side="right", padx=5)

# Запуск головного циклу вікна додатку
app.mainloop()