import settings as const
import random
import vk
import sys
import os
import shutil
import os.path as P
import re
from requests import *
import time
import datetime

def wait(min):
        sec = min*60
        while sec > 0:
        # Следующий пост через ХХ скунд.
            sys.stdout.write('Следующий пост через '+str(sec)+' скунд.\r')
            sys.stdout.flush()
            time.sleep(1)
            sec -= 1

def normal_name_file(_filename):
    '''
    Убираем лишние символы в названии файла
    '''
    buff = re.sub(r'(^[-])|(.jpg$)|(.JPG$)', '', _filename)
    buff = buff.strip()
    return buff

def autopost(_file_name, _message):
    '''
    Получает сессию ВК
    Грузит в ВК картинку (_file_name)
    Поститэту картинку на стене группы с сообщением (_message)
    '''
    f_log = open(const.MAIN_PATH_PICTURES + 'log.txt', 'a')
    f_log.write('autopost("{}", "{}")\n\t'.format(_file_name, _message))
    while True:
        try:
            print("Пробуем получить сессию от ВК.")
            f_log.write('Пробуем получить сессию от ВК...... ')
            session = vk.AuthSession(app_id=const.APP_ID, user_login=const.MY_LOGIN, user_password=const.MY_PASS, scope='photos, wall')
            vk_API = vk.API(session)
            print("Всё прошло успешно. Проболжаем работу")
            f_log.write('Всё прошло успешно. Проболжаем работу.\n\t\t')
            f_log.write('session: {}\n\t'.format(session))
            break
        except:
            print(session)
            print("\n\tВозникла проблема при получении сессии от ВК. Ждём 5 сек.\n\t")
            time.sleep(5)

    ph = open(_file_name, 'rb')
    f_log.write('Открыли картинку.\n\t\t')
    pfile = post(
        vk_API.photos.getWallUploadServer(
        v=const.VER_API_VK, 
        group_id=const.GROUP_IDP_IMG
        )['upload_url'], 
        files = {'photo': ph}).json()
    f_log.write('pfile: {}\n\t\t'.format(pfile))
    photo = vk_API.photos.saveWallPhoto(
        v=const.VER_API_VK, 
        group_id=const.GROUP_IDP_IMG, 
        server = pfile['server'], 
        photo = pfile['photo'], 
        hash = pfile['hash']
        )[0]
    f_log.write('pfile: {}\n\t\t'.format(photo))

    res = vk_API.wall.post(
        v=const.VER_API_VK, 
        owner_id=const.GROUP_ID_IMG, 
        from_group='1', 
        message=_message, 
        attachment='photo%s_%s'%(photo['owner_id'], photo['id'])
        )
    f_log.write('res: {}\n\t\t'.format(res))
    ph.close()
    f_log.write('Закрыли картинку.\n\t')

    f_log.write('{} - cоздан пост под номером [{}]\n\t'.format(datetime.datetime.now().strftime("%d.%m.%Y-%H:%M:%S"), res['post_id']))
    f_log.write('использованна кртинка по адресу [{}]\n\t\t'.format(_file_name))
    #os.remove(_file_name)
    newpath = _file_name.replace(const.MAIN_PATH_PICTURES, const.MAIN_PATH_PICTURES+'DELETE\\')
    shutil.move(_file_name, newpath)
    f_log.write('файл перемещён!\n')
    f_log.close()
    print('Готово!\n{}\n'.format(res))

def get_nameImages(_path):
    '''
    Получает список файлок из папки _path
    '''
    pth = const.MAIN_PATH_PICTURES + _path
    s = P.exists(pth)
    res = []
    if s:
        for d, dirs, files in os.walk(pth):
            for f in files:
                b = os.path.join(d,f) # формирование адреса 
                #b = normal_name_file(f)
                res.append(b)
                #print (b)
    else:
        print('Директория "{}" не существует!'.format(pth))
    return res

def run(step):
    flist = get_nameImages(const.PATH_IMAGE) # Список файлов из директории
    flist_desc = get_nameImages(const.PATH_IMAGE_HAVE_DESCRIPTIONS) # Список файлов из директории
    l_list = flist.__len__() # Количество файлов
    l_list_desc = flist_desc.__len__() # Количество файлов
    if ((l_list == 0) and (l_list_desc == 0)): # Если файлов вообщет нигде...
        return False # просто выходим
    elif ((l_list > 0) and (l_list_desc > 0)): # Если есть и там и там
        k = round(l_list / l_list_desc) # Берём кратность одной директории к другой (например 3 фотки из одной папки и 1 из другой)
        # 1966 | 633 = 3.105
        item_desc = random.randint(0, l_list_desc-1) # Выбираем случайную картинку c описанием
        shutil.copyfile(flist_desc[item_desc], const.MAIN_PATH_PICTURES + 'upload.jpg')
        autopost(const.MAIN_PATH_PICTURES + 'upload.jpg', normal_name_file(os.path.basename(flist_desc[item_desc]))) # Постим картинку
        newpath = flist_desc[item_desc].replace(const.MAIN_PATH_PICTURES, const.MAIN_PATH_PICTURES+'DELETE\\')
        shutil.move(flist_desc[item_desc], newpath)
        flist_desc.pop(item_desc)
        l_list_desc-=1
        wait(step)
        while k>0:
            item = random.randint(0, l_list-1) # Выбираем случайную картинку
            autopost(flist[item], '') # Постим картинку
            flist.pop(item)
            l_list-=1
            k-=1
            wait(step)
    return True

def main():
    while True:
        run(1)


if __name__ == "__main__":
    main()