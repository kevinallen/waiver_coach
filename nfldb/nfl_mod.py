
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn import linear_model

np.random.seed(1)

# load csv
stats = pd.read_csv('raw.csv')
print stats.head(5)

### draw box plot of rushing yards, all RBs

# yr = 2014
# stats_yr = stats[stats['year']==yr]

players_list = list(set(stats['full_name']))
stats_by_player = stats.groupby(['full_name'])
stats_list = []

for player in players_list[:50] :
    player_stat = stats_by_player.get_group(player)
    stats_list.append(list(player_stat['rushing_yds']))


plt.subplots(figsize=(10,20))
plt.boxplot(stats_list, vert=False)
plt.yticks(range(1,51), players_list[:50])
plt.show()

### generate two sets of training and test data set
# 0-filled: fills non-play weeks with 0s
# avg-filled: fills non-play weeks with the average stats of that player

# set number of past weeks to track
num_wks = 6
stat_list = ['time', 'rushing_att', 'rushing_tds', 'rushing_yds', 'receiving_yds','receiving_tar','receiving_rec','receiving_tds','fumbles_lost']

input_list = []; input_avg_list = []; output_list = []; player_name_list

for player in players_list :   # for every player
    player_stat = stats_by_player.get_group(player).sort_index(by=['time'], ascending=False)
    player_avg = list(player_stat.mean(axis=0))   # keep avg stat for this player
    array_stat = player_stat[stat_list].as_matrix()
    for i in range(array_stat.shape[0]-1) :
        wk = int(array_stat[i][0])
        wanted_input_wks = [str(x) for x in range(wk - num_wks, wk)]   # weeks to look for
        max_row = min(i+num_wks+1, array_stat.shape[0])
        played_wks = [str(array_stat[x][0]) for x in range(i+1, max_row)]   # weeks with play record
        if len(set(wanted_input_wks) & set(played_wks)) >= (num_wks * 0.6) :   # only if played in more than 60% of the past n weeks 
            output_list.append(array_stat[i][1:])   # add in the label set
            temp_list = []; temp_avg_list = []
            for j in range(num_wks) :
                if i+j < array_stat.shape[0] :
                    if str(array_stat[i+j][0]) in wanted_input_wks :
                        temp_list.extend(array_stat[i+j][1:])   # add in the data set
                        temp_avg_list.extend(array_stat[i+j][1:])
                    else:
                        temp_list.extend([0] * (len(stat_list)-1))   # fill with 0s
                        temp_avg_list.extend(player_avg[1:len(stat_list)+1])   # fill with avg stats
                else:
                    temp_list.extend([0] * (len(stat_list)-1))   # fill with 0s
                    temp_avg_list.extend(player_avg[1:len(stat_list)+1])   # fill with avg stats 
            input_list.append(temp_list)
            input_avg_list.append(temp_avg_list)


# convert to array
data = np.array(input_list)
data_avg = np.array(input_avg_list)
labels = np.array(output_list)

# shuffle and create training and test data set
shuffle = np.random.permutation(range(data.shape[0]))

data,data_avg,labels = data[shuffle],data_avg[shuffle],labels[shuffle]

train_data = data[:2000]
train_avg_data = data_avg[:2000]
train_labels = labels[:2000]

test_data = data[2000:]
test_avg_data = data_avg[2000:]
test_labels = labels[2000:]

print 'Train data set: ', train_data.shape, train_labels.shape
print 'Test data set: ' , test_data.shape, test_labels.shape


def PCA_proj():
    var=[]
    # run PCA for k from 1 to 20 and record the explained variance ratio
    for k in range(1,21):
        pca = PCA(n_components = k)
        pca.fit(train_data)
        var.append(sum(pca.explained_variance_ratio_))
    # plot the variance explained
    plt.plot(range(1,21), var)
    plt.xlabel("number of principal components", fontsize=12)
    plt.ylabel("variance explained", fontsize=12)
    plt.title("variance covered by first k principal components", fontsize=14)
    plt.show()
    
PCA_proj()

stat_num = 3

# no PCA regression
LR = linear_model.LinearRegression()
LR.fit(train_data, train_labels)
print "stat: %s, # of weeks: %d" % (stat_list[stat_num], num_wks)
print "Linear Regression(0 filled): RMSE %.2f" % np.sqrt(np.mean((LR.predict(test_data)[:,stat_num] - test_labels[:,stat_num]) ** 2))

LR2 = linear_model.LinearRegression()
LR2.fit(train_avg_data, train_labels)
print "Linear Regression(avg filled): RMSE %.2f" % np.sqrt(np.mean((LR2.predict(test_avg_data)[:,stat_num] - test_labels[:,stat_num]) ** 2))

# PCA with k components
k = 10
pca = PCA(n_components = k)
pca_train = pca.fit_transform(train_data)
pca_test = pca.fit_transform(test_data)

pcaLR = linear_model.LinearRegression()
pcaLR.fit(pca_train, train_labels)
print "PCA with %d components(0 filled): RMSE %.2f" % (k,np.sqrt(np.mean((pcaLR.predict(pca_test)[:,stat_num] - test_labels[:,stat_num]) ** 2)))

pca2 = PCA(n_components = k)
pca_train2 = pca2.fit_transform(train_avg_data)
pca_test2 = pca2.fit_transform(test_avg_data)

pcaLR2 = linear_model.LinearRegression()
pcaLR2.fit(pca_train2, train_labels)
print "PCA with %d components(avg filled): RMSE %.2f" % (k,np.sqrt(np.mean((pcaLR2.predict(pca_test2)[:,stat_num] - test_labels[:,stat_num]) ** 2)))