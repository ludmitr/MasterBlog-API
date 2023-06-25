// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}
function createPostElement(post) {
    const postDiv = document.createElement('div');
    postDiv.className = 'post';
    postDiv.innerHTML = `<h2>${post.title}</h2><p>${post.content}</p><p><strong>Author:</strong> ${post.author}</p><p><strong>Date:</strong> ${post.date}</p><button onclick="deletePost(${post.id})">Delete</button>`;
    return postDiv;
}

// Function to send a search request to the API and display the matching posts
function searchPosts() {
    // Retrieve the search values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var searchTitle = document.getElementById('search-title').value;
    var searchContent = document.getElementById('search-content').value;
    var searchAuthor = document.getElementById('search-author').value;
    var searchDate = document.getElementById('search-date').value;

    // Construct the search query string with the provided data
    var searchQuery = `?title=${searchTitle}&content=${searchContent}&author=${searchAuthor}&date=${searchDate}`;

    // Use the Fetch API to send a GET request to the /search endpoint with the search query parameters
    fetch(baseUrl + '/posts/search' + searchQuery)
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the search results, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = createPostElement(post);
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a GET request to the API with sorting parameters
function sortPosts() {
    // Retrieve the sort and direction values from the select elements
    var sortValue = document.getElementById('sort-by').value;
    var directionValue = document.getElementById('sort-direction').value;

    // Retrieve the base URL from the input field
    var baseUrl = document.getElementById('api-base-url').value;

    // Construct the URL with the sorting parameters
    var url = baseUrl + '/posts?sort=' + sortValue + '&direction=' + directionValue;

    // Use the Fetch API to send a GET request to the constructed URL
    fetch(url)
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = createPostElement(post);
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}


// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = createPostElement(post);
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;
    var postDate = document.getElementById('post-date').value;

    // Create a new post object with the relevant data
    var newPost = {
        title: postTitle,
        content: postContent,
        author: postAuthor,
        date: postDate
    };

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost)
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}
