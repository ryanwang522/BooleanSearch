# BooleanSearch
This is for DSAI homework2.

# Idea & algorithm
I calculate the 2-gram, 3-gram and english words in the source file, and therefore use them to build inverted index table with their index number.

My original idea is to use hash function, but I found out that Python already has data structure of Dictionary. So I just saved words and their index of occurence to dictionarys.

At last, after phrasing the query we can directly find query words' index by checking inverted index table directly and print the results to the output file.

# Some issues
I've tried to parallel the function of reading src data and build inverted index table wtih multiple process, but the performance turned out to be further bad.

After some information searching, it may due to the extra cost of creating processes and shared variable ascess. 

# TODO
Refector srcFile-processing code so that it can be parallel properly to improve performance.
