from orm.db import *
import logging
from sqlalchemy import and_

#Create a DB session to store the info from Pubmed, if not already in the db
db_session = DBHelper().session

logger = logging.getLogger("nlp_logger")

#Class with functions for querying the database
class DBQuery():

    #Check if the pubmed article already exists in the db, else parse and create an entry
    def checkArticleInDB(self,pmid):
        logger.debug('Inside checkArticleInDB(pmid) function')
        obj = db_session.query(Article).filter(Article.PMID == pmid).all()
        logger.info("Article count for given Pmid in DB is: "+str(len(obj)))
        return len(obj)

    #Insert articles into db
    def insertArticles(self, articles):
        logger.debug("Inside insertArticles(articles) function")
        for article in articles:
            #Insert the Article instance as a record in the DB
            db_session.add(article)
            db_session.commit()
        logger.debug('Inserted '+str(len(articles))+'into Articles table in DB')

    #Query db to retrieve the Pubmed articles
    def getArticles(self):
        logger.debug('Inside getArticles() function')
        articles = db_session.query(Article).all()
        logger.debug('Returning with articles')
        return articles

    #Query db to retrieve the Pubmed articles for a list of ids
    def getArticlesByIds(self,article_ids):
        logger.debug('Inside getArticles(article_ids) function')
        articles = db_session.query(Article).filter(Article.PMID.in_(article_ids)).all()
        logger.debug('Returning with articles for given pmids')
        return articles


    #Get Lexicon terms from db
    def getLexicon(self):
        logger.debug('Inside getLexicon() function')
        Lexterms = db_session.query(Lexicon).all()
        logger.debug("Returning with the lexicon table data")
        return Lexterms

    #Insert the NE terms in the DB
    def insertNamedEntity(self,ne_terms):
        logger.debug("Inside insertNamedEntity(ne_terms) function")
        for term in ne_terms:
            lex_term_id = term['LexTermID']
            art_pmid = term['articleID']

            #Check if an entry for the named entity in that pmid already exists in the db. If not, write to the db
            dbChk = db_session.query(NamedEntity).filter(and_(NamedEntity.LexTermID == lex_term_id),(NamedEntity.articleID ==art_pmid))
            test = db_session.query(dbChk.exists()).scalar()

            if not test.lower() == 'true':
                ne_term = NamedEntity(LexTermID=lex_term_id, TxtTerm=term['TxtTerm'], startPos=term['startPos'], endPos=term['endPos'], articleID=art_pmid, dictCanon=term['DictCanon'])
                #Insert the NE instance as a record in the DB
                db_session.add(ne_term)
                db_session.commit()

        logger.debug('Inserted '+str(len(ne_terms))+'into NamedEntity table in DB')