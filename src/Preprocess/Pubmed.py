from Bio import Entrez
import logging
from orm.db import *
from orm.DBQuery import *

logger = logging.getLogger("nlp_logger")

class PubmedData():

    # Specify email to tell NCBI who you are
    Entrez.email = 'jyothsna.sy@gmail.com'
    logger.debug("In the PubmedData Class")

    #Function to retrieve data from Pubmed for a list of Pmids using the BioPython's eutils and store the data in the db
    def getPubmedData(self,pmids):
        PmidList = pmids
        articles = []

        logger.debug("Fetching articles from Pubmed - Start")
        # Retrieve the entire abstract for each pmid
        for pmid in PmidList:

            #Create a DB session to store the info from Pubmed, if not already in the db
            dbqry = DBQuery()


            if(dbqry.checkArticleInDB(pmid) <1):
                #Fetch the abstracts from Pubmed
                handle = Entrez.efetch(db='pubmed', id=pmid, retmode='xml')
                #Parsed info from obtained from Pubmed
                records = Entrez.parse(handle)

                #Create a DB entry for each Pubmed record
                for record in records:
                    #print pmid
                    abs = ''
                    authors=''
                    article_date=''
                    keywords = ''

                    #If the article type is MedlineCitation and is defined
                    if 'MedlineCitation' in record:

                        #Retrieve Keyword list
                        if record['MedlineCitation']['KeywordList']:
                            keywordList = record['MedlineCitation']['KeywordList']
                            keywords = ', '.join(keywordList[0])

                        #Retrieve article title
                        title = record['MedlineCitation']['Article']['ArticleTitle']

                        #Retrieve abstract if defined
                        if record['MedlineCitation']['Article']:
                            if 'Abstract' in record['MedlineCitation']['Article']:
                                if 'AbstractText' in record['MedlineCitation']['Article']['Abstract']:
                                    abs = (record['MedlineCitation']['Article']['Abstract']['AbstractText'][0])

                        #Retrieve author list
                        for author_dict in record['MedlineCitation']['Article']['AuthorList'] :
                            #If first is defined, add author firstname and lastname
                            if 'ForeName' in author_dict:
                                authors+=" %(ForeName)s %(LastName)s" % author_dict +","
                            #Else add author Initials and lastname
                            else:
                                if 'Initials' in author_dict:
                                    authors+=" %(Initials)s %(LastName)s" % author_dict +","

                        #Retrieve article date, if specified
                        if record['MedlineCitation']['Article']['ArticleDate']:
                            article_date = record['MedlineCitation']['Article']['ArticleDate'][0]['Month']+'-'+record['MedlineCitation']['Article']['ArticleDate'][0]['Day']+'-'+record['MedlineCitation']['Article']['ArticleDate'][0]['Year']

                    #If the article type is BookDocument and is defined
                    if 'BookDocument' in record:

                        #print record['BookDocument']

                        #Retrieve Book title
                        title = record['BookDocument']['Book']['BookTitle']

                        #Retrieve author list
                        for author_dict in record['BookDocument']['Book']['AuthorList'][0]:
                            if 'ForeName' in author_dict:
                                authors+=" %(ForeName)s %(LastName)s" % author_dict +","
                            else:
                                if 'Initials' in author_dict:
                                    authors+=" %(Initials)s %(LastName)s" % author_dict +","

                        #Retrieve abstract if defined
                        if 'Abstract' in record['BookDocument']:
                             if 'AbstractText' in record['BookDocument']['Abstract']:
                                 abs = (record['BookDocument']['Abstract']['AbstractText'][0])


                        #Retrieve PubDate if defined
                        if record['BookDocument']['Book']['PubDate']:
                            article_date = record['BookDocument']['Book']['PubDate']['Month']+'-'+record['BookDocument']['Book']['PubDate']['Year']

                    #Create an Article instance with the data retrieved
                    article = Article(PMID=pmid, title=title, abstract=abs, authors=authors, doi='', keywords= keywords, articledate = article_date)
                    articles.append(article)

                handle.close()
        logger.info("Fetching articles from Pubmed - Done")
        print("Fetching articles from Pubmed - Done")

        logger.debug("Inserting articles into database - Start")
        dbqry.insertArticles(articles)
        logger.info("Inserting articles into database - Done")
        print("Inserting articles into database - Done")


pd = PubmedData()
#articles = ['26563128', '26467811', '26618099', '26650448', '26663950', '26656232', '26549782', '26553976', '26670362', '26504170', '26592654', '26666763', '26432165', '26664784', '26676792', '26663344', '26552419', '26368308', '26545955', '26527893', '26662304', '26677205', '26558264', '26637299', '26586118', '26662798', '26657485', '26530297', '26577420', '26653982', '26572803']
#pd.getPubmedData(articles)