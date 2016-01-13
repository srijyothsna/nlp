import cgi

DATA_DIR = '../data/'

#Add disease terms from HDO to the XML dictionary file used in UIMA
def HumanDO_XML_Dict():
    #dict_filename = DATA_DIR + "HDO_Disease_Dict.xml"
    dict_filename=DATA_DIR + "initialDict_base.xml"
    filename = DATA_DIR + "terms.csv"

    token_id = ""
    iter_started = False

    try:
        synonyms = {}
        ofile_handle  = open(dict_filename,'w+')
        ofile_handle.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        ofile_handle.write("<synonym>\n")
        ofile_handle.write("<token canonical=\"max key\" SemClass=\"Maxkey\" AttributeType=\"max\" AttributeValue=\"max\" POS=\"NN\" key=\"25485\" >\n")
        ofile_handle.write("</token>\n")

        #ofile_handle.write("<synonym>\n")
        lines = list(open(filename))
        key_cntr = 1
        parent_key = key_cntr

        for line in lines:
            elements = line.rstrip().split(", ")
            parent_id = ''
            if len(elements) >= 5:
                parent_id = elements[4]

            term = cgi.escape(elements[2])
            source = cgi.escape(elements[3])

            if token_id == elements[0]:
               #ofile_handle.write("\t\t<variant base=\"%s\"  POS=\"NN\" key=\"%s\" parent=\"%s\" source=\"%s\"/>\n" % (term, key_cntr, parent_key, source))
               ofile_handle.write("\t<variant base=\"%s\"  POS=\"NN\" key=\"%s\" parent=\"%s\"> " % (term, key_cntr, parent_key))
               ofile_handle.write("</variant>\n")
               key_cntr += 1

            else:
               token_id = elements[0]
               if iter_started:
                   ofile_handle.write("</token>\n")
                   parent_key = key_cntr
               else:
                   iter_started = True
               #ofile_handle.write("\t<token canonical=\"%s\" id=\"%s\" DictType=\"1\">\n" % (term, elements[0]))
               #ofile_handle.write("\t\t<variant base=\"%s\" source=\"Term\"/>\n" % (term))

               ofile_handle.write("<token canonical=\"%s\" SemClass=\"Disease\" AttributType=\"HDO\" AttributeValue=\"%s\" POS=\"NN\" key=\"%s\">\n" % (term, elements[0],key_cntr))
               #ofile_handle.write("\t\t<variant base=\"%s\" POS=\"NN\" key=\"%s\" parent=\"%s\" source=\"Term\"/>\n" % (term, key_cntr, parent_key))
               ofile_handle.write("\t<variant base=\"%s\" POS=\"NN\" key=\"%s\" parent=\"%s\">" % (term, key_cntr, parent_key))
               ofile_handle.write("</variant>\n")
               key_cntr += 1

            #term = Lexicon(termid=elements[0], typeid=elements[1], term=elements[2], syntype=elements[3], parentid=parent_id)
        if iter_started:
            ofile_handle.write("</token>\n")
        ofile_handle.write("</synonym>\n")

    except Exception, e:
        print e


HumanDO_XML_Dict()