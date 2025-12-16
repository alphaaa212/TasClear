from flask import Flask, render_template,request,redirect,url_for,flash
from datetime import datetime,timedelta
from services.ai_function2 import predict_priority
import psycopg2
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from tkinter import messagebox

app = Flask(__name__)
app.secret_key = 'dIOjfeuIFKDjpasJI97ws'  # セッション管理のための秘密鍵を設定

#データベース接続情報
DB_CONFIG = {
    "host":"localhost",
    "database":"aiappdb",
    "user":"postgres",
    "password":"hlstku",
    "port":5432
}

login_manager = LoginManager()
login_manager.init_app(app)


# Userクラス（Flask-Login用）
class User(UserMixin):
    def __init__(self,id, username,password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    """ユーザーIDからUserオブジェクトを還元"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id,username,password FROM users WHERE user_id = %s",(user_id,))
            result = cursor.fetchone()
            if result:
                return User(result[0],result[1],result[2])
            return None


def get_category_list(user_id):
    # """DBから最新のカテゴリリストを取得する関数"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT category_name FROM task_categories WHERE user_id IS NULL ORDER BY category_id",(user_id,))
            # リスト内包表記（リスト作成）
            category_list = [row[0] for row in cursor.fetchall()] #rowの中身はタプルだからrow[0]で値のみを取り出す
            return category_list

# def get_user_id(username):
#     """DBからユーザーIDを取得する関数"""
#     with psycopg2.connect(**DB_CONFIG) as conn:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
#             result = cursor.fetchone()
#             if result:
#                 return result[0]
#             else:
#                 return None
            
