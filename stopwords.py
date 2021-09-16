#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import hashlib
import os
import shutil
import sys
from itertools import chain

import requests
from pypinyin import Style, pinyin


class StopWordsRepo(object):
    def __init__(self, name, filename, url):
        self.name = name
        self.filename = os.getcwd() + '/stopwords/' + filename
        self.url = url

class Updater(object):
    def __init__(self, filename, url):
        self.filename = filename
        self.basename = os.path.basename(self.filename)
        self.filename_download = filename + '.download'
        self.filename_backup = filename + '.backup'
        self.url = url

    def __CalcFileSha256(self, filename):
        with open(filename, "rb") as f:
            sha256obj = hashlib.sha256()
            sha256obj.update(f.read())
            hash_value = sha256obj.hexdigest()
            return hash_value

    def Download(self):
        try:
            if not os.path.exists(os.getcwd() + '/stopwords'):
                os.mkdir(os.getcwd() + '/stopwords')
            isNeedUpdate = False
            if os.path.exists(self.filename_download):
                os.remove(self.filename_download)
            
            r = requests.get(self.url) 
            with open(self.filename_download,'wb') as f:
                f.write(r.content)

            if os.path.exists(self.filename_backup):
                sha256Old = self.__CalcFileSha256(self.filename_backup)
                sha256New = self.__CalcFileSha256(self.filename_download)
                if not sha256New == sha256Old:
                    os.remove(self.filename_backup)
                    os.rename(self.filename_download, self.filename_backup)
                    isNeedUpdate = True
            else:
                os.rename(self.filename_download, self.filename_backup)
                isNeedUpdate = True

            if isNeedUpdate:
                if os.path.exists(self.filename):
                    os.remove(self.filename)
                shutil.copyfile(self.filename_backup, self.filename)

            return isNeedUpdate
        except Exception as e:
            print(f'%s download failed: %s' % (self.basename, e))
            return False

def merge(stopWordsRepoList):
    def check_character(check_str):
        chinese = False # 中文优先级最高
        letter = False # 字母优先级中
        character = False # 字符优先级低
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                chinese = True
                break
            elif 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9':
                letter = True
            else:
                character = True
        return chinese, letter, character
    def to_pinyin(s):
        '''转拼音
        :param s: 字符串或列表
        :type s: str or list
        :return: 拼音字符串
        >>> to_pinyin('你好吗')
        'ni3hao3ma'
        >>> to_pinyin(['你好', '吗'])
        'ni3hao3ma'
        '''
        return ''.join(chain.from_iterable(pinyin(s, style=Style.TONE3)))
    try:
        stopWordsSet_Chinese = set() # 中文
        stopWordsSet_letter = set() # 字母
        stopWordsSet_character = set() # 字符
        for stopWordsRepo in stopWordsRepoList:
            filename = stopWordsRepo.filename
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    stopWord = line.strip('\n').strip()
                    if len(stopWord) == 0:
                        continue
                    chinese, letter, character = check_character(stopWord)
                    if chinese:
                        stopWordsSet_Chinese.add(stopWord)
                    elif letter:
                        stopWordsSet_letter.add(stopWord)
                    else:
                        stopWordsSet_character.add(stopWord)

        stopWordsList_Chinese = sorted(list(stopWordsSet_Chinese), key=to_pinyin) # 按拼音排序
        print(stopWordsList_Chinese)
        stopWordsList_letter = sorted(list(stopWordsSet_letter), key=lambda s: s.lower())
        print(stopWordsList_letter)
        stopWordsList_character = sorted(list(stopWordsSet_character))
        print(stopWordsList_character)
        filename = './stopwords/stopwords.txt'
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, "w", encoding="utf-8") as f:
            for stopWord in stopWordsList_character: # 字符
                f.write(stopWord + '\n')
            for stopWord in stopWordsList_letter: # 字母
                f.write(stopWord + '\n')
            for stopWord in stopWordsList_Chinese: # 汉字
                f.write(stopWord + '\n')
        return True
    except Exception as e:
        print(f'merge failed: %s' % e)
        return False

def run():
    stopWordsRepoList = []
    stopWordsRepoList.append(StopWordsRepo(f'中文停用词表', 'goto456_cn_stopwords.txt', 'https://raw.githubusercontent.com/goto456/stopwords/master/cn_stopwords.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'哈工大停用词表', 'goto456_hit_stopwords.txt', 'https://raw.githubusercontent.com/goto456/stopwords/master/hit_stopwords.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'百度停用词表', 'goto456_baidu_stopwords.txt', 'https://raw.githubusercontent.com/goto456/stopwords/master/baidu_stopwords.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'四川大学机器智能实验室停用词库', 'goto456_scu_stopwords.txt', 'https://raw.githubusercontent.com/goto456/stopwords/master/scu_stopwords.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'中文停用词表', 'elephantnose_stop_words', 'https://raw.githubusercontent.com/elephantnose/characters/master/stop_words'))
    stopWordsRepoList.append(StopWordsRepo(f'中文停用词表', 'ImportMe_chinese.txt', 'https://raw.githubusercontent.com/ImportMe/stop_words/master/chinese.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'英文停用词表', 'ImportMe_english.txt', 'https://raw.githubusercontent.com/ImportMe/stop_words/master/english.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'停用词表', 'nishiwen1214_stop_words.txt', 'https://raw.githubusercontent.com/nishiwen1214/NLP-Dictionary/master/stop_words.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'停用词表1205', 'nishiwen1214_停用词表1205.txt', 'https://raw.githubusercontent.com/nishiwen1214/NLP-Dictionary/master/停用词表1205.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'停用词表1893', 'nishiwen1214_停用词表1893.txt', 'https://raw.githubusercontent.com/nishiwen1214/NLP-Dictionary/master/停用词表1893.txt'))
    stopWordsRepoList.append(StopWordsRepo(f'停用词表2462', 'nishiwen1214_停用词表2462.txt', 'https://raw.githubusercontent.com/nishiwen1214/NLP-Dictionary/master/停用词表2462.txt'))

    isNeedUpdate = 0
    for stopWordsRepo in stopWordsRepoList:
        updater = Updater(stopWordsRepo.filename, stopWordsRepo.url)
        if updater.Download():
            isNeedUpdate += 1
    
    if isNeedUpdate > 0:
        merge(stopWordsRepoList)


if __name__ == '__main__':
    run()
