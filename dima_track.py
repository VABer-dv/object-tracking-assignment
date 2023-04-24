def tracker_strong(el, new_obj, last_frame, last_frame_2, last_frame_3):
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

    # Для первого фрейма ставим значения по порядку
    if el["frame_id"] == 1:
        for obj in el["data"]:
            obj["track_id"] = new_obj
            new_obj += 1
        return el, new_obj, el, el, el

    # Распарсим 3 послеждних фрема, чтобы получить из них {track_id: bounding_box}
    last_data_1 = {i["track_id"]: i["bounding_box"] for i in last_frame["data"] if i["bounding_box"]}
    last_data_2 = {i["track_id"]: i["bounding_box"] for i in last_frame_2["data"] if i["bounding_box"]}
    last_data_3 = {i["track_id"]: i["bounding_box"] for i in last_frame_3["data"] if i["bounding_box"]}

    
    # Пройдёмся по всем объектам
    for obj in el["data"]:
        bb = obj["bounding_box"]
        if bb:
            # Посчитаем расстояния до всех объектов на каждом фрейме
            dist_1 = {k:dist(v, bb) for k, v in last_data_1.items()}
            dist_2 = {k:dist(v, bb) for k, v in last_data_2.items()}
            dist_3 = {k:dist(v, bb) for k, v in last_data_3.items()}
            
            all_keys = list(set(list(dist_1.keys()) + list(dist_2.keys()) + list(dist_3.keys())))
            
            # Посчитаем средние расстояния до объектов
            mean_data = {}
            for key in all_keys:
                all_values = []
                for dist_ in [dist_1, dist_2, dist_3]:
                    if key in dist_.keys():
                        all_values.append(dist_[key])
                mean_data[key] = np.mean(all_values)
            
            # Найдём минимальное расстояние по 3м предыдущим кадрам
            idx_min = np.argmin(mean_data.values())
            obj["track_id"] = list(mean_data.keys())[idx_min]
            _ = mean_data.pop(obj["track_id"])

    return el, new_obj, el, last_frame, last_frame_2