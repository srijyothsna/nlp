#!/usr/bin/python

from config import ConfigParserHelper
import logging
import os
from orm.DBQuery import *


#Helper class to create input and output folders for text processing (NER) and to prepare the input
class InputHelper:
    dbqry = DBQuery()

    #create input and output folders for NER and create input txt files to run tet processing (NER)
    def create_input_files(self, filename, txt_input, xmi_output):

        #Check if the input and output dirs exist and create them if they don't exist
        if not os.path.exists(txt_input):
            os.makedirs(txt_input)

        if not os.path.exists(xmi_output):
            os.makedirs(xmi_output)

        #pmids = self.get_pmids_from_file(filename)
        inp_txts = self.create_input(filename)

        for record in inp_txts.keys():
            inp_filename = txt_input+record+".txt"
            inp_file = open(inp_filename,'w')
            inp_file.write(inp_txts[record])
            inp_file.close()

    #Get pmids from file
    def get_pmids_from_file(self,filename):
        #open a file object and read the lines in the file
        with open(filename) as f:
            lines = f.read().splitlines()
        return lines

    #Create a list of text input with PMID and title+abstract+keywords as key-value pairs, pmids obtained from file - filename
    def create_input(self, filename):
        input_list = {}
        lines = self.get_pmids_from_file(filename)

        #Create input text files with title, abstract and keywords for each pmid in the list
        articles = self.dbqry.getArticlesByIds(lines)
        for article in articles:

            if article.keywords:
                text = article.title.encode('utf-8') + "\n" + article.abstract.encode('utf-8') +"\n"+ article.keywords.encode('utf-8')
            else:
                text = article.title.encode('utf-8') + "\n" + article.abstract.encode('utf-8')
            input_list[str(article.PMID)] = text
        return input_list

        # Retrieve the title, abstract and keywords of a given PMID
    def get_pmid_details(self, pmid):
        pmid_details = {}
        articles = self.dbqry.getArticlesByIds([pmid])
        for article in articles:

            pmid_details['title'] = article.title.encode('utf-8')
            pmid_details['abstract'] = article.abstract.encode('utf-8')
            if article.keywords:
                pmid_details['keywords'] = article.keywords.encode('utf-8')
                #text = article.title.encode('utf-8') + "\n" + article.abstract.encode('utf-8') +"\n"+ article.keywords.encode('utf-8')
                #text = article.title + "\n" + article.abstract +"\n"+ article.keywords
            #else:
            #    text = article.title.encode('utf-8') + "\n" + article.abstract.encode('utf-8')
                #text = article.title + "\n" + article.abstract
            #input_list[str(article.PMID)] = text
        return pmid_details