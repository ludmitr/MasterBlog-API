import json
import os
import re


class DataHandlerJson:
    """json data CRUD handler for master blog app"""
    def __init__(self, path="blog_data.json"):
        self.file_path = path


    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, path):
        """Check if storage with that name exist. if not creates one. setting file_path"""
        converted_path = os.path.normpath(path)
        if not os.path.exists(converted_path):
            if not converted_path.endswith('.json'):
                raise ValueError("Invalid file format. Only JSON files are allowed.")
            with open(path, "w") as file:
                json.dump([], file)

        self._file_path = converted_path

    def _save_data(self, blog_data: list) -> None:
        """Serialize the blog data(list of dictionaries) in json file"""
        with open(self._file_path, "w") as file:
            json.dump(blog_data, file)

    def add(self, post: dict):
        """Adding blog post to json file. the function will add unique id"""
        if not self._is_date_validate(post['date']):
            raise ValueError("Incorrect date format, should be 'YYYY-MM-DD'")

        blog_posts: list = self.load_data()

        # generate and add unique id to post
        new_unique_id = max(blog_posts, key=lambda p: p['id'])['id'] + 1 if blog_posts else 1
        post['id'] = new_unique_id
        blog_posts.append(post)

        self._save_data(blog_posts)

    def delete_post(self, id_to_delete: int):
        """Delete post by id_to_delete. if delete succeeded
        will return the dict that represent deleted post"""
        # finding post to delete
        blog_posts = self.load_data()
        post_to_delete = next((post for post in blog_posts if post['id'] == id_to_delete), None)
        if post_to_delete:
            blog_posts.remove(post_to_delete)
            self._save_data(blog_posts)
            return post_to_delete

    def load_data(self) -> list:
        """return a list of dictionaries that contain blog posts
                :return example
                [
                    {
                    'id': 1,
                    'author': 'John Doe',
                    'date': '2023-03-22',
                    'title': 'First Post',
                    'content': 'This is my first post.'
                    },
                    .....
                ]
                """
        with open(self._file_path, "r") as file:
            blog_posts = json.load(file)

        return blog_posts


    def update_data(self, post_to_update: dict):
        """update the post. if the post has wrong date format will raise an error
        if post updated will return the updated post"""
        if not self._is_date_validate(post_to_update['date']):
            raise ValueError("Incorrect date format, should be 'YYYY-MM-DD'")

        blog_posts = self.load_data()
        for index, post in enumerate(blog_posts):
            if post['id'] == post_to_update['id']:
                blog_posts[index] = post_to_update
                self._save_data(blog_posts)
                return post_to_update
                break

    def _is_date_validate(self, date: str) -> bool:
        """Check if a given date string is in the 'YYYY-MM-DD'
        format and is a valid date."""
        date_match = re.match('^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$', date)
        if date_match:
            return True
        return False
