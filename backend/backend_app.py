from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

ERROR_MSG_ID_NOT_FOUND = {"error": "id not found"}
ERROR_MSG_DECODE_JSON = {"error": "Failed to decode JSON object"}

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

#  --- Routes ------------------------------------------------------
@app.route('/api/posts', methods=['GET'])
def get_posts():
    # case when no args passed. return posts as it is.
    if not request.args:
        return jsonify(POSTS), 200

    sort_criteria = request.args.get('sort')
    direction_criteria = request.args.get('direction')

    # case when passed arguments are validated
    if sort_criteria in ["title", "content"] and direction_criteria in ["asc", "desc"]:
        is_reverse = True if direction_criteria == 'desc' else False
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_criteria], reverse=is_reverse)

        return jsonify(sorted_posts), 200

    # case for passing wrong arguments
    error_messages = []

    # check sort_criteria
    if sort_criteria is None:
        error_messages.append("You didn't pass the sort argument.")
    elif sort_criteria not in ["title", "content"]:
        error_messages.append(
            "Sort argument value wrong, should be 'title' or 'content'.")

    # check direction_criteria
    if direction_criteria is None:
        error_messages.append("You didn't pass the direction argument.")
    elif direction_criteria not in ["asc", "desc"]:
        error_messages.append(
            "Direction argument value wrong, should be 'asc' or 'desc'.")

    return jsonify({"error":f"{' ||| '.join(error_messages)}"}), 400

@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Handle POST requests to the '/api/posts' route.
    - POST: Adds a new post using JSON data from the request body.
            The request body must contain 'title' and 'content' keys.
            Returns JSON with  added post with a unique 'id', or an error message
            and status code 400 if 'title' or 'content' are missing.
    """
    # case when json was not passed/ failed to decode json
    new_post_data = get_validated_json()
    if new_post_data is None:
        return jsonify(ERROR_MSG_DECODE_JSON), 400

    # Validate if all required keys are present and have a value
    missing_keys = [key for key in ['title', 'content'] if not new_post_data.get(key)]
    if missing_keys:
        return jsonify({'error': f"Missing or empty key(s): {missing_keys}"}), 400

    # creating new post and adding to db
    new_post = {
        'id': get_unique_id_for_post(),
        'content': new_post_data['content'],
        'title': new_post_data['title']}
    POSTS.append(new_post)

    return jsonify(new_post), 201



@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id: str):
    """
     Delete a post with the given post_id.

     Returns:
         A JSON response containing a success message if the post was deleted successfully,
         or an error message if the ID is not numeric or no post was found with that ID.
     """
    if post_id.isnumeric():
        post_id = int(post_id)

        # remove post by id (if exist) amd return json of deleted post
        post_to_delete = get_post_by_id(post_id)
        if post_to_delete:
            POSTS.remove(post_to_delete)
            message_for_return = {
                "message": f"Post with id {post_id} has been deleted successfully"
            }
            return jsonify(message_for_return), 200

    # case when id is not numeric or there is no post with that id
    return jsonify(ERROR_MSG_ID_NOT_FOUND), 404


@app.route("/api/posts/<post_id>", methods=['PUT'])
def update_post(post_id: str):
    # case when id is not numeric
    if not post_id.isnumeric():
        return jsonify(ERROR_MSG_ID_NOT_FOUND), 404

    # case when failed to decode json data from client
    data_from_user_to_update = get_validated_json()
    if data_from_user_to_update is None:
        return jsonify(ERROR_MSG_DECODE_JSON), 400

    # case when id is numeric but there is no post with that id
    post_to_update = get_post_by_id(int(post_id))
    if not post_to_update:
        return jsonify(ERROR_MSG_ID_NOT_FOUND), 404

    # updating post
    data_to_update = get_data_to_update(data_from_user_to_update)
    for key, val in data_to_update.items():
        post_to_update[key] = val

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_to_search = request.args.get('title')
    content_to_search = request.args.get('content')

    title_search_result = search_posts_by_word_in_title(title_to_search)
    content_to_search = search_posts_by_word_in_content(content_to_search)

    combined_result: list = title_search_result + content_to_search

    # removing duplicates
    combined_result = [post for index, post in enumerate(combined_result)
                       if combined_result.index(post) == index]

    return jsonify(combined_result), 200


#  --- inner logic ------------------------------------------------------
def search_posts_by_word_in_title(title_word_to_search: str) -> list[dict]:
    """search posts where title got title_word_to_search"""
    result_of_search = []
    title_word_to_search = title_word_to_search.lower()
    for post in POSTS:
        split_lower_words_of_title: list = post['title'].lower().split()
        if title_word_to_search in split_lower_words_of_title:
            result_of_search.append(post)

    return result_of_search

def search_posts_by_word_in_content(content_word_to_search: str) -> list[dict]:
    """search posts where content got content_word_to_search"""
    result_of_search = []
    title_word_to_search = content_word_to_search.lower()
    for post in POSTS:
        split_lower_words_of_title: list = post['content'].lower().split()
        if title_word_to_search in split_lower_words_of_title:
            result_of_search.append(post)

    return result_of_search


def get_data_to_update(data_for_update: dict) -> dict:
    """Returns dictionary with elements that needed to be updated in post"""
    data_for_update = {key: val for key, val in data_for_update.items()
                       if key in ['content', 'title'] and val}
    return data_for_update


def get_post_by_id(post_id: int):
    """Returns post with post_id, if not exist - returns None"""
    return next((post for post in POSTS if post['id'] == post_id), None)

def get_unique_id_for_post() -> int:
    # case for no posts
    if not POSTS:
        return 1

    post_with_max_id = max(POSTS, key=lambda x: x['id'])

    return post_with_max_id['id'] + 1

def get_validated_json() -> dict:
    """if decoding went right, will return dict, otherwise None """
    try:
        json_data = request.get_json()

        return json_data

    except BadRequest as e:
        return None
# ------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
