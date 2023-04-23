import csv
import datetime

import pytz as pytz
import vk

from comment import Comment, add_post_comments, get_post_comments_by_date
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
                created_at = datetime.datetime.utcfromtimestamp(item.date)
                user_pair = tuple(sorted([item.user_id, item.owner_id]))

                # calculate time interval and frequency if there is a previous item for the user pair
                if user_pair in user_pairs:
                    writer.writerow(
                        [created_at.strftime('%Y-%m-%d %H:%M:%S'), user_pair[0], user_pair[1], item.date])

                # update count and previous created_at for the user pair
                user_pairs[user_pair] = (created_at, user_pairs.get(user_pair, (None, 0))[1] + 1)


def distribute_lines(filename, time_start, time_slot_length):
    date1_unix = int(time_start.timestamp())

    output_file = filename[:-4] + "_new.csv"  # create a new filename for the output file

    with open(filename, 'r') as input_file, open(output_file, 'w', newline='') as output_file:
        reader = csv.reader(input_file, delimiter=';')
        writer = csv.writer(output_file, delimiter=';')
        header = next(reader)
        writer.writerow(header)

        unique_rows = set()  # to store unique rows based on u1, u2, and time_interval

        # Loop through each row of the input file
        for row in reader:
            u1 = row[1]
            u2 = row[2]
            time_interval = int(row[3])

            current_interval = date1_unix
            while time_interval >= current_interval:
                current_interval += time_slot_length
            created_at = datetime.datetime.utcfromtimestamp(current_interval)

            if (u1, u2, time_interval) not in unique_rows:
                unique_rows.add((u1, u2, time_interval))
                writer.writerow((created_at, u1, u2, time_interval))  # write the row to the output file

    return output_file


if __name__ == "__main__":
    access_token = "0c8512290c8512290c851229580f9745a900c850c8512296f4aca4683b7880e4d7a40d3"  # Service access key
    vk_api = vk.API(access_token=access_token)
    group_id = get_group_id("lentach", vk_api)
    posts_data = get_posts_by_date(vk_api, group_id,
                                   datetime.datetime(2023, 3, 18, 12, 29, 0, tzinfo=pytz.timezone('Europe/London')),
                                   datetime.datetime(2023, 3, 19, 12, 29, 0, tzinfo=pytz.timezone('Europe/London')))
    comments_data = [comment for post in posts_data for comment in
                     get_post_comments_by_date(vk_api, post,
                                               datetime.datetime(2023, 3, 18, 12, 29, 0,
                                                                 tzinfo=pytz.timezone('Europe/London')),
                                               datetime.datetime(2023, 3, 19, 12, 29, 0,
                                                                 tzinfo=pytz.timezone('Europe/London')))]
    posts_data = add_post_comments(posts_data, comments_data)
    sorted_data = sorted(posts_data, key=lambda x: x.date)
    write_to_csv(sorted_data, "data.csv")
    distribute_lines("data.csv", datetime.datetime(2023, 3, 18, 12, 29, 0, tzinfo=pytz.timezone('Europe/London')), 3600)
