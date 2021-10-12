import sys
from random import choice
import sqlite3
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QInputDialog, QTableWidgetItem


class Character:
    def __init__(self, name, hp, dam=0, save=0):
        self.name = name
        self.hp = hp
        self.dam = dam
        self.save = save


class Player(Character):
    def __init__(self, name, hp, weap, arm, inw):
        Character.__init__(self, name, hp)
        self.weap = weap
        self.arm = arm
        self.inw = Inventory(self, inw)
        if self.weap is not None:
            self.dam = weap.dam
            self.inw.add(weap)
        if self.arm is not None:
            self.save = arm.save
            self.inw.add(arm)

    def ininw(self, name):
        for item in self.inw.inw.items():
            if item[1].name == name:
                return True
        return False

    def inwadd(self, item):
        self.inw.add(item)


class Inventory:
    def __init__(self, player, inw):
        self.inw = inw
        self.player = player

    def add(self, item):
        if item.name in list(self.inw.keys()):
            if item.type == 'item':
                self.inw[item.name].col += item.col
                if self.inw[item.name].col == 0:
                    del self.inw[item.name]
        else:
            self.inw[item.name] = item
            if item.type == 'armor':
                self.player.save = item.save
            elif item.type == 'weapon':
                self.player.dam = item.dam

    def __str__(self):
        return str(self.inw)

    def __getitem__(self, item):
        return self.inw[item]


class Item:
    def __init__(self, name, col=1):
        self.name = name
        self.col = col
        self.type = 'item'

    def __repr__(self):
        return f'Item({self.name}, {self.col})'

    def setcol(self, col):
        self.col = col
        return self

    def __str__(self):
        return f'Item({self.name}, {self.col})'


class Weapon(Item):
    def __init__(self, name, dam):
        Item.__init__(self, name)
        self.dam = dam
        self.type = 'weapon'

    def __repr__(self):
        return f'Weapon({self.name}, {self.dam})'

    def __str__(self):
        return f'Weapon({self.name}, {self.dam})'


class Armor(Item):
    def __init__(self, name, save):
        Item.__init__(self, name)
        self.save = save
        self.type = 'armor'

    def __repr__(self):
        return f'Armor({self.name}, {self.save})'

    def __str__(self):
        return f'Armor({self.name}, {self.save})'


class Monster(Character):
    def __init__(self, name, window, player, hp, save, dam, lut, alive):
        Character.__init__(self, name, hp, dam, save)
        self.window = window
        self.player = player
        self.lut = lut
        self.var = -1
        self.p_var = -1
        self.alive = alive

    def run(self):
        print('run!')
        if self.alive:
            print('alive!')
            if self.player.hp <= 0:
                self.window.text += 'Вы мертвы'
                self.window.setBtns(['В меню'])
                if self.window.btn > -1:
                    self.window.main_menu()
            elif self.hp > 0:
                print('-' * 20)
                print(f'monster {self.hp}')
                print(f'player {self.player.hp}')
                print(f'var={self.var}, btn={self.window.btn}')
                text = ''
                if self.window.btn > -1:
                    lack = choice([True, False])
                    print('lack =', lack)
                    l_vars = [lack, self.var, self.window.btn]
                    if l_vars in [[True, 0, 1], [True, 1, 0], [True, 2, 2]]:
                        text = f'Вы ранили {self.name}'
                        self.hp -= self.player.dam - self.save
                    elif l_vars in [[True, 0, 0], [True, 2, 0], [False, 0, 2], [False, 1, 1]]:
                        text = f'{self.name.capitalize()} ранил вас'
                        self.player.hp -= self.dam - self.player.save
                    elif l_vars in [[False, 0, 0], [False, 1, 0]]:
                        text = f'Вы и {self.name} одновременно ранили друг друга'
                        self.hp -= self.player.dam - self.save
                        self.player.hp -= self.dam - self.player.save
                    elif l_vars in [[False, 1, 2], [False, 2, 0], [False, 2, 1]]:
                        text = f'{self.name.capitalize()} сильно ранил вас'
                        self.player.hp -= self.dam * 2 - self.player.save
                    else:
                        text = 'Вы не смогли друг другу навредить'
                    print(text)
                    print(f'monster {self.hp}')
                    print(f'player {self.player.hp}')
                    self.window.draw_lbls()
                    self.var = -1
                    self.window.btn = -1
                self.window.text += f'Жизни {self.name}: {self.hp}'
                self.window.text += text
                if self.player.hp <= 0 or self.hp <= 0:
                    self.window.btn = -1
                    self.window.point.run()
                if self.var == -1:
                    self.var = choice([0, 1, 2])
                vars_texts = ['бьет лапой', 'бьет хвостом', 'вытягивает голову']
                self.window.text += f'{self.name.capitalize()} {vars_texts[self.var]}'
                self.window.setBtns(['Ударить', 'Защититься', 'Увернуться'])
            else:
                self.window.text.clear()
                self.player.hp = 10
                self.window.text += f'Вы убили {self.name}'
                self.window.text += f'Вы нашли {self.lut.name}'
                self.window.setBtns(['Уйти'])
                print('else btn', self.window.btn)
                if self.window.btn > -1:
                    self.window.notes += f'Убил {self.name}'
                    self.player.inw.add(self.lut)
                    self.window.btn = -1
                    self.window.cango = True
                    self.window.point.ran = True
                    self.alive = False
        else:
            self.window.point.ran = True

    def __repr__(self):
        return f'Monster({self.name}, {self.hp}, {self.save}, {self.dam}, {self.lut}'


