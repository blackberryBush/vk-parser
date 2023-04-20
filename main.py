import csv
import time
from datetime import datetime

import vk

from comment import get_post_comments, add_post_comments, Comment
from post import get_posts, Post, get_posts_by_date


# s.insert
# data format: owner_type, owner_id, content_type, content_id, user_type, user_id, date (unixtime)
# owner_type: club, user (nearest)
# content_type: post, like, repost
# user_type: club, user, club_admin


def get_members(groupid):
    first = vk_api.groups.getMembers(group_id=groupid, v=5.92)
    data = first["items"]
    count = first["count"] // 1000
    for i in range(1, count + 1):
        data = data + vk_api.groups.getMembers(group_id=groupid, v=5.92, offset=i * 1000)["items"]
        print(f"Идёт парсинг {groupid}: извлечено {i * 1000} постов")
        time.sleep(0.5)
    return data


def get_group_id(group_link):
    first = vk_api.groups.getById(group_id=group_link, v=5.131)
    return -first[0]['id']


def get_data_fields(data, *fields):
    fields_len = len(fields)
    if fields_len == 0:
        return []
    for i in range(len(data)):
        for column in data[i].keys():
            if column not in fields:
                del data[i][column]
    return data


# Returnable fields for each note:
# id, owner_id, from_id, date (unixtime), text,
# reply_owner_id, reply_post_id, comments, copyright,
# likes, reposts, views and others


def save_data(data, filename="data.txt"):
    with open(filename, "w") as file:
        for item in data:
            file.write(str(item) + "\n")


def enter_data(filename="data.txt"):  # Функция ввода базы из txt файла
    with open(filename) as file:  # Открываем файл на чтение
        b = []
        # Записываем каждую строчку файла в список,
        # убирая "vk.com/id" и "\n" с помощью среза.
        for line in file:
            b.append(line[9:len(line) - 1])
    return b


def get_intersection(group1, group2):
    group1 = set(group1)
    group2 = set(group2)
    intersection = group1.intersection(group2)  # Находим пересечение двух множеств
    all_members = len(group1) + len(group2) - len(intersection)
    result = len(intersection) / all_members * 100  # Высчитываем пересечение в процентах
    print("Пересечение аудиторий: ", round(result, 2), "%", sep="")
    return list(intersection)


def union_members(group1, group2):
    group1 = set(group1)
    group2 = set(group2)
    union = group1.union(group2)  # Объединяем два множества
    return list(union)


def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["created_at", "u1", "u2", "time_interval"])

        # dictionary to keep track of the count of items for each user pair
        user_pairs = {}

        # loop through each item in the data list
        for item in data:
            if isinstance(item, Comment):
                created_at = datetime.utcfromtimestamp(item.date)
                user_pair = tuple(sorted([item.user_id, item.owner_id]))
            elif isinstance(item, Post):
                created_at = datetime.utcfromtimestamp(item.date)
                user_pair = tuple(sorted([item.user_id, item.owner_id]))

            # calculate time interval and frequency if there is a previous item for the user pair
            if user_pair in user_pairs:
                # prev_created_at, count = user_pairs[user_pair]
                # time_interval = (created_at - prev_created_at).total_seconds()
                time_interval = item.date
                # frequency = count / time_interval
                writer.writerow([created_at.strftime('%Y-%m-%d %H:%M:%S'), user_pair[0], user_pair[1], time_interval])

            # update count and previous created_at for the user pair
            user_pairs[user_pair] = (created_at, user_pairs.get(user_pair, (None, 0))[1] + 1)


"""def trim_and_split(lst, time_frame, interval_dim):
    for entry in lst:
        print(entry.date)

    print("\n", time_frame)

    start_time, end_time = time_frame
    interval_seconds = (end_time - start_time) // interval_dim
    result = []
    for entry in lst:
        if start_time <= entry.date <= end_time:
            entry.date = entry.date - entry.date % interval_seconds
            result.append(entry)
    return result
"""


if __name__ == "__main__":
    token = "0c8512290c8512290c851229580f9745a900c850c8512296f4aca4683b7880e4d7a40d3"  # Сервисный ключ доступа
    vk_api = vk.API(access_token=token)
    gid = get_group_id("lentach")
    data1 = get_posts_by_date(vk_api, gid, datetime(2023, 3, 18, 12, 30, 0), datetime(2023, 3, 19, 12, 30, 0))
    # data1 = get_posts(vk_api, gid)
    data2 = []
    for ii in data1:
        data2 += get_post_comments(vk_api, ii)
    data1 = add_post_comments(data1, data2)
    # save_data(data1)
    unix_time = int(time.mktime(time.strptime("2023-03-24 12:00:00", "%Y-%m-%d %H:%M:%S")))
    unix_time1 = int(time.mktime(time.strptime("2023-03-23 12:00:00", "%Y-%m-%d %H:%M:%S")))
    # data = trim_and_split(data1, {unix_time1, unix_time}, 60)
    write_to_csv(data1, "data.csv")
