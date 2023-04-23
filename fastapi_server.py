from fastapi import FastAPI, WebSocket
from track_4 import track_data, country_balls_amount
import asyncio
import glob
import numpy as np
import json

app = FastAPI(title='Tracker assignment')
imgs = glob.glob('imgs/*')
country_balls = [{'cb_id': x, 'img': imgs[x % len(imgs)]} for x in range(country_balls_amount)]
print('Started')


def dist(a, b):
    return sum(abs(np.array(a) - np.array(b)))


def tracker_soft(el, new_obj, last_frame):
    """
    Необходимо изменить у каждого словаря в списке значение поля 'track_id' так,
    чтобы как можно более длительный период времени 'track_id' соответствовал
    одному и тому же кантри болу.

    Исходные данные: координаты рамки объектов

    Ограничения:
    - необходимо использовать как можно меньше ресурсов (представьте, что
    вы используете embedded устройство, например Raspberri Pi 2/3).
    -значение по ключу 'cb_id' является служебным, служит для подсчета метрик качества
    вашего трекера, использовать его в алгоритме трекера запрещено
    - запрещается присваивать один и тот же track_id разным объектам на одном фрейме
    """

    # Проходимся по новому объекту и присваиваем новый id на первом фрейме
    if el["frame_id"] == 1:
        for obj in el["data"]:
            obj["track_id"] = new_obj
            new_obj += 1
        # Перед выходом запомним послежний фрейм
        last_frame = el
        return el, new_obj, last_frame

    # Если фрейм уже не первый...
    # Смотрим предыдущий фрейм
    last_data = {i["track_id"]: i["bounding_box"] for i in last_frame["data"] if i["bounding_box"]}
    for obj in el["data"]:
        bb = obj["bounding_box"]
        if not last_data:
            obj["track_id"] = new_obj
            new_obj += 1
        if bb and last_data:
            idx_min = np.argmin([dist(i, bb) for i in last_data.values()])
            obj["track_id"] = list(last_data.keys())[idx_min]
            _ = last_data.pop(obj["track_id"])
    return el, new_obj, last_frame


def tracker_strong(el):
    """
    Необходимо изменить у каждого словаря в списке значение поля 'track_id' так,
    чтобы как можно более длительный период времени 'track_id' соответствовал
    одному и тому же кантри болу.

    Исходные данные: координаты рамки объектов, скриншоты прогона

    Ограничения:
    - вы можете использовать любые доступные подходы, за исключением
    откровенно читерных, как например захардкодить заранее правильные значения
    'track_id' и т.п.
    - значение по ключу 'cb_id' является служебным, служит для подсчета метрик качества
    вашего трекера, использовать его в алгоритме трекера запрещено
    - запрещается присваивать один и тот же track_id разным объектам на одном фрейме

    P.S.: если вам нужны сами фреймы, измените в index.html значение make_screenshot
    на true для первого прогона, на повторном прогоне можете читать фреймы из папки
    и по координатам вырезать необходимые регионы.
    TODO: Ужасный костыль, на следующий поток поправить
    """
    return el


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket.accept()
    # отправка служебной информации для инициализации объектов
    # класса CountryBall на фронте
    await websocket.send_text(str(country_balls))
    created_track = []
    new_obj = 0
    last_frame = None
    for el in track_data:
        await asyncio.sleep(0.5)
        el, new_obj, last_frame = tracker_soft(el, new_obj, last_frame)
        created_track.append(el)
        # TODO: part 2
        # el = tracker_strong(el)
        # отправка информации по фрейму
        await websocket.send_json(el)

    for frame in created_track:
        list_of_ids = [i["track_id"] for i in frame["data"] if i["track_id"]]
        if len(list_of_ids) != len(set(list_of_ids)):
            print("ERROR!!!", frame["frame_id"], "Frame has the same ids")

    with open("created_track.json", "w") as f:
        json.dump(created_track, f)



    print('Bye..')
