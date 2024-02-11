#Версия 1.5 от 05.02.2024, 20:30
from PyQt5 import QtWidgets, QtGui, QtCore
import sys, time, os
import requests
from bs4 import BeautifulSoup as bs
import string
from datetime import datetime, timedelta
from pathlib import Path
from pynput import mouse
import keyboard
import pyperclip
import webbrowser
import io
import win32gui
import pyautogui
from PyQt5.QtCore import QTimer

#Постоянные
Clean = ['\n', 'Глава', 'Офицер', 'Член', 'Новобранец', 'Участники', '[', ']']
double_click_interval = 0.3
last_click_time = time.time()
auto_refresh_interval = 60 * 60
current_timer_value = auto_refresh_interval
auto_refresh_timer = QTimer()
Login = ""

#Обновление таймера
def update_timer():
    global current_timer_value
    current_timer_value -= 1
    if current_timer_value <= 0:
        window.showNormal()
        DataRefresh()
        current_timer_value = auto_refresh_interval
        window.showMinimized()
    else:
        # Обновление отображения времени в интерфейсе, если необходимо
        label_timer.setText(f'Осталось времени: {current_timer_value} секунд')

#Сохранение SSID
def SavePOESESSID():
	SSID = POESESSIDline.text()
	f = open('Settings.ini', 'w', encoding= 'utf-8')
	f.write(SSID)
	f.close()
	window.close()

#Загрузка БД гильдии
def GuildMembers():
	if os.path.exists('GuildData.txt'):
		GuildMember = open ('GuildData.txt', 'r', encoding='utf-8')
		GuildMember = GuildMember.readlines()
		GuildMember = [line.rstrip() for line in GuildMember]
		return GuildMember
	else:
		GuildMember = (['Отсутствуют данные. Обновите базу данных.'])
		return GuildMember
GuildMember = GuildMembers()

#Загрузка ливнувших из гильдии
def LeftMembers():
	if os.path.exists('LeftMember.txt'):
		LeftMember = open ('LeftMember.txt', 'r', encoding='utf-8')
		LeftMember = LeftMember.readlines()
		LeftMember = [line.rstrip() for line in LeftMember]
		return LeftMember
	else:
		LeftMember = (['Гильдию никто не покидал.'])
		return LeftMember
LeftMember = LeftMembers()

#Загрузка вступивших в гильдию
def NewMembers():
	if os.path.exists('NewMember.txt'):
		NewMember = open ('NewMember.txt', 'r', encoding='utf-8')
		NewMember = NewMember.readlines()
		NewMember = [line.rstrip() for line in NewMember]
		return NewMember
	else:
		NewMember = (['В гильдию никто не вступал.'])
		return NewMember
NewMember = NewMembers()

def DataRefresh():
    btnGuildStats.setVisible(False)
    window.repaint()
    PlayerName.clear()
    LeftGuild.clear()
    NewGuild.clear()

    # Отправляем новый запрос
    response = requests.get('https://ru.pathofexile.com/guild/profile/463983', cookies=cookies, headers=headers)

    if response.status_code == 200:
        # Формируем новый список игроков
        soup = bs(response.text, 'html.parser')
        Name = soup.find('div', 'members').text
        Name = Name.split()
        Data = [i for i in Name if i not in Clean]

        # Создаем новую базу данных гильдии
        with open('GuildDataNew.txt', 'w', encoding="utf-8") as f:
            for element in Data:
                f.write(element)
                f.write('\n')

        print('Создана свежая база данных гильдии. Начинаю сравнение.')

		#Подгрузка БД
		

        # Загружаем базы для сравнения
        if os.path.exists('GuildData.txt'):
            OldData = open ('GuildData.txt', 'r', encoding='utf-8')
            OldData = OldData.readlines()
            OldData = [line.rstrip() for line in OldData]
            print('Data zagruz')
        else:
            print('No data!')
        NewData = Data

        # Проверка вступивших
        for i in NewData:
            if i not in OldData:
                file = open("NewMember.txt", "a", encoding="utf-8")
                datanow = str(datetime.now())
                file.write(datanow[0:19] + ' ' + i + ' вступил.' + '\n')
                file.close()

        # Проверка ушедших
        for i in OldData:
            if i not in NewData:
                LeftMemberGuild = LeftInfo(i)
                file = open("LeftMember.txt", "a", encoding="utf-8")
                datanow = str(datetime.now())
                file.write(datanow[0:19] + ' ' + i + ' покинул, ' + LeftMemberGuild + '\n')
                file.close()

        # Запись нового списка игроков
        with open('GuildData.txt', 'w', encoding="utf-8") as f:
            for element in Data:
                f.write(element)
                f.write('\n')

        # Удаляем временный файл
        os.remove('GuildDataNew.txt')

