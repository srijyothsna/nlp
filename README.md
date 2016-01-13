# Cluserting PubMed abstracts based on diseases using NLP

#Introduction

The application is built to retrieve the Pubmed abstracts for a list of PMIDs and cluster them into groups of different diseases.

The pipeline retrieves the abstracts, keywords (along with other information like title, authors, date, etc.) for a list of PMIDs and saves them to a local database; runs the Medical Knowledge Analysis Tool (MedKATp) framework, which is based on Apache UIMA for Named Entity Recognition (NER); runs a k-means clustering algorithm on the identified NEs (disease terms) in text and keywords, for which it uses 'cosine similarity' as the metric; and generates and displays the clusters in text format, which can also be viewed as a 'zoomable circle packing' visualization in a web browser.

##How To Run

An automated install script is provided in the repo. Run the install script as a super user. This will install all the dependencies and set up the environment. Then, launch the application by running main.py in src folder. 


#Design

This application is  built as a pipeline with a combination of Python and Java. The Entrez module from Biopython is used for retrieving the Pubmed abstracts. The text is processed with a dictionary-based approach for NER. The dictionary/ lexicon used for NER is build from the Human Disease Ontology (HDO). The MedKATp framework uses an xml-based dictionary. So, the terms from the HDO are processed and an xml dictionary is built. The dictionary has been further fine-tuned iteratively based on the results.

##Sample Output

