import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import psycopg2

# --- ① DB設定追加 ---
DB_CONFIG = {
    "host": "localhost",
    "database": "aiappdb",
    "user": "postgres",
    "password": "hlstku"
}

def predict_priority(task_data=None,cat_list=None,base_tasks=None):
    try:
        if base_tasks is not None and len(base_tasks) >0:
            print("既存のタスクデータを使用します")
            if "category" not in base_tasks.columns and "cat_name" in base_tasks.columns:
                base_tasks["category"] = base_tasks["cat_name"]
            df = pd.DataFrame(base_tasks)
        else:
            with psycopg2.connect(**DB_CONFIG) as conn:
                query = """
                SELECT
                    tasks.task_name,
                    tasks.priority,
                    tasks.rem_days,
                    tasks.criticality,
                    tasks.time_required,
                    tasks.impact_scope,
                    tasks.urgency,
                    task_categories.category_name AS category
                FROM tasks
                JOIN task_categories ON tasks.category_id = task_categories.category_id;
                """
                df = pd.read_sql_query(query, conn)
                print(df.columns)
            print("DBからデータ取得成功")

        if df.empty:
            print("データベースにデータが存在しません")
            return None
        # ラベルと特徴量に分ける
        # task_target（y）を priority 列に設定
        y = df["priority"]
        # task_data（x）を priority 以外の列に設定
        x = df.drop(columns=["priority","task_name","category"]) 

        if task_data is None:
            print("新しいタスクデータがありません")
            return None
        
        if cat_list is None:
            raise ValueError("カテゴリリストが指定されていません")

        # 新しいタスクをDataFrame化
        new_task = pd.DataFrame([{
            "task_name":task_data["task_name"],
            "rem_days":task_data["rem_days"],
            "criticality":task_data["criticality"],
            "time_required":task_data["time_required"],
            "impact_scope":task_data["impact_scope"],
            "urgency":task_data["urgency"],
            "category":task_data.get("category") or task_data.get("cat_name")#["category"] 文字列で保持
        }])

        # カテゴリ分けの処理（カテゴリのダミー列を0で初期化）
        for i in range(len(cat_list)):
            new_task[f"category_{i}"] = 0

        # new_taskのカテゴリ名を取得
        cat_name = new_task["category"].iloc[0].strip()
        # カテゴリ名が既存リストにある場合
        if cat_name in cat_list:
            idx = cat_list.index(cat_name)
            new_task.loc[0,f"category_{idx}"] = 1
        else:
            # 新しいカテゴリの場合はcat_listに追加して新しい列を作成
            cat_list.append(cat_name)
            new_idx = len(cat_list) -1 #新しい列番号
            df[f"category_{new_idx}"] = 0
            new_task[f"category_{new_idx}"] = 1

        # 訓練データとテストデータに8:2の割合で分割
        x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.2, random_state=42)

        print(f"訓練データ数：{len(x_train)}")
        print(f"テストデータ数：{len(y_train)}")

        # RandomForestRegressorモデルを初期化
        model = RandomForestRegressor(n_estimators=100,
        random_state=42)
        model.fit(x_train, y_train)

        new_task_features = new_task.drop(columns=["category","task_name"])
        new_task_features = new_task_features.reindex(columns=x.columns,fill_value=0)

        # 優先度を予測
        new_priority = model.predict(new_task_features)[0]
        new_priority = round(float(new_priority),2)
        print(f"新しいタスクの優先度は・・・{new_priority}です!")

        # with psycopg2.connect(**DB_CONFIG) as conn:
        #     with conn.cursor() as cursor:
        #         insert_sql = """
        #         INSERT INTO tasks (task_name, priority, rem_days, criticality, time_required, impact_scope, urgency, category_id, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, (SELECT category_id FROM task_categories WHERE category_name = %s),(SELECT user_id FROM users WHERE username = %s))"""
        #         cursor.execute(insert_sql, (
        #             task_data["task_name"],
        #             new_priority,
        #             task_data["rem_days"],
        #             task_data["criticality"],
        #             task_data["time_required"],
        #             task_data["impact_scope"],
        #             task_data["urgency"],
        #             task_data["category"],
        #             task_data.get("username") #デフォルトユーザー
        #         ))
        #     conn.commit()
        # print("新しいタスクをDBに追加しました")

        # # CSV用DataFrameを作成
        # new_task_to_save = new_task_features.copy()
        # new_task_to_save["task_name"] = task_data["task_name"]
        # new_task_to_save["priority"] = new_priority
        # new_task_to_save["category"] = task_data["category"]

        # new_task_to_save = new_task_to_save.reindex(columns=df.columns,fill_value=0)
        
        # # CSVに列を追加
        # df_new = pd.concat([df,new_task_to_save],ignore_index=False)
        # df_new.to_csv("static/csv/MLdata.csv",index=False)
        # print("新しいタスクをCSVに追加しました")

    except FileNotFoundError:
        print("CSVファイルが見つかりません。パスを確認してください")
        return None
    
    return new_priority

if __name__ == "__main__":
    print("スクリプト開始")
    predict_priority()
    print("スクリプト終了")
# モデルはここに書く