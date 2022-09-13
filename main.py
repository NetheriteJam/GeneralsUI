import sys
import pygame
import numpy as np

import random
import queue
from termcolor import colored

dirX = [-1, 1, 0, 0, -1, 1, -1, 1]
dirY = [0, 0, -1, 1, 1, -1, -1, 1]
generated = False

side_tr = {
    0: 'N',  # None
    1: 'B',  # Blue
    2: 'R'  # Red
}
terr_tr = {
    0: '.',  # Empty
    1: 'M',  # Mountain
    2: 'A',  # Army
    3: 'C',  # City
    4: 'K'  # Crown
}
def rnd(l, r):
    return random.randint(l, r)

def prob(numerator, denominator):
    return rnd(1, denominator) <= numerator

def jam_print(side, terr, cnt, n, m):
    for i in range(n):
        for j in range(m):
            cell_str = ''
            if terr[i][j] != 2:
                cell_str += terr_tr[terr[i][j]]
            if cnt[i][j] != 0:
                cell_str += str(cnt[i][j])
            cell_col = 'white'
            cell_on = None
            if side[i][j] == 1:
                cell_on = 'on_blue'
            elif side[i][j] == 2:
                cell_on = 'on_red'
            if terr[i][j] == 1:
                cell_col = 'green'
            elif terr[i][j] == 3 or terr[i][j] == 4:
                cell_col = 'yellow'
            print(colored('{:>3}'.format(cell_str), cell_col, cell_on), end='')
        print('\n', end='')

def jam_generator(n, m, tower_range, mt_range, mt_prob, city_num_range):
    while True:
        tot = n * m
        side = np.zeros(shape=(n, m), dtype=int)
        terr = np.zeros(shape=(n, m), dtype=int)
        # 0:空地 1:山 3:塔 4:皇冠
        cnt = np.zeros(shape=(n, m), dtype=int)
        adj = np.zeros(shape=(n, m), dtype=bool)
        # 是否已存在相邻山脉
        mt = rnd(mt_range[0], mt_range[0])
        # 山脉数量
        towerr = rnd(tower_range[1], tower_range[1])
        # 塔数量
        q = queue.Queue()
        for i in range(n):
            for j in range(m):
                if prob(mt, tot) and not adj[i][j]:
                    terr[i][j] = 1
                    q.put((i, j))
                    for d in range(8):
                        new_x = i + dirX[d]
                        new_y = j + dirY[d]
                        if 0 <= new_x < n and 0 <= new_y < m:
                            adj[new_x][new_y] = True
        adj = np.zeros(shape=(n, m), dtype=bool)
        cntmt = q.qsize()
        while not q.empty():
            (x, y) = q.get()
            for d in range(8):
                new_x = x + dirX[d]
                new_y = y + dirY[d]
                if 0 <= new_x < n and 0 <= new_y < m and not adj[new_x][new_y]:
                    if prob(mt_prob[0], mt_prob[1]):
                        terr[new_x][new_y] = 1
                        cntmt += 1
                        q.put((new_x, new_y))
                    else:
                        adj[new_x][new_y] = True
        city = []
        for i in range(n):
            for j in range(m):
                if terr[i][j] == 1:
                    if prob(towerr * 100, cntmt * 100):
                        terr[i][j] = 3
                        cnt[i][j] = rnd(city_num_range[0], city_num_range[1])
                        city.append((i, j))
        if len(city) < 2:
            continue
        citycnt = len(city)
        crownpair = []
        # 可以组成一对皇冠的城市的下标的二元组
        for i in range(citycnt - 1):
            for j in range(i + 1, citycnt):
                if abs(city[i][0] - city[j][0]) + abs(city[i][1] - city[j][1]) > n // 2 + m // 2:
                    crownpair.append((i, j))
        if len(crownpair) < 1:
            continue
        crownpair_i = rnd(1, len(crownpair)) - 1
        crown_b = city[crownpair[crownpair_i][0]]
        crown_r = city[crownpair[crownpair_i][1]]
        terr[crown_b[0]][crown_b[1]] = 4
        side[crown_b[0]][crown_b[1]] = 1
        cnt[crown_b[0]][crown_b[1]] = 1
        terr[crown_r[0]][crown_r[1]] = 4
        side[crown_r[0]][crown_r[1]] = 2
        cnt[crown_r[0]][crown_r[1]] = 1
        blue = np.zeros(shape=(n, m), dtype=bool)
        q.put(crown_b)
        blue[crown_b[0]][crown_b[1]] = True
        while not q.empty():
            (x, y) = q.get()
            for d in range(4):
                new_x = x + dirX[d]
                new_y = y + dirY[d]
                if 0 <= new_x < n and 0 <= new_y < m:
                    if not blue[new_x][new_y] and (terr[new_x][new_y] == 0 or terr[new_x][new_y] == 4):
                        blue[new_x][new_y] = True
                        q.put((new_x, new_y))
        if not blue[crown_r[0]][crown_r[1]]:
            continue
        else:
            break
    jam_print(side, terr, cnt, n, m)
    return side, terr, cnt

