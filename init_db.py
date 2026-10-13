import sqlite3

def init_db():#데베 초기화 함수 선언
    conn = sqlite3.connect("seichi.db")
    cursor = conn.cursor()#커서쓰는 명령어

    cursor.execute("PRAGMA foreign_keys = ON;")#커서에게 말함. 외래키 켠다고.

    with open("schema.sql", "r", encoding="utf-8") as f:#이건 모르겠네 스키마 여는거고 엔코딩은 유니코드로 할건데 중간에 r은 모르겠음 as f도 모르겠음
        cursor.executescript(f.read())#그리고 커서에게 스크립트 읽으라고 함 아 f가 파일일 가능성이 매우 높네 파일읽으라는 뜻이구만
    
    conn.commit()#커밋하고
    conn.close()#파일닫기 하지만 conn이랑 연결했을때를 봐야할거같음

if __name__ == "__main__":#메인함수...?
    init_db()
