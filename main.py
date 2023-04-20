import csv
from datetime import datetime

import vk

from comment import Comment, add_post_comments, get_post_comments
from post import Post, get_posts_by_date


def get_group_id(group_link, api_vk):
    first = api_vk.groups.getById(group_id=group_link, v=5.131)
    return -first[0]['id']


def write_to_csv(data, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["created_at", "u1", "u2", "time_interval"])

        # dictionary to keep track of the count of items for each user pair
        user_pairs = {}

        # loop through each item in the data list
        for item in data:
            if isinstance(item, Comment) or isinstance(item, Post):
                created_at = datetime.utcfromtimestamp(item.date)
                user_pair = tuple(sorted([item.user_id, item.owner_id]))

                # calculate time interval and frequency if there is a previous item for the user pair
                if user_pair in user_pairs:
                    writer.writerow(
                        [created_at.strftime('%Y-%m-%d %H:%M:%S'), user_pair[0], user_pair[1],  item.date])

                # update count and previous created_at for the user pair
                user_pairs[user_pair] = (created_at, user_pairs.get(user_pair, (None, 0))[1] + 1)


if __name__ == "__main__":
    token = "0c8512290c8512290c851229580f9745a900c850c8512296f4aca4683b7880e4d7a40d3"  # Сервисный ключ доступа
    vk_api = vk.API(access_token=token)
    gid = get_group_id("lentach", vk_api)
    data1 = get_posts_by_date(vk_api, gid, datetime(2023, 3, 18, 12, 30, 0), datetime(2023, 3, 19, 12, 30, 0))
    data2 = [comment for post in data1 for comment in get_post_comments(vk_api, post)]
    data1 = add_post_comments(data1, data2)
    write_to_csv(data1, "data.csv")
