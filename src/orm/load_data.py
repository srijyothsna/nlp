from orm.db import *
from sqlalchemy import and_

#Insert data into the LexType table
def set_Lex_Type():
    db_session = DBHelper().session
    lex = LexType(id=1, name="Disease", source="Human Disease Ontology")
    obj = db_session.query(LexType).filter(LexType.id == 1).all()
    if len(obj) < 1:
       db_session.add(lex)
    db_session.commit()
    db_session.close()

#Insert disease terms from HDO to the Lexicon table
def load_HumanDO_Terms():
    db_session = DBHelper().session

    filename = "../data/terms.csv"
    lines = list(open(filename)) 
    for line in lines:
        elements = line.rstrip().split(", ")
        parent_id = ''
        if len(elements) >= 5:
            parent_id = elements[4]
        term = Lexicon(termid=elements[0], typeid=elements[1], term=elements[2], syntype=elements[3], parentid=parent_id)

        obj = db_session.query(Lexicon).filter(Lexicon.termid == elements[0]).all()
        if len(obj) < 1:
           db_session.add(term)

    db_session.commit()
    db_session.close()

#Insert XRefs for disease terms from HDO into the Linkout table
def load_HumanDO_Xrefs():
    db_session = DBHelper().session

    filename = "../data/linkouts.csv"
    lines = list(open(filename)) 
    for line in lines:
        elements = line.rstrip().split(", ")
        linkout = LinkOut(termid=elements[2], linkoutid=elements[0], linkoutsource=elements[1])

        obj = db_session.query(LinkOut).filter(and_(LinkOut.termid == elements[2]),LinkOut.linkoutid == elements[0]).all()
        if len(obj) < 1:
           db_session.add(linkout)

    db_session.commit()
    db_session.close()


#set_Lex_Type()
#load_HumanDO_Terms()
#load_HumanDO_Xrefs()