def get_or_create_category_id(category_name,user_id):
    """DBからカテゴリIDを取得する関数。存在しない場合は新規作成"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT category_id FROM task_categories WHERE category_name = %s AND user_id = %s", (category_name,user_id))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                cursor.execute("INSERT INTO task_categories(category_name,user_id) VALUES (%s,%s) RETURNING category_id", (category_name,user_id))
                category_id = cursor.fetchone()[0]
                conn.commit()
                return category_id
            
def insert_task(task_data, priority, user_id, category_id):
    """タスクをDBに挿入する関数"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            insert_sql = """
            INSERT INTO tasks (
                user_id, task_name, priority, rem_days, criticality, time_required, impact_scope, urgency, category_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
            """
            cursor.execute(insert_sql, (
                user_id,
                task_data["task_name"],
                priority,
                task_data["rem_days"],
                task_data["criticality"],
                task_data["time_required"],
                task_data["impact_scope"],
                task_data["urgency"],
                category_id
            ))
            conn.commit()
            print("タスクが正常に挿入されました。")

def get_task_by_user(user_id, limit=None):
    """指定したユーザーのタスクを取得する関数"""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT  tasks.task_id,
                    tasks.task_name,
                    tasks.priority,
                    tasks.rem_days,
                    tasks.criticality,
                    tasks.time_required,
                    tasks.impact_scope,
                    tasks.urgency,
                    task_categories.category_name,
                    tasks.memo
            FROM tasks
            LEFT JOIN task_categories
            ON tasks.category_id = task_categories.category_id
            WHERE tasks.user_id = %s
            ORDER BY tasks.priority DESC
            """
            if limit:
                query += " LIMIT %s"
                cursor.execute(query, (user_id, limit))
            else:
                cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
    task_list = []
    for row in rows:
        task_info = {
            "task_id":row[0],
            "task_name": row[1],
            "priority": float(row[2]),
            "rem_days": float(row[3]),
            "criticality": int(row[4]),
            "time_required": float(row[5]),
            "impact_scope": int(row[6]),
            "urgency": float(row[7]),
            "cat_name": row[8],
            "memo":row[9]
        }
        task_list.append(task_info)
    return task_list
# ----ここまでSQL操作-----

# ルーティング（画面遷移）設定
@app.route("/",methods=["GET","POST"])
def login():
    if request.method == "POST":
        # ここでログイン処理を実装
        username = request.form["username"]
        password_input = request.form["password"]
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id, username, password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

            if user and check_password_hash(user[2],password_input):
                login_user(User(user[0],user[1],user[2]))
                flash("ログイン成功！")
                return redirect(url_for("top"))
            else:
                flash("ユーザー名またはパスワードが間違っています。")
                return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """ログアウトする関数"""
    logout_user()
    flash("ログアウトしました。")
    return redirect(url_for("login"))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # ここでサインイン処理を実装
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                # ユーザー名が既に存在するか確認
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    flash("そのユーザー名は既に使用されています。")
                    return render_template("signin.html")
                # 新しいユーザーをデータベースに挿入
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
                flash("サインイン成功！ログインしてください。")
                return redirect(url_for("login"))
        # ユーザー認証のロジックを追加
    return render_template("signin.html")

@app.route("/top")
@login_required
def top():
    user_id = current_user.id
    top_tasks = get_task_by_user(user_id, limit=5)
    return render_template("top.html", top_tasks=top_tasks,username=current_user.username)

@app.route("/task/<int:task_id>/edit_task",methods=["GET"])
@login_required
def edit_task(task_id):
    user_id = current_user.id
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.task_name, t.rem_days, t.criticality, t.time_required, t.impact_scope, t.category_id, c.category_name FROM tasks t LEFT JOIN task_categories c ON t.category_id = c.category_id WHERE t.task_id = %s AND t.user_id = %s
            """, (task_id,user_id))

            task = cursor.fetchone()
    if not task:
        flash("タスクが見つかりません。")
        return redirect(url_for("top"))
    
    criticality_map = {0: "なし", 1: "小", 2: "中", 3: "大", 4: "大"}
    impact_scope_map = {0: "onlyMe", 1: "smallGroup", 2: "allTeam", 3: "moreThanTeam"}
    
    task_data = {
        "task_id": task_id,
        "task_name": task[0],
        "rem_days": task[1],
        "criticality": criticality_map.get(task[2],"なし"),
        "time_required": task[3],
        "impact_scope": impact_scope_map.get(task[4],"onlyMe"),
        "category_id": task[5],
        "category_name":task[6]
    }

    return render_template("editTask.html",task=task_data,cat_list=get_category_list(user_id))

@app.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    user_id = current_user.id
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE task_id = %s AND user_id = %s",(task_id,user_id))
            conn.commit()
    flash("タスクを削除しました。")
    return redirect(url_for("top"))

# @app.route("/add_imp_task")
# @login_required
# def add_imp_task():
#     user_id = current_user.id
#     selected_cat = request.args.get("category","すべて")
#     sort_value = request.args.get("sortValue","latest")

#     # 並べ替え条指定指定
#     if sort_value == "priority":
#         order_by = "ORDER BY t.priority DESC"
#     elif sort_value == "rem_days":
#         order_by = "ORDER BY t.rem_days ASC"
#     elif sort_value == "priority":
#         order_by = "ORDER BY t.time_required DESC"
#     else:
#         order_by = "ORDER BY t.task_id ASC"

#     with psycopg2.connect(**DB_CONFIG) as conn:
#         with conn.cursor() as cursor:
#             if selected_cat and selected_cat != "すべて":
#                 cursor.execute(f"""
#                     SELECT t.task_name,
#                             t.priority,
#                             t.rem_days,
#                             t.criticality,
#                             t.time_required,
#                             t.impact_scope,
#                             t.urgency,
#                             c.category_name
#                     FROM tasks t
#                     LEFT JOIN task_categories c
#                     ON t.category_id = c.category_id WHERE t.user_id = %s AND c.category_name = %s {order_by};
#                 """,(user_id,selected_cat))
#             else:
#                 cursor.execute(f"""
#                     SELECT t.task_name,
#                             t.priority,
#                             t.rem_days,
#                             t.criticality,
#                             t.time_required,
#                             t.impact_scope,
#                             t.urgency,
#                             c.category_name
#                     FROM tasks t
#                     LEFT JOIN task_categories c
#                     ON t.category_id = c.category_id WHERE t.user_id = %s {order_by};
#                 """,(user_id,))

#             rows = cursor.fetchall()

#         task_list = []
#         for row in rows:
#             # criticality_map = {3: "大", 2: "中", 1: "小", 0: "なし"}
#             # impact_scope_map = {3: "それ以上", 2: "チーム全体", 1: "小グループ", 0: "なし"}
#             task_info = {
#             # 文字列以外の列の型変換
#             "task_name" : row[0],
#             "priority" : float(row[1]),
#             "rem_days" : float(row[2]),
#             "criticality" : int(row[3]),
#             "time_required" : float(row[4]),
#             "impact_scope" : int(row[5]),
#             "urgency" : float(row[6]),
#             "cat_name" : row[7],
#             }
#             task_list.append(task_info)
        
#     return render_template("addImpTask.html", task_list=task_list, cat_list=get_category_list(user_id),selected_cat=selected_cat,sort_value=sort_value)

@app.route("/add_to_top", methods=["POST"])
@login_required
def add_to_top():
    task_ids = request.form.getlist("task_ids")  # 選択されたタスクIDのリスト
    user_id = current_user.id

    # 選択タスクを top_tasks に追加する処理（DBにフラグを追加する例）
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            for task_id in task_ids:
                cursor.execute(
                    "UPDATE tasks SET is_top = TRUE WHERE task_id = %s AND user_id = %s",
                    (task_id, user_id)
                )
        conn.commit()

    flash(f"{len(task_ids)} 件のタスクをトップに追加しました。")
    return redirect(url_for("top_view"))

@app.route("/list", methods = ["GET"])
@login_required
def task_list_view():
    user_id = current_user.id
    selected_cat = request.args.get("category","すべて")
    sort_value = request.args.get("sortValue","latest")

    # 並べ替え条指定指定
    if sort_value == "priority":
        order_by = "ORDER BY t.priority DESC"
    elif sort_value == "rem_days":
        order_by = "ORDER BY t.rem_days ASC"
    elif sort_value == "priority":
        order_by = "ORDER BY t.time_required DESC"
    else:
        order_by = "ORDER BY t.task_id ASC"

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            if selected_cat and selected_cat != "すべて":
                cursor.execute(f"""
                    SELECT t.task_name,
                            t.priority,
                            t.rem_days,
                            t.criticality,
                            t.time_required,
                            t.impact_scope,
                            t.urgency,
                            c.category_name, t.task_id
                    FROM tasks t
                    LEFT JOIN task_categories c
                    ON t.category_id = c.category_id WHERE t.user_id = %s AND c.category_name = %s {order_by};
                """,(user_id,selected_cat))
            else:
                cursor.execute(f"""
                    SELECT t.task_name,
                            t.priority,
                            t.rem_days,
                            t.criticality,
                            t.time_required,
                            t.impact_scope,
                            t.urgency,
                            c.category_name, t.task_id
                    FROM tasks t
                    LEFT JOIN task_categories c
                    ON t.category_id = c.category_id WHERE t.user_id = %s {order_by};
                """,(user_id,))

            rows = cursor.fetchall()

        task_list = []
        for row in rows:
            # criticality_map = {3: "大", 2: "中", 1: "小", 0: "なし"}
            # impact_scope_map = {3: "それ以上", 2: "チーム全体", 1: "小グループ", 0: "なし"}
            task_info = {
            # 文字列以外の列の型変換
            "task_name" : row[0],
            "priority" : float(row[1]),
            "rem_days" : float(row[2]),
            "criticality" : int(row[3]),
            "time_required" : float(row[4]),
            "impact_scope" : int(row[5]),
            "urgency" : float(row[6]),
            "cat_name" : row[7],
            "task_id": row[8],
            }
            task_list.append(task_info)
        
    return render_template("taskList.html", task_list=task_list, cat_list=get_category_list(user_id),selected_cat=selected_cat,sort_value=sort_value)

@app.route("/edit",methods=["GET","POST"])
@login_required
def finish_edit():
    user_id = current_user.id
    category_list = get_category_list(user_id)
    task_id = request.args.get("task_id")

    if not task_id:
        flash("タスクが指定されていません。")
        return redirect(url_for("top"))

    # 編集モードのときは、DBからデータを取得してフォーム初期値に渡す
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT task_id,task_name, rem_days, criticality, time_required, impact_scope, category_id FROM tasks WHERE task_id = %s AND user_id = %s""",(task_id,user_id))
            result = cursor.fetchone()

    if result:
        rem_days = result[2]
        deadline_date = datetime.now() + timedelta(days=rem_days)
        task_data = {
            "task_id": result[0],
            "task_name": result[1],
            "deadline":deadline_date.strftime("%Y-%m-%dT%H:%M"),
            "rem_days": result[2],
            "criticality": result[3],
            "time_required": result[4],
            "impact_scope": result[5],
            "category_id": result[6],
        }
    else:
        flash("指定されたタスクが見つかりません。")
        return redirect(url_for("top"))

# POST：編集完了時
    if request.method == "POST":
        # HTMLのinputから受け取った値（例:'2025-10-10T18:30'）
        specific_date_str = request.form["specific_date"]
        
        # criticalityを取得し、数値に変換
        criticality_str = request.form["criticality"]

        if criticality_str == "大":
            criticality = 3
        elif criticality_str == "中":
            criticality = 2
        elif criticality_str == "小":
            criticality = 1
        else:
            criticality = 0  # 不明な値の場合は0に設定
        
        # 影響範囲を取得し、数値に変換
        impact_scope_str = request.form["impact_scope"]
        if impact_scope_str == "それ以上":
            impact_scope = 3
        elif impact_scope_str == "チーム全体":
            impact_scope = 2
        elif impact_scope_str == "小グループ":
            impact_scope = 1
        else:
            impact_scope = 0  # 不明な値の場合は0に設定


        # 文字列をdatetime型に変換
        specific_date = datetime.strptime(specific_date_str, "%Y-%m-%dT%H:%M")

        # 今日の日付を取得
        now = datetime.now()

        diff = specific_date - now
        diff_days = diff.days  # 残り日数
        print(f"あと{diff_days}日です。")


        task_data = {
            "task_name": request.form["task_name"],
            "rem_days": diff_days,
            "criticality": criticality,
            "time_required": float(request.form["time_required"]),
            "impact_scope": impact_scope,
            "urgency" : round(float(request.form["time_required"]) / diff_days,2),
            "category": request.form["category"].strip(),
            "memo":request.form["memo"]
        }
        priority = predict_priority(task_data,category_list)

        #priorityがDataFrameの場合に、floatに変換
        if isinstance(priority, pd.DataFrame):
            priority = float(priority['priority'].iloc[0])

# # -----ここからSQL操作-----

        # category_idを取得または作成
        category_id = get_or_create_category_id(task_data["category"],user_id)

# 編集モードならUPDATE、それ以外ならINSERT
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE tasks SET task_name=%s,priority=%s, rem_days=%s,criticality=%s,time_required=%s,impact_scope=%s, urgency=%s, category_id=%s,memo=%s WHERE task_id=%s AND user_id=%s
                    """,(
                        task_data["task_name"], priority,task_data["rem_days"],task_data["criticality"],task_data["time_required"],task_data["impact_scope"],task_data["urgency"],category_id,
                        task_data["memo"],task_id,user_id
                    ))
                    flash("タスクを更新しました。")
            conn.commit()
    return redirect(url_for("lanking"))

