# タスクをcsvからデータベースに移動するスクリプト（済）


# import pandas as pd
# import psycopg2
# df = pd.read_csv("./static/csv/MLdata.csv")

# #データベース接続情報
# conn = psycopg2.connect(
#     host="localhost",
#     database="aiappdb",
#     user="postgres",
#     password="hlstku"
# )
# cursor = conn.cursor()

# # ---カテゴリ登録---
# categories = df["category"].drop_duplicates(keep='first').tolist()
# for cat in categories:
#     cursor.execute("INSERT INTO task_categories (category_name) VALUES (%s) ON CONFLICT (category_name) DO NOTHING", (cat,))

# conn.commit()
# print("カテゴリ登録完了")

# # 仮ユーザー登録
# cursor.execute("INSERT INTO users (username,password) VALUES(%s,%s) ON CONFLICT (username) DO NOTHING", ("learnDataUser","nviwbhk"))
# cursor.execute("SELECT user_id FROM users WHERE username = %s", ("learnDataUser",))
# user_id = cursor.fetchone()[0]

# # タスク登録
# for index, row in df.iterrows():
#     # category_idを取得
#     cursor.execute("SELECT category_id FROM task_categories WHERE category_name = %s", (row["category"],))
#     category_id = cursor.fetchone()[0]

#     cursor.execute("""
#     INSERT INTO tasks (
#         user_id, task_name, priority, rem_days, criticality, time_required, impact_scope, urgency, category_id
#     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """, (
#         user_id,
#         row["task_name"],
#         row["priority"],
#         row["rem_days"],
#         row["criticality"],
#         row["time_required"],
#         row["impact_scope"],
#         row["urgency"],
#         category_id
#     ))
# conn.commit()
# print("タスク登録完了")
# # リソース解放
# cursor.close()
# conn.close()