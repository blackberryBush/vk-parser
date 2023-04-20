import time


class Comment:
    def __init__(self, data):
        self.content_id = data.get("id", "-1")
        self.content_type = "comment"
        self.date = data.get("date", -1)
        self.owner_id = data.get("reply_to_user", -1) or data.get("owner_id", -1)
        self.owner_content_id = (
                data.get("reply_to_comment", -1)
                or data.get("parents_stack", [-1])[0]
                or data.get("post_id", -1)
        )
        self.user_id = data.get("from_id", -1)
        likes = data.get("likes", -1)
        self.likes = likes.get("count") if isinstance(likes, dict) else likes
        thread = data.get("thread", -1)
        self.comments = thread.get("count") if thread != -1 else 0

    def __str__(self):
        return (
            f"{self.content_type}: {self.content_id} / time: {self.date} / "
            f"owner: {self.owner_id} / owner_content_id: {self.owner_content_id} / user: {self.user_id} / "
            f"likes: {self.likes} / comments: {self.comments}"
        )

    def __eq__(self, other):
        return self.content_id == other


def get_threads(vk_api, post, data, last_check=0):
    for i in range(last_check, len(data)):
        if data[i].comments > 0:
            raw_data = get_raw_comment_replies(vk_api, post.owner_id, data[i].content_id)
            data += get_classed_post_comments(raw_data)
    return data


def get_post_comments(vk_api, post):
    if post.comments == 0:
        return []
    raw_data = get_raw_post_comments(vk_api, post.owner_id, post.content_id)
    data = get_classed_post_comments(raw_data)
    data = get_threads(vk_api, post, data)
    return data


def get_raw_post_comments(vk_api, owner_id, post_id):
    time.sleep(0.35)
    first = vk_api.wall.getComments(owner_id=owner_id, post_id=post_id, need_likes=1, v=5.131)
    data = first["items"]
    count = first["count"] // 100
    if count > 1:
        count = 1
    print(f"Идёт парсинг {owner_id}, запись {post_id}")
    for i in range(1, count + 1):
        time.sleep(0.35)
        data += vk_api.wall.getComments(v="5.131", owner_id=owner_id, post_id=post_id, need_likes=1,
                                        offset=i * 100)["items"]
        print(f"Идёт парсинг {owner_id}, запись {post_id}: извлечено {i * 100} записей")
    return data


def get_classed_post_comments(raw_data):
    return [Comment(item) for item in raw_data]


def get_raw_comment_replies(vk_api, owner_id, comment_id):
    time.sleep(0.35)
    first = vk_api.wall.getComments(owner_id=owner_id, comment_id=comment_id, need_likes=1, v=5.131)
    data = first["items"]
    count = first["count"] // 100
    if count > 1:
        count = 1
    print(f"Идёт парсинг {owner_id}, запись {comment_id}")
    for i in range(1, count + 1):
        time.sleep(0.35)
        data += vk_api.wall.getComments(owner_id=owner_id, comment_id=comment_id, need_likes=1,
                                        offset=i * 100, v=5.131)["items"]
        print(f"Идёт парсинг {owner_id}, запись {comment_id}: извлечено {i * 100} записей")
    return data


def add_post_comments(data: list, data_comments: list) -> list:
    for i in data_comments:
        try:
            ind = data.index(i.owner_content_id)
        except ValueError:
            ind = -1
        data.insert(ind + 1, i)
    return data