@app.route("/add", methods = ["GET","POST"])
@login_required
def add_task2():
    user_id = current_user.id
    category_list = get_category_list(user_id)
    task_data = None

    if request.method == "POST":
        # HTMLのinputから受け取った値（例:'2025-10-10T18:30'）
        specific_date_str = request.form["specific_date"]
        
        # criticalityを取得し、数値に変換
        criticality_str = request.form["criticality"]

        if criticality_str == "大":
            criticality = 3
        elif criticality_str == "中":
            criticality = 2
        elif criticality_str == "小":
            criticality = 1
        else:
            criticality = 0  # 不明な値の場合は0に設定
        
        # 影響範囲を取得し、数値に変換
        impact_scope_str = request.form["impact_scope"]
        if impact_scope_str == "それ以上":
            impact_scope = 3
        elif impact_scope_str == "チーム全体":
            impact_scope = 2
        elif impact_scope_str == "小グループ":
            impact_scope = 1
        else:
            impact_scope = 0  # 不明な値の場合は0に設定


        # 文字列をdatetime型に変換
        specific_date = datetime.strptime(specific_date_str, "%Y-%m-%dT%H:%M")

        # 今日の日付を取得
        now = datetime.now()

        diff = specific_date - now
        diff_days = diff.days  # 残り日数
        print(f"あと{diff_days}日です。")


        task_data = {
            "task_name": request.form["task_name"],
            "rem_days": diff_days,
            "criticality": criticality,
            "time_required": float(request.form["time_required"]),
            "impact_scope": impact_scope,
            "urgency" : round(float(request.form["time_required"]) / diff_days,2),
            "category": request.form["category"].strip(),
            "memo":request.form["memo"]
        }
        priority = predict_priority(task_data,category_list)

        #priorityがDataFrameの場合に、floatに変換
        if isinstance(priority, pd.DataFrame):
            priority = float(priority['priority'].iloc[0])

