import random

import numpy
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

cur_rk_df = pd.read_csv('Текущая РК.csv', header=None)
org_df = pd.read_csv('Органический трафик.csv')
prev_rk_df = pd.read_csv('Предыдущая РК.csv')

labels = ['action', 'views', 'conv_views', 'visits', 'conv_visits', 'aborted', 'perc_aborted', 'depth', 'time',
          'new_users_with_abort', 'perc_new_users_with_abort', 'new_users', 'perc_new_users']
cur_rk_df.columns = labels
cur_rk_df.drop([0, 1], inplace=True)


max_val = cur_rk_df['views'].max()
max_row = cur_rk_df.loc[cur_rk_df['views'].idxmax()]
# print(max_val, max_row[labels])
cur_rk_df.views = pd.to_numeric(cur_rk_df.views)
cur_rk_df.visits = pd.to_numeric(cur_rk_df.visits)

print('data', cur_rk_df[cur_rk_df['visits'] != 0]['visits'].values)
quantile = cur_rk_df[cur_rk_df['visits'] != 0]['visits'].quantile([0.25, 0.50, 0.75])
print(cur_rk_df.visits)
IQR = quantile.iloc[2] - quantile.iloc[0]
print('квантили', quantile)
print('межквартилиальный размах', IQR)
print('полтора квантиля', IQR * 1.5)

print('данные с выбросами')
outliers_row = cur_rk_df[cur_rk_df['views'] > IQR * 1.5]
print(outliers_row)
print([(i[0], i[3]) for i in outliers_row.values])

d = cur_rk_df.nlargest(3, 'views')
v = cur_rk_df.nlargest(3, 'visits')
print('наибольшие параметрты для просмотров:', [(l[0], l[1]) for l in d.values])
print('наибольшие параметрты для визитов:', [(l[0], l[3]) for l in v.values])

params = [int(i) for i in cur_rk_df.views]
names = cur_rk_df.action

# Создаем матрицу разностей
matrix = np.zeros((len(params), len(params)))
annotations = np.empty_like(matrix, dtype=object)

for i in range(len(params)):
    for j in range(len(params)):
        sub = params[i] - params[j]
        matrix[i, j] = sub

        if sub > 0:
            annotations[i, j] = f"+{sub}"
        elif sub < 0:
            annotations[i, j] = f"{sub}"
        else:
            annotations[i, j] = "0"

plt.figure(figsize=(12, 10))
sns.heatmap(matrix,
            annot=annotations,
            fmt='',
            cmap='RdBu_r',
            center=0,
            xticklabels=names,
            yticklabels=names,
            cbar_kws={'label': 'Разность значений'})

print('макс значение матрицы', matrix.max())
print('строка-столбец максимального значения', numpy.unravel_index(matrix.argmax(), matrix.shape))
print(matrix[2][1])
plt.title('Матрица сравнений доли новых пользователей', fontsize=14)
plt.xticks(rotation=80)
plt.yticks(rotation=0)
plt.tight_layout()
print([i for i in range(2, 5*3, 3)])
plt.show()
data = cur_rk_df.drop(columns=['action', 'time']).corr()
plt.figure(figsize=[10,10])
sns.heatmap(data, xticklabels=data.columns, yticklabels=data.columns, annot=True)
plt.show()