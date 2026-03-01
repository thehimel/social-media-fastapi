# The App that We Will Be Building

## API Endpoints

### Post Endpoints

| Method | Endpoint       | Description              |
|--------|----------------|--------------------------|
| GET    | `/posts/`      | Retrieve all posts       |
| POST   | `/posts/`      | Create a post            |
| GET    | `/posts/{id}`  | Retrieve individual post |
| PUT    | `/posts/{id}`  | Update a post            |
| DELETE | `/posts/{id}`  | Delete a post            |

### User Endpoints

| Method | Endpoint       | Description  |
|--------|----------------|--------------|
| POST   | `/users/`      | Create user  |
| GET    | `/users/{id}`  | Get user     |

### Authentication

| Method | Endpoint | Description      |
|--------|----------|------------------|
| POST   | `/login` | Login            |

### Voting

| Method | Endpoint | Description      |
|--------|----------|------------------|
| POST   | `/vote/` | Vote on a post   |

### Default

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Root        |

## Summary

* **Social media** app with **CRUD** operations on posts (create, read, update, delete)
* Users can create posts, read others' posts, and vote (like) on posts
* **Authentication** required—users must log in to read posts (returns **401** when unauthorized)
* **FastAPI** built-in documentation for testing endpoints
* Create user: provide **email** and **password**
* Create post: provide **title**, **content**, and optional **published** (defaults to `true`)

## The Application Overview

The course builds a **social media** application where users can create posts, read other users' posts, perform full **CRUD** operations, and vote on posts. Most social media apps have a like or voting system, and this app includes that capability.

### Built-in Documentation

**FastAPI** provides built-in documentation that lists all **API endpoints**. The documentation shows:

* **Post endpoints**—retrieve all posts, create posts, retrieve an individual post, update a post, delete a post
* **User endpoints**—create a user, get a user's information
* **Authentication**—login
* **Voting**—like a post

### Testing the API

Use the built-in documentation to test the **API**. For example, hitting **GET** on posts returns **401** when not logged in—the **API** requires users to be logged in to read posts.

**Create a user** via the users endpoint. Provide an **email** (e.g., `john@gmail.com`) and **password**. A **201** response indicates success and returns the user **ID**, email, and creation date.

**Log in** via the login endpoint or the **Authorize** button at the top. After authorizing, retrieving posts returns all posts in the database.

**Create a post** via the create post endpoint. The schema requires:

* **title** (required)
* **content** (required)
* **published** (optional, defaults to `true`)

The response includes the post **ID**, **owner_id** (who created it), and owner information.

### CRUD and Voting

After creating a post, you can retrieve an individual post, update it, and delete it. The vote endpoint allows liking a post. This forms the backbone of a traditional social media application—once you can do this, you have a solid foundation to build any **API** you want.
