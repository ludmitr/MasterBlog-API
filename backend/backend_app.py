from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from werkzeug.exceptions import BadRequest


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

#  --- Routes ------------------------------------------------------
@app.route('/api/posts', methods=['GET','POST'])
def manage_posts():
    """
    Handle GET and POST requests to the '/api/posts' route.

    - GET: Returns a JSON list of all posts.
    - POST: Adds a new post using JSON data from the request body.
            The request body must contain 'title' and 'content' keys.
            Returns JSON with  added post with a unique 'id', or an error message
            and status code 400 if 'title' or 'content' are missing.
    """
    if request.method == 'POST':
        # case when json was not passed
        new_post_data = get_validated_json()
        if new_post_data is None:
            return jsonify({"error": "Failed to decode JSON object"}), 400

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

    # GET request
    return jsonify(POSTS)


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
        post_to_delete = next((post for post in POSTS if post['id'] == post_id), None)
        if post_to_delete:
            POSTS.remove(post_to_delete)
            message_for_return = {
                "message": f"Post with id {post_id} has been deleted successfully"
            }
            return jsonify(message_for_return), 200

    # case when id is not numeric or there is no post with that id
    return jsonify({"error": "id not found"}), 404


#  --- inner logic ------------------------------------------------------
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
    app.run(host="0.0.0.0", port=5002)
