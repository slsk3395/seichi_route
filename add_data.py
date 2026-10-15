import json
import sqlite3

def get_or_create(cursor, select_sql, insert_sql, select_params, insert_params):
    cursor.execute(select_sql, select_params) 
    row = cursor.fetchone()#아래를 보니 그냥 파라미터 보고 행 하나만 가져오네
    if row:
        return row[0] 
    cursor.execute(insert_sql, insert_params)
    return cursor.lastrowid

def insert_seichi_from_json(json_path="input_templerun.json"):#제이슨 파일이네요 인자는 제이슨 파일입니다. 대입도 그냥 인자정의부분해서 완료함
    try:#이거 그건데 예외처리 문법
        with open(json_path, "r", encoding="utf-8") as f:#파일 여는데 저 utf-8(유니코드인가?) 그걸로 엔코딩해서 파일로 열어라 같음 as f가 이 뜻이 맞다면 말이지
            data = json.load(f)# 데이터 = 파일에서 로드한 제이슨 구문들.
    except FileNotFoundError:
        print(f"오류: {json_path} 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:#정해놓은 그 템플릿 예외네요. 근데 문법오류가 어느경우 이려나?
        print(f"오류: JSON 문법 오류입니다 -> {e}")
        return
    
    conn = sqlite3.connect("seichi.db")#통로 뚫기
    cursor = conn.cursor()#통로 돌아다닐 일꾼 고용
    cursor.execute("PRAGMA foreign_keys = ON;")#외래키 허용한 상태로 일꾼 일 시작

    try:
        anime_id = get_or_create(
            cursor,
            "SELECT id FROM animes WHERE title = ?",#애니에서 아이디를 가져와라. 근데 타이틀이 물음표에 들어갈것과 같은행에서ㅇㅇ
            "INSERT INTO animes (title) VALUES (?)",#없으면 타이틀에 이름 알려준걸로 추가하고ㅇㅇ
            (data["anime"],),#맨위에 물음표에 드갈거
            (data["anime"],)#아래 물음표에 드갈거. 이렇게 보니 구조가 잘 보이네ㅋㅋ
        )

        reg = data["region"]
        region_id= get_or_create(
            cursor,
            "SELECT id FROM regions WHERE prefecture = ?  AND city = ? AND IFNULL(district, '') = IFNULL(?,'')",#애니때랑 똑같은데 그냥 교집합으로 검사하나봄. 근데 마지막 등호식이 좀 애매하네
            "INSERT INTO regions (prefecture, city, district) VALUES (?,?,?)", #없으면 추가하고ㅇㅇ
            (reg["prefecture"], reg["city"], reg.get("district")),
            (reg["prefecture"], reg["city"], reg.get("district"))
        )
        sp = data["spot"]
        spot_id = get_or_create(
            cursor,
            "SELECT id FROM spots WHERE region_id = ? AND name = ?",#뭐 항상하던거ㅇㅇ
            "INSERT INTO spots (region_id, name, latitude, longitude) VALUES (?, ?, ?, ?)",
            (region_id, sp["name"]),
            (region_id, sp["name"], sp.get("latitude"), sp.get("longitude"))
        )

        space = data["space"]
        space_id = get_or_create(
            cursor,  # 1. 일꾼(cursor) 전달
            "SELECT id FROM spaces WHERE spot_id = ? AND point_name = ?",  # 2. 장소 이름까지 함께 검사
            "INSERT INTO spaces (anime_id, spot_id, point_name, episode, scene_desc, stay_time) VALUES (?, ?, ?, ?, ?, ?)",
            (spot_id, space["point_name"]),  # 3. 조회 파라미터 (2개짜리 튜플)
            (anime_id, spot_id, space["point_name"], space.get("episode"), space.get("scene_desc"), space.get("stay_time", 30))
        )
        space_id = cursor.lastrowid

        for tag_name in data.get("tags", []):
            tag_id = get_or_create(#태그도 별개의 테이블이라 추가함ㅇㅇ
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