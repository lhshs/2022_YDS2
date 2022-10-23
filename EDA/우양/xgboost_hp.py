from xgboost import XGBClassifier
import xgboost

model = XGBClassifier(gamma=3, learning_rate=0.3)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(accuracy_score(y_pred, y_test))

fig, ax = plt.subplots(1,1,figsize=(10,8))
plt.rcParams['font.family'] = 'AppleGothic'
xgboost.plot_importance(model, title='feature_importances', xlabel='', ax=ax, max_num_features=20, height=0.4)
# xgboost.plot_importance(xgb, title='feature_importances', xlabel='', grid=False, ax=ax)
plt.show()