class Npc:
    def __init__(self, window, name, args0, args):
        self.window = window
        self.name = name
        args.insert(0, args0)
        self.args = args

    def run(self):
        if self.name == 'рыбак':
            if self.args[0]:
                self.window.text.clear()
                self.window.text += 'Рыбак: - Дарова, салага. Слышал мои ребята тебя из под обломков корабля на ' + \
                                    'пляже вытащили. Это как так тебя угораздило?'
                if self.args[1] == -1:
                    self.window.setBtns(['"В шторм попал"', '"Не твое дело"', 'Промолчать'])
                    self.args[1] = self.window.btn
                    self.window.btn = -1
                if self.args[1] > -1:
                    if self.args[1] == 0:
                        self.window.text += 'Вы: - В шторм попал.'
                        self.window.text += 'Рыбак: - Вот так не повезло... Изрядно тебя потрепало.'
                    elif self.args[1] == 1:
                        self.window.text += 'Вы: - Не твое дело.'
                        self.window.text += 'Рыбак: - Ну, тебе видней.'
                        self.args[3] -= 1
                    else:
                        self.window.text += 'Вы промолчали.'
                        self.window.text += 'Рыбак: - Ну ладно, не будем об этом.'
                    self.window.text[2] = self.window.text[1] + ' Слушай, тебя тут наш староста вызывал. ' + \
                                                                'Хотел на пару слов. Заглянешь?'
                    self.args[2] = self.window.btn
                    self.window.btn = -1
                    if self.args[2] == -1:
                        self.window.setBtns(['Хорошо'])
                        self.args[2] = self.window.btn
                        self.window.btn = -1
                    if self.args[2] > -1:
                        self.window.text += 'Он тут рядом живёт. Выходишь и на против дом старейшины. Не ' + \
                                            'заблудишься. Хмм... Тебя как звать то?'
                        name, ok_pressed = QInputDialog.getText(self.window, "Введите имя",
                                                                "Тебя как звать то?")
                        if ok_pressed:
                            self.window.player.name = name
                        else:
                            self.window.point.run()
                        self.window.text += ''
                        self.window.notes += 'Познакомился с Рыбаком'
                        self.args[0] = False
                        self.window.text.clear()
                        self.window.point.ran = True
                        self.window.cango = True
                        self.window.point.run()
            elif self.window.player.ininw('мясо амфибии'):
                self.window.text.clear()
                self.window.text += 'Рыбак: - Эй, а что это от тебя рыбой разит? Ба, да это мясо амфибии у тебя ' + \
                                    'в мешке! Отдай кусок, а я тебе монет отсыплю.'
                self.window.setBtns(['Продать\n1 кусок мяса ->\n5 монет', 'Уйти'])
                self.args[1] = self.window.btn
                if self.args[1] == 0:
                    self.window.btn = -1
                    self.window.text.clear()
                    self.window.text += 'Вы продали один кусок мяса'
                    self.window.notes += 'Продал один кусок мяса'
                    self.window.money += 5
                    self.window.draw_lbls()
                    self.window.player.inwadd(self.window.items['мясо амфибии'].setcol(-1))
                    if not self.window.player.ininw('мясо амфибии'):
                        self.window.setBtns(['Уйти'])
                if self.args[1] == 1:
                    self.window.btn = -1
                    self.args[1] = -1
                    self.window.point.ran = True
                    self.window.cango = True
                    self.window.point.run()
            else:
                if self.window.npcs['старейшина'].args[0]:
                    self.window.text += 'Рыбак: - Хей, салага. Мне сейчас надо подсуетиться чтобы мужикам помочь, ' + \
                                        'можешь пока к старейшине наведаться - он тебя звал.'
                else:
                    self.window.text += 'Рыбак: - Хэй, салага. Щас говорить не могу, занят больно.'
                self.window.setBtns(['Уйти'])
                self.args[1] = self.window.btn
                if self.args[1] == 0:
                    self.window.btn = -1
                    self.args[1] = -1
                    self.window.point.ran = True
                    self.window.cango = True
                    self.window.point.run()
        elif self.name == 'старейшина':
            if self.args[0]:
                self.window.text.clear()
                self.window.text += f'Страроста: - Здорова! Тебя вроде {self.window.player.name} звать? ' + \
                                    'Что делаешь в нашем захолустье?'
                self.window.text += 'Вы: - Я тут проездом. Не знаешь, где здесь можно найти корабль до Пэйи?'
                self.window.text += 'Староста: - Корабль? Разве что в Панталане. Иди на север по тропе ' + \
                                    'через горы, а там увидишь с высока церковь, у ней и причал.'

                self.window.setBtns(['Далее'])
                self.args[1] = self.window.btn
                self.window.btn = -1
                if self.args[1] > -1:
                    self.args[1] = -1
                    self.window.btn = -1
                    self.window.text += ''
                    self.window.notes += 'Познакомился со Старостой'
                    self.window.notes += 'Узнал, что нужно идти на север'
                    self.args[0] = False
                    self.window.point.run()
            elif self.window.money >= 10 and self.args[2] > -1:
                self.window.text.clear()
                self.window.text += 'Староста: - Что это за шум по всей округе? Ни как ты амфибию зарубил? ' + \
                                    'Слышал я, одна из них особо сильная. Могу куртку свою проадть за 10 монет, ' + \
                                    'спасет тебя от когтей.'
                self.window.setBtns(['Купить\n10 монет ->\nкуртка', 'Уйти'])
                self.args[1] = self.window.btn
                if self.args[1] == 0:
                    self.args[2] = -1
                    self.window.notes += 'Купил куртку'
                    self.window.btn = -1
                    self.window.money -= 10
                    self.window.draw_lbls()
                    self.window.player.inwadd(self.window.items['куртка'])
                    self.window.player.arm = self.window.player.inw.inw['куртка']
                if self.args[1] == 1:
                    self.window.btn = -1
                    self.args[1] = -1
                    self.window.point.run()
            else:
                self.window.text += 'Вы: - До встречи.'
                self.window.text += 'Страоста: - Не хворай!'
                self.window.setBtns(['Уйти'])
                self.args[1] = self.window.btn
                if self.args[1] == 0:
                    self.window.btn = -1
                    self.args[1] = -1
                    self.window.point.ran = True
                    self.window.cango = True
                    self.window.point.run()
        elif self.name == 'старик':
            if self.args[0]:
                self.window.text.clear()
                self.window.text += f'Старик: - Привет! Кто таков?'
                self.window.text += 'Вы: - Путешественник'
                self.window.text += 'Старик: - О! А расскажи че-нить, а то я дальше огорода в жизни не бывал.'
                self.window.text += 'Вы: - Я спешу. Не знаешь, как перебраться через горы?'
                self.window.text += 'Старик: - Знаю. Но задаром не скажу. Есть у тебя рожок?'
                self.window.setBtns(['Далее'])
                self.args[1] = self.window.btn
                self.window.btn = -1
                if self.args[1] > -1:
                    self.args[1] = -1
                    self.window.btn = -1
                    self.window.text += ''
                    self.window.notes += 'Познакомился со Стариком'
                    self.window.notes += 'Узнал, что нужен рог'
                    self.args[0] = False
                    self.window.point.run()
            elif self.window.player.ininw('рог амфибии'):
                self.window.text.clear()
                self.window.text += 'Старик: - Спасибо, услужил! Пойдем'
                self.window.text += 'Победа! Вы прошли пробную версию игры. Полная версия не является частью ' + \
                                    'проекта для Яндекс.Лицея'
                self.window.setBtns(['Закончить'])
                self.args[1] = self.window.btn
                if self.args[1] == 0:
                    self.window.main_menu()
            else:
                self.window.text += 'Старик: - Нету рога? Жаль, жаль!'
                self.window.setBtns(['Уйти'])
                self.args[1] = self.window.btn
                if self.args[1] == 0:
                    self.window.btn = -1
                    self.args[1] = -1
                    self.window.point.ran = True
                    self.window.cango = True
                    self.window.point.run()
        else:
            print('else')

    def __str__(self):
        return f'Npc({self.name}, {self.args})'


