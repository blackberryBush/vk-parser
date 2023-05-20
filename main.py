import csv
import datetime
import time

import pytz as pytz
import vk

from comment import Comment, get_post_comments_by_date
from post import Post, get_posts_by_date


def get_groups_or_users_id(links, api_vk):
    ids = []
    print("Получение id пользователей/групп...")
    for link in links:
        time.sleep(0.334)
        ids.append(get_group_or_user_id(link, api_vk))
    return ids


def get_group_or_user_id(link, api_vk):
    try:
        first = -(api_vk.groups.getById(group_id=link, v=5.131))[0]['id']
    except Exception:
        first = (api_vk.users.get(user_ids=link, v=5.131))[0]['id']
    return first


def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["created_at", "u1", "u2", "time_interval"])

        # loop through each item in the data list
        for item in data:
            if isinstance(item, Comment) or isinstance(item, Post):
                created_at = datetime.datetime.utcfromtimestamp(item.date)
                writer.writerow(
                    [created_at.strftime('%Y-%m-%d %H:%M:%S'), item.owner_id, item.user_id, item.date])


def distribute_lines(filename, time_start, time_slot_length):
    date1_unix = int(time_start.timestamp())

    output_file = filename[:-4] + "_new.csv"  # create a new filename for the output file

    with open(filename, 'r') as input_file, open(output_file, 'w', newline='') as output_file:
        reader = csv.reader(input_file, delimiter=';')
        writer = csv.writer(output_file, delimiter=';')
        header = next(reader)
        header.append('frequency')  # add the new column header
        writer.writerow(header)

        unique_rows = set()  # to store unique rows based on u1, u2, and time_interval
        no_unique_rows = dict()

        # Loop through each row of the input file
        for row in reader:

            u1 = row[1]
            u2 = row[2]
            u1, u2 = sorted([u1, u2])
            time_interval = int(row[3])
            if (time_interval % time_slot_length) != 0:
                current_interval = time_interval + time_slot_length - (time_interval % time_slot_length)
            else:
                current_interval = time_interval

            if (u1, u2, current_interval) not in unique_rows:
                unique_rows.add((u1, u2, current_interval))
                no_unique_rows[(u1, u2, current_interval)] = 1
            else:
                no_unique_rows[(u1, u2, current_interval)] += 1

        # Enumerate the no_unique_rows dictionary and write the rows to the output file
        for ((u1, u2, time_interval), frequency) in no_unique_rows.items():
            if u1 != u2:
                created_at = datetime.datetime.utcfromtimestamp(time_interval)
                writer.writerow(
                    [created_at.strftime('%Y-%m-%d %H:%M:%S'), u1, u2,
                     (time_interval - date1_unix) // time_slot_length,
                     frequency])

    return output_file


def correct_parents(comments):
    for comment in comments:
        k = get_parent(comments, comment)
        if k != -1:
            comment.owner_id = k


def get_parent(comments: list, comment: Comment) -> int:
    parent_content_id = comment.owner_content_id
    for comment in comments:
        if comment.content_id == parent_content_id:
            return comment.user_id
    return -1


if __name__ == "__main__":
    access_token = "0c8512290c8512290c851229580f9745a900c850c8512296f4aca4683b7880e4d7a40d3"  # Service access key
    vk_api = vk.API(access_token=access_token)
    groups_ids = get_groups_or_users_id(
        ["gladkov_vv", "v_v_demidov", "belinter", "belgorod_region", "autobelgorod", "newsbelgorod", "belgorod1",
         "pervyj_bgd", "belgorod", "beladm31", "fonartv", "mirbelogorya"], vk_api)
    posts_data = []
    for group_id in groups_ids:
        posts_data += get_posts_by_date(vk_api, group_id,
                                        datetime.datetime(2023, 4, 21, 1, 0, 0,
                                                          tzinfo=pytz.UTC),
                                        datetime.datetime(2023, 4, 22, 19, 0, 0,
                                                          tzinfo=pytz.UTC))
    print("Постов собрано: {}".format(len(posts_data)))
    comments_data = [comment for post in posts_data for comment in
                     get_post_comments_by_date(vk_api, post,
                                               datetime.datetime(2023, 4, 21, 1, 0, 0,
                                                                 tzinfo=pytz.UTC),
                                               datetime.datetime(2023, 4, 22, 19, 0, 0,
                                                                 tzinfo=pytz.UTC))]
    correct_parents(comments_data)
    print("Комментариев собрано: {}".format(len(comments_data)))
    raw_data = posts_data + comments_data
    sorted_data = sorted(raw_data, key=lambda x: x.date)
    write_to_csv(sorted_data, "data.csv")
    distribute_lines("data.csv", datetime.datetime(2023, 4, 21, 3, 0, 0, tzinfo=pytz.utc), 3600)
