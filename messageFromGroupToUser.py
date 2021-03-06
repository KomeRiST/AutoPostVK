import random
import sqlite3
import vk

from requests import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont 

import time
import settings

def glob(step, precent):
    def spl(text, maxlen):
        # Перевод строки по количеству символов. Возвращаем новый текст.
        text1 = ''  # записываем сюда новую строку
        text = text.split('\n')
        for line in text:
            c = 0  # счётчик символов с строке
            for i in line.split():  # проходим по каждому слову
                c += i.__len__()  # прибавляем длину слова
                if c >= maxlen:  # если символов больше максимума
                    text1 += '\n     '  # перенос строки
                    c = i.__len__()  # счётчик равен первому слову в строке
                elif text1 != '':  # условие, чтобы не ставить пробел перед 1-м словом
                    text1 += ' '  # ставим пробел после непоследнего слова в строке
                    c += 1  # учитываем его в счётчике
                text1 += i  # прибавляем слово
            text1 += '\n'  # прибавляем слово
        return text1

    def create_imgDrawer(val):
        # Рисуем заготовку для наложения текста
        # val('путь к картинке')
        # val({"size": (800, 600), "color": (100, 200, 0, 0)})
        if type(val).__name__ == 'str':
            img = Image.open(val).convert('RGBA') # открываем фон
            imgDrawer = ImageDraw.Draw(img) # отрисовываем фон
        else:
            img = Image.new('RGBA', val['size'], val['color']) # создаём фон
            imgDrawer = ImageDraw.Draw(img) # отрисовываем фон
        return imgDrawer, img

    def add_Title_txtDrawer(text, size=144, color=(0,0,0, 170), align='center', spicer=50):
        font = ImageFont.truetype("DualityRegular.otf", size) # Настраиваем шрифт для заголовка
        font_size = font.getsize(text) # Узнаём размер текста
        font_width = font_size[0] # Узнаём ширину текста
        font_height = font_size[1] # Узнаём высоту текста
        txtDrawer.multiline_text(xy=((img.size[0] // 2) - (font_width // 2), spicer), text=text, font=font, fill=color, align=align) # рисуем текст, с позиционированием
        return (font_height * 2)

    def add_Desc_txtDrawer(text, size=50, color=(0,0,0, 170), align='left', spicer=200):
        font = ImageFont.truetype("DualityRegular.otf", size) # Настраиваем шрифт для заголовка
        txtDrawer.multiline_text(xy=(200, spicer), text=text, font=font, fill=color, spacing=25, align=align) # рисуем текст, с позиционированием
    
    def get_Random_word_desc():
        conn = sqlite3.connect("ojegov.db") # или :memory: чтобы сохранить в RAM
        cursor = conn.cursor()
        # Получаем количество слов в БД
        sql = "SELECT COUNT(word) as c FROM words;"
        cursor.execute(sql)
        max_word = cursor.fetchall()[0][0]
        if max_word == 0:
            NULL_BD = True
            return ('', '', '-'*51, 2)
        else:
            rand_word = random.randint(1, max_word)
            #rand_word = 29456 #33250
            # Получаем случайное слово
            sql = "SELECT word FROM words WHERE id={};".format(rand_word) #rand_word
            cursor.execute(sql)
            title = cursor.fetchall()[0][0]

            sql = "SELECT description FROM descriptions WHERE id={};".format(rand_word) #rand_word
            cursor.execute(sql)
            desc = cursor.fetchall()[0][0]

            sql = "DELETE FROM words WHERE id={};".format(rand_word) #rand_word

            d=desc.replace('&acute;', "'")
            d=d.replace('<1>', '')
            d=d.replace('</1>', '')
            d=d.replace('<2>', '')
            d=d.replace('</2>', '')
            d=d.replace('<9>', '\n')
            #d=d.split('\n')
            desc=spl(d, 60)
            length = len(desc.split('\n'))
            return (title, desc, rand_word, length)

    while True:
        popytka = 0
        lins = 1
        col = 0
        while ((lins <= 1) or (col <= 50)):
            popytka += 1
            word, desc, id_w, lins = get_Random_word_desc()
            col = len(desc)
        imgDrawer, img = create_imgDrawer("original.jpg")
        txt = Image.new('RGBA', img.size, (255,255,255,0))
        txtDrawer = ImageDraw.Draw(txt)
        spiser = add_Title_txtDrawer(text=word)
        add_Title_txtDrawer(text="[id:{} | p:{}]".format(id_w, popytka), size=24, spicer=5)
        add_Desc_txtDrawer(text=desc, spicer=spiser)
        out = Image.alpha_composite(img, txt)
        out.save("pil-example.png") # сохраняем в файл

        session = vk.Session(ACC_TOKEN_VK_FULL)
        vk_API = vk.API(session)

        ran_id = random.randint(0, MAX_INT32)

        pfile = post(vk_API.photos.getMessagesUploadServer(v=VER_API_VK, peer_id='0')['upload_url'], files = {'photo': open('pil-example.png', 'rb')}).json()
        photo = vk_API.photos.saveMessagesPhoto(v=VER_API_VK, server = pfile['server'], photo = pfile['photo'], hash = pfile['hash'])[0]
        vk_API.messages.send(v=VER_API_VK, user_id=MY_ID, random_id=ran_id, peer_id='0', message='#'+word, attachment='photo%s_%s'%(photo['owner_id'], photo['id']))

        p = int(step * precent / 100)
        p = random.randint(-p, p)

        time.sleep(step+p)

glob(60*15, 23)