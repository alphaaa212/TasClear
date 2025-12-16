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
            if not isinstance(base_tasks, pd.DataFrame):
                df = pd.DataFrame(base_tasks)
            else:
                df = base_tasks.copy()

            # cat_name -> category 列に統一
            if "category" not in df.columns and "cat_name" in df.columns:
                df["category"] = df["cat_name"]
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
        # --- カテゴリのダミー変数化 ---
        if cat_list is None:
            cat_list = sorted(df["category"].dropna().unique().tolist())

        for idx, cat_name in enumerate(cat_list):
            df[f"category_{idx}"] = (df["category"] == cat_name).astype(int)

        # --- ラベルと特徴量 ---
        y = df["priority"]
        x = df.drop(columns=["priority", "task_name", "category"])

        # 数値以外の列をすべてfloatに変換（安全策）
        for col in x.columns:
            x[col] = pd.to_numeric(x[col], errors='coerce')

        # --- 新しいタスクデータ ---
        if task_data is None:
            print("新しいタスクデータがありません")
            return None

        new_task = pd.DataFrame([{
            "task_name": task_data["task_name"],
            "rem_days": task_data["rem_days"],
            "criticality": task_data["criticality"],
            "time_required": task_data["time_required"],
            "impact_scope": task_data["impact_scope"],
            "urgency": task_data["urgency"],
            "category": task_data.get("category") or task_data.get("cat_name")
        }])

        # カテゴリのダミー列を追加
        for idx, cat_name in enumerate(cat_list):
            new_task[f"category_{idx}"] = (new_task["category"] == cat_name).astype(int)

        new_task_features = new_task.drop(columns=["task_name", "category"])
        new_task_features = new_task_features.reindex(columns=x.columns, fill_value=0)

        # --- モデル学習 ---
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(x_train, y_train)

        # --- 優先度予測 ---
        new_priority = model.predict(new_task_features)[0]
        new_priority = round(float(new_priority), 2)
        print(f"新しいタスクの優先度は・・・{new_priority}です!")

    except Exception as e:
        print("エラー:", e)
        return None

    return new_priority


if __name__ == "__main__":
    print("スクリプト開始")
    # 例: predict_priority(task_data={"task_name":"テスト", "rem_days":3, "criticality":2, "time_required":1, "impact_scope":1, "urgency":2, "category":"仕事"}, cat_list=["仕事","家庭"])
    print("スクリプト終了")