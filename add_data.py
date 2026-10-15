import json
import sqlite3

def get_or_create(cursor, select_sql, insert_sql, select_params, insert_params):
    cursor.execute(select_sql, select_params)
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(insert_sql, insert_params)
    return cursor.lastrowid

def insert_seichi_from_json(json_path="input_templerun.json"):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: [json_path] 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"오류: JSON 문법 오류입니다 -> {e}")
        return
    
    conn = sqlite3.connect("seichi.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_key = ON;")

    try:
        anime_id = get_or_create(
            cursor,
            "SELECT id FROM animes WHERE title = ?",
            "INSERT INTO animes (title) VALUES (?)",
            (data["anime"],),
            (data["anime"],)
        )

        reg = data["region"]
        region_id= get_or_create(
            cursor,
            "SELECT id FROM regions WHERE prefecture = ?  AND city = ? AND IFNULL(district, '') = IFNULL(?,'')",
            "INSERT INTO regions (prefecture, city, district) VALUES (?,?,?)",
            (reg["prefecture"], reg["city"], reg.get("district")),
            (reg["prefecture"], reg["city"], reg.get("district"))
        )
        sp = data["spot"]
        spot_id = get_or_create(
            cursor,
            "SELECT id FROM spots WHERE region_id = ? AND name = ?",
            "INSERT INTO spots (region_id, name, latitude, longitude) VALUES (?, ?, ?, ?)",
            (region_id, sp["name"]),
            (region_id, sp["name"], sp.get("latitude"), sp.get("longitude"))
        )

        space = data["space"]
        cursor.execute(
            """
            INSERT INTO spaces (anime_id, spot_id, point_name, episode, scene_desc, stay_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                anime_id,
                spot_id,
                space["point_name"],
                space.get("episode"),
                space.get("scene_desc"),
                space.get("stay_time", 30)
            )
        )
        space_id = cursor.lastrowid

        for tag_name in data.get("tags", []):
            tag_id = get_or_create(
                cursor,
                "SELECT id FROM tags WHERE name = ?",
                "INSERT INTO tags (name) VALUES (?)",
                (tag_name,),
                (tag_name,)
            )
            cursor.execute(
                "INSERT OR IGNORE INTO space_tags (space_id, tag_id) VALUES (?, ?)",
                (space_id, tag_id)
            )

        conn.commit()
        print(f"등록 성공: [{data['anime']}] {sp['name']} -> {space['point_name']} (공간 ID: {space_id})")
    except Exception as e:
        conn.rollback()
        print(f"오류로 인하여 등록 취소됨: {e}")
    finally:
        conn.close()
        
if __name__ == "__main__":
    insert_seichi_from_json()