# Загружаем данные для интерфейса
    PlayerName.addItems(Data)
    LeftGuild.addItems(LeftMembers())
    NewGuild.addItems(NewMembers())
    btnGuildStats.setVisible(True)

#Подсветка игроков вступивших в гильду и покинувших её.
    i = 1
    Check = True
    for i in range (1, 11):
        if Check == True:
            LastLeft = LeftGuild.item(LeftGuild.count() - i).text()
            LastLeft = LastLeft.split()
            DateofLeft = LastLeft[0] + ' ' + LastLeft[1]
            DateofLeft = datetime.strptime(DateofLeft, '%Y-%m-%d %H:%M:%S')
            DateNow = datetime.now()
            Time_diff = DateNow - DateofLeft
            item_color = LeftGuild.item(LeftGuild.count() - i)
            if Time_diff < timedelta(minutes = 10):
                print ('Последний игрок вышел за последние 10 минут')
                item_color.setBackground(QtGui.QColor('black'))
                item_color.setForeground(QtGui.QColor('white'))
            else:
                print('Больше вышедших игроков нет.')
                item_color.setBackground(QtGui.QColor(255, 255, 255, 0))
                item_color.setForeground(QtGui.QColor('black'))
                Check = False

    i = 1
    Check = True
    for i in range (1, 11):
        if Check == True:
            LastJoin = NewGuild.item(NewGuild.count() - i).text()
            LastJoin = LastJoin.split()
            DateofJoin = LastJoin[0] + ' ' + LastJoin[1]
            DateofJoin = datetime.strptime(DateofJoin, '%Y-%m-%d %H:%M:%S')
            DateNow = datetime.now()
            Time_diff = DateNow - DateofJoin
            item_color = NewGuild.item(NewGuild.count() - i)
            if Time_diff < timedelta(minutes = 10):
                print ('Новый игрок присоединился к гильдии за последние 10 минут')
                item_color.setBackground(QtGui.QColor('yellow'))
            else:
                print('Новых игроков нет.')
                item_color.setBackground(QtGui.QColor(255, 255, 255, 0))
                Check = False
    if chkAutoRefresh.isChecked():
        chkAutoRefresh.setChecked(False)
        chkAutoRefresh.setChecked(True)


# Интервал автообновления в секундах (60 минут = 60 * 60 секунд)
auto_refresh_interval = 60 * 60

# Флаг автообновления (изначально установлен в False)
auto_refresh_enabled = False

# Функция для автоматического обновления данных
def auto_refresh_data():
    if auto_refresh_enabled:
        if DataRefresh():
            # Планируем следующее автообновление через auto_refresh_interval секунд
            QtCore.QTimer.singleShot(auto_refresh_interval * 1000, auto_refresh_data)

#Копирование строки мышкой
def on_click(x, y, button, pressed):
    global last_click_time
    active_window = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(active_window)

    if pressed == False and window_title == 'Статистика по гильдии':
        # Проверяем, что клик произошел в пределах окна
        window_rect = win32gui.GetWindowRect(active_window)
        if x >= window_rect[0] and x <= window_rect[2] and y >= window_rect[1] and y <= window_rect[3]:
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.001)
            Name = pyperclip.paste()
            count = Name.count(' ')
            if count > 2:
                Name = Name.split()
                Name = Name[2]
                pyperclip.copy(Name)

            current_time = time.time()
            if (current_time - last_click_time) < double_click_interval:
                web(Name)

            last_click_time = current_time

#Открытие вебстранички
def web(Name):
	Page = 'https://ru.pathofexile.com/account/view-profile/' + Name
	webbrowser.open(Page)

#Контроль в какую гильдию ушёл человек
def LeftInfo(Name):
	Page = 'https://ru.pathofexile.com/account/view-profile/' + Name[:-1]
	response = requests.get(Page, cookies=cookies, headers=headers)
	soup = bs(response.text, 'html.parser')

	status_element = soup.find('div', 'layoutBox1 layoutBoxFull defaultTheme')

	if status_element is None:
		LeftMemberGuild = 'аккаунт не существует.'
	else:
		Status = status_element.text.split('\n')

		if Status[2] == 'Профиль не найден':
			LeftMemberGuild = 'аккаунт не существует.'
		else:
			profile_box_element = soup.find('div', 'profile-box profile')

			if profile_box_element is None:
				LeftMemberGuild = 'информация о профиле не найдена.'
			else:
				Info = profile_box_element.text.split('\n')
				LeftMemberGuild = 'новая гильдия: ' + Info[3]
	return LeftMemberGuild

listener = mouse.Listener(on_click=on_click)
listener.start()

#Проверка Settings
if os.path.exists('Settings.ini'):
	f = open('Settings.ini')
	POESESSID = f.readlines()
	f.close()
	print(POESESSID)