def generate_map():
    tower_min = 10
    tower_max = 12
    # 塔数量范围
    mt_min = 27
    mt_max = 30
    # 山脉数量范围
    mt_prob_numerator = 1800
    mt_prob_denominator = 10000
    # 山脉延申概率分子分母
    city_num_min = 40
    city_num_max = 50
    # 城市范围
    return jam_generator(n, m, (tower_min, tower_max), (mt_min, mt_max),
                         (mt_prob_numerator, mt_prob_denominator), (city_num_min, city_num_max))

def get_map():
    return map_side, map_terr, map_cnt

# 地图长宽
n = 30
m = 30

map_side, map_terr, map_cnt = generate_map()
generated = True

if not generated:
    map_side = np.zeros(shape=(n, m), dtype=int)
    map_terr = np.zeros(shape=(n, m), dtype=int)
    map_cnt = np.zeros(shape=(n, m), dtype=int)

# 初始化窗口和pygame
pygame.init()
img = pygame.image
screen = pygame.display.set_mode((m*32+256, n*32))
pygame.display.set_caption('AlphaGenerals')
pygame.display.set_icon(pygame.image.load('icon.png'))

# 颜色，但似乎没用
color_none = (242, 246, 250)
color_red = (236, 28, 36)
color_blue = (63, 72, 204)

# 初始化 ARMY 和 LAND 字样
text_army = img.load('army.png')
text_land = img.load('land.png')
text_time = img.load('time.png')

# 初始化背景格子图片
block_none = img.load('block_none.png')
block_blue = img.load('block_blue.png')
block_red = img.load('block_red.png')
block_mountain = img.load('block_mountain.png')
block_tower = img.load('block_tower.png')
block_unknown = img.load('block_unknown.png')
block_cover = img.load('block_cover.png')
block_cover.set_alpha(150)

# 初始化内容物图片
frame = img.load('frame.png')
frame_white = img.load('frame_white.png')
tower = img.load('tower.png')
crown = img.load('crown.png')
mountain = img.load('mountain.png')
obstacle = img.load('obstacle.png')
arrow = img.load('arrow.png')
empty = img.load('empty.png')

# 初始化数字图片
numberStr = '0123456789'
number = []
for i in range(10):
    number.append(img.load(numberStr[i]+'.png'))
number_2x = []
for i in range(10):
    number_2x.append(img.load(numberStr[i]+'_2x.png'))
half = img.load('50percent.png')

# 开始界面
screen.fill(color_none)
screen.blit(pygame.image.load('startscreen.png'), (0, 0))

started = False
turn = 0
pygame.display.update()
def pix(x, y):  # 一个格子的左上角坐标
    return y * 32, x * 32
def inside(pos):  # 判断一个点是否在地图内
    return 0 <= pos[0] < n and 0 <= pos[1] < m
