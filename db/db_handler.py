# import psycopg2

# #データベース接続情報
# conn = psycopg2.connect(
#     host="localhost",
#     database="aiappdb",
#     user="testuser1",
#     password="dosijd"
# )

# #カーソル生成
# cursor = conn.cursor()

# # --ここでSQL操作--
# username = "alphaaa1"

# # user_idを取得
# cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
# user_result = cursor.fetchone()

# if user_result is None:
#     print("ユーザーが見つかりません。")
# else:
#     user_id = user_result[0]
#     print(f"ユーザー{username}のuserID: {user_id}")

#     # カテゴリ名からIDを取得
#     cursor.execute("SELECT category_id FROM task_categories WHERE category_name = %s", (task_data["category"],))
#     cat_result = cursor.fetchone()

#     if cat_result is None:
#         print("fカテゴリ{category_name}が見つかりません}")
#     else:
#         category_id = cat_result[0]

#     # タスク情報を挿入
#     insert_sql = """
#     INSERT INTO tasks (
#         user_id, task_name, priority, rem_days, criticality, time_required, impact_scope, urgency, category_id
#     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#     """

#     cursor.execute(insert_sql, (
#         user_id,
#         task_data["task_name"],
#         priority,
#         task_data["rem_days"],
#         task_data["criticality"],
#         task_data["time_required"],
#         task_data["impact_scope"],
#         task_data["urgency"],
#         category_id
#     ))
#     conn.commit()
#     print("タスクが正常に挿入されました。")

# # リソース解放
# cursor.close()
# conn.close()