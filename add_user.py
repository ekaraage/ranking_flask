import psycopg2
import random
import hashlib
import os


def connect():
    url=os.environ.get('DATABASE_URL')
    return psycopg2.connect(url)


def gen_salt():
    chars = "0123456789abcdefghijklmnopqrstuvwxABCDEFGHIJKLMNOPQRSTUVWX"
    res = ""
    for i in range(8):
        t = random.randint(0, len(chars)-1)
        res += chars[t]
    return res


def calc_hash(password):
    salt = gen_salt()
    password += salt
    password_utf = password.encode('utf-8')
    res = hashlib.sha256(password_utf).hexdigest()
    return res, salt


def main():
    print("input id")
    id = input()
    print("input password")
    pass_raw = input()
    password_sha_256ed_with_salt, salt = calc_hash(pass_raw)

    with connect() as con:
        with con.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute("insert into users(id,password_sha_256ed_with_salt,salt) values (%s,%s,%s)", (
                id, password_sha_256ed_with_salt, salt))
            con.commit()


if __name__ == "__main__":
    main()
