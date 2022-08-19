# -*- coding: utf-8 -*-

from crypt import methods
import datetime
import hashlib
from webbrowser import get
from flask import Flask, flash, g, jsonify, redirect, render_template, request, send_file, url_for, session
import random
import os
import csv
from psycopg2.extras import DictCursor
import psycopg2
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def connect():
    url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(url)


def invalid_input():
    flash("入力が不正です。", "alert-warning")
    return


def wrong_password():
    flash("パスワードが違います。", "alert-warning")
    return


def needs_login():
    flash("ログインしてください。", "alert-danger")
    return


def added_successfully():
    flash("正常に追加されました。", "alert-success")
    return


def uploaded_successfully():
    flash("正常に登録されました。", "alert-success")
    return


def modified_successfully():
    flash("正常に変更されました。", "alert-success")
    return


def deleted_successfully():
    flash("削除に成功しました。", "alert-success")
    return


def gen_songs_path(id):
    ret = "./db/"
    ret += str(id)
    ret += "/songs.db"
    return ret


def gen_sub_path(id):
    ret = "./db/"
    ret += str(id)
    ret += "/submissions.db"
    return ret


def add_ranking(ir_title, date_start, date_end, is_visible, password_sha_256ed_with_salt, salt):
    with connect() as con:
        with con.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS irs(ir_id SERIAL PRIMARY KEY , title TEXT NOT NULL, date_start TEXT NOT NULL, date_end TEXT NOT NULL,is_visible INTEGER NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute("insert into irs(title,date_start,date_end,is_visible,password_sha_256ed_with_salt,salt) values (%s,%s,%s,%s,%s,%s)", (
                ir_title, date_start, date_end, int(is_visible), password_sha_256ed_with_salt, salt))
    return


def add_songs(ir_id, model, title, password_sha_256ed_with_salt, salt):
    with connect() as con:
        with con.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS songs(songs_id SERIAL PRIMARY KEY ,ir_id INTEGER NOT NULL, model TEXT NOT NULL, title TEXT NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute("insert into songs(ir_id,model,title,password_sha_256ed_with_salt,salt) values (%s,%s,%s,%s,%s)", (
                int(ir_id), model, title, password_sha_256ed_with_salt, salt))

    return


def add_submission(name, songs_id, score, url, comment, password_sha_256ed_with_salt, salt):
    with connect() as con:
        with con.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS submissions(sub_id SERIAL PRIMARY KEY ,name TEXT NOT NULL,songs_id INTEGER NOT NULL, score INTEGER NOT NULL, url TEXT, comment TEXT NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL,belongs TEXT)")
            cur.execute("insert into submissions(name,songs_id,score,url,comment,password_sha_256ed_with_salt,salt,belongs) values (%s,%s,%s,%s,%s,%s,%s,%s)", (
                name, int(songs_id), int(score), url, comment, password_sha_256ed_with_salt, salt, session['id']))

    return


def get_one_ranking(ir_id):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("select * from irs where ir_id=%s", (ir_id,))
            ir_data = cur.fetchone()
            return ir_data


def get_one_song(songs_id):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("select * from songs where songs_id=%s", (songs_id,))
            songs_data = cur.fetchone()
            return songs_data


def get_one_submission(sub_id):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "select * from submissions where sub_id=%s", (sub_id,))
            sub_data = cur.fetchone()
            return sub_data


def get_songs_information(ir_id):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS songs(songs_id SERIAL PRIMARY KEY,ir_id INTEGER NOT NULL, model TEXT NOT NULL, title TEXT NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute(
                "select * from songs where ir_id=%s order by model,title", (ir_id,))
            songs_data = cur.fetchall()
            return songs_data


def get_all_submissions(songs_id, is_visible):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS submissions(sub_id SERIAL PRIMARY KEY,name TEXT NOT NULL,songs_id INTEGER NOT NULL, score INTEGER NOT NULL, url TEXT, comment TEXT NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL,belongs TEXT)")
            if is_visible == 1:
                cur.execute(
                    "select * from submissions where songs_id=%s order by score desc", (songs_id,))
            else:
                cur.execute(
                    "select * from submissions where songs_id=%s order by sub_id desc", (songs_id,))
            submissions_data = cur.fetchall()
            return submissions_data


def can_auth(pass_raw, salt, password_sha256_ed):
    pass_raw += salt
    password_utf = pass_raw.encode('utf-8')
    ret = hashlib.sha256(password_utf).hexdigest()
    return ret == password_sha256_ed


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


def get_user_data(id):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute("select * from users where id=%s", (id,))
            user_data = cur.fetchone()
            return user_data


def is_logged_in():
    return 'id' in session


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/contest/")
def get_all_contest_in_json():
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS irs(ir_id SERIAL PRIMARY KEY, title TEXT NOT NULL, date_start TEXT NOT NULL, date_end TEXT NOT NULL,is_visible INTEGER NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute(
                "select ir_id,title,date_start,date_end from irs order by ir_id desc")
            all_ir_data = cur.fetchall()
            return jsonify(all_ir_data)


@app.route("/api/contest_detail/<id>/", methods=["GET"])
def get_contest_detail_in_json(id):
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                "select id,model,title from songs where ir_id=%s order by model,title desc", (id,))
            one_ir_detail = cur.fetchone()
            return jsonify(one_ir_detail)


@app.route("/login/")
def get_login_info():
    return render_template("login.html")


@app.route("/login/post/", methods=['POST'])
def login():
    id = request.form['id']
    pass_raw = request.form['password']
    info = get_user_data(id)
    if info is None or not can_auth(pass_raw, info['salt'], info['password_sha_256ed_with_salt']):
        flash("IDまたはパスワードが間違っています。", "alert-warning")
        return redirect(url_for("get_login_info"))
    else:
        flash("ログインに成功しました。", "alert-success")
        session['id'] = id
        return redirect(url_for("index"))


@app.route("/logout/")
def logout():
    session.pop('id', None)
    flash("正常にログアウトされました。", "alert-success")
    return redirect(url_for("index"))


@app.route("/faqs/")
def faq():
    return render_template("faqs.html")


@app.route("/release_notes/")
def release_note():
    return render_template("release_notes.html")


@app.route("/rankings/")
def show_all_rankings():
    with connect() as con:
        with con.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS irs(ir_id SERIAL PRIMARY KEY, title TEXT NOT NULL, date_start TEXT NOT NULL, date_end TEXT NOT NULL,is_visible INTEGER NOT NULL, password_sha_256ed_with_salt TEXT,salt TEXT NOT NULL)")
            cur.execute("select * from irs order by ir_id desc")
            all_ir_data = cur.fetchall()
            return render_template("all_ranking_template.html", all_ir=all_ir_data)


@app.route("/rankings/add_ranking/")
def get_ranking_input():
    if is_logged_in():
        return render_template("add_ranking.html")
    else:
        needs_login()
        return redirect(url_for("show_all_rankings"))


@app.route("/rankings/add_ranking/post/", methods=['POST'])
def format_and_add_ranking():
    if is_logged_in():
        title = request.form['title']
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        pass_raw = request.form['password']
        is_visible = request.form['Radios']
        password_sha256ed, salt = calc_hash(pass_raw)
        if datetime.datetime.strptime(date_start, '%Y-%m-%d') < datetime.datetime.strptime(date_end, '%Y-%m-%d'):
            add_ranking(title, date_start, date_end,
                        is_visible, password_sha256ed, salt)
            added_successfully()
            return redirect(url_for("show_all_rankings"))
        else:
            invalid_input()
            return redirect(url_for("get_ranking_input"))
    else:
        needs_login()
        return redirect(url_for("show_all_rankings"))


@app.route("/rankings/status/<id>/")
def show_ranking_details(id):
    ir_data = get_one_ranking(id)
    now = datetime.datetime.today()

    return render_template("ranking_status_template.html", id=id, title=ir_data['title'], date_start=datetime.datetime.strptime(ir_data['date_start'], '%Y-%m-%d'), date_end=datetime.datetime.strptime(ir_data['date_end'], '%Y-%m-%d'), all_songs=get_songs_information(id), now=now)


@app.route("/rankings/status/<id>/modify/")
def get_ir_mods(id):
    if is_logged_in():
        ir_data = get_one_ranking(id)
        return render_template("modify_ranking.html", id=id, title=ir_data['title'], date_start=datetime.datetime.strptime(ir_data['date_start'], '%Y-%m-%d'), date_end=datetime.datetime.strptime(ir_data['date_end'], '%Y-%m-%d'))
    else:
        needs_login()
        return redirect(url_for("show_all_rankings"))


@app.route("/rankings/status/<id>/modify/post/", methods=['POST'])
def modify_ir(id):
    if is_logged_in():
        ir_title = request.form['title']
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        pass_raw = request.form['password']
        is_visible = request.form['Radios']
        ir_data = get_one_ranking(id)

        salt = ir_data['salt']
        pass_hashed = ir_data['password_sha_256ed_with_salt']

        if(can_auth(pass_raw, salt, pass_hashed)):
            if datetime.datetime.strptime(date_start, '%Y-%m-%d') < datetime.datetime.strptime(date_end, '%Y-%m-%d'):
                with connect() as con:
                    with con.cursor(cursor_factory=DictCursor) as cur:
                        cur.execute("update irs set title=%s,date_start=%s,date_end=%s,is_visible=%s where ir_id=%s", (
                            ir_title, date_start, date_end, int(is_visible), id))
                        con.commit()
                modified_successfully()
                return redirect(url_for("show_all_rankings"))
            else:
                invalid_input()
                return redirect(url_for("get_ir_mods", id=id, title=ir_data['title'], date_start=datetime.datetime.strptime(ir_data['date_start'], '%Y-%m-%d'), date_end=datetime.datetime.strptime(ir_data['date_end'], '%Y-%m-%d')))
        else:
            wrong_password()
            return redirect(url_for("get_ir_mods", id=id, title=ir_data['title'], date_start=datetime.datetime.strptime(ir_data['date_start'], '%Y-%m-%d'), date_end=datetime.datetime.strptime(ir_data['date_end'], '%Y-%m-%d')))
    else:
        needs_login()
        return redirect(url_for("show_all_rankings"))


@app.route("/rankings/status/<id>/add_songs/")
def get_songs_input(id):
    if is_logged_in():
        return render_template("add_songs.html")
    else:
        needs_login()
        return redirect(url_for("show_ranking_details", id=id))


@app.route("/rankings/status/<id>/add_songs/post/", methods=['POST'])
def format_and_add_songs(id):
    if is_logged_in():
        model = request.form['model']
        title = request.form['title']
        pass_raw = request.form['password']
        password_sha256ed, salt = calc_hash(pass_raw)
        add_songs(id, model, title, password_sha256ed, salt)
        added_successfully()
        return redirect(url_for("show_ranking_details", id=id))
    else:
        needs_login()
        return redirect(url_for("show_ranking_details", id=id))


@app.route("/rankings/status/<id>/delete/")
def get_ir_pass(id):
    if is_logged_in():
        ir_data = get_one_ranking(id)
        return render_template("delete.html", title=ir_data['title'])
    else:
        needs_login()
        return redirect(url_for("show_all_rankings"))


@app.route("/rankings/status/<id>/delete/post/", methods=['POST'])
def delete_ranking(id):
    if is_logged_in():
        pass_raw = request.form['password']
        ir_data = get_one_ranking(id)
        if can_auth(pass_raw, ir_data['salt'], ir_data['password_sha_256ed_with_salt']):
            with connect() as con:
                with con.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("delete from irs where ir_id=%s", (id,))
                    con.commit()
            deleted_successfully()
            return redirect(url_for("show_all_rankings"))
        else:
            wrong_password()
            return redirect(url_for("get_ir_pass", id=id))
    else:
        needs_login()
        return redirect(url_for("show_all_rankings"))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/")
def show_all_submissions(ir_id, songs_id):
    songs_data = get_one_song(songs_id)
    ir_data = get_one_ranking(ir_id)
    tw = None
    if 'tweet' in session:
        tw = session['tweet']
    now = datetime.datetime.today()

    return render_template("all_submissions_template.html", title=songs_data['title'], model=songs_data['model'], all_submissions=get_all_submissions(songs_id, int(ir_data['is_visible'])), now=now, date_start=datetime.datetime.strptime(ir_data['date_start'], '%Y-%m-%d'), date_end=datetime.datetime.strptime(ir_data['date_end'], '%Y-%m-%d'), ir_title=ir_data['title'], tweet=tw)


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/export/")
def get_ir_password(ir_id, songs_id):
    ir_data = get_one_ranking(ir_id)
    songs_data = get_one_song(songs_id)
    if is_logged_in():
        return render_template("download.html", ir_title=ir_data['title'], title=songs_data['title'])
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/export/post/", methods=['POST'])
def make_csv(ir_id, songs_id):
    ir_data = get_one_ranking(ir_id)
    songs_data = get_one_song(songs_id)
    pass_raw = request.form['password']
    titl = [ir_data['title']]
    titl.append(songs_data['title'])
    header = ['name', 'score', 'comment']
    path = "./db/" + str(ir_id) + "/export_" + \
        str(ir_id) + "_" + str(songs_id) + ".csv"
    file_name = "export_" + str(ir_id) + "_" + str(songs_id) + ".csv"
    with open(path, 'w', newline='', encoding='utf_8_sig') as f:
        writer = csv.writer(f)
        writer.writerow(titl)
        writer.writerow(header)
        sub_datas = get_all_submissions(ir_id, songs_id)
        for data in sub_datas:
            target = [data['name'], data['score'], data['comment']]
            writer.writerow(target)
    if is_logged_in():
        if can_auth(pass_raw, ir_data['salt'], ir_data['password_sha_256ed_with_salt']):
            return send_file(path, as_attachment=True, attachment_filename=file_name, mimetype="text/csv")
        else:
            wrong_password()
            return redirect(url_for("get_ir_password", ir_id=ir_id, songs_id=songs_id))
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/delete/")
def get_songs_pass(ir_id, songs_id):
    if is_logged_in():
        songs_data = get_one_song(songs_id)
        ir_data = get_one_ranking(ir_id)
        return render_template("delete.html", title=ir_data['title']+"から"+songs_data['title'])
    else:
        needs_login()
        return redirect(url_for("show_ranking_details", id=ir_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/delete/post/", methods=['POST'])
def delete_songs(ir_id, songs_id):
    if is_logged_in():
        pass_raw = request.form['password']
        songs_data = get_one_song(songs_id)
        if can_auth(pass_raw, songs_data['salt'], songs_data['password_sha_256ed_with_salt']):
            with connect() as con:
                with con.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        "delete from songs where songs_id=%s", (songs_id,))
                    con.commit()
            deleted_successfully()
            return redirect(url_for("show_ranking_details", id=ir_id))
        else:
            wrong_password()
            return redirect(url_for("get_songs_pass", ir_id=ir_id, songs_id=songs_id))
    else:
        needs_login()
        return redirect(url_for("show_ranking_details", id=ir_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/modify/")
def get_song_mod(ir_id, songs_id):
    if is_logged_in():
        songs_data = get_one_song(songs_id)
        ir_data = get_one_ranking(ir_id)
        return render_template("modify_song.html", ir_title=ir_data['title'], model=songs_data['model'], title=songs_data['title'])
    else:
        needs_login()
        return redirect(url_for("show_ranking_details", id=ir_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/modify/post/", methods=['POST'])
def modify_song(ir_id, songs_id):
    if is_logged_in():
        ir_data = get_one_ranking(ir_id)
        songs_data = get_one_song(songs_id)
        model = request.form['model']
        title = request.form['title']
        pass_raw = request.form['password']
        if can_auth(pass_raw, songs_data['salt'], songs_data['password_sha_256ed_with_salt']):
            with connect() as con:
                with con.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("update songs set model=%s, title=%s where songs_id=%s", (
                        model, title, songs_id))
                    con.commit()
            modified_successfully()
            return redirect(url_for("show_ranking_details", id=ir_id))
        else:
            wrong_password()
            return redirect(url_for("get_song_mod", ir_id=ir_id, songs_id=songs_id, ir_title=ir_data['title'], title=songs_data['title'], model=songs_data['model']))
    else:
        needs_login()
        return redirect(url_for("show_ranking_details", id=ir_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/add_submission/")
def get_submission_input(ir_id, songs_id):
    if is_logged_in():
        return render_template("add_submission.html")
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/add_submission/post/", methods=['POST'])
def format_and_add_submission(ir_id, songs_id):
    if is_logged_in():
        name = request.form['name']
        score = request.form['score']
        url = request.form['url']
        comment = request.form['comment']
        pass_raw = request.form['password']
        password_sha256ed, salt = calc_hash(pass_raw)
        add_submission(name, songs_id, score, url,
                       comment, password_sha256ed, salt)
        ir_data = get_one_ranking(ir_id)
        songs_data = get_one_song(songs_id)
        st = ir_data['title'] + "の" + songs_data['title'] + "に登録しました！\nスコア:" + \
            str(score) + "\nコメント:" + comment + "\n締め切りは" + \
            ir_data['date_end']+"まで！\n#PUCIR"
        session['tweet'] = st
        uploaded_successfully()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/<sub_id>/delete/")
def get_submission_pass(ir_id, songs_id, sub_id):
    if is_logged_in():
        ir_data = get_one_ranking(ir_id)
        songs_data = get_one_song(songs_id)

        return render_template("delete.html", title=ir_data['title']+"の"+songs_data['title']+"への提出")
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/<sub_id>/delete/post/", methods=['POST'])
def delete_submissions(ir_id, songs_id, sub_id):
    if is_logged_in():
        pass_raw = request.form['password']
        sub_data = get_one_submission(sub_id)

        if(can_auth(pass_raw, sub_data['salt'], sub_data['password_sha_256ed_with_salt'])):
            with connect() as con:
                with con.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        "delete from submissions where sub_id=%s", (sub_id,))
                    con.commit()
            deleted_successfully()
            return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))
        else:
            wrong_password()
            return redirect(url_for("get_submission_pass", ir_id=ir_id, songs_id=songs_id, sub_id=sub_id))
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/<sub_id>/modify/")
def get_sub_mod(ir_id, songs_id, sub_id):
    if is_logged_in():
        ir_data = get_one_ranking(ir_id)
        songs_data = get_one_song(songs_id)
        sub_data = get_one_submission(sub_id)
        return render_template("modify_submission.html", ir_title=ir_data['title'], title=songs_data['title'], name=sub_data['name'], score=sub_data['score'], url=sub_data['url'], comment=sub_data['comment'])
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


@app.route("/rankings/status/<ir_id>/songs/<songs_id>/submissions/<sub_id>/modify/post/", methods=['POST'])
def modify_sub(ir_id, songs_id, sub_id):
    if is_logged_in():
        ir_data = get_one_ranking(ir_id)
        songs_data = get_one_song(songs_id)
        sub_data = get_one_submission(sub_id)
        name = request.form['name']
        score = request.form['score']
        url = request.form['url']
        comment = request.form['comment']
        pass_raw = request.form['password']
        if can_auth(pass_raw, sub_data['salt'], sub_data['password_sha_256ed_with_salt']):
            with connect() as con:
                with con.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("update submissions set name=%s,score=%s,url=%s,comment=%s where sub_id=%s", (
                        name, score, url, comment, sub_id))
                    con.commit()
                    con.close()
                    return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))
        else:
            wrong_password()
            return redirect(url_for("get_sub_mod", ir_id=ir_id, songs_id=songs_id, sub_id=sub_id, ir_title=ir_data['title'], title=songs_data['title'], name=sub_data['name'], score=sub_data['score'], url=sub_data['url'], comment=sub_data['comment']))
    else:
        needs_login()
        return redirect(url_for("show_all_submissions", ir_id=ir_id, songs_id=songs_id))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
