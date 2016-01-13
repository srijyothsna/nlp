from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from config import ConfigParserHelper
Base = declarative_base()
 
class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True)
    PMID = Column(Integer)
    title = Column(String)
    abstract = Column(String)
    authors = Column(String)
    doi = Column(String)
    keywords = Column(String)
    articledate = Column(String)
 
class Lexicon(Base):
    __tablename__ = 'lexicon'
    id = Column(Integer, primary_key=True)
    termid = Column(Integer)
    typeid = Column(Integer, ForeignKey('lextype.id'))
    term = Column(String)
    syntype = Column(Integer)
#    linkoutid = Column(Integer, ForeignKey('linkout.id'))
    parentid = Column(Integer)

class LexType(Base):
    __tablename__ = 'lextype'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    source = Column(String)

class LinkOut(Base):
    __tablename__ = 'linkout'
    id = Column(Integer, primary_key=True)
    linkoutid = Column(Integer)
    linkoutsource = Column(String)
#    sourcebaseurl = Column(String)
    termid = Column(Integer, ForeignKey('lexicon.id'))
 
class NamedEntity(Base):
    __tablename__ = 'namedentity'
    id = Column(Integer, primary_key=True)
    #NEid = Column(Integer)
    LexTermID = Column(Integer, ForeignKey('lexicon.termid'))
    TxtTerm = Column(String)
    startPos = Column(Integer)
    endPos = Column(Integer)
    articleID = Column(Integer, ForeignKey('article.PMID'))
    dictCanon = Column(String)
    #sentenceID = Column(Integer, ForeignKey('articlesentence.id'))
    #locationID = Column(Integer)

#Not used currently, for extensibility
class ArticleSentence(Base):
    __tablename__ = 'articlesentence'
    id = Column(Integer, primary_key=True)
    #sentenceID = Column(Integer)
    articleID = Column(Integer, ForeignKey('article.PMID'))
    startPos = Column(Integer)
    endPos = Column(Integer)
    #sentIndex = Column(Integer)

class DBHelper:

    session = None

    def __init__(self):
        engine = create_engine(cfg.get('main', 'db_conn_string'))
        # create a configured "Session" class
        Session = sessionmaker(bind=engine)

        # create a Session
        self.session = Session()


cfg = ConfigParserHelper()
engine = create_engine(cfg.get('main', 'db_conn_string'))

from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
