from datetime import datetime
import requests
import os
from tqdm import tqdm
import json


def get_photos(owner, album):
    with open('vk.cfg', 'r') as file:
        TOKEN = file.read().strip()

    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': owner,
        'album_id': album,
        'extended': 1,
        'access_token': TOKEN,
        'v': '5.131'
    }

    res = requests.get(url=url, params=params)

    if not os.path.isdir('photos'):
        os.mkdir('photos')
    res = res.json()
    counter = 0
    while counter <= 5:
        for photo in tqdm(res['response']['items']):

            for size in photo['sizes']:
                if 'w' in size['type']:

                    name_file = f'{photo["likes"]["count"]}'
                    counter += 1
                    if os.path.isfile(f'{os.path.join(os.getcwd(), "photos", name_file)}.jpeg') is False:
                        photo_info = {'file_name': str(photo["likes"]["count"]), 'size': 'w'}

                        with open(f'{os.path.join(os.getcwd(), "photos", name_file)}.jpeg', "wb") as p:
                            resp = requests.get(size['url'])
                            p.write(resp.content)

                        if not os.path.isdir('photo_data'):
                            os.mkdir('photo_data')
                        with open(f'{os.path.join(os.getcwd(), "photo_data", name_file)}.json', "w") as f:
                            json.dump(photo_info, f, ensure_ascii=False, indent=2)

                            print('Фото сохранилось, совпадений нет')

                    else:
                        date = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')
                        name = f'{str(photo["likes"]["count"])} {date}'
                        photo_info = {'file_name': name, 'size': 'w'}

                        with open(f'{os.path.join(os.getcwd(), "photos", name)}.jpeg', "wb") as p:
                            resp = requests.get(size['url'])
                            p.write(resp.content)

                        with open(f'{os.path.join(os.getcwd(), "photo_data", name)}.json', "w") as f:
                            json.dump(photo_info, f, ensure_ascii=False, indent=2)
                            print('Есть совпадение, фото сохранено')


# Ниже указываем id, profile для загрузки аватарок
get_photos()


def upload_file(file_path, ydisk_file_path, replace=False):
    with open('YD.cfg', 'r') as file:
        TOKEN = file.read().strip()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': TOKEN
    }
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    res = requests.get(f'{url}/upload?path={ydisk_file_path}&overwrite={replace}', headers=headers).json()

    with open(file_path, 'rb') as f:
        try:
            req = requests.put(res['href'], files={'file': f})
            req.raise_for_status()
            print('Фото успешно загружено')
        except KeyError:
            print('Файл не загружен')
            print(res)


files = []
for root, directories, filenames in os.walk('photos'):
    for filename in tqdm(filenames):
        file_path = os.path.join(os.getcwd(), 'photos', filename)
        files.append(file_path)
        upload_file(file_path=f'{file_path}', ydisk_file_path=f'PythonTest/{filename}')
