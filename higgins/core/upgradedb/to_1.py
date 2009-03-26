from higgins.core.upgradedb.logger import logger

def upgrade(db):
    sql = """
CREATE TABLE "dbinfo" (
    "version" integer NOT NULL,
    "date" datetime NOT NULL
);
CREATE TABLE "auth_group" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL UNIQUE
);
CREATE TABLE "auth_group_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("group_id", "permission_id")
);
CREATE TABLE "auth_message" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "message" text NOT NULL
);
CREATE TABLE "auth_permission" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "content_type_id" integer NOT NULL,
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);
CREATE TABLE "auth_user" (
    "id" integer NOT NULL PRIMARY KEY,
    "username" varchar(30) NOT NULL UNIQUE,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL,
    "email" varchar(75) NOT NULL,
    "password" varchar(128) NOT NULL,
    "is_staff" bool NOT NULL,
    "is_active" bool NOT NULL,
    "is_superuser" bool NOT NULL,
    "last_login" datetime NOT NULL,
    "date_joined" datetime NOT NULL
);
CREATE TABLE "auth_user_groups" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
    UNIQUE ("user_id", "group_id")
);
CREATE TABLE "auth_user_user_permissions" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("user_id", "permission_id")
);
CREATE TABLE "core_album" (
    "id" integer NOT NULL PRIMARY KEY,
    "date_added" datetime NOT NULL,
    "name" varchar(256) NOT NULL,
    "artist_id" integer NOT NULL REFERENCES "core_artist" ("id"),
    "genre_id" integer NOT NULL,
    "release_date" integer NULL,
    "rating" integer NULL
);
CREATE TABLE "core_artist" (
    "id" integer NOT NULL PRIMARY KEY,
    "date_added" datetime NOT NULL,
    "name" varchar(256) NOT NULL,
    "website" varchar(200) NOT NULL,
    "rating" integer NULL
);
CREATE TABLE "core_file" (
    "id" integer NOT NULL PRIMARY KEY,
    "path" varchar(512) NOT NULL,
    "mimetype" varchar(80) NOT NULL,
    "size" integer NOT NULL
);
CREATE TABLE "core_genre" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL
);
CREATE TABLE "core_playlist" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL,
    "data" text NOT NULL,
    "rating" integer NULL
);
CREATE TABLE "core_playlist_songs" (
    "id" integer NOT NULL PRIMARY KEY,
    "playlist_id" integer NOT NULL REFERENCES "core_playlist" ("id"),
    "song_id" integer NOT NULL REFERENCES "core_song" ("id"),
    UNIQUE ("playlist_id", "song_id")
);
CREATE TABLE "core_playlist_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "playlist_id" integer NOT NULL REFERENCES "core_playlist" ("id"),
    "tag_id" integer NOT NULL REFERENCES "core_tag" ("id"),
    UNIQUE ("playlist_id", "tag_id")
);
CREATE TABLE "core_song" (
    "id" integer NOT NULL PRIMARY KEY,
    "file_id" integer NOT NULL REFERENCES "core_file" ("id"),
    "date_added" datetime NOT NULL,
    "name" varchar(256) NOT NULL,
    "artist_id" integer NOT NULL REFERENCES "core_artist" ("id"),
    "album_id" integer NOT NULL REFERENCES "core_album" ("id"),
    "duration" integer NOT NULL,
    "track_number" integer NULL,
    "volume_number" integer NULL,
    "rating" integer NULL
);
CREATE TABLE "core_song_featuring" (
    "id" integer NOT NULL PRIMARY KEY,
    "song_id" integer NOT NULL REFERENCES "core_song" ("id"),
    "artist_id" integer NOT NULL REFERENCES "core_artist" ("id"),
    UNIQUE ("song_id", "artist_id")
);
CREATE TABLE "core_song_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "song_id" integer NOT NULL REFERENCES "core_song" ("id"),
    "tag_id" integer NOT NULL REFERENCES "core_tag" ("id"),
    UNIQUE ("song_id", "tag_id")
);
CREATE TABLE "core_tag" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(80) NOT NULL
);
CREATE TABLE "django_admin_log" (
    "id" integer NOT NULL PRIMARY KEY,
    "action_time" datetime NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "content_type_id" integer NULL REFERENCES "django_content_type" ("id"),
    "object_id" text NULL,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint unsigned NOT NULL,
    "change_message" text NOT NULL
);
CREATE TABLE "django_content_type" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
);
CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);
CREATE TABLE "django_site" (
    "id" integer NOT NULL PRIMARY KEY,
    "domain" varchar(100) NOT NULL,
    "name" varchar(50) NOT NULL
);
CREATE INDEX "auth_message_user_id" ON "auth_message" ("user_id");
CREATE INDEX "auth_permission_content_type_id" ON "auth_permission" ("content_type_id");
CREATE INDEX "core_album_artist_id" ON "core_album" ("artist_id");
CREATE INDEX "core_album_genre_id" ON "core_album" ("genre_id");
CREATE INDEX "core_song_album_id" ON "core_song" ("album_id");
CREATE INDEX "core_song_artist_id" ON "core_song" ("artist_id");
CREATE INDEX "core_song_file_id" ON "core_song" ("file_id");
CREATE INDEX "django_admin_log_content_type_id" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id" ON "django_admin_log" ("user_id");
    """
    cursor = db.cursor()
    cursor.executescript(sql)
    db.commit()
