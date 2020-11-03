import numpy as np
import pandas as pd
import math
import json

data = pd.read_csv("C:\\Users\\Maxim\\Downloads\\data.csv")
context_day = pd.read_csv("C:\\Users\\Maxim\\Downloads\\context_day.csv")
context_place = pd.read_csv("C:\\Users\\Maxim\\Downloads\\context_place.csv")

myUserId = 17
markNotSet = -1
movieStr = " Movie "
k = 4
homeMark = 'h'
weekendMark = ["Sat", 'Sun']
res = {"user": myUserId + 1, "1": {}, "2": {}}


def avgUserMark(userId):
    marks = data.loc[userId]
    counter = 0
    sum = 0
    for key, value in marks.items():
        if (value != markNotSet):
            try:
                sum += value
                counter += 1
            except:
                continue
    return sum / counter


def predictMark(userId, filmId):
    ru = avgUserMark(userId)
    sumUpper = 0
    sumLower = 0
    maxSims = findMaxSimsWithMark(sims, filmId, k)
    for key, value in maxSims.items():
        rvi = data.loc[key][filmId]
        rv = avgUserMark(key)
        sumUpper += value * (rvi - rv)
        sumLower += abs(value)
    return ru + sumUpper / sumLower


def sim(userU, userV):
    sumUV = 0
    sumU2 = 0
    sumV2 = 0
    userU_marks = data.loc[userU]
    userV_marks = data.loc[userV]
    for i in range(1, data.shape[1]):
        markUI = userU_marks[movieStr + str(i)]
        markVI = userV_marks[movieStr + str(i)]
        if markUI != markNotSet and markVI != markNotSet:
            sumUV += markUI * markVI
            sumU2 += markUI ** 2
            sumV2 += markVI ** 2
    simuv = sumUV / (math.sqrt(sumU2) * math.sqrt(sumV2))
    return simuv


def findSims(userId):
    sims = {}
    for i in range(0, data.shape[0]):
        if (i == myUserId):
            continue
        sims[i] = sim(userId, i)
    return sims


def findMaxSimsWithMark(sims, filmId, amount):
    sortedSims = pd.Series(sims).sort_values(0, False)
    newSims = {}
    for key in sortedSims.keys():
        if (newSims.__len__() == amount):
            break
        if (data.loc[key][filmId] != markNotSet):
            newSims[key] = sortedSims.get(key)
    return newSims


def recommendFilm():
    avgFilmMarks = []
    for i in range(1, data.shape[1]):
        avgFilmMarks.append(data[movieStr + str(i)].where(data[movieStr + str(i)] != markNotSet).mean())

    homePart = []
    for i in range(1, context_place.shape[1]):
        all = context_place[movieStr + str(i)]
        watched = 0
        at_home = 0
        for key, value in all.items():
            if (value.strip() != str(markNotSet)):
                watched += 1
                if (value.strip() == homeMark):
                    at_home += 1
        homePart.append(at_home / watched)

    weekendPart = []
    for i in range(1, context_day.shape[1]):
        all = context_day[movieStr + str(i)]
        watched = 0
        at_weekends = 0
        for key, value in all.items():
            if value.strip() != str(markNotSet):
                watched += 1
                if weekendMark.__contains__(value.strip()):
                    at_weekends += 1
        weekendPart.append(at_weekends / watched)

    resList = []
    for i in range(data.shape[1] - 1):
        resList.append(avgFilmMarks[i] * weekendPart[i] * homePart[i])

    return resList.index(max(resList)) + 1


sims = findSims(myUserId)
my_user_marks = data.loc[myUserId]

for movie, mark in my_user_marks.items():
    if mark == markNotSet:
        res["1"][movie] = round(predictMark(myUserId, movie), 1)

res["2"] = movieStr + str(recommendFilm())
with open("res.json", "w", encoding="utf-8") as file:
    json.dump(res, file)
