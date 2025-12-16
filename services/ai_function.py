# import pandas as pd
# import numpy as np
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# # from sklearn.preprocessing import OneHotEncoder

# # from sklearn.metrics import mean_squared_error, r2_score
# # import matplotlib.pyplot as plt
# # import seaborn as sns

# def predict_priority(task_data=None,cat_list=None):
#     try:
#         df = pd.read_csv("static/csv/MLdata.csv")
#         # ラベルと特徴量に分ける
#         # task_target（y）を priority 列に設定
#         y = df["priority"]
#         # task_data（x）を priority 以外の列に設定
#         x = df.drop(columns=["priority","task_name","category"]) 

#         # # category列をエンコーディング
#         # x = pd.get_dummies(x, columns=["category"])
#         # encoder_df = pd.DataFrame(encoder.fit_transform(df[['category']]).toarray())

#         # final_df = df.join(encoder_df)
#         # final_df.drop('category',axis=1,inPlace=True)

# # 【以下学習データの精度を評価するプロセス】
#         # # 学習済みモデルでテストデータの優先度を予測
#         # y_pred = model.predict(x_test)

#         # # 決定係数R2スコアでモデルの精度を評価
#         # r2 = r2_score(y_test,y_pred)
#         # mse = mean_squared_error(y_test, y_pred)

#         # print(f"決定係数(R2 Score)：{r2:.3f}")
#         # print(f"平均二乗誤差(MSE)：{mse:.3f}")

#         # # 特徴量の重要度を取得
#         # importances = model.feature_importances_
        
#         # # 可視化のためのデータフレームを作成
#         # feature_importance_df = pd.DataFrame({
#         #     "Feature":x.columns,
#         #     "Importance":importances
#         #     }).sort_values("Importance",ascending=False)
        
#         # # 棒グラフで可視化
#         # plt.figure(figsize=(10,6))
#         # sns.barplot(x="Importance",y="Feature",data=feature_importance_df)
#         # plt.title("Feature Importance")
#         # plt.show()
# # ＜精度評価ここまで＞

#         if task_data is None:
#             print("新しいタスクデータがありません")
#             return None
        
#         if cat_list is None:
#             raise ValueError("カテゴリリストが指定されていません")

#         # 新しいタスクをDataFrame化
#         new_task = pd.DataFrame([{
#             "task_name":task_data["task_name"],
#             "rem_days":task_data["rem_days"],
#             "criticality":task_data["criticality"],
#             "time_required":task_data["time_required"],
#             "impact_scope":task_data["impact_scope"],
#             "urgency":task_data["urgency"],
#             "category":task_data["category"] #文字列で保持
#         }])

#         # カテゴリ分けの処理（カテゴリのダミー列を0で初期化）
#         for i in range(len(cat_list)):
#             new_task[f"category_{i}"] = 0
#         # new_taskのカテゴリ名を取得
#         cat_name = new_task["category"].iloc[0].strip()
        
#         # カテゴリ名が既存リストにある場合
#         if cat_name in cat_list:
#             idx = cat_list.index(cat_name)
#             new_task.loc[0,f"category_{idx}"] = 1
#         else:
#             # 新しいカテゴリの場合はcat_listに追加して新しい列を作成
#             cat_list.append(cat_name)
#             new_idx = len(cat_list) -1 #新しい列番号
#             df[f"category_{new_idx}"] = 0
#             new_task[f"category_{new_idx}"] = 1

#         # 訓練データとテストデータに8:2の割合で分割
#         x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.2, random_state=42)

#         print(f"訓練データ数：{len(x_train)}")
#         print(f"テストデータ数：{len(y_train)}")

#         # RandomForestRegressorモデルを初期化
#         model = RandomForestRegressor(n_estimators=100,
#         random_state=42)
#         model.fit(x_train, y_train)


#         # #category列を削除して学習データと合わせる
#         # # 学習時の列だけを取得（task_nameを除外）
#         # feature_columns = x.columns

#         # # new_task_featuresに学習列だけを残す
#         # feature_columns = list(x.columns) #学習列
#         # for col in new_task.columns:
#         #     if col.startswith("category_") and col not in feature_columns:
#         #         feature_columns.append(col)

#         new_task_features = new_task.drop(columns=["category","task_name"])
#         new_task_features = new_task_features.reindex(columns=x.columns,fill_value=0)

#         # 優先度を予測
#         new_priority = round(model.predict(new_task_features)[0],4)
#         print(f"新しいタスクの優先度は・・・{new_priority}です!")

#         # CSV用DataFrameを作成
#         new_task_to_save = new_task_features.copy()
#         new_task_to_save["task_name"] = task_data["task_name"]
#         new_task_to_save["priority"] = new_priority
#         new_task_to_save["category"] = task_data["category"]

#         new_task_to_save = new_task_to_save.reindex(columns=df.columns,fill_value=0)
        
#         # CSVに列を追加
#         df_new = pd.concat([df,new_task_to_save],ignore_index=False)
#         df_new.to_csv("static/csv/MLdata.csv",index=False)
#         print("新しいタスクをCSVに追加しました")

#     except FileNotFoundError:
#         print("CSVファイルが見つかりません。パスを確認してください")
#         return None
    
#     print("CSV読み込み成功")
#     print(df.tail(3))
#     return df_new

# if __name__ == "__main__":
#     print("スクリプト開始")
#     predict_priority()
#     print("スクリプト終了")
# # モデルはここに書く