import numpy as np
import pandas as pd
import math
import json

data = pd.read_csv("C:\\Users\\Maxim\\Downloads\\data.csv", index_col=0)
context_day = pd.read_csv("C:\\Users\\Maxim\\Downloads\\context_day.csv", index_col=0)
context_place = pd.read_csv("C:\\Users\\Maxim\\Downloads\\context_place.csv", index_col=0)

myUserId = 18
markNotSet = -1
k = 4
res = {"user": myUserId, "1": {}, "2": {}}

def avgUserMark(userId):
    marks = data.loc["User " + str(userId)]
    counter = 0
    sum = 0
    for key, value in marks.items():
        if (value != markNotSet):
            counter += 1
            sum += value
    return sum / counter


def predictMark(userId, filmId):
    ru = avgUserMark(userId)
    sumUpper = 0
    sumLower = 0
    maxSims = findMaxSimsWithMark(sims, filmId, k)
    for key, value in maxSims.items():
        rvi = data.loc["User " + str(key)][filmId]
        rv = avgUserMark(key)
        sumUpper += value * (rvi - rv)
        sumLower += abs(value)
    return ru + sumUpper / sumLower


def sim(userU, userV):
    sumUV = 0
    sumU2 = 0
    sumV2 = 0
    userU_marks = data.loc["User " + str(userU)]
    userV_marks = data.loc["User " + str(userV)]
    for i in range(1, data.shape[1] + 1):
        markUI = userU_marks[" Movie " + str(i)]
        markVI = userV_marks[" Movie " + str(i)]
        if (markUI != markNotSet and markVI != markNotSet):
            sumUV += markUI * markVI
            sumU2 += markUI ** 2
            sumV2 += markVI ** 2
    simuv = sumUV / (math.sqrt(sumU2) * math.sqrt(sumV2))
    return simuv

def findSims(userId):
    sims = {}
    for i in range(1, data.shape[0] + 1):
        if (i == myUserId):
            continue
        sims[i] = sim(userId, i)
    return sims


def findMaxSimsWithMark(sims, filmId, amount):
    sortedSims = pd.Series(sims).sort_values(0, False)
    newSims = {}
    for key in sortedSims.keys():
        if(newSims.__len__() == amount):
            break
        if(data.loc['User '+str(key)][filmId] != markNotSet):
            newSims[key] = sortedSims.get(key)
    return newSims


def recommendFilm():
    avgFilmMarks = []
    for i in range(1, data.shape[1] + 1):
        avgFilmMarks.append(data[" Movie " + str(i)].where(data[" Movie " + str(i)] != -1).mean())
    homePart = []
    for i in range(1, context_day.shape[1] + 1):
        all = context_place[" Movie " + str(i)]
        watched = 0
        at_home = 0
        for key, value in all.items():
            if (value != -1):
                watched += 1
                if (value == ' h'):
                    at_home += 1
        homePart.append(at_home / watched)
    weekendPart = []
    for i in range(1, context_day.shape[1] + 1):
        all = context_day[" Movie " + str(i)]
        watched = 0
        at_weekends = 0
        for key, value in all.items():
            if (value != -1):
                watched += 1
                if (value == ' Sun' or value == ' Sat'):
                    at_weekends += 1
        weekendPart.append(at_weekends / watched)

    resList = []
    for i in range(data.shape[1]):
        resList.append(avgFilmMarks[i] * weekendPart[i] * homePart[i])
    return resList.index(max(resList)) + 1


sims = findSims(myUserId)
my_user_marks = data.loc["User " + str(myUserId)]

for movie, mark in my_user_marks.items():
    if mark == markNotSet:
        res["1"][movie] = round(predictMark(myUserId, movie), 1)

res["2"] = " Movie " + str(recommendFilm())

with open("res.json", "w", encoding="utf-8") as file:
    json.dump(res, file)