else:
	app = QtWidgets.QApplication(sys.argv)
	window = QtWidgets.QWidget()
	window.setWindowTitle ('Ввод POESESSID при первом запуске')
	window.resize(300, 70)
	lable1 = QtWidgets.QLabel('<center>Зафиксирован первый запуск программы, прошу указать POESESSID:</center>')
	POESESSIDline = QtWidgets.QLineEdit()
	POESESSIDSaveBtn = QtWidgets.QPushButton('&Сохранить POESESSID')
	gird = QtWidgets.QGridLayout()
	gird.addWidget(lable1, 0, 0)
	gird.addWidget(POESESSIDline, 1, 0)
	gird.addWidget(POESESSIDSaveBtn, 2, 0)
	window.setLayout(gird)
	POESESSIDSaveBtn.clicked.connect(SavePOESESSID)
	window.show()
	sys.exit(app.exec_())
	DataRefresh()

#Check SSID
POESESSID = str(POESESSID)

cookies = {
    'POESESSID': POESESSID[2:-2]
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
}
print('До респаунса')
response = requests.get('https://ru.pathofexile.com/guild/profile/463983', cookies=cookies, headers=headers)
print('После респаунса')
soup = bs(response.text,'html.parser').text
if 'Войти' in soup:
	app = QtWidgets.QApplication(sys.argv)
	window = QtWidgets.QWidget()
	window.setWindowTitle ('Замена устаревшего POESESSID')
	window.resize(300, 70)
	lable1 = QtWidgets.QLabel('<center>Ваш POESESSID устарел, введите новый:</center>')
	POESESSIDline = QtWidgets.QLineEdit()
	POESESSIDSaveBtn = QtWidgets.QPushButton('&Сохранить POESESSID')
	gird = QtWidgets.QGridLayout()
	gird.addWidget(lable1, 0, 0)
	gird.addWidget(POESESSIDline, 1, 0)
	gird.addWidget(POESESSIDSaveBtn, 2, 0)
	window.setLayout(gird)
	POESESSIDSaveBtn.clicked.connect(SavePOESESSID)
	window.show()
	sys.exit(app.exec_())
else:
	Login = True

#Check SSID
print('Проверил ссид')

#Создание основной базы данных гильдии
if Login == True and os.path.exists('GuildData.txt') == False:
	Data = []
	soup = bs(response.text,'html.parser')
	GuildMembersData = soup.find('div', 'members').text
	GuildMembersData = GuildMembersData.split()
	for i in GuildMembersData:
		if i in Clean:
			continue
		else:
			Data.append(i)
	f = open ('GuildData.txt', 'w', encoding="utf-8") 
	for element in Data:
		f.write(element)
		f.write('\n')
	f.close()
	f = open ('GuildData.txt', 'r', encoding="utf-8")
	GuildMember = f.readlines()
	GuildMember = [line.rstrip() for line in GuildMember]
	f.close()
	print('Создание базы гильдии завершено.')

#Создание текущей базы данных гильдии
soup = bs(response.text,'html.parser')
Name = soup.find('div', 'members').text
Name = Name.split()
Data = []
for i in Name:
		if i in Clean:
			continue
		else:
			Data.append(i)
if response.status_code == 200:#Создание новой базы данных
	f = open ('GuildDataNew.txt', 'w', encoding="utf-8") 
	for element in Data:
		f.write(element)
		f.write('\n')
	f.close()
	print('Создана свежая база данных гильдии. Начинаю сравнение.')

#Загрузка баз для сравнения
if os.path.exists('GuildData.txt') == True and os.path.exists('GuildDataNew.txt') == True:
	OldData = []
	NewData = []
	Old = open('GuildData.txt', 'r', encoding= 'utf-8')
	for i in Old:
		if i != '\n':
			OldData.append (i)
		else:
			continue
	New = open('GuildDataNew.txt', 'r', encoding= 'utf-8')
	for n in New:
		if n != '\n':
			NewData.append (n)
		else:
			continue
	Old.close()
	New.close()

#Проверка вступивших
#Check = 0
for i in NewData:
	if i in OldData:
		continue
	else:
		print(i)
		print(type(i))
		file = open("NewMember.txt", "a", encoding="utf-8")
		datanow = str(datetime.now())
		file.write(datanow[0:19] + ' ' + i[:-1] + ' вступил.' + '\n')
		file.close()

#Проверка ушедших
for i in OldData:
	if i in NewData:
		continue
	else:
		LeftMemberGuild = LeftInfo(i)
		file = open("LeftMember.txt", "a", encoding="utf-8")
		datanow = str(datetime.now())
		file.write(datanow[0:19] + ' ' + i[:-1] + ' покинул, ' + LeftMemberGuild + '\n')
		file.close()

