from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('data/7_Yvalue.csv')
df.date = pd.to_datetime(df.date)
df = df.set_index('date')

scaler = MinMaxScaler()
scaler.fit(df)
df_scaled = scaler.transform(df)

df_scaled_f = pd.DataFrame(df_scaled, columns=['priceMinMax','kospiMinMax'])
df = df.reset_index()
df_scaled_f.insert(0,'date', df['date'] )

df = df.merge(df_scaled_f, how='left')
df['k-p_diff'] = df['kospiMinMax'] - df['priceMinMax']

df.head()

def consecutive_fall(df:pd.DataFrame, cons_day:int, mean_day:int, rest_value:int)->pd.DataFrame:
    k_p = list(df['k-p_diff'])
    k_p_day = []

    for i in range(369-cons_day):
        cnt = 0
        for j in k_p[i:i+cons_day]:
            if j > 0:
                cnt += 1
            else :
                break

        if cnt == cons_day:
            k_p_day.append(1)

        elif (cnt>mean_day)&(np.mean(k_p[i:i+cons_day]) > 0.05):
            k_p_day.append(0.5)
            
        else:
            k_p_day.append(0)

    for i in range(cons_day):
        k_p_day.append(rest_value)
            
    df[f'k_p{cons_day}'] = k_p_day
    return df.head()

consecutive_fall(df, 10, 4, 0)

# 주가 데이터 그래프
plt.figure(figsize=(15, 6))
plt.rcParams['font.family'] = 'AppleGothic'
# plt.rcParams['font.size'] = 23
# plt.rcParams['figure.figsize'] = (13, 8) # figsize 고정
sns.lineplot(data=df, x="date", y="priceMinMax", label='priceMinMax')
sns.lineplot(data=df, x="date", y="kospiMinMax", label='kospiMinMax')
sns.lineplot(data=df, x="date", y="k-p_diff", label='kospi-price')
sns.scatterplot(data=df, x="date", y='k_p10')


plt.show()