class Point:
    def __init__(self, simb, x, y, window):
        self.ran = False
        self.window = window
        if simb == ' ':
            self.func = None
            if x % 2 == 0 and y % 2 == 0 or x % 2 == 1 and y % 2 == 1:
                self.im = 'forest_1'
            else:
                self.im = 'forest_2'
        elif simb == '*':
            self.func = None
            if x % 2 == 0 and y % 2 == 0 or x % 2 == 1 and y % 2 == 1:
                self.im = 'path_1'
            else:
                self.im = 'path_2'
        elif simb == '=':
            self.func = None
            self.im = f'street_{window.locn + 1}_{str(x).rjust(2, "0")}{str(y).rjust(2, "0")}'
        elif simb == '-':
            self.func = None
            self.im = f'street_bank_{x % 2 + 1}'
        elif simb == 'x':
            self.name = 'амфибия'
            if x < 7:
                self.func = window.mons['амфибия1'].run
            else:
                self.func = window.mons['амфибия2'].run
            if x % 2 == 0 and y % 2 == 0 or x % 2 == 1 and y % 2 == 1:
                self.im = 'forest_1'
            else:
                self.im = 'forest_2'
        elif simb == '+':
            self.func = window.mons['вожак-амфибия'].run
            self.name = 'вожак-амфибия'
            if x % 2 == 0 and y % 2 == 0 or x % 2 == 1 and y % 2 == 1:
                self.im = 'forest_1'
            else:
                self.im = 'forest_2'
        elif simb == 'h':
            if x == 4 and y == 8:
                name = 'рыбак'
            elif x == 6 and y == 8:
                name = 'старейшина'
            else:
                name = 'старик'
            self.func = window.npcs[name].run
            self.name = name
            self.im = f'house_{window.locn + 1}_{str(x).rjust(2, "0")}{str(y).rjust(2, "0")}'
        elif simb == 'g':
            self.func = None
            self.im = 'gate'
        elif simb == '0':
            self.func = None
            if x % 2 == 0 and y % 2 == 0 or x % 2 == 1 and y % 2 == 1:
                self.im = 'forest_1'
            else:
                self.im = 'forest_2'
        else:
            self.func = None
            self.im = 'else'

    def run(self):
        if self.func is not None and not self.ran:
            self.window.battle_window()
            self.window.setimage(self.name)
            self.func()
        else:
            self.window.main_window()
            self.window.setimage(self.im)


class Text:
    def __init__(self, window, text=None, in_b_window=True):
        if text is None:
            self.text = []
        else:
            self.text = text
        self.in_b_window = in_b_window
        self.window = window

    def rewrite(self):
        if self.window.opend_battle_window == self.in_b_window:
            self.window.text_b.setText('\n'.join(self.text))

    def __iadd__(self, other):
        self.text.append(other)
        self.rewrite()
        return self

    def clear(self):
        self.text = []
        self.rewrite()

    def __setitem__(self, key, v):
        self.text[key] = v
        self.rewrite()
        return self

    def __getitem__(self, key):
        return self.text[key]


class Labella(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        # self.setStyleSheet('QFrame {background-color:grey;}')
        self.show()
        self.parent = parent
        self.move(1440, 120)
        self.resize(480, 480)
        self.canpaint = True
        self.repaint()

    def paintEvent(self, e):
        if self.canpaint:
            qp = QPainter(self)
            self.draw(qp)
            self.canpaint = False

    def draw(self, qp):
        qp.save()  # save the QPainter config
        qp.restore()  # restore the QPainter config
        ln = len(self.parent.opens)
        qp.setPen(QColor(255, 0, 0))
        qp.drawRect(481 // ln * self.parent.x, 482 // ln * self.parent.y, 481 // ln, 482 // ln)
        # for y in range(ln):
        #     for x in range(ln):
        #         p = self.parent.opens[y][x]
        #         if p == '0':
        #             # 1440 120
        #             qp.setBrush(QColor(231, 198, 151))
        #             qp.setPen(QColor(0, 0, 0))
        #             qp.drawRect(481 // ln * x, 482 // ln * y, 481 // ln, 482 // ln)


class Ui_start_window(object):
    def start_window_setupUi(self, main_menu):
        main_menu.setObjectName("main_menu")
        main_menu.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(main_menu)
        self.centralwidget.setObjectName("centralwidget")
        self.b_start = QtWidgets.QPushButton(self.centralwidget)
        self.b_start.setGeometry(QtCore.QRect(720, 840, 480, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_start.setFont(font)
        self.b_start.setObjectName("b_start")
        self.l_logo = QtWidgets.QLabel(self.centralwidget)
        self.l_logo.setGeometry(QtCore.QRect(60, 120, 1800, 600))
        self.l_logo.setObjectName("l_logo")
        main_menu.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_menu)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 21))
        self.menubar.setObjectName("menubar")
        main_menu.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_menu)
        self.statusbar.setObjectName("statusbar")
        main_menu.setStatusBar(self.statusbar)

        self.start_window_retranslateUi(main_menu)
        QtCore.QMetaObject.connectSlotsByName(main_menu)

    def start_window_retranslateUi(self, main_menu):
        _translate = QtCore.QCoreApplication.translate
        main_menu.setWindowTitle(_translate("main_menu", "main_menu"))
        self.b_start.setText(_translate("main_menu", "начать"))
        self.l_logo.setText(_translate("main_menu", "лого"))