# # -----ここからSQL操作-----

        # category_idを取得または作成
        category_id = get_or_create_category_id(task_data["category"],user_id)

        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                # タスクを挿入
                insert_task(task_data, priority, current_user.id, category_id)
                flash("新しいタスクを追加しました。")
            conn.commit()

        return redirect(url_for("lanking"))
    return render_template("taskAdd2.html",cat_list=category_list, task_data=task_data)

@app.route("/lanking", methods=["GET","POST"])
@login_required
def lanking():
    user_id = current_user.id

    if request.method == "POST":
        # 並び順データを取得
        task_order = request.form.get("task_order","")
        if not task_order:
            flash("タスクの並び順が取得できませんでした。")
            return redirect(url_for("lanking"))
        
        task_id_list = task_order.split(",")
        # 自分とデフォルトユーザーのタスクを取得
        user_tasks = get_task_by_user(user_id)
        default_tasks = get_task_by_user(3)
        all_tasks_for_ai = pd.DataFrame(user_tasks + default_tasks)

        # カテゴリリスト作成
        cat_list = get_category_list(user_id)

        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                for i, task_id in enumerate(task_id_list):
                    # task_data = next((t for t in user_tasks if str(t["task_id"]) == task_id), None)
                    # if not task_data:
                    #     continue  # タスクが見つからない場合はスキップ

                    # # AIでpriprity予測
                    # new_priority = predict_priority(task_data=task_data, cat_list=cat_list, base_tasks=all_tasks_for_ai)

                    # # 丸めて100点以内におさめる
                    # new_priority = max(0,min(100,round(new_priority, 2)))
                    cursor.execute("UPDATE tasks SET priority = %s WHERE task_id = %s AND user_id = %s", (100-i, task_id, user_id))
            conn.commit()
        flash("タスクの優先順位を更新しました。")
        return redirect(url_for("task_list_view"))
    task_list = get_task_by_user(user_id)
    cat_list = get_category_list(user_id)
    return render_template("taskLanking.html",task_list=task_list, cat_list=cat_list)

if __name__ == "__main__":
    app.run(debug=True)