import time


class Comment:
    def __init__(self, data):
        self.raw_data = data
        self.content_id = data.get("id", "-1")
        self.content_type = "comment"
        self.date = data.get("date", -1)
        if self.date != -1:
            self.date += 3600 * 3
        self.owner_id = data.get("reply_to_user", -1)
        if self.owner_id == -1:
            self.owner_id = data.get("owner_id", -1)
        self.owner_content_id = data.get("reply_to_comment", -1)
        if self.owner_content_id == -1:
            try:
                self.owner_content_id = data.get("parents_stack", [-1])[0]
            except IndexError:
                self.owner_content_id = -1
        if self.owner_content_id == -1:
            self.owner_content_id = data.get("post_id", -1)
        self.user_id = data.get("from_id", -1)
        likes = data.get("likes", -1)
        self.likes = likes.get("count") if isinstance(likes, dict) else likes
        thread = data.get("thread", -1)
        self.comments = thread.get("count") if thread != -1 else 0

    def __str__(self):
        return str(self.raw_data)

    def __eq__(self, other):
        return self.content_id == other


def get_threads_by_date(vk_api, post, data, date1, date2, last_check=0):
    for i in range(last_check, len(data)):
        if data[i].comments > 0:
            raw_data = get_raw_comment_replies_by_date(vk_api, post.owner_id, data[i].content_id, date1, date2)
            data += get_classed_post_comments(raw_data)
    return data


def get_post_comments_by_date(vk_api, post, date1, date2):
    if post.comments == 0:
        return []
    raw_data = get_raw_post_comments_by_date(vk_api, post.owner_id, post.content_id, date1, date2)
    data = get_classed_post_comments(raw_data)
    data = get_threads_by_date(vk_api, post, data, date1, date2)
    return data


def get_raw_post_comments_by_date(vk_api, owner_id, post_id, date1, date2):
    date1_unix = int(date1.timestamp())
    date2_unix = int(date2.timestamp())

    time.sleep(0.334)
    first = vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, count=100, need_likes=1, v=5.131)
    data = list()
    count = first["count"] // 100
    if count < 1:
        count = 1
    print(f"Идёт парсинг комментов {owner_id}, запись {post_id}")
    for i in range(count):
        time.sleep(0.334)
        need_break = False
        comments = vk_api.wall.getComments(v="5.131", owner_id=owner_id, post_id=post_id, count=100, need_likes=1,
                                           offset=i * 100)["items"]
        for comment in comments:
            if date1_unix <= comment["date"] <= date2_unix:
                data.append(comment)
            elif comment["date"] < date1_unix:
                need_break = True
                break
        if need_break:
            break
        print(f"Идёт парсинг {owner_id}, запись {post_id}: извлечено {len(comments)} записей")
    return data


def get_classed_post_comments(raw_data):
    return [Comment(item) for item in raw_data if not item.get("deleted", False)]


def get_raw_comment_replies_by_date(vk_api, owner_id, comment_id, date1, date2):
    date1_unix = int(date1.timestamp())
    date2_unix = int(date2.timestamp())

    time.sleep(0.334)
    first = vk_api.wall.getComments(owner_id=owner_id, comment_id=comment_id, count=100, need_likes=1, v=5.131)
    data = list()
    count = first["count"] // 100
    if count < 1:
        count = 1
    print(f"Идёт парсинг комментов {owner_id}, коммент {comment_id}")
    for i in range(count):
        time.sleep(0.334)
        need_break = False
        comments = vk_api.wall.getComments(owner_id=owner_id, comment_id=comment_id, count=100, need_likes=1,
                                           offset=i * 100, v=5.131)["items"]
        for comment in comments:
            if date1_unix <= comment["date"] <= date2_unix:
                data.append(comment)
            elif comment["date"] < date1_unix:
                need_break = True
                break
        if need_break:
            break
        print(f"Идёт парсинг {owner_id}, коммент {comment_id}: извлечено {len(comments)} реплаев")
    return data


def add_post_comments(data: list, data_comments: list) -> list:
    for i in data_comments:
        try:
            ind = data.index(i.owner_content_id)
        except ValueError:
            ind = -1
        data.insert(ind + 1, i)
    return data