class Ui_main_menu(object):
    def main_menu_setupUi(self, main_menu):
        main_menu.setObjectName("main_menu")
        main_menu.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(main_menu)
        self.centralwidget.setObjectName("centralwidget")
        self.l_logo = QtWidgets.QLabel(self.centralwidget)
        self.l_logo.setGeometry(QtCore.QRect(60, 80, 600, 200))
        self.l_logo.setObjectName("l_logo")
        self.b_new = QtWidgets.QPushButton(self.centralwidget)
        self.b_new.setGeometry(QtCore.QRect(720, 120, 480, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.b_new.setFont(font)
        self.b_new.setAutoFillBackground(False)
        self.b_new.setObjectName("b_new")
        self.b_load = QtWidgets.QPushButton(self.centralwidget)
        self.b_load.setGeometry(QtCore.QRect(720, 360, 480, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_load.setFont(font)
        self.b_load.setObjectName("b_load")
        self.b_about = QtWidgets.QPushButton(self.centralwidget)
        self.b_about.setGeometry(QtCore.QRect(720, 600, 480, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_about.setFont(font)
        self.b_about.setObjectName("b_about")
        self.b_tomaker = QtWidgets.QPushButton(self.centralwidget)
        self.b_tomaker.setGeometry(QtCore.QRect(720, 840, 480, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_tomaker.setFont(font)
        self.b_tomaker.setObjectName("b_tomaker")
        self.b_exit = QtWidgets.QPushButton(self.centralwidget)
        self.b_exit.setGeometry(QtCore.QRect(1440, 120, 360, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_exit.setFont(font)
        self.b_exit.setObjectName("b_exit")
        self.l_desc = QtWidgets.QLabel(self.centralwidget)
        self.l_desc.setGeometry(QtCore.QRect(1250, 480, 480, 360))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.l_desc.setFont(font)
        self.l_desc.setText("")
        self.l_desc.setObjectName("l_desc")
        main_menu.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_menu)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 26))
        self.menubar.setObjectName("menubar")
        main_menu.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_menu)
        self.statusbar.setObjectName("statusbar")
        main_menu.setStatusBar(self.statusbar)

        self.main_menu_retranslateUi(main_menu)
        QtCore.QMetaObject.connectSlotsByName(main_menu)

    def main_menu_retranslateUi(self, main_menu):
        _translate = QtCore.QCoreApplication.translate
        main_menu.setWindowTitle(_translate("main_menu", "main_menu"))
        self.l_logo.setText(_translate("main_menu", "картинка с названием"))
        self.b_new.setText(_translate("main_menu", "НОВАЯ ИГРА"))
        self.b_load.setText(_translate("main_menu", "ПРОДОЛЖИТЬ"))
        self.b_about.setText(_translate("main_menu", "о разработчиках"))
        self.b_tomaker.setText(_translate("main_menu", "обратная связь"))
        self.b_exit.setText(_translate("main_menu", "ВЫХОД ИЗ ИГРЫ"))


class Ui_main_window(object):
    def main_window_setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.l_image = QtWidgets.QLabel(self.centralwidget)
        self.l_image.setGeometry(QtCore.QRect(180, 0, 1080, 1080))
        self.l_image.setObjectName("l_image")
        self.l_map = QtWidgets.QLabel(self.centralwidget)
        self.l_map.setGeometry(QtCore.QRect(1440, 120, 480, 480))
        self.l_map.setObjectName("l_map")
        self.b_info = QtWidgets.QPushButton(self.centralwidget)
        self.b_info.setGeometry(QtCore.QRect(1440, 0, 120, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(36)
        self.b_info.setFont(font)
        self.b_info.setObjectName("b_info")
        self.b_bt = QtWidgets.QPushButton(self.centralwidget)
        self.b_bt.setGeometry(QtCore.QRect(1560, 0, 120, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(36)
        self.b_bt.setFont(font)
        self.b_bt.setObjectName("b_bt")
        self.b_menu = QtWidgets.QPushButton(self.centralwidget)
        self.b_menu.setGeometry(QtCore.QRect(1680, 0, 240, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_menu.setFont(font)
        self.b_menu.setObjectName("b_menu")
        self.l_hp = QtWidgets.QLabel(self.centralwidget)
        self.l_hp.setGeometry(QtCore.QRect(0, 0, 84, 120))
        self.l_hp.setObjectName("l_hp")
        self.L_hp_num = QtWidgets.QLabel(self.centralwidget)
        self.L_hp_num.setGeometry(QtCore.QRect(840, 0, 121, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(48)
        self.L_hp_num.setFont(font)
        self.L_hp_num.setObjectName("L_hp_num")
        self.l_coin = QtWidgets.QLabel(self.centralwidget)
        self.l_coin.setGeometry(QtCore.QRect(960, 0, 120, 120))
        self.l_coin.setObjectName("l_coin")
        self.qwestlist = QtWidgets.QListWidget(self.centralwidget)
        self.qwestlist.setGeometry(QtCore.QRect(1440, 840, 480, 240))
        self.qwestlist.setObjectName("qwestlist")
        self.l_hp_2 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_2.setGeometry(QtCore.QRect(84, 0, 84, 120))
        self.l_hp_2.setObjectName("l_hp_2")
        self.l_hp_3 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_3.setGeometry(QtCore.QRect(168, 0, 84, 120))
        self.l_hp_3.setObjectName("l_hp_3")
        self.l_hp_4 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_4.setGeometry(QtCore.QRect(252, 0, 84, 120))
        self.l_hp_4.setObjectName("l_hp_4")
        self.l_hp_5 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_5.setGeometry(QtCore.QRect(336, 0, 84, 120))
        self.l_hp_5.setObjectName("l_hp_5")
        self.l_hp_6 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_6.setGeometry(QtCore.QRect(420, 0, 84, 120))
        self.l_hp_6.setObjectName("l_hp_6")
        self.l_hp_7 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_7.setGeometry(QtCore.QRect(504, 0, 84, 120))
        self.l_hp_7.setObjectName("l_hp_7")
        self.l_hp_8 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_8.setGeometry(QtCore.QRect(588, 0, 84, 120))
        self.l_hp_8.setObjectName("l_hp_8")
        self.l_hp_9 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_9.setGeometry(QtCore.QRect(672, 0, 84, 120))
        self.l_hp_9.setObjectName("l_hp_9")
        self.l_hp_10 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_10.setGeometry(QtCore.QRect(756, 0, 84, 120))
        self.l_hp_10.setObjectName("l_hp_10")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(1210, -1, 231, 121))
        self.label.setText("")
        self.label.setObjectName("label")
        self.L_coins = QtWidgets.QLabel(self.centralwidget)
        self.L_coins.setGeometry(QtCore.QRect(1080, 0, 121, 121))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(48)
        self.L_coins.setFont(font)
        self.L_coins.setObjectName("L_coins")
        self.text_b = QtWidgets.QTextBrowser(self.centralwidget)
        self.text_b.setGeometry(QtCore.QRect(1440, 600, 480, 441))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.text_b.setFont(font)
        self.text_b.setObjectName("text_b")
        self.t_info = QtWidgets.QTextBrowser(self.centralwidget)
        self.t_info.setGeometry(QtCore.QRect(840, 120, 600, 240))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.t_info.setFont(font)
        self.t_info.setObjectName("t_info")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.main_window_retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def main_window_retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.l_image.setText(_translate("MainWindow", "экран"))
        self.l_map.setText(_translate("MainWindow", "карта"))
        self.b_info.setText(_translate("MainWindow", "i"))
        self.b_bt.setText(_translate("MainWindow", "?"))
        self.b_menu.setText(_translate("MainWindow", "МЕНЮ"))
        self.l_hp.setText(_translate("MainWindow", "строка HP"))
        self.L_hp_num.setText(_translate("MainWindow", "10"))
        self.l_coin.setText(_translate("MainWindow", "монета"))
        self.l_hp_2.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_3.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_4.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_5.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_6.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_7.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_8.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_9.setText(_translate("MainWindow", "строка HP"))
        self.l_hp_10.setText(_translate("MainWindow", "строка HP"))
        self.L_coins.setText(_translate("MainWindow", "10"))


class Ui_battle_window(object):
    def battle_window_setupUi(self, battle_window):
        battle_window.setObjectName("battle_window")
        battle_window.resize(1920, 1149)
        self.centralwidget = QtWidgets.QWidget(battle_window)
        self.centralwidget.setObjectName("centralwidget")
        self.l_image = QtWidgets.QLabel(self.centralwidget)
        self.l_image.setGeometry(QtCore.QRect(0, 0, 1920, 600))
        self.l_image.setObjectName("l_image")
        self.l_but = QtWidgets.QLabel(self.centralwidget)
        self.l_but.setGeometry(QtCore.QRect(1079, 599, 841, 481))
        self.l_but.setText("")
        self.l_but.setObjectName("l_but")
        self.b_1 = QtWidgets.QPushButton(self.centralwidget)
        self.b_1.setGeometry(QtCore.QRect(1140, 660, 330, 150))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_1.setFont(font)
        self.b_1.setObjectName("b_1")
        self.b_3 = QtWidgets.QPushButton(self.centralwidget)
        self.b_3.setGeometry(QtCore.QRect(1140, 870, 330, 150))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_3.setFont(font)
        self.b_3.setObjectName("b_3")
        self.b_2 = QtWidgets.QPushButton(self.centralwidget)
        self.b_2.setGeometry(QtCore.QRect(1530, 660, 330, 150))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_2.setFont(font)
        self.b_2.setObjectName("b_2")
        self.b_4 = QtWidgets.QPushButton(self.centralwidget)
        self.b_4.setGeometry(QtCore.QRect(1530, 870, 330, 150))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_4.setFont(font)
        self.b_4.setObjectName("b_4")
        self.text_b = QtWidgets.QTextBrowser(self.centralwidget)
        self.text_b.setGeometry(QtCore.QRect(0, 600, 1080, 491))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(12)
        self.text_b.setFont(font)
        self.text_b.setObjectName("text_b")
        self.l_hp = QtWidgets.QLabel(self.centralwidget)
        self.l_hp.setGeometry(QtCore.QRect(0, 0, 84, 120))
        self.l_hp.setObjectName("l_hp")
        self.l_hp_6 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_6.setGeometry(QtCore.QRect(420, 0, 84, 120))
        self.l_hp_6.setObjectName("l_hp_6")
        self.l_hp_5 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_5.setGeometry(QtCore.QRect(336, 0, 84, 120))
        self.l_hp_5.setObjectName("l_hp_5")
        self.L_coins = QtWidgets.QLabel(self.centralwidget)
        self.L_coins.setGeometry(QtCore.QRect(1080, 0, 121, 121))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(48)
        self.L_coins.setFont(font)
        self.L_coins.setObjectName("L_coins")
        self.l_hp_2 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_2.setGeometry(QtCore.QRect(84, 0, 84, 120))
        self.l_hp_2.setObjectName("l_hp_2")
        self.l_hp_9 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_9.setGeometry(QtCore.QRect(672, 0, 84, 120))
        self.l_hp_9.setObjectName("l_hp_9")
        self.l_hp_4 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_4.setGeometry(QtCore.QRect(252, 0, 84, 120))
        self.l_hp_4.setObjectName("l_hp_4")
        self.L_hp_num = QtWidgets.QLabel(self.centralwidget)
        self.L_hp_num.setGeometry(QtCore.QRect(840, 0, 121, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(48)
        self.L_hp_num.setFont(font)
        self.L_hp_num.setObjectName("L_hp_num")
        self.l_hp_3 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_3.setGeometry(QtCore.QRect(168, 0, 84, 120))
        self.l_hp_3.setObjectName("l_hp_3")
        self.l_hp_7 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_7.setGeometry(QtCore.QRect(504, 0, 84, 120))
        self.l_hp_7.setObjectName("l_hp_7")
        self.l_hp_10 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_10.setGeometry(QtCore.QRect(756, 0, 84, 120))
        self.l_hp_10.setObjectName("l_hp_10")
        self.l_hp_8 = QtWidgets.QLabel(self.centralwidget)
        self.l_hp_8.setGeometry(QtCore.QRect(588, 0, 84, 120))
        self.l_hp_8.setObjectName("l_hp_8")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(1210, -1, 231, 121))
        self.label.setText("")
        self.label.setObjectName("label")
        self.l_coin = QtWidgets.QLabel(self.centralwidget)
        self.l_coin.setGeometry(QtCore.QRect(960, 0, 120, 120))
        self.l_coin.setObjectName("l_coin")
        self.b_menu = QtWidgets.QPushButton(self.centralwidget)
        self.b_menu.setEnabled(False)
        self.b_menu.setGeometry(QtCore.QRect(1680, 0, 240, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_menu.setFont(font)
        self.b_menu.setObjectName("b_menu")
        self.t_info = QtWidgets.QTextBrowser(self.centralwidget)
        self.t_info.setGeometry(QtCore.QRect(840, 120, 600, 240))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.t_info.setFont(font)
        self.t_info.setObjectName("t_info")
        self.b_info = QtWidgets.QPushButton(self.centralwidget)
        self.b_info.setGeometry(QtCore.QRect(1440, 0, 120, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(36)
        self.b_info.setFont(font)
        self.b_info.setObjectName("b_info")
        self.b_bt = QtWidgets.QPushButton(self.centralwidget)
        self.b_bt.setGeometry(QtCore.QRect(1560, 0, 120, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(36)
        self.b_bt.setFont(font)
        self.b_bt.setObjectName("b_bt")
        self.l_image.raise_()
        self.l_but.raise_()
        self.text_b.raise_()
        self.l_hp.raise_()
        self.l_hp_6.raise_()
        self.l_hp_5.raise_()
        self.L_coins.raise_()
        self.l_hp_2.raise_()
        self.l_hp_9.raise_()
        self.l_hp_4.raise_()
        self.L_hp_num.raise_()
        self.l_hp_3.raise_()
        self.l_hp_7.raise_()
        self.l_hp_10.raise_()
        self.l_hp_8.raise_()
        self.label.raise_()
        self.l_coin.raise_()
        self.b_4.raise_()
        self.b_2.raise_()
        self.b_1.raise_()
        self.b_3.raise_()
        self.b_menu.raise_()
        self.t_info.raise_()
        self.b_info.raise_()
        self.b_bt.raise_()
        battle_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(battle_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 26))
        self.menubar.setObjectName("menubar")
        battle_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(battle_window)
        self.statusbar.setObjectName("statusbar")
        battle_window.setStatusBar(self.statusbar)

        self.battle_window_retranslateUi(battle_window)
        QtCore.QMetaObject.connectSlotsByName(battle_window)

    def battle_window_retranslateUi(self, battle_window):
        _translate = QtCore.QCoreApplication.translate
        battle_window.setWindowTitle(_translate("battle_window", "battle_window"))
        self.l_image.setText(_translate("battle_window", "экран"))
        self.b_1.setText(_translate("battle_window", "кнопка 1"))
        self.b_3.setText(_translate("battle_window", "кнопка 3"))
        self.b_2.setText(_translate("battle_window", "кнопка 2"))
        self.b_4.setText(_translate("battle_window", "кнопка 4"))
        self.l_hp.setText(_translate("battle_window", "строка HP"))
        self.l_hp_6.setText(_translate("battle_window", "строка HP"))
        self.l_hp_5.setText(_translate("battle_window", "строка HP"))
        self.L_coins.setText(_translate("battle_window", "10"))
        self.l_hp_2.setText(_translate("battle_window", "строка HP"))
        self.l_hp_9.setText(_translate("battle_window", "строка HP"))
        self.l_hp_4.setText(_translate("battle_window", "строка HP"))
        self.L_hp_num.setText(_translate("battle_window", "10"))
        self.l_hp_3.setText(_translate("battle_window", "строка HP"))
        self.l_hp_7.setText(_translate("battle_window", "строка HP"))
        self.l_hp_10.setText(_translate("battle_window", "строка HP"))
        self.l_hp_8.setText(_translate("battle_window", "строка HP"))
        self.l_coin.setText(_translate("battle_window", "монета"))
        self.b_menu.setText(_translate("battle_window", "МЕНЮ"))
        self.b_info.setText(_translate("battle_window", "i"))
        self.b_bt.setText(_translate("battle_window", "?"))


class Ui_inventory(object):
    def inventory_setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 1681, 1021))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.tableWidget.setFont(font)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.b_exit = QtWidgets.QPushButton(self.centralwidget)
        self.b_exit.setGeometry(QtCore.QRect(1680, 0, 240, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(18)
        self.b_exit.setFont(font)
        self.b_exit.setObjectName("b_exit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.inventory_retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def inventory_retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.b_exit.setText(_translate("MainWindow", "выход"))


class MainWindow(QMainWindow, Ui_start_window, Ui_main_menu, Ui_main_window, Ui_battle_window, Ui_inventory):
    def __init__(self):
        super().__init__()
        self.cango = False
        self.start_window()

    def start_window(self):
        self.start_window_setupUi(self)
        self.showFullScreen()
        self.setStyleSheet("QMainWindow { background-image: url(pic/фон.png) }")
        self.b_start.setStyleSheet("background-color: #BCA97C")
        self.im = Image.open('pic/лого.png')
        self.paint = ImageQt(self.im)
        self.pixmap = QPixmap.fromImage(self.paint)
        self.l_logo.setPixmap(self.pixmap)
        self.b_start.clicked.connect(self.main_menu)

    def main_menu(self):
        self.main_menu_setupUi(self)
        self.showFullScreen()
        self.im = Image.open('pic/лого.png')
        self.paint = ImageQt(self.im)
        self.pixmap = QPixmap.fromImage(self.paint)
        self.pixmap = self.pixmap.scaledToHeight(200)
        self.l_logo.setPixmap(self.pixmap)
        self.b_exit.setStyleSheet("background-color: #BCA97C")
        self.b_new.setStyleSheet("background-color: #BCA97C")
        self.b_load.setStyleSheet("background-color: #BCA97C")
        self.b_about.setStyleSheet("background-color: #BCA97C")
        self.b_tomaker.setStyleSheet("background-color: #BCA97C")
        self.b_exit.clicked.connect(self.ext)
        self.b_new.clicked.connect(self.new)
        self.b_load.clicked.connect(self.load)
        self.b_about.clicked.connect(self.about)
        self.b_tomaker.clicked.connect(self.tomaker)

    def main_window(self):
        if self.opend_battle_window:
            self.opend_battle_window = False
            print('main_window')
            self.main_window_setupUi(self)
            self.showFullScreen()
            self.b_menu.setStyleSheet("background-color: #BCA97C")
            self.b_info.setStyleSheet("background-color: #BCA97C")
            self.b_bt.setStyleSheet("background-color: #BCA97C")
            self.t_info.setStyleSheet("background-color: #E7C697")
            self.text_b.setStyleSheet("background-color: #E7C697")
            self.qwestlist.hide()
            self.setimage(self.point.im)
        self.save()
        self.hps = [self.l_hp,
                    self.l_hp_2,
                    self.l_hp_3,
                    self.l_hp_4,
                    self.l_hp_5,
                    self.l_hp_6,
                    self.l_hp_7,
                    self.l_hp_8,
                    self.l_hp_9,
                    self.l_hp_10,
                    ]
        self.draw_lbls()
        self.drawing = False
        self.draw_map()
        self.b_menu.clicked.connect(self.main_menu)
        self.b_info.clicked.connect(self.info)
        self.b_bt.clicked.connect(self.bt)
        self.t_info.hide()
        self.notes.rewrite()
        self.cango = True

    def battle_window(self):
        self.cango = False
        if not self.opend_battle_window:
            print('battle_window')
            self.opend_battle_window = True
            self.battle_window_setupUi(self)
            self.b_menu.setStyleSheet("background-color: #BCA97C")
            self.text_b.setStyleSheet("background-color: #E7C697")
            self.l_but.setStyleSheet("background-color: #E7C697")
            self.b_info.setStyleSheet("background-color: #BCA97C")
            self.b_bt.setStyleSheet("background-color: #BCA97C")
            self.t_info.setStyleSheet("background-color: #E7C697")
            self.showFullScreen()
            self.btn = -1
        self.b_menu.clicked.connect(self.main_menu)
        self.hps = [self.l_hp,
                    self.l_hp_2,
                    self.l_hp_3,
                    self.l_hp_4,
                    self.l_hp_5,
                    self.l_hp_6,
                    self.l_hp_7,
                    self.l_hp_8,
                    self.l_hp_9,
                    self.l_hp_10,
                    ]
        self.draw_lbls()
        self.b_info.clicked.connect(self.info)
        self.b_bt.clicked.connect(self.bt)
        self.t_info.hide()
        self.text = Text(self)
        self.btns = [self.b_1,
                     self.b_2,
                     self.b_3,
                     self.b_4]
        for b in self.btns:
            b.setStyleSheet("background-color: #BCA97C")
            b.clicked.connect(self.btn_c)
        self.cango = False

    def inventory_window(self):
        self.cango = False
        self.inventory_setupUi(self)
        self.showFullScreen()
        self.opend_battle_window = True
        self.b_exit.clicked.connect(self.main_window)
        self.b_exit.setStyleSheet("background-color: #BCA97C")
        self.tableWidget.setStyleSheet("background-color: #E7C697")
        title = ['id', 'name', 'type', 'char']
        self.tableWidget.setColumnCount(len(title))
        self.tableWidget.setHorizontalHeaderLabels(title)
        self.tableWidget.setRowCount(0)
        keyes = self.player.inw.inw.keys()
        for i in range(len(list(keyes))):
            item = self.player.inw[list(keyes)[i]]
            if item.type == 'weapon':
                row = [str(i + 1), item.name, item.type, str(item.dam)]
            elif item.type == 'armor':
                row = [str(i + 1), item.name, item.type, str(item.save)]
            else:
                row = [str(i + 1), item.name, item.type, str(item.col)]
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()

    def keyPressEvent(self, event):
        if self.cango:
            e = ''
            if event.key() == Qt.Key_W:
                e = 'w'
            elif event.key() == Qt.Key_A:
                e = 'a'
            elif event.key() == Qt.Key_S:
                e = 's'
            elif event.key() == Qt.Key_D:
                e = 'd'
            elif event.key() == Qt.Key_E:
                e = 'e'
            if e in 'wasd':
                move = [0, 0]  # (y, x)
                if e == 'w':
                    move[0] = -1
                elif e == 'a':
                    move[1] = -1
                elif e == 's':
                    move[0] = 1
                elif e == 'd':
                    move[1] = 1
                slf = self.density[self.y][self.x]
                other = self.density[self.y + move[0]][self.x + move[1]]
                if slf in 'wasd':
                    if e != slf:
                        move = [0, 0]
                else:
                    if other in 'wasd' and other != 'wasd'['wasd'.index(e) - 2]:
                        move = [0, 0]
                    elif other == '!':
                        move = [0, 0]
                self.y += move[0]
                self.x += move[1]
                if move == [0, 0]:
                    self.cango = True
                else:
                    self.cango = False
                    point = self.location[self.y][self.x]
                    self.point = Point(point, self.x, self.y, self)
                    self.point.run()
            elif e == 'e':
                self.cango = False
                self.inventory_window()
                self.cango = True

    def about(self):
        self.l_desc.setText('Разработчик: Вавилов К.\nАвтор сюжета: Трифонов В.')

    def tomaker(self):
        self.l_desc.setText('vavikons@mail.ru')

    def new(self):
        self.locn = 0
        # амфибия
        # self.x = 5
        # self.y = 4
        self.x = 4
        self.y = 8
        self.money = 0
        with open(f'start_map_o_{self.locn}.txt', 'r', encoding='utf-8') as s_map:
            self.opens = []
            for line in s_map:
                self.opens.append(list(line))
        self.notes = Text(self, in_b_window=False)

        con = sqlite3.connect("gamedatabase.sqlite")
        cur = con.cursor()
        self.items = {}
        result = cur.execute("""SELECT * FROM items""").fetchall()
        for item in result:
            if item[2] == 'weapon':
                self.items[item[1]] = Weapon(item[1], int(item[3]))
            elif item[2] == 'armor':
                self.items[item[1]] = Armor(item[1], int(item[3]))
            else:
                self.items[item[1]] = Item(item[1])
        self.player = Player('Игрок', 10, self.items['нож'], None, {})
        self.npcs = {}
        result = cur.execute("""SELECT * FROM start_npcs""").fetchall()
        for npc in result:
            self.npcs[npc[1]] = Npc(self, npc[1], tobool(npc[2]),
                                         list(map(int, npc[3].split(','))))
        self.mons = {}
        result = cur.execute("""SELECT * FROM start_mons""").fetchall()
        for mon in result:
            self.mons[mon[1]] = Monster(mon[1], self, self.player, int(mon[2]), int(mon[3]),
                                             int(mon[4]),
                                             Item(self.items[mon[5]].name).setcol(int(mon[6])), True)
        con.close()
        self.cango = False
        self.game()

    def load(self):
        with open(f'main.txt', 'r', encoding='utf-8') as file:
            text = file.read().split('\n')
            self.locn = int(text[0])
            self.x = int(text[1])
            self.y = int(text[2])
            self.money = int(text[3])
        with open(f'saves_map_o_{self.locn}.txt', 'r', encoding='utf-8') as s_map:
            self.opens = []
            for line in s_map:
                self.opens.append(list(line))
        with open(f'notes.txt', 'r', encoding='utf-8') as notes:
            self.notes = Text(self, notes.read().split('\n'))
            self.notes.in_b_window = False

        con = sqlite3.connect("gamedatabase.sqlite")
        cur = con.cursor()
        self.items = {}
        result = cur.execute("""SELECT * FROM items""").fetchall()
        for item in result:
            if item[2] == 'weapon':
                self.items[item[1]] = Weapon(item[1], int(item[3]))
            elif item[2] == 'armor':
                self.items[item[1]] = Armor(item[1], int(item[3]))
            else:
                self.items[item[1]] = Item(item[1])
        self.items['None'] = None
        inw = {}
        result = cur.execute("""SELECT * FROM inw""").fetchall()
        for item in result:
            if item[2] == 'weapon':
                inw[item[1]] = Weapon(item[1], int(item[3]))
            elif item[2] == 'armor':
                inw[item[1]] = Armor(item[1], int(item[3]))
            else:
                inw[item[1]] = Item(item[1], int(item[3]))
        with open(f'player.txt', 'r', encoding='utf-8') as file:
            text = file.read().split('\n')
            self.player = Player(text[0], int(text[1]), self.items[text[2]], self.items[text[3]], inw)
        self.npcs = {}
        result = cur.execute("""SELECT * FROM npcs""").fetchall()
        for npc in result:
            self.npcs[npc[1]] = Npc(self, npc[1], tobool(npc[2]),
                                    list(map(int, npc[3].split(','))))
        self.mons = {}
        result = cur.execute("""SELECT * FROM mons""").fetchall()
        for mon in result:
            self.mons[mon[1]] = Monster(mon[1], self, self.player, int(mon[2]), int(mon[3]),
                                        int(mon[4]),
                                        Item(self.items[mon[5]].name).setcol(int(mon[6])), tobool(mon[7]))
        con.close()
        self.cango = False
        self.game()

    def save(self):
        with open(f'main.txt', 'w', encoding='utf-8') as file:
            file.write(str(self.locn) + '\n')
            file.write(str(self.x) + '\n')
            file.write(str(self.y) + '\n')
            file.write(str(self.money))
        with open(f'saves_map_o_{self.locn}.txt', 'w', encoding='utf-8') as s_map:
            for line in self.opens:
                s_map.write(''.join(line))
        with open(f'notes.txt', 'w', encoding='utf-8') as notes:
            notes.write('\n'.join(self.notes.text))
        with open(f'player.txt', 'w', encoding='utf-8') as file:
            file.write(str(self.player.name) + '\n')
            file.write(str(self.player.hp) + '\n')
            if self.player.weap is not None:
                file.write(str(self.player.weap.name) + '\n')
            else:
                file.write('None')
            if self.player.arm is not None:
                file.write(str(self.player.arm.name) + '\n')
            else:
                file.write('None')

        con = sqlite3.connect("gamedatabase.sqlite")
        cur = con.cursor()
        cur.execute('DELETE from inw')
        for i in range(len(self.player.inw.inw.keys())):
            item = self.player.inw[list(self.player.inw.inw.keys())[i]]
            if item.type == 'weapon':
                command = f"INSERT INTO inw(id,name,type,char) \
VALUES({str(i + 1)},'{item.name}','weapon',{str(item.dam)})"
                cur.execute(command)
            elif item.type == 'armor':
                command = f"INSERT INTO inw(id,name,type,char) \
VALUES({str(i + 1)},'{item.name}','armor',{str(item.save)})"
                cur.execute(command)
            else:
                command = f"INSERT INTO inw(id,name,type,char) \
VALUES({str(i + 1)},'{item.name}','item',{str(item.col)})"
                cur.execute(command)

        cur.execute('DELETE from npcs')
        for i in range(len(self.npcs.keys())):
            ind = list(self.npcs.keys())[i]
            command = f"INSERT INTO npcs(id,name,args0,args1) \
VALUES({str(i + 1)},'{self.npcs[ind].name}',{str(self.npcs[ind].args[0])},\
'{', '.join(map(str, self.npcs[ind].args[1:]))}')"
            cur.execute(command)

        cur.execute('DELETE from mons')
        for i in range(len(self.npcs.keys())):
            ind = list(self.mons.keys())[i]
            command = f"INSERT INTO mons(id,name,hp,save,dam,lut,col,alive) \
VALUES({str(i + 1)},'{self.mons[ind].name}',{str(self.mons[ind].hp)},{str(self.mons[ind].save)},\
{str(self.mons[ind].dam)},'{str(self.mons[ind].lut.name)}',{str(self.mons[ind].lut.col)},{self.mons[ind].alive})"
            cur.execute(command)

        con.commit()
        con.close()

    def game(self):
        try:
            main(self)
        except FileNotFoundError as e:
            print(f'Папка сохранений либо файл оттуда не обнаружены: {e}')
        except BaseException as e:
            print('Обнаружена ошибка.')
            print('Сообщите разработчику ее название и место, в котором произошел вылет.')
            print(e)

    def ext(self):
        sys.exit()

    def setimage(self, name):
        print(f'image: {name} ({str(self.x)}, {str(self.y)})')
        # self.l_image.setText(f'image: {name} ({str(self.x)}, {str(self.y)})')
        try:
            self.im = Image.open('pic/' + name + '.png')
            self.paint = ImageQt(self.im)
            self.pixmap = QPixmap.fromImage(self.paint)
            self.l_image.setPixmap(self.pixmap)
        except FileNotFoundError:
            self.im = Image.open('pic/no_image.png')
            self.paint = ImageQt(self.im)
            self.pixmap = QPixmap.fromImage(self.paint)
            self.l_image.setPixmap(self.pixmap)

    def draw_lbls(self):
        for i in range(10):
            # Убрать
            # print(i + 1, self.player.hp, end=' ')
            if i + 1 <= self.player.hp:
                name = 'hp1'
            else:
                name = 'hp0'
            # print(name)
            self.im = Image.open('pic/' + name + '.png')
            self.paint = ImageQt(self.im)
            self.pixmap = QPixmap.fromImage(self.paint)
            self.hps[i].setPixmap(self.pixmap)
        self.L_hp_num.setText(str(self.player.hp))
        self.im = Image.open('pic/coin.png')
        self.paint = ImageQt(self.im)
        self.pixmap = QPixmap.fromImage(self.paint)
        self.l_coin.setPixmap(self.pixmap)
        self.L_coins.setText(str(self.money))

    def draw_map(self):
        try:
            self.im = Image.open('pic/map' + str(self.locn + 1) + '.png')
            self.paint = ImageQt(self.im)
            self.pixmap = QPixmap.fromImage(self.paint)
            self.l_map.setPixmap(self.pixmap)
        except FileNotFoundError:
            self.im = Image.open('pic/no_image.png')
            self.paint = ImageQt(self.im)
            self.pixmap = QPixmap.fromImage(self.paint)
            self.pixmap = self.pixmap.scaledToHeight(480)
            self.l_map.setPixmap(self.pixmap)
        self.l_map_c = Labella(self)

    def info(self):
        if self.t_info.isHidden():
            self.t_info.show()
            self.t_info.setText('Время в игре: {не добавлено}\nОсталось монстров: {не добавлено}')
        else:
            self.t_info.hide()

    def bt(self):
        if self.t_info.isHidden():
            self.t_info.show()
            self.t_info.setText('Для перемещения используйте клавиши w, a, s и d\nДля открытия инвентаря используйте e')
        else:
            self.t_info.hide()

    def setBtns(self, lst):
        print('btns =', lst)
        self.canpush = True
        for i in range(4):
            if len(lst) >= i + 1:
                self.btns[i].show()
                self.btns[i].setText(lst[i])
            else:
                self.btns[i].hide()

    def btn_c(self):
        if self.canpush:
            self.canpush = False
            source = self.sender()
            self.btn = self.btns.index(source)
            print('> button run')
            self.point.run()


def main(window):
    window.canpush = False
    window.location = [
        ['.............',
         '.......g.....',
         '.......*.....',
         '.....x * x...',
         '...+xx * xx..',
         '..0++ h=h  ..',
         '..hhhhh==---g',
         '*g====h=h....',
         '..hhh=h=h....',
         '....====.....',
         '.............',
         '.............',
         '.............']
    ][window.locn]
    window.density = [
        ['!!!!!!!!!!!!!',
         '!!!!!!!!!!!!!',
         '!!!!!!!.!!!!!',
         '!!!!!.....!!!',
         '!!!........!!',
         '!!....d.!..!!',
         '!!!!!!!.....!',
         '!!....!.!!!!!',
         '!!!!d.a.!!!!!',
         '!!!!....!!!!!',
         '!!!!!!!!!!!!!',
         '!!!!!!!!!!!!!',
         '!!!!!!!!!!!!!']
    ][window.locn]
    point = window.location[window.y][window.x]
    if point in ' *=':
        window.opend_battle_window = True
    else:
        window.opend_battle_window = False
    window.point = Point(point, window.x, window.y, window)
    window.point.run()


def tobool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    elif s == 1:
        return True
    return False


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
