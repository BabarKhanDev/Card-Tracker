-- SCHEMA: sdk_cache

CREATE SCHEMA IF NOT EXISTS sdk_cache
    AUTHORIZATION cards;

-- Table: sdk_cache.set

CREATE TABLE IF NOT EXISTS sdk_cache.set
(
    id text COLLATE pg_catalog."default" NOT NULL,
    image_uri text COLLATE pg_catalog."default",
    name text COLLATE pg_catalog."default",
    series text COLLATE pg_catalog."default",
    release_date date,
    CONSTRAINT set_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE sdk_cache.set
    OWNER to cards;

-- Table: sdk_cache.card

CREATE TABLE IF NOT EXISTS sdk_cache.card
(
    id text COLLATE pg_catalog."default" NOT NULL,
    image_uri_large text COLLATE pg_catalog."default",
    image_uri_small text COLLATE pg_catalog."default",
    name text COLLATE pg_catalog."default",
    set_id text COLLATE pg_catalog."default",
    CONSTRAINT card_pkey PRIMARY KEY (id),
    CONSTRAINT set_id FOREIGN KEY (set_id)
        REFERENCES sdk_cache.set (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE sdk_cache.card
    OWNER to cards;

-- SCHEMA: user_data

CREATE SCHEMA IF NOT EXISTS user_data
    AUTHORIZATION cards;

-- Table: user_data.library

CREATE TABLE IF NOT EXISTS user_data.library
(
    card_id text COLLATE pg_catalog."default" NOT NULL,
    quantity integer,
    CONSTRAINT library_pkey PRIMARY KEY (card_id),
    CONSTRAINT card_id FOREIGN KEY (card_id)
        REFERENCES sdk_cache.card (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS user_data.library
    OWNER to cards;

-- Table: user_data.wishlist

CREATE TABLE IF NOT EXISTS user_data.wishlist
(
    card_id text COLLATE pg_catalog."default" NOT NULL,
    quantity integer,
    CONSTRAINT wishlist_pkey PRIMARY KEY (card_id),
    CONSTRAINT card_id FOREIGN KEY (card_id)
        REFERENCES sdk_cache.card (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS user_data.wishlist
    OWNER to cards;