###Output on the Console
![Output on the console](https://www.dropbox.com/s/oasubezmyzlh1xw/Text-output.png?dl=0&raw=1)

###Cluster Visualization

![Visualization screen](https://www.dropbox.com/s/efijnz9kettkt8o/Browser-output_1.png?dl=0&raw=1)

![Visualization continued](https://www.dropbox.com/s/mri0yhj6b3txnpq/Browser-output_2.png?dl=0&raw=1)

![List of PMIDs for a cluster](https://www.dropbox.com/s/u2g17ske8kh6epk/Browser-output_3.png?dl=0&raw=1)

![PMID abstract](https://www.dropbox.com/s/e1dw5hpklkxs2hc/Browser-output_4.png?dl=0&raw=1)

##Process Flow

###Python
* Create the xml dictionary files for the pipeline, if needed.

* Launch the application.
  * Run the application by calling a launch python script. Input parameter is a file containing a list of PMIDs, one per line.
* Create db schema, if it does not exist
  * Check if the articles to be processed are present in the db
  * Load the dictionary/ lexicon in the database. This is for extensibility and not used currently.

* Retrieve the Pubmed abstracts to be processed
* Prepare input for text processing
  * Create the input and output folders for the pipeline
  * Create the input files in the input folder for each PMID

###Java
* Run preprocessing and text processing steps - using MedKATp/ UIMA
  * Set environment variables: JAVA_HOME, UIMA_HOME, CLASSPATH, PATH etc.
  * Run the NER pipeline on input files.
The steps in the NER pipeline include sentence detection, tokenization, stop word removal, stemming, POS tagging, lexicon-based named entity recognition and annotation. MedKATp uses OpenNLP models for sentence detection, tokenizing, chunking, parsing, POS tagging. It implements the MedTerm stemmer, apecifically for medical words.

###Python
* Retrieve and process the NE data from text processing
  * Insert NEs etc to DB
  * Run clustering algorithm. The k-means clustering algorithm is used with the metric as 'cosine similarity'. The nltk snowball stemmer implementation is used at this stage. The machine-learning scikit package is used for creating the tf-idf vector, pairwise distance (or similarity) calculation using cosine similarity and K-means clustering the words in the text, with configurable parameters to display number of clusters and number of words per cluster.

* Display final o/p clusters
  * Show UI to display final o/p

##Assumptions

* The application has been developed and tested on Ubuntu 14.04.
* The Java code in the application is built with jdk1.8.0_65. So, the java runtime environment (to run java command) has to be the same version.
* Input is a list of PMIDs, one PMID per line in a txt file.
* The required dependencies, libraries, environment variables and permissions are all set properly.
  * The opt-nlp.zip is unzipped and the contents are placed in to /opt/nlp
  * The MedKATp_20160109.jar is present in the root folder of the project along with the config file.
  * User has write perrmissions to /var/www/html and the output is written to this folder.
  * apache2 is running in orde to view the output visualization in the web browser.

The following have not yet been implemented and are planned to be done later:
* Boundary or failure conditions for the following have not been implemented:
  * input file like no file, empty file, PMIDs in one single line (with any separator)
  * MedKATp jar file, configuration file and depencencies like libraries, analysis engine descriptor files, dictionary file in xml format, OpenNLP models - no file/ empty file.
  * incorrect configuration parameters - like file paths, type of input - int/str/boolean etc.
* Use the named entities details stored in the database to highlight in the text in final ouput visualization.
* Write sentence annotations containing the named entities to the database to use for highlighting in the text in the output visualization.

##Package / Directory Structure

nlp (project's root folder)
* file: main.py - main class to initialize, set up the environment, read input and run each step in the process till the output is displayed
  * main()
    Input parameters: None
    Returns: None

* file: PMIDs_mixed.txt - Input file containing the PMIDs, one per line.
* file: nlp_db.sqlite - The database. Stores the article, lexicon, named entity and linkout data.
* file: config.ini - Configuration parameters and file paths required for every step in the process.
* file: config.py - Configuration helper to load config parameters from the file.
  * Class: ConfigParserHelper: Contains functions
    * __init() - Initialize the config parser and read the config.ini file
    Input parameters: None
    Returns: None
    * get(section, key) - Get the value for the key in the specified section of the config file
      Input parameters: section, key
      Returns: str - Value of the key in the given section

* file: MedKATp-20160109.jar - Executable Java archive (jar) file that processes text input and identifies the disease terms in the text from a predefined dictionary.
* MedKATpRunnerConfig.prop - Configuration file for the NER pipeline, MedKATp.
* ner-processing.log - Log file

* subdir/package: Preprocess
  * file: Pubmed.py - Retrieve the abstract, title, keywords, authors, date etc. for the input PMIDs
    * Class: PubmedData:  Contains functions
      * getPubmedData(PMIDs) - retrieve data from Pubmed for a list of Pmids using the BioPython's eutils and store the data in the db.
        Input parameter: list of PMIDs.
        Returns: None

* subdir: lib - Java libraries required to run the MedKATp (text processing and NER) pipeline

* subdir/package: process_text
  * create_input_text_files.py - create input and output directories and input files for the NER pipeline or complete text input for analysis and clusteting, if NER step is turned off.
  * parse_xmi_output.py - Parse the xmi output from the NER step, run analysis and clustering on the text and prepare output for display.

* subdir/package: orm
  * file: db.py - Classes that define and create the database schema. (Refer DATABASE SCHEMA)
  * file: DBQuery.py -  DB connections, insert/ delete/select/update queries to db
    * Class: DBQuery: contains functions
      * checkArticleInDB(PMID) - Check if the pubmed article already exists in the db, else parse and create an entry
        Input parameter  - PMID
        Returns: int (number of rows matching the PMID in the db, ideally 1 or 0)
      * insertArticles(articles) - Insert articles into db
        Input parameter - List of articles
        Returns: None
      * getArticles() - Retrieve the Pubmed articles from the db
        Input parameter - None
        Returns: A list of 'Article' objects, corresponding to the database table 'Article'
      * getArticlesByIds(article_ids) - Retrieve the Pubmed articles for a list of PMIDs from the db
        Input parameter: List of PMIDs
        Returns: A list of 'Article' objects, corresponding to the database table 'Article', for the list of PMIDs given
      * insertNamedEntity(ne_terms) - Insert the NE terms in the DB. Implemented for externsibility, the terms are not used currently.
        Input parameter: A list of 'NamedEntity' objects, corresponding to the database table 'NamedEntity'
        Returns: None
      * getLexicon() - Get Lexicon terms from db.  Implemented for externsibility, not used currently.
        Input parameter: None
        Returns: List of 'Lexicon' objects, corresponding to the database table 'Lexicon'

  * file: load_data.py - Load the data in Lexicon tables from HDO files. This is for extensibility and currently is not being used.
    * set_Lex_Type() - Insert data into the LexType table. Currently, has only one type 'disease'
      Input parameter - None
      Returns: None
    * load_HumanDO_Terms() - Insert disease terms from HDO to the Lexicon table. Reads input from file 'data/terms.csv'
      Input parameter - None
      Returns: None
    * load_HumanDO_Xrefs() - Insert XRefs for disease terms from HDO into the Linkout table. Reads input from file 'data/linkouts.csv'
      Input parameter - None
      Returns: None

  * file: UIMA_dict_creator.py - Utility script that creates the lexicon/ dictionary of disease terms from the HDO file in xml format as required by the MedKATp pipeline for NER.
NOTE: This has been run and the XML dictionary file is provided. Therefore, this script is not invoked anywhere in the pipeline and has to be run separately, if required, prior to running the application. The output xml file created has to be copied to the /opt/nlp/MedKATp/resources/dict to be used by the MedKATp pipeline.
     * HumanDO_XML_Dict() - Add disease terms from HDO to the XML dictionary file used in MedKATp (UIMA). Reads input from data/terms.csv and writes output to data/initialDict_base.xml
       Input parameters: None
       Returns: None

* subdir: data - Input files based on data derived from HDO files used to build the XML-based disease dictionary and the resultant XML file. This file has been generated and placed at the right filepath and does not need to be regenerated. These files are also used to load the data in the Lexicon tables. This is for extensibility and currently is not being used.

* subdir: input - Created during processing and populated with text files as input to the MedKATp pipeline

* subdir: output - Created during processing and populated with the xmi files output by the MedKATp pipeline


##Database Schema

The database is in Sqlite3 and the ORM used is Sqlalchemy. In order to run any database commands through the console, the sqlite3 package needs to be installed.


![Articles](https://www.dropbox.com/s/6sfpjmfrmtxru87/Article.png?dl=0&raw=1)

![Lexicon - Dictionary](https://www.dropbox.com/s/8gj3rhjdmllmdl9/Lexicon.png?dl=0&raw=1)

![Lex type](https://www.dropbox.com/s/b2l0znmqisqp9we/LexType.png?dl=0&raw=1)

![Named Entity](https://www.dropbox.com/s/tbir6yau2b2hqhl/NamedEntity.png?dl=0&raw=1)

![ArticleSentence](https://www.dropbox.com/s/m4cpserwnfifcko/ArticleSentence.png?dl=0&raw=1)

![Linkout](https://www.dropbox.com/s/03y3mzpr779rp63/Linkout.png?dl=0&raw=1)

##Dependencies

###Python packages:
* python-sqlalchemy
* python-beautifulsoup
* python-biopython
* python-nltk
* python-pip
* python-sklearn
* python-matplotlib
* pandas

###Other packages:
* OpenNLP models
* apache2

###Environment setup:
* Unzip the contents of the opt-nlp.zip into /opt/nlp and give required permissions to read and execute the files. (Refer to MedKATp documentation for description and how to change these files)
* Change permissions of the /var/www directory (and it's subdirectories) with all, read, write and execute permission for the current user. The final output is written to /var/ww/html and can be visualized on a Web browser. This can be done by executing the command 'sudo chown yourusername.users /var/www', where 'yourusername' is the current user running the application.

##Components

###Human Disease Ontology
(http://disease-ontology.org/)
The Disease Ontology is a community driven, open source ontology that is designed to link disparate datasets through disease concepts. It has been developed as a standardized ontology for human disease with the purpose of providing the biomedical community with consistent, reusable and sustainable descriptions of human disease terms, phenotype characteristics and related medical vocabulary disease concepts through collaborative efforts of researchers at Northwestern University, Center for Genetic Medicine and the University of Maryland School of Medicine, Institute for Genome Sciences.

The Disease Ontology semantically integrates disease and medical vocabularies through extensive cross mapping of DO terms to MeSH, ICD, NCI’s thesaurus, SNOMED and OMIM.


###BioPython
(http://biopython.org/wiki/Main_Page)
Biopython is a set of freely available tools for biological computation written in Python by an international team of developers. It is a distributed collaborative effort to develop Python libraries and applications which address the needs of current and future work in bioinformatics.
The Entrez module in BioPython provides code to access NCBI over the WWW. The efetch and read functions of this module have been used in this pipeline. 'efetch' Retrieves records in the requested format from a list of one or more primary IDs or from the user's environment. 'parse' Parses the XML results returned by those of the above functions which can return multiple records - such as efetch, esummary and elink.
LICENSE: http://www.biopython.org/DIST/LICENSE


###MedKATp
(http://ohnlp.sourceforge.net/MedKATp/)
MedKATp (Medical Knowledge Analysis Tool) is tailored to the medical/pathology domain, containing components for extracting cancer-specific characteristics from unstructured text. It is based on Natural Language Processing (NLP) principles, and contains both rule-based and machine-learning based components. MedKAT/P is built on the open source Unstructured Information Management Architecture (UIMA) framework, and consists of a set of modules (annotators), each having a configuration file in XML format. In general terms, annotators mark up an unstructured textual document, inserting “annotations” that can be associated with a particular piece of text or which can be container objects for other annotations. A subsequent annotator can read and process all previously created annotations. The execution sequence, or pipeline, of annotators is also described in a configuration file.

Functionally, the MedKAT/P pipeline can be broken into several sets of components:
Document ingestion: annotators that determine document structure and extract implicit meaning from that structure.
General natural language processing: components for tokenization, sentence discovery, part-of-speech tagging, and shallow parsing
Concept finding: components that determine concepts based on specified terminology or patterns and determines negation
Relation finding: components that populate the Cancer Disease Knowledge Model (CDKM) and resolves co-references.

The document ingestion, NLP and concept finding steps have been used in this pipeline.
LICENSE: ALv2 (Refer: http://ohnlp.org/index.php/MedKAT/p, http://www.apache.org/licenses/LICENSE-2.0)


###Scikit Learn (sklearn)
(http://scikit-learn.org/stable/index.html)
Scikit learn implements machine Learning in Python. Simple and efficient tools for data mining and data analysis. Accessible to everybody, and reusable in various contexts. Built on NumPy, SciPy, and matplotlib. Open source, commercially usable.
LICENSE: Scikit - BSD

###Natural Language Toolkit (nltk)
(http://www.nltk.org/)
NLTK is a leading platform for building Python programs to work with human language data. It provides easy-to-use interfaces to over 50 corpora and lexical resources such as WordNet, along with a suite of text processing libraries for classification, tokenization, stemming, tagging, parsing, and semantic reasoning, wrappers for industrial-strength NLP libraries. NLTK is available for Windows, Mac OS X, and Linux. NLTK is a free, open source, community-driven project.
LICENSE: ALv2 (Refer: https://github.com/nltk/nltk, http://www.apache.org/licenses/LICENSE-2.0)
