#!/usr/bin/env python
# -*- encoding=utf-8 -*-

import sys
import math
import random

# Split data set into M parts, of which 
# M-1 parts is train data and the rest 
# 1 part is test data
def split_data(data, M, k, seed):
    test = dict() 
    train = dict() 
    
    random.seed(seed)
    for user, item in data:
        if random.randint(0, M) == k:
            if user not in test:
                test[user] = []
            test[user].append(item)
        else:
            if user not in train:
                train[user] = []
            train[user].append(item)
    return train, test

def recall(train, test, N):
    total = 0
    hit = 0
    for user, items in test.items():
        tu = test[user]
        rec_items = get_recommendation(user, train, N, K)
        for item, pui in rec_items.items():
            if item in tu:
                hit += 1
        total += len(tu)
    return hit / (total * 1.0)

def precision(train, test, N):
    total = 0
    hit = 0
    for user, items in test.items():
        tu = test[user]
        rec_items = get_recommendation(user, train, N, K)
        for item, pui in rec_items.items():
            if item in tu:
                hit += 1
        total += len(rec_items)
    return hit / (total * 1.0)

def coverage(train, test, N):
    recommend_items = set()
    all_items = set()
    for user, items in train.items():
        for item in items:
            all_items.add(item)
        rec_items = get_recommendation(user, train, N, K)
        for item, pui in rec_items.items():
            recommend_items.add(item)
    return len(recommend_items) / (len(all_items) * 1.0)

def popularity(train, test, N):
    item_popularity = dict()
    for user, items in train.items():
        for item in items:
            if item not in item_popularity:
                item_popularity[item] = 0
            item_popularity[item] += 1
    ret = 0
    n = 0
    for user in train:
        rec_items = get_recommendation(user, train, N, K)
        for item in rec_items:
            ret += math.log(1 + item_popularity[item])
        n += len(rec_items)
    ret /= (n * 1.0)
    return ret

def user_similarity(train):
    # build inverse table for item_users
    item_users = dict() 
    for user, items in train.items():
        for item in items:
            if item not in item_users:
                item_users[item] = set()
            item_users[item].add(user)

    # Calculate co-rated items between users
    C = dict()
    N = dict()
    for item, users in item_users.items():
        for user1 in users:
            if user1 not in C:
                C[user1] = dict()
            if user1 not in N:
                N[user1] = 0
            N[user1] += 1
            for user2 in users:
                if user1 == user2:
                    continue
                if user2 not in C[user1]:
                    C[user1][user2] = 0
                C[user1][user2] += 1

    # Calculate finial similarity matrix W
    W = dict()
    for user1 in C:
        W[user1] = dict()
        for user2 in C[user1]:
            W[user1][user2] = C[user1][user2] / math.sqrt(N[user1] * N[user2])
    return W

def recommend_training(train, K):
    rank = dict()
    W = user_similarity(train)
    interacted_items = train[user]
    ranked_users = sorted(W[u].items, key=itemgetter(1), reverse=True)
    length = min(K, len(ranked_users))
    for i in range(0, length):
        v = ranked_users[i][0]
        wuv = ranked_users[i][1]
        for item in train[v]:
            if item in interacted_items:
                continue
            if item not in rank:
                rank[item] = 0.0
            rank[item] += wuv
    return rank

def get_recommendation(user, train, N, K):
    sorted_rank = sorted(recommend_training(train, K).items, key=itemgetter(1), reverse=True)
    length = min(N, len(sorted_rank))
    return sorted_rank[0:length] 

def load_data(filename):
    fd = open(filename, 'r')
    
    data = [] 
    for line in fd:
        try:
            user, item, rate, timestamp = line.strip().split('::')
        except:
            continue
        data.append([user, item])

    fd.close()
    return data

M = 8
seed = 1
N = 5
K = 10
def test(data_file):
    data = load_data(data_file)

    for k in range(0, M):
        train, test = split_data(data, M, k, seed)
        r = recall(train, test, N)
        p = precision(trian, test, N)
        c = coverage(train, test, N)
        pop = popularity(train, test, N)

        print "k = %d: r=%f, p=%f, c=%f, pop=%f" %(k, r, p, c, pop)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <data file>" %(sys.argv[0])
        sys.exit(-1)

    test(sys.argv[1])

