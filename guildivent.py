# Версия v.1.3 от 20.01.2024, 22:02
import os
import datetime
import time
import tkinter as tk
from tkinter import filedialog
import configparser
import pygetwindow
import keyboard
import threading
from PIL import Image, ImageTk
import re
from pystray import Icon, MenuItem as item

exit_flag = False

current_utc_time = datetime.datetime.now(datetime.timezone.utc)
current_time = (current_utc_time + datetime.timedelta(hours=3)).strftime("%H:%M:%S")

# Добавьте определение переменной previous_lines
previous_lines = set()

def close_window_after_1min(window):
    window.after(60000, window.quit)

def handle_choice(choice):
    if choice == "Участвую":
        game_window = pygetwindow.getWindowsWithTitle('Path of Exile')[0]
        game_window.activate()
        keyboard.send('enter')
        keyboard.write('%Участвую')
        keyboard.send('enter')
        root.after(1000, close_window)

    print(choice)

def close_window():
    root.destroy()

def show_choice_window(time_date, message):
    global root
    root = tk.Tk()
    root.attributes("-alpha", 1)
    root.title("Оповещение события")
    root.attributes('-topmost', True)

    main_frame = tk.Frame(root)
    main_frame.pack()

    label_date = tk.Label(main_frame, text=f"Дата и время: {time_date}", font=("Arial", 14))
    label_date.pack()

    # Используем регулярные выражения для извлечения информации из строки события
    match = re.search(r'\[(.*?)\] %(.+?): .*событие: (.+?)\..*требования: (.+?)\..*цена: (.+?)\.?', message)

    if match:
        author = match.group(2)
        requirements = match.group(4)
        price = match.group(5) if match.group(5) else "0"

        # Выделение важных моментов оповещения
        label_author = tk.Label(main_frame, text=f"НИК АВТОРА СОБЫТИЯ: {author}", font=("Arial", 24), padx=10, pady=10)
        label_author.configure(bg="red")
        label_author.pack()

        label_price = tk.Label(main_frame, text=f"ЦЕНА: {price}", font=("Arial", 33), padx=10, pady=10)
        label_price.configure(bg="green")
        label_price.pack()

        label_requirements = tk.Label(main_frame, text=f"ТРЕБОВАНИЯ: {requirements}", font=("Arial", 33), padx=10, pady=10)
        label_requirements.configure(bg="blue")
        label_requirements.pack()

    label_message = tk.Label(main_frame, text=f"ОПИСАНИЕ: {message}", font=("Arial", 24), wraplength=300)
    label_message.pack()

    button_frame = tk.Frame(main_frame)
    button_frame.pack()

    participate_button = tk.Button(button_frame, text="Участвую", command=lambda: handle_choice("Участвую"))
    participate_button.pack(side=tk.LEFT)

    decline_button = tk.Button(button_frame, text="Отказаться", command=root.destroy)
    decline_button.pack(side=tk.RIGHT)

    close_window_after_1min(root)
    root.bind("<Return>", lambda event: handle_choice("Участвую"))

    # Создаем значок в трее
    icon_thread = threading.Thread(target=create_and_run_tray_icon, args=(root,))
    icon_thread.start()

    # Устанавливаем положение окна в левый верхний угол
    root.geometry("+10+10")

    root.mainloop()

def on_exit_clicked(icon, item):
    global exit_flag
    icon.stop()
    root.quit()
    exit_flag = True

def home_folder(icon, item):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    os.startfile(current_directory)

def on_open_folder_clicked(icon, item):
    config = read_config_file()
    if 'FileSettings' in config and 'client_file_path' in config['FileSettings']:
        folder_path = os.path.dirname(config['FileSettings']['client_file_path'])
        os.startfile(folder_path)

def on_open_settings_clicked(icon, item):
    os.startfile('settingsg.ini')

def create_and_run_tray_icon(root_icon):
    icon = create_tray_icon()
    icon.run()

def create_tray_icon():
    print('Иконка')
    image_path = "cat.ico"  # Замените на путь к вашему изображению
    icon = Image.open(image_path)
    icon = icon.resize((30, 30), Image.BICUBIC)
    icon = Image.open(image_path).resize((30, 30), Image.BICUBIC)
    icon = Image.open(image_path).resize((30, 30), Image.BICUBIC)
    tk_icon = ImageTk.PhotoImage(icon)

    # Сохраните изображение в формате ICO
    icon_path = 'path_to_save_icon.ico'
    icon.save(icon_path, format='ICO')

    menu = (item('Выход', lambda icon, item: on_exit_clicked(icon, item)),
            item('Открыть папку Client.txt', lambda icon, item: on_open_folder_clicked(icon, item)),
            item('Открыть папку программы', lambda icon, item: home_folder(icon, item)),
            item('Открыть настройки', lambda icon, item: on_open_settings_clicked(icon, item)))

    icon_tray = Icon("name", icon, "Оповещение", menu)
    return icon_tray

def check_file_for_new_lines():
    global previous_lines
    config = read_config_file()

    target_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d")

    if 'FileSettings' not in config:
        root = tk.Tk()
        root.withdraw()
        client_file_path = filedialog.askopenfilename(title="Выберите файл в папке Path of Exile\\logs\\Client.txt")
        if client_file_path:
            config['FileSettings'] = {}
            config['FileSettings']['client_file_path'] = client_file_path
            with open('settingsg.ini', 'w') as configfile:
                config.write(configfile)
            root.quit()
        else:
            root.quit()
            print("Файл не выбран. Завершение скрипта.")
            import sys
            sys.exit()

    else:
        i = 0
        try:
            client_file_path = config['FileSettings']['client_file_path']
            with open(client_file_path, 'r', encoding='utf-8') as file:
                lines = set(file.readlines())
                new_lines = lines.difference(previous_lines)
                for line in new_lines:
                    i += 1
                    if '%' in line and '/сбор/' in line:
                        log_parts = line.split(' ')
                        log_time = log_parts[1]
                        if log_time >= current_time:
                            message = line.split('%')[1].strip()
                            log_datetime = f"{target_date} {log_time}"
                            show_choice_window(log_datetime, message)
                            break
                previous_lines = lines.copy()
        except Exception as e:
            print(f"Произошла ошибка при чтении файла: {e}")

def read_config_file():
    config = configparser.ConfigParser()
    config.read('settingsg.ini')
    return config

# Основной цикл
while not exit_flag:
    check_file_for_new_lines()
    time.sleep(1)