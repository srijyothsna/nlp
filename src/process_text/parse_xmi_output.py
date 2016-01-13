from __future__ import print_function
import xml.etree.ElementTree as ET
import glob
import numpy as np
import pandas as pd
import nltk
#from bs4 import BeautifulSoup
import re
import os
import codecs
from sklearn import feature_extraction
#import mpld3
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from process_text.create_input_text_files import *

#Class for parsing xmi output from NER; analysis; and clustering
class XMIParser:

    namespaces = {'conceptMapper': 'http:///org/ohnlp/medkat/taes/conceptMapper.ecore', 'tt':'http:///uima/tt.ecore'}

    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = SnowballStemmer("english")
    #ne_terms = []

    #Parse XMI output files from MedKaTp pipeline
    def parse_xmi_files(self, folder, num_clusters, num_words):
        logger.debug("In parse_xmi_files function of process_text.parse_mi_output.XMIParser")
        pmids_array = []
        diseases_array = []

        print("Parsing XMI files - Start")
        files = glob.glob(folder + "*.xmi")
        for f in files:
            tree = ET.parse(f)
            root = tree.getroot()

            pmid = self.get_filename(f)
            pmids_array.append(pmid)
            diseases_str = ""

            for child in root.findall('conceptMapper:DictTerm', self.namespaces):
                disease = child.attrib['matchedText']

                '''#Writing NEs to db, not used currently - for extensibiliy
                ne_term = {}
                ne_term['TxtTerm'] = disease
                ne_term['startPos'] = child.attrib['begin']
                ne_term['endPos'] = child.attrib['end']
                ne_term['articleID'] = pmid
                ne_term['LexTermID'] = child.attrib['AttributeValue']
                ne_term['DictCanon'] = child.attrib['DictCanon']
                self.ne_terms.append(ne_term)'''

                diseases_str += disease + ', '
            diseases_str = diseases_str.translate(None, '.,><(){}')
            diseases_array.append(diseases_str)

        logger.info("Parsing XMI files - Done")
        print("Parsing XMI files - Done")

        '''logger.debug("Writing NEs to DB XMI files - Start")
        #Writing NEs to db, not used currently - for extensibiliy
        dbq = DBQuery()
        dbq.insertNamedEntity(self.ne_terms)
        logger.info("Writing NEs to DB XMI files - Done")
        print("Writing NEs to DB XMI files - Done")'''

        self.analyze_and_cluster(pmids_array,diseases_array, num_clusters, num_words)

    #Run analysis and clustering on the text
    def analyze_and_cluster(self, pmids_array, diseases_array, num_clusters, num_words):
        logger.debug("Analysis and clustering - Start")
        totalvocab_stemmed = []
        totalvocab_tokenized = []

        for i in diseases_array:
            i = str(i.decode('utf-8').encode('ascii', 'ignore').decode('ascii'))
            i = i.translate(None,'.,><(\/\':;)%{}[]=')

            allwords_stemmed = self.tokenize_and_stem(i)
            totalvocab_stemmed.extend(allwords_stemmed)

            allwords_tokenized = self.tokenize_only(i)
            totalvocab_tokenized.extend(allwords_tokenized)

        vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index = totalvocab_stemmed)

        ranks = []

        for i in range(0,len(pmids_array)):
            ranks.append(i)

        tfidf_vectorizer = TfidfVectorizer(tokenizer=self.tokenize_and_stem, stop_words='english')

        tfidf_matrix = tfidf_vectorizer.fit_transform(diseases_array)
        terms = tfidf_vectorizer.get_feature_names()
        dist = 1 - cosine_similarity(tfidf_matrix)

        num_clusters = int(num_clusters)
        num_words = int(num_words)
        km = KMeans(n_clusters=num_clusters)
        km.fit(tfidf_matrix)
        clusters = km.labels_.tolist()

        diseases_frame_features = { 'pmids': pmids_array, 'rank': ranks, 'diseases': diseases_array, 'cluster': clusters }
        frame = pd.DataFrame(diseases_frame_features, index = [clusters] , columns = ['rank', 'pmids', 'cluster'])

        grouped = frame['rank'].groupby(frame['cluster'])

        import uuid
        job_name = str(uuid.uuid1())
        json_string = {}
        json_string["name"] = job_name
        json_string["children"] = []

        print("Top terms per cluster:")
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]

        for i in range(num_clusters):
            tmp_obj = {}

            print("Cluster %d:" % i)
            print("----------")
            print("Terms:")

            top_words_in_cluster = '';

            #print()

            for ind in order_centroids[i, :num_words]:
                #Checking for the type of word - if float/ int then cast them to str in order to append to the string
                word = vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0]

                from math import isnan
                if not (((isinstance(word, float) and isnan(word))) or ((isinstance(word,int) and isnan(word)))):
                    #word = str(float(word))
                    #print(int(word))
                    #word = str(int(word))

                    print(' %s' % word, end=',')
                    top_words_in_cluster += word + ', '

                #print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0], end=',')
                #top_words_in_cluster += vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0] + ','


            print()
            tmp_obj["name"] = 'Cluster ' + str(i+1)
            tmp_obj["top_words"] = top_words_in_cluster[:-2]

            print("PMIDs:")
            pmids_in_cluster = [];
            pmid_count = 0
            for pmid in frame.ix[i]['pmids'].values.tolist():
                print(' %s,' % pmid, end='')
                pmid_helper = InputHelper()
                pmid_details = pmid_helper.get_pmid_details(pmid)
                keywords = 'NA'
                if keywords in pmid_details:
                    keywords = pmid_details['keywords']
                pmids_in_cluster.append({"name": pmid, "size":200, "title": pmid_details['title'], "abstract": pmid_details['abstract'], "keywords": keywords})
                pmid_count += 1

            tmp_obj["children"] = pmids_in_cluster
            tmp_obj["pmid_count"] = pmid_count
            json_string["children"].append(tmp_obj)

            print()
            print()

            logger.info("Analysis and clustering - Done")

        logger.debug("writing clusters to json - Start")

        import json
        try:  #write the json file to /var/www if proper persmissions are set
            f = open('/var/www/html/' + job_name + '.json', 'w')
            f.write(json.dumps(json_string))
            f.close()
        except: #else write it to the json folder in the current directory
            print('There seems to be permission issues for writing into /var/www/html/.')
            os.makedirs('json_files')
            f = open('json_files/' + job_name + '.json', 'w')
            f.write(json.dumps(json_string))
            f.close()
            print('Please move json_file/' + job_name + '.json to /var/www/html/.')
        print('Visit http://localhost/cluster_visualization.html?' + job_name + ' for the cluster visualization')
        logger.info("writing clusters to json - Done")


    # Get the file name from the string
    def get_filename(self, f):
        import ntpath
        return ntpath.basename(f).split(".")[0]

    def tokenize_and_stem(self, text):
        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        stems = [self.stemmer.stem(t) for t in tokens]
        return stems

    def tokenize_only(self, text):
        # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
        tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
        return tokens

xmi_parser = XMIParser()
#xmi_parser.parse_xmi_files('./output/')
