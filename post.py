import time


class Post:
    def __init__(self, d):
        self.raw_data = d
        self.content_id = d.get("id", "-1")
        self.date = d.get("date", -1)
        if self.date != -1:
            self.date += 3600 * 3
        self.owner_id = d.get("owner_id", -1)
        self.owner_content_id = -1
        self.user_id = d.get("from_id", -1)
        self.reposts = d.get("reposts", {}).get("count", 0)
        self.comments = d.get("comments", {}).get("count", 0)

    def __str__(self):
        return str(self.raw_data)


def get_raw_posts_by_date(vk_api, owner_id, date1, date2):
    date1_unix = int(date1.timestamp())
    date2_unix = int(date2.timestamp())

    time.sleep(0.334)
    first = vk_api.wall.get(owner_id=owner_id, v=5.131)
    data = list()
    count = first["count"] // 100
    if count < 1:
        count = 1
    for i in range(count):
        time.sleep(0.334)
        need_break = False
        posts = vk_api.wall.get(owner_id=owner_id, v=5.131, count=100, offset=i * 100)["items"]
        for post in posts:
            if date1_unix <= post["date"] <= date2_unix:
                data.append(post)
            elif post["date"] < date1_unix:
                need_break = True
                break
        if need_break:
            break
        print(f"Идёт парсинг постов {owner_id}: извлечено {len(posts)} записей")
    return data


def get_classed_posts(raw_data):
    return [Post(i) for i in raw_data]


def get_posts_by_date(vk_api, owner_id, date1, date2):
    raw_data = get_raw_posts_by_date(vk_api, owner_id, date1, date2)
    return get_classed_posts(raw_data)
