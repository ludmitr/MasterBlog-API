from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import datetime
import data_handler_json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

ERROR_MSG_ID_NOT_FOUND = {"error": "id not found"}
ERROR_MSG_DECODE_JSON = {"error": "Failed to decode JSON object"}


#  --- Routes ------------------------------------------------------
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Return different result based on

    - No query args passed - will return json with posts as it is.
    - With passed args - will return sorted list of posts.

        Query Parameters (both must be present):
        - sort : Attribute of the post to sort by. Acceptable values are "title" or "content" or... .
        - direction : Direction of the sort. Acceptable values are "asc" (ascending) or "desc" (descending).

    """
    blog_data = data_handler.load_data()

    # case when no args passed. return posts as it is.
    if not request.args:
        return jsonify(blog_data), 200

    sort_criteria = request.args.get('sort')
    direction_criteria = request.args.get('direction')

    # case when passed arguments are validated
    if is_query_args_are_valid(sort_criteria, direction_criteria):
        is_reverse = True if direction_criteria == 'desc' else False

        # sorting. different sort for value of key 'date'
        if sort_criteria == "date":
            sorted_posts = sorted(blog_data,
                                  key=lambda post: datetime.datetime.strptime(post[sort_criteria], '%Y-%m-%d'),
                                  reverse=is_reverse)
        else:
            sorted_posts = sorted(blog_data, key=lambda post: post[sort_criteria], reverse=is_reverse)

        return jsonify(sorted_posts), 200

    # ---- case for passing wrong query arguments-----
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

    return jsonify({"error": f"{' ||| '.join(error_messages)}"}), 400


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Handle POST requests to the '/api/posts' route.
    - POST: Adds a new post using JSON data from the request body.
            Returns JSON with  added post with a unique 'id', or an error message
            and status code 400 if 'title' or 'content' are missing.
    """
    # case when json was not passed / failed to decode json
    new_post_data = get_validated_json()
    if new_post_data is None:
        return jsonify(ERROR_MSG_DECODE_JSON), 400

    # Validate if all required keys are present and have a value
    missing_keys = [key for key in ['title', 'content', 'author', 'date'] if not new_post_data.get(key)]
    if missing_keys:
        return jsonify({'error': f"Missing or empty key(s): {missing_keys}"}), 400
    if not is_valid_date_format(new_post_data.get('date')):
        return jsonify(
            {'error': f"date format should be: YYYY-MM-DD"}), 400

    # creating new post and adding to db
    new_post = {
        'content': new_post_data['content'],
        'title': new_post_data['title'],
        'author': new_post_data['author'],
        'date': new_post_data['date']}
    new_post = data_handler.add(new_post)

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
        deleted_post = data_handler.delete_post(post_id)
        if deleted_post:
            message_for_return = {
                "message": f"Post with id {post_id} has been deleted successfully"
            }
            return jsonify(message_for_return), 200

    # case when id is not numeric or there is no post with that id
    return jsonify(ERROR_MSG_ID_NOT_FOUND), 404


@app.route("/api/posts/<post_id>", methods=['PUT'])
def update_post(post_id: str):
    """
       Update a blog post with the given post_id.

       Args:
           post_id (str): The ID of the post to update.

       Returns:
           Flask Response: The updated post as a JSON response.

       Raises:
           404: If the post_id is not numeric or no post with that ID is found.
           400: If the JSON data from the client fails to decode.
       """
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
    post_to_update = data_handler.update_data(post_to_update)

    return jsonify(post_to_update), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts based on provided search parameters.

    Returns:
        Flask Response: A JSON response containing the search results.
    """
    search_params = {
        'title': request.args.get('title'),
        'content': request.args.get('content'),
        'author': request.args.get('author'),
        'date': request.args.get('date')
    }

    search_result = []
    for search_key, search_word in search_params.items():
        if search_params[search_key]:
            search_result.extend(search_posts_by_word(search_word, search_key))

    # removing duplicates
    combined_result = [post for index, post in enumerate(search_result)
                       if search_result.index(post) == index]

    return jsonify(combined_result), 200


#  --- inner logic ------------------------------------------------------
def is_valid_date_format(date_string) -> bool:
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def is_query_args_are_valid(sort_criteria: str, direction_criteria: str) -> bool:
    return sort_criteria in ["title", "content", "author", "date"] \
        and direction_criteria in ["asc", "desc"]


def search_posts_by_word(word_to_search: str, key_to_search: str):
    """search posts where word_to_search is matched to one of the words in value
    of the key_to_search"""
    blog_data = data_handler.load_data()
    result_of_search = []
    word_to_search = word_to_search.lower()
    for post in blog_data:
        splitted_lower_words_of_post: list = post[key_to_search].lower().strip('.').split()
        if word_to_search in splitted_lower_words_of_post:
            result_of_search.append(post)

    return result_of_search


def get_data_to_update(data_for_update: dict) -> dict:
    """Returns dictionary with elements that needed to be updated in post"""
    data_for_update = {key: val for key, val in data_for_update.items()
                       if key in ['content', 'title', 'author', 'date'] and val}
    return data_for_update


def get_post_by_id(post_id: int):
    """Returns post with post_id, if not exist - returns None"""
    blog_data = data_handler.load_data()
    return next((post for post in blog_data if post['id'] == post_id), None)


def get_validated_json():
    """if decoding went right, will return dict, otherwise None """
    try:
        json_data = request.get_json()

        return json_data

    except BadRequest:
        return None

# ------------------------------------------------------------------------


if __name__ == '__main__':
    data_handler = data_handler_json.DataHandlerJson()
    app.run(host="0.0.0.0", port=5002, debug=True)
