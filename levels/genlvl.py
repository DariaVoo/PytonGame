import random
from datetime import datetime

import arcade

from ability.abilityFactory import ability_factory
from constants import SPRITE_SCALING, SPRITE_SCALING_COIN
from enemies.enemyFactory import create_enemies
from position import Position


def genlvl(box):
    start_time = datetime.now()

    # lvl_width = random.randint(20, 50)
    lvl_height = random.randint(20, 50)
    lvl_width = 35

    lvl = []
    strings = []

    print('ширина уровня :', lvl_width)
    print('высота уровня :', lvl_height)

    i = 0
    cf = 0
    while i < lvl_width:
        strings.append('-')
        i = i + 1
    lvl.append(list(strings))
    strings.clear()

    q = 0
    while q < lvl_height - 2:
        w = 0
        strings.append('-')
        while w < lvl_width - 2:
            strings.append(' ')
            w = w + 1
            cf = cf + 1
        strings.append('-')
        lvl.append(list(strings))
        strings.clear()
        q = q + 1

    i = 0
    while i < lvl_width:
        strings.append('-')
        i = i + 1
    lvl.append(list(strings))
    strings.clear()

    print("pustix", cf)

    block_count = cf / 5
    i = 0
    while i < block_count:
        y_block = random.randint(2, len(lvl) - 1)
        x_block = random.randint(2, len(lvl[1]) - 1)
        lvl[y_block][x_block] = "-"
        i = i + 1

    print(lvl[1][1])
    print(y_block, x_block, lvl[y_block])

    coin_count = cf / 8
    i = 0
    while i < coin_count:
        y_coin = random.randint(2, len(lvl) - 1)
        x_coin = random.randint(2, len(lvl[1]) - 1)
        if lvl[y_coin][x_coin] != '-':
            lvl[y_coin][x_coin] = '*'
        i = i + 1
    enemy_count = cf / 25
    i = 0
    while i < enemy_count:
        y_enemy = random.randint(2, len(lvl) - 1)
        x_enemy = random.randint(2, len(lvl[1]) - 1)
        if lvl[y_enemy][x_enemy] != '-':
            lvl[y_enemy][x_enemy] = '%'
        i = i + 1
    abi_count = cf / 15
    i = 0

    while i < abi_count:
        y_abi = random.randint(2, len(lvl) - 1)
        x_abi = random.randint(2, len(lvl[1]) - 1)
        if lvl[y_abi][x_abi] != '-':
            lvl[y_abi][x_abi] = '#'
        i = i + 1

    lvl[lvl_height - 2][lvl_width - 1] = ' '

    i = 0
    while i < lvl_height:
        lvl[i] = ''.join(lvl[i])
        i = i + 1

    print(datetime.now() - start_time)

    wall_list = arcade.SpriteList()
    coin_list = arcade.SpriteList()
    pos_enemy = []
    pos_ability = []
    scale_cords = 51.2

    x = y = 0  # координаты
    wall = arcade.Sprite(box, SPRITE_SCALING)
    for row in lvl:  # вся строка
        for col in row:  # каждый символ
            if col == "-":
                # создаем блок
                wall = arcade.Sprite(box, SPRITE_SCALING)
                wall.center_x = x
                wall.center_y = y
                wall_list.append(wall)

            x += wall._get_width()  # блоки платформы ставятся на ширине блоков
        y += wall._get_height()  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    x = y = 0  # координаты
    coin = arcade.Sprite(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)
    for row in lvl:  # вся строка
        for col in row:  # каждый символ
            if col == "*":
                # создаем блок
                coin = arcade.Sprite(":resources:images/items/coinGold.png", SPRITE_SCALING_COIN)
                coin.center_x = x
                coin.center_y = y
                coin_list.append(wall)

            x += coin._get_width()  # блоки платформы ставятся на ширине блоков
        y += coin._get_height()  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    x = y = 0  # координаты
    for row in lvl:  # вся строка
        for col in row:  # каждый символ
            if col == "%":
                # добавляем позицию врака
                x = scale_cords * x
                y = scale_cords * y
                type = random.randint(1, 3)
                pos_enemy.append(Position(x, y, type))

            x += 1
        y += 1  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    x = y = 0  # координаты
    for row in lvl:  # вся строка
        for col in row:  # каждый символ
            if col == "#":
                # добавляем позицию абилки
                x = scale_cords * x
                y = scale_cords * y
                type = random.randint(1, 3)
                pos_ability.append(Position(x, y, type))
            x += 1
        y += 1  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    ability_list = ability_factory(pos_ability)
    enemy_list = create_enemies(pos_enemy)
    return wall_list, coin_list, ability_list, enemy_list