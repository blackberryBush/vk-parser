import time
import datetime


class Post:
    def __init__(self, d: dict):
        self.content_id = d.get("id", "-1")
        self.content_type = d.get("post_type", "post")
        self.date = d.get("date", -1)
        self.owner_id = d.get("owner_id", -1)
        self.owner_content_id = -1
        self.user_id = d.get("from_id", -1)
        self.likes = d.get("likes", -1).get("count", 0)
        self.reposts = d.get("reposts", -1).get("count", 0)
        self.comments = d.get("comments", -1).get("count", 0)

    def __str__(self):
        return f'{self.content_type}: {self.content_id} / time: {self.date} / ' \
               f'owner: {self.owner_id} / user: {self.user_id} / ' \
               f'likes: {self.likes} / reposts: {self.reposts} / comments: {self.comments}'

    def __eq__(self, other):
        if self.content_id == other:
            return True
        return False


def get_raw_posts(vk_api, owner_id):
    time.sleep(0.35)
    first = vk_api.wall.get(owner_id=owner_id, v=5.131)
    data = first["items"]
    count = first["count"] // 100
    if count > 1:
        count = 1
    for i in range(1, count + 1):
        time.sleep(0.35)
        data += vk_api.wall.get(owner_id=owner_id, v=5.131, offset=i * 100)["items"]
        print(f"Идёт парсинг {owner_id}: извлечено {i * 100} записей")
    return data


def get_raw_posts_by_date(vk_api, owner_id, date1, date2):
    # convert datetime to Unix time
    date1_unix = int(date1.timestamp())
    date2_unix = int(date2.timestamp())

    time.sleep(0.35)
    first = vk_api.wall.get(owner_id=owner_id, v=5.131)
    data = first["items"]
    count = first["count"] // 100
    if count > 1:
        count = 1
    for i in range(1, count + 1):
        time.sleep(0.35)
        posts = vk_api.wall.get(owner_id=owner_id, v=5.131, offset=i * 100)["items"]
        for post in posts:
            if date1_unix <= post["date"] <= date2_unix:
                data.append(post)
            elif post["date"] < date1_unix:
                break
        print(f"Идёт парсинг {owner_id}: извлечено {i * 100} записей")
    return data


def get_classed_posts(raw_data):
    data = []
    for i in raw_data:
        data.append(Post(i))
    return data


def get_posts(vk_api, owner_id):
    raw_data = get_raw_posts(vk_api, owner_id)
    return get_classed_posts(raw_data)


def get_posts_by_date(vk_api, owner_id, date1, date2):
    raw_data = get_raw_posts_by_date(vk_api, owner_id, date1, date2)
    return get_classed_posts(raw_data)
