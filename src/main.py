#!/usr/bin/python

from config import ConfigParserHelper
import logging
from Preprocess.Pubmed import *
from orm.load_data import *
from process_text.create_input_text_files import *
from process_text.parse_xmi_output import XMIParser

def main():

    logger.debug("Reading config parameters from file - Start")
    cfg = ConfigParserHelper()
    print cfg.get('main', 'title')

    #Get the config parameters
    filename = cfg.get('main','input_filename')                        #inp file with pmids
    source_type = cfg.get('main','source_type')                        #source type - currently supports only 'Pubmed'
    java_path = cfg.get('ner','java_path')                             #java path to run the MedKATp jar
    medkat_conf = cfg.get('ner','medkat_conf_file')                    #MedKATp config file
    txt_input = cfg.get('ner','txt_inp_filepath')                      #MedKATp input folder with txt files
    xmi_output = cfg.get('ner','xmi_out_filepath')                     #MedKATp output folder with xmi files
    enable = cfg.get('ner','enable')                                   #To enable/disable running ner
    num_clusters = cfg.get('cluster','num_clusters')                   #Number of clusters
    num_words_per_cluster = cfg.get('cluster','num_words_per_cluster') #Number of top words to be displayed per cluster

    logger.info("Reading config parameters - Done")
    print("Reading config parameters - Done")

    logger.debug("Retrieving pmids from file - Start")
    #open a file object and read the lines in the file
    with open(filename) as f:
        lines = f.read().splitlines()
    logger.info("Retrieving pmids from file - Done")
    print("Retrieving pmids from file - Done")

    logger.debug("Retrieving and storing Pubmed data - Start")
    #If the source type is Pubmed, process the list of pmids to get the data from pubmed
    if(source_type=='Pubmed'):
        pubdata = PubmedData()
        pubdata.getPubmedData(lines)
    logger.info("Retrieving and storing Pubmed data - Done")
    print("Retrieving and storing Pubmed data - Done")

    #Call InputHelper to create the input text files for processing
    ihelper = InputHelper()
    xmi_parser = XMIParser()

    #If NER is set to true, prepare input and run the MedKATp pipeline and run the analysis on the terms identified
    #Else run the analysis on the complete text
    if enable.lower() == 'true':
        logger.debug("NER enable set to true")

        logger.debug("Creating input and output directories for NER and preparing input - Start")
        ihelper.create_input_files(filename, txt_input, xmi_output)
        logger.info("Creating input and output directories for NER and preparing input - Done")
        print("Creating input and output directories for NER and preparing input - Done")

        logger.debug("Running text file processing (NER) on input text - Start")
        #start the required environment variables and run a Java process for NER by calling the MedKATp pipeline and block until done
        env = dict(os.environ)
        env["MEDKATp_INP_CONFIG_FILE"] = medkat_conf
        env["CLASSPATH"] = ".:lib/*:MedKATp-20160109.jar:/opt/nlp/MedKATp/resources/"

        import subprocess
        subprocess.call([java_path, '-Xmx1024m', '-Xms256m', 'nlp.pubmed.ner.inputReader.MedKATRunner'],env=env)
        logger.info("Running text file processing (NER) on input text - Done")
        print("Running text file processing (NER) on input text - Done")

        logger.debug("Running analysis an clustering on NER output - Start")
        xmi_parser.parse_xmi_files(xmi_output, num_clusters, num_words_per_cluster)
        logger.info("Running analysis an clustering on NER output - Done")
        #print("Running analysis an clustering on NER output - Done")

    else:
        logger.debug("NER enable set to false")

        pmids_array = []
        text_array = []

        logger.debug("Preparing input for analysis and clustering- Start")
        input_list = ihelper.create_input(filename)
        for key in input_list.keys():
            pmids_array.append(key)
            text_array.append(input_list[key])
        logger.info("Preparing input for analysis and clustering- Done")
        print("Preparing input for analysis and clustering- Done")

        logger.debug("Running analysis and clustering on text - Start")
        xmi_parser.analyze_and_cluster(pmids_array, text_array, num_clusters, num_words_per_cluster)
        logger.info("Running analysis and clustering on text - Done")

if __name__ == '__main__':
    logger = logging.getLogger("nlp_logger")
    if cfg.get('main', 'DEBUG').lower() == 'true':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
 
    # create the logging file handler
    fh = logging.FileHandler(cfg.get('main', "log_file"))
 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
 
    # add handler to logger object
    logger.addHandler(fh)

    main()
