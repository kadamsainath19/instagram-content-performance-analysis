-- Instagram Content Performance Analysis: database schema
-- Works in SQLite, MySQL and PostgreSQL (tiny type differences only).

CREATE TABLE accounts (
    account_id  VARCHAR(10) PRIMARY KEY,   -- primary key
    niche       VARCHAR(30) NOT NULL,
    followers   INT         NOT NULL
);

CREATE TABLE posts (
    post_id          VARCHAR(10) PRIMARY KEY,
    account_id       VARCHAR(10) NOT NULL,
    post_date        DATE        NOT NULL,
    hour             INT         NOT NULL,
    weekday          VARCHAR(15) NOT NULL,
    post_type        VARCHAR(15) NOT NULL,
    hashtag_count    INT,
    caption_length   INT,
    has_cta          INT,
    impressions      INT,
    reach            INT,
    likes            INT,
    comments         INT,
    shares           INT,
    saves            INT,
    profile_visits   INT,
    follows_gained   INT,
    engagement_rate  DECIMAL(8,4),
    FOREIGN KEY (account_id) REFERENCES accounts (account_id)   -- foreign key
);
