import pandas as pd
import csv
import re
import time

if __name__ == '__main__':
    # You should not modify this part.
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--source',
                       default='dataset/source.csv',
                       help='input source data file name')
    parser.add_argument('--query',
                        default='dataset/query.txt',
                        help='query file name')
    parser.add_argument('--output',
                        default='dataset/output.txt',
                        help='output file name')
    args = parser.parse_args()

    # extract eng word to speed up n-gram
    def extractEngWord(stnc):
        reg = r"\^[\u4e00-\ufaff]+|[a-zA-z]+"
        return re.findall(reg, stnc, re.UNICODE)

    def addWordIndex(table, words, index):
        for wrd in words:
            if wrd in table:
                table[wrd] |= set([index])
            else:
                table[wrd] = set([index])  

    # load source data, build search engine
    srcData = pd.read_csv(args.source, names = ["index", "sentence"])
    srcDataList = srcData["sentence"].values
    ignoreSymbols = "：！…？"
    ngramTables = []
    engTable = {}

    startTime = time.time()
    # find all 2-gram, 3-gram
    for n in range(2, 4):
        gramTable = {}
        for index, line in enumerate(srcDataList):
            # eliminate useless symbol character
            stnc = ''.join(c for c in line if c not in ignoreSymbols)
            index = index + 1            
            # build inverted index by ngram and engwords
            engWords = extractEngWord(stnc)
            if len(engWords) != 0:
                for eng in engWords:
                    stnc = stnc.replace(eng, '')
                addWordIndex(engTable, engWords, index)
            
            # eliminate brackets after handling english words 
            stnc = re.sub(r"[《》「」【】〈〉〞〝（）()]", '', stnc)

            ngram = [stnc[i:i+n] for i in range(len(stnc) - (n-1))]
            addWordIndex(gramTable, ngram, index)

        ngramTables.append(gramTable)
    # save inverted index of 2-gram, 3-gram, English seperatly
    ngramTables.append(engTable)
    print("--- ngram cost {} sec ---".format(time.time() - startTime))


    # compute query result

    lines = [line.rstrip('\n') for line in open(args.query)]
  
    def discardSpace(tokens):
        for i, token in enumerate(tokens):
                if ' ' in token:
                    tokens[i] = token.strip()
    
    def isEng(word):
        if len(re.findall(r"[a-zA-Z]+", word, re.UNICODE)) == 0:
            return False
        else: return True

    # lookup inverted index by word
    def getIndexSet(word):
        result = None

        if isEng(word):
            result = ngramTables[2][word]
        else:
            if len(word) == 2:
                # 2-gram
                result = ngramTables[0][word]
            elif len(word) == 3:
                # 3-gram
                result = ngramTables[1][word]
            else:
                print("No support for over 3-gram chinese")

        return result

    def performOperation(idxSets, oper):
        if oper == "and":
            res = idxSets[0]
            for i in range(1,len(idxSets)):
                res = res & idxSets[i]
            return res
    
        elif oper == "or":
            res = idxSets[0]
            for i in range(1,len(idxSets)):
                res = res | idxSets[i]
            return res

        elif oper == "not":
            res = idxSets[0]
            for i in range(1,len(idxSets)):
                res = res - idxSets[i]
            return res

        else:
            print("Error operation")
            return None

    def outputRes(res, file):
        # result is empty, print '0'
        if len(res) == 0: file.write('0')
        for i, idx in enumerate(res):
            if i != len(res) - 1:
                file.write(str(idx) + ',')
            else:
                file.write(str(idx))

    isFirstLine = True
    with open(args.output, 'w') as outputFile:

        for query in lines:
            # No new line char at the last line
            if not isFirstLine: outputFile.write('\n')
            isFirstLine = False
            
            if 'and' in query:      
                tokens = query.split("and")
                discardSpace(tokens)
                idxSets = []
                for word in tokens:
                    idxSets.append(getIndexSet(word))

                res = sorted(performOperation(idxSets, "and"))
                outputRes(res, outputFile)
                        
            elif 'or' in query:
                tokens = query.split("or")
                discardSpace(tokens)
                idxSets = []
                for word in tokens:
                    idxSets.append(getIndexSet(word))

                res = sorted(performOperation(idxSets, "or"))
                outputRes(res, outputFile)

            elif 'not' in query:
                tokens = query.split("not")
                discardSpace(tokens)
                idxSets = []
                for word in tokens:
                    idxSets.append(getIndexSet(word))

                res = sorted(performOperation(idxSets, "not"))
                outputRes(res, outputFile)

            else:
                print("Query Error")
    