def write_cnt(num, x, y):  # 渲染数
    if num == 0:
        if map_terr[x][y] == 3:
            screen.blit(number[0], (y * 32 + 15, x * 32 + 13))
    elif num < 10:
        screen.blit(number[num], (y * 32 + 15, x * 32 + 13))
    elif num < 100:
        screen.blit(number[num % 10], (y * 32 + 18, x * 32 + 13))
        screen.blit(number[num // 10], (y * 32 + 11, x * 32 + 13))
    elif num < 1000:
        screen.blit(number[num % 10], (y * 32 + 22, x * 32 + 13))
        screen.blit(number[(num // 10) % 10], (y * 32 + 15, x * 32 + 13))
        screen.blit(number[num // 100], (y * 32 + 8, x * 32 + 13))
    else:
        screen.blit(number[num % 10], (y * 32 + 25, x * 32 + 13))
        screen.blit(number[(num // 10) % 10], (y * 32 + 18, x * 32 + 13))
        screen.blit(number[(num // 100) % 10], (y * 32 + 11, x * 32 + 13))
        screen.blit(number[num // 1000], (y * 32 + 4, x * 32 + 13))

def operate(select, target, percent):  # 操作
    sel_x = select[0]  # 方便处理
    sel_y = select[1]
    tar_x = target[0]
    tar_y = target[1]
    if percent == 1:  # 准备移动的兵力
        select_cnt = map_cnt[sel_x][sel_y] - 1
    else:
        select_cnt = map_cnt[sel_x][sel_y] // 2
    map_cnt[sel_x][sel_y] -= select_cnt
    if select_cnt == 0:  # 没兵走个毛
        return False
    # 对于每一步合法移动，只可能 空 山 兵 城市
    if map_side[tar_x][tar_y] == 0:  # 走到空地或空塔
        if map_terr[tar_x][tar_y] == 0:  # 走到空地
            map_side[tar_x][tar_y] = 1
            map_terr[tar_x][tar_y] = 2
            map_cnt[tar_x][tar_y] = select_cnt
            return True
        else:  # 走到空塔
            if select_cnt > map_cnt[tar_x][tar_y]:  # 如果可以占领
                map_cnt[tar_x][tar_y] = select_cnt - map_cnt[tar_x][tar_y]
                map_side[tar_x][tar_y] = 1
                return True
            else:
                map_cnt[tar_x][tar_y] -= select_cnt
                return True
    elif map_side[tar_x][tar_y] == 1:  # 走到自己有兵的地方
        map_cnt[tar_x][tar_y] += select_cnt
        return True
    else:  # 走到对面有兵的地方
        if map_terr[tar_x][tar_y] == 2:  # 走到普通的有兵的地方
            if select_cnt > map_cnt[tar_x][tar_y]:  # 如果可以占领
                map_cnt[tar_x][tar_y] = select_cnt - map_cnt[tar_x][tar_y]
                map_side[tar_x][tar_y] = 1
                return True
            else:
                map_cnt[tar_x][tar_y] -= select_cnt
                return True
        elif map_terr[tar_x][tar_y] == 3:  # 走到塔
            if select_cnt > map_cnt[tar_x][tar_y]:  # 如果可以占领
                map_cnt[tar_x][tar_y] = select_cnt - map_cnt[tar_x][tar_y]
                map_side[tar_x][tar_y] = 1
                return True
            else:
                map_cnt[tar_x][tar_y] -= select_cnt
                return True
        else:
            if select_cnt > map_cnt[tar_x][tar_y]:  # 如果可以占领
                map_cnt[tar_x][tar_y] = select_cnt - map_cnt[tar_x][tar_y]
                map_side[tar_x][tar_y] = 1
                return True
            else:
                map_cnt[tar_x][tar_y] -= select_cnt
                return True

def content(x, y):  # 内容物
    if map_terr[x][y] == 1:
        return mountain
    if map_terr[x][y] == 3:
        return tower
    if map_terr[x][y] == 4:
        return crown
    return empty

def update():  # 更新兵力 和 时间 总兵力 总领地大小
    if turn % 2 == 0:
        for i in range(n):
            for j in range(m):
                if map_side[i][j] != 0:
                    if map_terr[i][j] == 3 or map_terr[i][j] == 4:
                        map_cnt[i][j] += 1
    if turn % 50 == 0:
        for i in range(n):
            for j in range(m):
                if map_side[i][j] != 0:
                    map_cnt[i][j] += 1


def get_show(pos):
    i = pos[0]
    j = pos[1]
    ret = (map_side[i][j] == 1)
    for d in range(8):
        newX = i + dirX[d]
        newY = j + dirY[d]
        if 0 <= newX < n and 0 <= newY < m:
            if map_side[newX][newY] == 1:
                ret = True
                break
    return ret

def block_render(pos):
    i = pos[0]
    j = pos[1]
    if get_show(pos):
        if map_side[i][j] == 0:
            if map_terr[i][j] == 3:
                screen.blit(block_tower, pix(i, j))
            else:
                screen.blit(block_none, pix(i, j))
        elif map_side[i][j] == 1:
            screen.blit(block_blue, pix(i, j))
        else:
            screen.blit(block_red, pix(i, j))
        screen.blit(frame, pix(i, j))
        if map_terr[i][j] == 1:
            screen.blit(mountain, pix(i, j))
        elif map_terr[i][j] == 2:
            write_cnt(map_cnt[i][j], i, j)
        elif map_terr[i][j] == 3:
            screen.blit(tower, pix(i, j))
            write_cnt(map_cnt[i][j], i, j)
        elif map_terr[i][j] == 4:
            screen.blit(crown, pix(i, j))
            write_cnt(map_cnt[i][j], i, j)
    else:
        screen.blit(block_unknown, pix(i, j))
        if map_terr[i][j] == 1 or map_terr[i][j] == 3:
            screen.blit(obstacle, pix(i, j))

def deselect_render(pos):  # 重新渲染一个选中的格子及其周围来取消选择
    # 重新渲染选中的格子
    block_render(pos)
    for d in range(4):  # 重新渲染选中的格子四周的格子
        newX = pos[0] + dirX[d]
        newY = pos[1] + dirY[d]
        if inside((newX, newY)):  # 判断四周的格子是否在图中
            block_render((newX, newY))

def select_render(pos):
    screen.blit(frame_white, pix(pos[0], pos[1]))  # 打上选择框
    for d in range(4):  # 给四周可能的目标打上阴影
        newX = pos[0] + dirX[d]
        newY = pos[1] + dirY[d]
        if inside((newX, newY)):  # 判断一个目标是否在地图内
            if get_show((newX, newY)):  # 如果目标显示
                if not map_terr[newX][newY] == 1:  # 不是山的目标才可以走哦
                    screen.blit(block_cover, pix(newX, newY))
                    screen.blit(frame, pix(newX, newY))
            else:
                screen.blit(block_cover, pix(newX, newY))

def write_int(num, pos):
    for i in str(num):
        screen.blit(number_2x[int(i)], pos)
        pos = (pos[0] + 16, pos[1])
selected = 0
select = (-1, -1)
while True:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if not started:
        if event.type == pygame.KEYDOWN:
            started = True
        continue
    map_side, map_terr, map_cnt = get_map()  # 获取地图
    screen.fill(color_none)
    for i in range(n):  # 渲染地图
        for j in range(m):
            block_render((i, j))
    select_render(select)
    # 统计信息
    army_blue = 0  # 总兵力
    army_red = 0
    land_blue = 0  # 总领地大小
    land_red = 0
    for i in range(n):
        for j in range(m):
            if map_side[i][j] == 1:
                land_blue += 1
                army_blue += map_cnt[i][j]
            if map_side[i][j] == 2:
                land_red += 1
                army_red += map_cnt[i][j]
    screen.blit(block_blue, (m * 32 + (16 - 1), 0 + (16 - 1)))  # 渲染玩家信息
    screen.blit(text_land, (m * 32 + (16 - 1) + 32 + 6, 0 + (16 - 1) + 6))
    screen.blit(text_army, (m * 32 + (16 - 1) + 32 + 6, 0 + (16 - 1) + 32 + 6 + 6))
    write_int(land_blue, (m * 32 + (16 - 1) + 32 + 6 + 80, 0 + (16 - 1) + 6))
    write_int(army_blue, (m * 32 + (16 - 1) + 32 + 6 + 80, 0 + (16 - 1) + 32 + 6 + 6))
    screen.blit(block_red, (m * 32 + (16 - 1), 80 + (16 - 1)))  # 渲染玩家信息
    screen.blit(text_land, (m * 32 + (16 - 1) + 32 + 6, 80 + (16 - 1) + 6))
    screen.blit(text_army, (m * 32 + (16 - 1) + 32 + 6, 80 + (16 - 1) + 32 + 6 + 6))
    write_int(land_red, (m * 32 + (16 - 1) + 32 + 6 + 80, 80 + (16 - 1) + 6))
    write_int(army_red, (m * 32 + (16 - 1) + 32 + 6 + 80, 80 + (16 - 1) + 32 + 6 + 6))
    screen.blit(text_time, (m * 32 + (16 - 1) + 32 + 6, 80 + (16 - 1) + 32 + 6 + 6 + 64))
    write_int(turn, (m * 32 + (16 - 1) + 32 + 6 + 80, 80 + (16 - 1) + 32 + 6 + 6 + 64))
    moved = False
    # clock = pygame.time.Clock()
    while not moved:
        for event in pygame.event.get():
            # clock.tick(20)
            if event.type == pygame.QUIT:  # 退出游戏，点叉
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # 按下键盘
                if event.key == pygame.K_w or event.key == pygame.K_UP:  # W或上
                    moveDir = 0
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:  # S或下
                    moveDir = 1
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:  # A或左
                    moveDir = 2
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:  # D或右
                    moveDir = 3
                elif event.key == pygame.K_SPACE:  # 拍空格不动
                    deselect_render(select)
                    selected = 0
                    select = (-1, -1)
                    moved = True
                    break
                else:
                    continue
                if not selected:
                    continue
                # 已经选择了一个格子
                if map_side[select[0]][select[1]] == 1:  # 如果选中的格子是你的，那就尝试朝moveDir方向移动一步
                    target = (select[0] + dirX[moveDir], select[1] + dirY[moveDir])
                    if inside(target) and not map_terr[target[0]][target[1]] == 1:  # 目标可以走
                        if operate(select, target, 1):  # 合法移动
                            moved = True
                            selected = 1
                            deselect_render(select)
                            select = target
                            block_render(select)
                            select_render(select)
                            pygame.display.update()
                            break
                        else:  # 不合法移动，选择目标格子
                            selected = 1
                            deselect_render(select)
                            select = target
                            select_render(select)
                            pygame.display.update()
                    else:  # 目标不能走，取消选择
                        selected = 0
                        deselect_render(select)
                        pygame.display.update()
                        select = (-1, -1)
                else:  # 选中的格子不是你的，就移动选中目标
                    target = (select[0] + dirX[moveDir], select[1] + dirY[moveDir])
                    if inside(target):  # 目标格子在地图内才可以去
                        if get_show(target):  # 目标格子显示
                            if not map_terr[target[0]][target[1]] == 1:  # 如果目标格子不是山，选中目标格子
                                selected = 1
                                deselect_render(select)
                                select = target
                                select_render(select)
                                pygame.display.update()
                        else:  # 目标格子不显示，直接选中目标格子
                            selected = 1
                            deselect_render(select)
                            select = target
                            select_render(select)
                            pygame.display.update()
                    else:  # 目标格子不在地图内，取消选择
                        selected = 0
                        deselect_render(select)
                        pygame.display.update()
                        select = (-1, -1)
            elif event.type == pygame.MOUSEBUTTONDOWN:  # 点击鼠标
                clickPos = (event.pos[1] // 32, event.pos[0] // 32)
                if not inside(clickPos):
                    continue
                if selected == 0:  # 如果点的时候没有选中任何格子，就选上
                    if map_side[clickPos[0]][clickPos[1]] == 1 and map_cnt[clickPos[0]][clickPos[1]] > 0:
                        selected = 1
                        select = clickPos
                        select_render(select)
                        pygame.display.update()
                else:  # 点的时候有选中的格子
                    if select == clickPos:  # 如果点了选中的格子
                        if selected == 1:  # 如果选中100%，变成50%
                            selected = 2
                            screen.blit(block_blue, pix(select[0], select[1]))
                            screen.blit(frame_white, pix(select[0], select[1]))
                            screen.blit(content(select[0], select[1]), pix(select[0], select[1]))
                            screen.blit(half, pix(select[0], select[1]))
                            pygame.display.update()
                        elif selected == 2:  # 如果选中50%，变成没选
                            selected = 0  # 重新渲染选中的格子，选中的格子只可能是你自己的
                            deselect_render(select)
                            pygame.display.update()
                            select = (-1, -1)
                    else:  # 点了一个没选中的格子
                        neighbour = False  # 判断点的地方是否为选中的格子四周（来决定这次点击是不是要走一步）
                        moveDir = -1
                        for d in range(4):  # 枚举选中的格子的四周
                            newX = select[0] + dirX[d]
                            newY = select[1] + dirY[d]
                            if inside((newX, newY)):  # 判断目标是否在地图内
                                if (newX, newY) == clickPos:
                                    moveDir = d
                                    neighbour = True
                        if not neighbour:  # 点的地方不是选中的格子四周
                            if map_side[clickPos[0]][clickPos[1]] == 1:  # 可以选就选上
                                selected = 1
                                deselect_render(select)
                                select = clickPos
                                select_render(select)
                                pygame.display.update()
                            else:  # 不能选就取消选择
                                selected = 0
                                deselect_render(select)
                                select = (-1, -1)
                                pygame.display.update()
                        else:  # 点的地方是选中的格子四周，即走一步
                            if map_side[select[0]][select[1]] == 1:  # 如果选中的格子是你的，那就尝试朝moveDir方向移动一步
                                target = (select[0] + dirX[moveDir], select[1] + dirY[moveDir])
                                if inside(target) and not map_terr[target[0]][target[1]] == 1:  # 目标可以走
                                    if operate(select, target, 1):  # 合法移动
                                        moved = True
                                        selected = 1
                                        deselect_render(select)
                                        select = target
                                        block_render(select)
                                        select_render(select)
                                        pygame.display.update()
                                        break
                                    else:  # 不合法移动，选择目标格子
                                        selected = 1
                                        deselect_render(select)
                                        select = target
                                        select_render(select)
                                        pygame.display.update()
                                else:  # 目标不能走，取消选择
                                    selected = 0
                                    deselect_render(select)
                                    pygame.display.update()
                                    select = (-1, -1)
                            else:  # 选中的格子不是你的，就移动选中目标
                                target = (select[0] + dirX[moveDir], select[1] + dirY[moveDir])
                                if inside(target):  # 目标格子在地图内才可以去
                                    if get_show(target):  # 目标格子显示
                                        if not map_terr[target[0]][target[1]] == 1:  # 如果目标格子不是山，选中目标格子
                                            selected = 1
                                            deselect_render(select)
                                            select = target
                                            select_render(select)
                                            pygame.display.update()
                                    else:  # 目标格子不显示，直接选中目标格子
                                        selected = 1
                                        deselect_render(select)
                                        select = target
                                        select_render(select)
                                        pygame.display.update()
                                else:  # 目标格子不在地图内，取消选择
                                    selected = 0
                                    deselect_render(select)
                                    pygame.display.update()
                                    select = (-1, -1)
    # print("one turn passed")
    turn += 1
    update()
    pygame.display.update()
