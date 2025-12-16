# from flask import Flask, render_template,request,redirect,url_for
# from datetime import datetime
# from services.ai_function import predict_priority

# import pandas as pd
# import csv

# app = Flask(__name__)

# category_list = pd.read_csv("./static/csv/MLdata.csv")["category"].drop_duplicates(keep='first').tolist()

# # ルーティング（画面遷移）設定
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/list", methods = ["GET","POST"])
# def list():
#     task_list = []
#     with open("./static/csv/MLdata.csv", mode="r",newline="" ,encoding="utf-8") as f:
#         reader = csv.reader(f) #デフォルトはカンマ区切り
#         header = next(reader)  # ヘッダー行をスキップ

#         # category列の数をあらかじめ取得
#         category_count = 0
#         while f"category_{category_count}" in header:
#             category_count += 1
        
#         for row in reader:
#             # 文字列以外の列の型変換
#             task_name = row[0]
#             priority = float(row[1])
#             rem_days = float(row[2])
#             criticality_int = int(row[3])
#             time_required = float(row[4])
#             impact_scope_int = int(row[5])
#             urgency = float(row[6])

#             # category列をまとめて型置換
#             categories = [int(row[7 + i]) for i in range(category_count)]

#             # 単一カテゴリ名を取得(最初の1だけ)
#             for i, cat in enumerate(categories):
#                 if cat == 1:
#                     cat_name = category_list[i]
#                     break
#                 else:
#                     categories[i] = ""
#             # cat_one = [cat for cat in categories if cat == 1]

#             # criticalityを取得し、文字に変換
#             if criticality_int == 3:
#                 criticality_str = "大"
#             elif criticality_int == 2:
#                 criticality_str = "中"
#             elif criticality_int == 1:
#                 criticality_str = "小"
#             else:
#                 criticality_str = "なし"
            
#             # 影響範囲を取得し、文字に変換
#             if impact_scope_int == 3:
#                 impact_scope_str = "それ以上"
#             elif impact_scope_int == 2:
#                 impact_scope_str = "チーム全体"
#             elif impact_scope_int == 1:
#                 impact_scope_str = "小グループ"
#             else:
#                 impact_scope_str = "なし"

#             task_info = {
#                 "task_name": task_name,
#                 "priority": priority,
#                 "rem_days": rem_days,
#                 "criticality": criticality_str,
#                 "time_required": time_required,
#                 "impact_scope": impact_scope_str,
#                 "urgency": urgency,
#                 "cat_name": cat_name,
#             }
#             task_list.append(task_info)

        
#     return render_template("taskList.html", task_list=task_list, cat_list=category_list)

# @app.route("/add", methods = ["GET","POST"])
# def add_task():
#     if request.method == "POST":
#         # HTMLのinputから受け取った値（例:'2025-10-10T18:30'）
#         specific_date_str = request.form["specific_date"]
        
#         # criticalityを取得し、数値に変換
#         criticality_str = request.form["criticality"]

#         if criticality_str == "大":
#             criticality = 3
#         elif criticality_str == "中":
#             criticality = 2
#         elif criticality_str == "小":
#             criticality = 1
#         else:
#             criticality = 0  # 不明な値の場合は0に設定
        
#         # 影響範囲を取得し、数値に変換
#         impact_scope_str = request.form["impact_scope"]
#         if impact_scope_str == "それ以上":
#             impact_scope = 3
#         elif impact_scope_str == "チーム全体":
#             impact_scope = 2
#         elif impact_scope_str == "小グループ":
#             impact_scope = 1
#         else:
#             impact_scope = 0  # 不明な値の場合は0に設定


#         # 文字列をdatetime型に変換
#         specific_date = datetime.strptime(specific_date_str, "%Y-%m-%dT%H:%M")

#         # 今日の日付を取得
#         now = datetime.now()

#         diff = specific_date - now
#         diff_days = diff.days  # 残り日数
#         print(f"あと{diff_days}日です。")


#         task_data = {
#             "task_name": request.form["task_name"],
#             "rem_days": diff_days,
#             "criticality": criticality,
#             "time_required": float(request.form["time_required"]),
#             "impact_scope": impact_scope,
#             "urgency" : round(float(request.form["time_required"]) / diff_days,2),
#             "category": request.form["category"].strip()
#         }
#         predict_priority(task_data,category_list)


#         return redirect(url_for("lanking"))
#     return render_template("taskAdd.html",cat_list=category_list)

# @app.route("/lanking")
# def lanking():
#     return render_template("taskLanking.html")

# @app.route("/setting")
# def setting():
#     return render_template("setting.html")

# @app.route("/history")
# def history():
#     return render_template("history.html")

# if __name__ == "__main__":
#     app.run(debug=True)