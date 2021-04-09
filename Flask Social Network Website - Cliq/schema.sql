-- ACCOUNTS TABLE
SELECT * FROM accounts;
DELETE FROM accounts;
DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    username VARCHAR(20) PRIMARY KEY,
    password VARCHAR(25),
    joined VARCHAR(10),
    pfp VARCHAR(255),
    cover VARCHAR(255),
    name VARCHAR(30),
    bio VARCHAR(255),
    clique VARCHAR(10),
    niche VARCHAR(25)
)



-- URLs TABLE
SELECT * FROM urls;
DELETE FROM urls;
DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
    username VARCHAR(20),
    clique VARCHAR(10),
    role VARCHAR(25),
    url VARCHAR(255)
)

-- (URL roles) --
-- UPBL = user profile bio link (clique 1)
-- UPL = user post link (clique 3 - N/A)



-- CLIQUE 1 POSTS TABLE
SELECT * FROM posts;
DELETE FROM posts;
DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id VARCHAR(255),
    username VARCHAR(20),
    clique VARCHAR(10), -- REMOVE IN THE FUTURE!!
    title VARCHAR(25),
    body VARCHAR(255),
    file VARCHAR(255),
    file_type VARCHAR(10)
)

-- CLIQUE 1 FOLLOWERS TABLE
SELECT * FROM clique1_followers;
DELETE FROM clique1_followers
DROP TABLE IF EXISTS clique1_followers;

CREATE TABLE clique1_followers (
    user VARCHAR(20),
    followed_by VARCHAR(20),
    follower_clique VARCHAR(10),
    is_following INT(1)
)

-- CLIQUE 1 POST RATINGS TABLE
SELECT * FROM clique1_ratings;
DELETE FROM clique1_ratings;
DROP TABLE IF EXISTS clique1_ratings;

CREATE TABLE clique1_ratings (
    post_owner VARCHAR(20),
    post_id VARCHAR(255),
    viewer VARCHAR(20),
    is_rated INT(1)
)



-- CLIQUE 2 POSTS TABLE
SELECT * FROM posts2;
DELETE FROM posts2;
DROP TABLE IF EXISTS posts2;

CREATE TABLE posts2 (
    id VARCHAR(255),
    username VARCHAR(20),
    clique VARCHAR(10), -- REMOVE IN THE FUTURE!!
    colgroup INT(1),
    caption VARCHAR(100),
    file VARCHAR(255),
    file_type VARCHAR(10),
    timestamp VARCHAR(255),
    likes INT(255)
)

-- CLIQUE 2 FOLLOWERS TABLE
SELECT * FROM clique2_followers;
DELETE FROM clique2_followers;
DROP TABLE IF EXISTS clique2_followers;

CREATE TABLE clique2_followers (
    user VARCHAR(20),
    followed_by VARCHAR(20),
    follower_clique VARCHAR(10),
    is_following INT(1)
)

-- CLIQUE 2 POST LIKES TABLE
SELECT * FROM clique2_likes;
DELETE FROM clique2_likes;
DROP TABLE IF EXISTS clique2_likes;

CREATE TABLE clique2_likes (
    post_owner VARCHAR(20),
    post_id VARCHAR(255),
    viewer VARCHAR(20),
    is_liked INT(1)
)