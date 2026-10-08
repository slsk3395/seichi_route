--1.작품 테이블
CREATE TABLE IF NOT EXISTS animes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);

--2.지역테이블(얘네는 행정구역말하는거)
CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prefecture TEXT NOT NULL,
    city TEXT NOT NULL,
    district TEXT
);

--3.장소테이블(얘네는 장소 계획 구상의 최소단위임)
CREATE TABLE IF NOT EXISTS spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (region_id) REFERENCES regions (id) ON DELETE CASCADE
);

--4.공간테이블(장소의 더 세부적인 개념 사용자가 장소에 포함된 공간들의 리스트만 확인하는 느낌임(빅사이트-> 빅사이트 1층 광장))
CREATE TABLE IF NOT EXISTS spaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER NOT NULL,
    spot_id INTEGER NOT NULL,
    point_name TEXT NOT NULL,
    episode TEXT,
    scene_desc TEXT,
    stay_time INTEGER DEFAULT 30,
    FOREIGN KEY (anime_id) REFERENCES animes (id) ON DELETE CASCADE,
    FOREIGN KEY (spot_id) REFERENCES spots (id) ON DELETE CASCADE
);

--5.태그 테이블(태그 모아놓은거, 아마도요)
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT
);

--6.성지-태그 매칭 테이블
CREATE TABLE IF NOT EXISTS space_tags (
    space_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (space_id, tag_id),
    FOREIGN KEY (space_id) REFERENCES spaces (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