#Запись нового списка игроков
f = open ('GuildData.txt', 'w', encoding="utf-8")
for element in Data:
		f.write(element)
		f.write('\n')
f.close()
os.remove('GuildDataNew.txt')

# Добавление обработчика событий клавиш
def keyPressEvent(event):
    # Проверяем, что нажата клавиша Delete
    if event.key() == QtCore.Qt.Key_Delete:
        # Определяем, в каком из трех окошек программа было активным
        active_list_widget = window.focusWidget()

        # Проверяем, что активное окошко является списком (QListWidget)
        if isinstance(active_list_widget, QtWidgets.QListWidget):
            selected_items = active_list_widget.selectedItems()
            for item in selected_items:
                active_list_widget.takeItem(active_list_widget.row(item))

#Интерфейс окна
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle ('Статистика по гильдии')
window.resize(850, 556)
window.setFixedSize(850, 556)
lable1 = QtWidgets.QLabel('<center>ТЕКУЩИЙ</center>')
lable1.setStyleSheet('color: rgb(255, 255, 255);')
lable2 = QtWidgets.QLabel('<center>ПОКИНУВШИЕ</center>')
lable2.setStyleSheet('color: rgb(255, 255, 255);')
lable3 = QtWidgets.QLabel('<center>ВСТУПИВШИЕ</center>')
lable3.setStyleSheet('color: rgb(255, 255, 255);')
btnGuildStats = QtWidgets.QPushButton('&Обновить статистику')
PlayerName = QtWidgets.QListWidget()
PlayerName.addItems(GuildMember)
PlayerName.setStyleSheet ("background-color: rgba(255, 255, 255, 60);")#Фон таблички 4 цифра 0 - прозрачный 255 не прозрачный
LeftGuild = QtWidgets.QListWidget()
LeftGuild.addItems(LeftMember)
LeftGuild.setStyleSheet ("background-color: rgba(255, 255, 255, 60);")
NewGuild = QtWidgets.QListWidget()
NewGuild.addItems(NewMember)
NewGuild.setStyleSheet ("background-color: rgba(255, 255, 255, 60);")
grid = QtWidgets.QGridLayout()
btnGuildStats.clicked.connect(DataRefresh)
# Добавляем чекбокс для включения/выключения автообновления
chkAutoRefresh = QtWidgets.QCheckBox('Автообновление')
chkAutoRefresh.setChecked(False)
chkAutoRefresh.stateChanged.connect(lambda: toggle_auto_refresh(chkAutoRefresh))
label_timer = QtWidgets.QLabel('Осталось времени: 0 секунд')
vbox = QtWidgets.QVBoxLayout()
vbox.addWidget(chkAutoRefresh)
vbox.addWidget(label_timer)
vbox.addWidget(btnGuildStats)
spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
vbox.addItem(spacer_item)



grid.addWidget(lable1, 0, 0)
grid.addWidget(lable2, 0, 1)
grid.addWidget(lable3, 2, 0)
grid.addWidget(PlayerName, 1, 0)
grid.addWidget(LeftGuild, 1, 1)
grid.addWidget(NewGuild, 3, 0)
grid.addLayout(vbox, 3, 1)
window.setLayout(grid)


def btnGuildStats_clicked():
    global current_timer_value
    DataRefresh()
    current_timer_value = auto_refresh_interval
    # Обновление отображения времени в интерфейсе, если необходимо
    # Например, label_timer.setText(f'Осталось времени: {current_timer_value} секунд')

# Добавленная функция для включения/выключения автообновления
def toggle_auto_refresh(checkbox):
    global auto_refresh_enabled, current_timer_value

    auto_refresh_enabled = checkbox.isChecked()
    if auto_refresh_enabled:
        auto_refresh_timer.timeout.connect(update_timer)
        auto_refresh_timer.start(1000)  # Таймер срабатывает каждую секунду
    else:
        auto_refresh_timer.disconnect()
        #auto_refresh_timer.stop()
        current_timer_value = auto_refresh_interval
# После обновления данных, проверяем флаг автообновления
if auto_refresh_enabled:
    # Планируем следующее автообновление через auto_refresh_interval секунд
    QtCore.QTimer.singleShot(auto_refresh_interval * 1000, auto_refresh_data)

#Иконка
ico = QtGui.QIcon('icon.jpg')
window.setWindowIcon(ico)
app.setWindowIcon(ico)

#Задний фон
pal = window.palette()
pal.setBrush(QtGui.QPalette.Normal, QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap('background.png')))
pal.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap('background.png')))
window.setPalette(pal)

#Задний фон
window.show()
QtCore.QTimer.singleShot(10, DataRefresh)
sys.exit (app.exec_())

#Удаление строки
window.keyPressEvent = keyPressEvent