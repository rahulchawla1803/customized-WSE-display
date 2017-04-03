import json
from general import cleaning
import operator
import enchant
from stemming.porter2 import stem
from PyDictionary import PyDictionary
dictionary_synonym = PyDictionary()
dictionary_spelling = enchant.Dict("en_UK")

def search(search_query):

    query_synonym = []
    query_suggestion = []
    word_synonyms = []
    word_suggestions=[]

    synonym_docs = []
    for line in open('synonym.json', 'r'):
        synonym_docs.append(json.loads(line))



    print(search_query)
    clean_query = cleaning(search_query)

    for word in clean_query:
        for doc in synonym_docs:
            if word in doc['words']:
                query_synonym = query_synonym + doc['words']

    print(query_synonym)

    for word in clean_query:
        if dictionary_spelling.check(word):
            word_synonyms = dictionary_synonym.synonym(word)
            query_synonym = query_synonym + word_synonyms

    for word in clean_query:
        word_suggestions = dictionary_spelling.suggest(word)
        query_suggestion = query_suggestion+word_suggestions


    clean_query_root = []
    for word in clean_query:
        root_word = stem(word)
        clean_query_root.append(root_word)

    query_synonym_root = []
    for word in query_synonym:
        root_word = stem(word)
        query_synonym_root.append(root_word)

    query_suggestion_root = []
    for word in query_suggestion:
        root_word = stem(word)
        query_suggestion_root.append(root_word)



    title_rank = {}
    docs = []
    for line in open('indexed_repo_title.json', 'r'):
        docs.append(json.loads(line))

    for doc in docs:
        title_match_value = 0
        for index, title_word_root in enumerate(doc['title_root']):

            for query_word_root in clean_query_root:
                if title_word_root == query_word_root:
                    title_match_value = title_match_value + doc['idf_word_list'][index]

            for query_word_synonym_root in query_synonym:
                if title_word_root == query_word_synonym_root:
                    title_match_value = title_match_value + 0.75*doc['idf_word_list'][index]

            for query_word_suggestion_root in query_suggestion:
                if title_word_root == query_word_suggestion_root:
                    title_match_value = title_match_value + 0.5*doc['idf_word_list'][index]

        title_rank[doc['url']] = title_match_value


    title_sorted_rank_dict={}

    for key, value in sorted(title_rank.items(), key=operator.itemgetter(1), reverse=True):
        if value > 0:
            title_sorted_rank_dict[key] = value


    title_sorted_rank_list = []
    for key in title_sorted_rank_dict:
        title_sorted_rank_list.append(key)

    document_filtered= []
    for i in docs:
        if i['url'] in title_sorted_rank_list:
            document_filtered.append(i)


    link_title_sorted_dict = {}

    doc_dict = {}
    for doc in document_filtered:
        doc_dict[doc['url']] = doc['title']

    for link in title_sorted_rank_list:
        for (key, value) in doc_dict.items():
            if link == key:
                link_title_sorted_dict[key] = value
    print(link_title_sorted_dict)
    return link_title_sorted_dict


search("creation")