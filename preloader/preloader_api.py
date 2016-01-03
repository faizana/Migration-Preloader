
from dateutil.parser import parser
from date_parser_v2 import start_date_parse
from date_parser_v2 import parse_date
import csv
import simplejson
import os
import uuid
from multiprocessing import Process,Queue
import HTMLParser
import Queue as lq
import traceback
import sys
import re
import HTMLParser

htmlparsetool=HTMLParser.HTMLParser()

geography_map='controlled_list_map/country.csv'
classification_map='controlled_list_map/classification.csv'
classification_map=open(classification_map,'rU')
classification_map=csv.DictReader(classification_map,delimiter=',',dialect=csv.excel_tab)
geography_map=open(geography_map,'rU')
geography_map=csv.DictReader(geography_map,delimiter=',',dialect=csv.excel_tab)

def generate_country_dict(csv_dict):
    country_term_dict={}
    country_id_dict={}
    for row in csv_dict:
        country_term_dict[row['Source Geography Term'].lower()]=dict(artstor_term=row['Artstor Geography Term'],tgn_id=row['TGN ID'])
        country_id_dict[row['TGN ID']]=dict(artstor_term=row['Artstor Geography Term'],source_term=row['Source Geography Term'])
    return country_term_dict,country_id_dict

def generate_class_dict(csv_dict):
    class_term_dict={}
    for row in csv_dict:
        class_term_dict[row['Keyword'].lower()]=dict(artstor_term=row['Artstor Classification Term'])
    return class_term_dict


def find_term_match(val,val_arr):
    terms=[]
    for vals in val_arr:
        try:
          if bool(re.search(r'\b'+vals.lower()+r'\b',val.lower())):
              terms.append(vals)
        except:
          pass
          #print vals,val
    if len(terms)==0:
        terms=False
    return terms


def country_parse(terms):
    terms=terms.split('|')
    global country_term_dict
    parsed_terms_list=[]
    sm=0
    for row in terms:
        parsed_term_dict={}
        try:
            row=htmlparsetool.unescape(row).encode('utf-8')
        except:
            row=row.decode('latin-1')
            row=htmlparsetool.unescape(row).encode('utf-8')
        contains_brackets=bool(re.search('[a-z]+\s+\(\D+\)',row.strip().lower()))
        if contains_brackets==True:
            query_val=re.sub('\(\D+\)','',row)
            query_val=query_val.split(',')
        else:
            query_val=row.split(',')
        for qv in query_val:
            term_match=find_term_match(qv.lower().strip(),country_term_dict.keys())
            if term_match!=False and len(term_match)<2:

                parsed_term_dict['query_term']=row
                parsed_term_dict['artstor_country']=country_term_dict[term_match[0]]['artstor_term']
                parsed_term_dict['tgn_id']=country_term_dict[term_match[0]]['tgn_id']
                parsed_term_dict['status']='Matched'

                sm=1
                break
            elif term_match!=False and len(term_match)>=2:
                parsed_term_dict['query_term']=row
                countries=[]
                tgns=[]
                for terms in term_match:
                    countries.append(country_term_dict[terms]['artstor_term'])
                    tgns.append(country_term_dict[terms]['tgn_id'])
                parsed_term_dict['artstor_country']="|".join(countries)
                parsed_term_dict['tgn_id']="|".join(tgns)
                parsed_term_dict['status']='Matched'
                sm=1
                break

        if sm==0 and query_val[0]!='':
            parsed_term_dict['status']='Not Matched'
            parsed_term_dict['query_term']=' '.join(query_val)
        elif sm==0 and query_val[0]=='':
            parsed_term_dict['status']='null'
            parsed_term_dict['query_term']=''

        parsed_terms_list.append(parsed_term_dict)


    return parsed_terms_list




def class_parse(terms):
    terms=terms.split('|')
    global class_term_dict
    parsed_terms_list=[]
    sm=0
    for row in terms:
        parsed_term_dict={}

        try:
                row=htmlparsetool.unescape(row).encode('utf-8')
        except:
                row=row.decode('latin-1')
                row=htmlparsetool.unescape(row).encode('utf-8')
        query_val=row.split(',')
        for qv in query_val:
                        # print qv.strip(),class_term_dict.keys()
                if qv.strip()!='':
                    term_match=find_term_match(qv.lower().strip(),class_term_dict.keys())
                    if term_match!=False and len(term_match)<2:
                        parsed_term_dict['query_term']=' '.join(query_val)
                        parsed_term_dict['keyword']=term_match[0]
                        parsed_term_dict['artstor_classification']=class_term_dict[term_match[0]]['artstor_term']
                        parsed_term_dict['status']='Matched'
                        sm=1
                        break
                    elif term_match!=False and len(term_match)>=2:
                        parsed_term_dict['query_term']=' '.join(query_val)
                        classes=[]
                        keywords=[]
                        for terms in term_match:
                            classes.append(class_term_dict[terms]['artstor_term'])
                            keywords.append(terms)
                        parsed_term_dict['artstor_classification']="|".join(classes)
                        parsed_term_dict['keyword']="|".join(keywords)
                        parsed_term_dict['status']='Matched'
                        sm=1
                        break
        if sm==0 and query_val[0]!='':
            parsed_term_dict['status']='Not Matched'
            parsed_term_dict['query_term']=' '.join(query_val)
        elif sm==0 and query_val[0]=='':
            parsed_term_dict['status']='null'
            parsed_term_dict['query_term']=''

        parsed_terms_list.append(parsed_term_dict)

    return parsed_terms_list



def date_parse(terms):
    terms=terms.split('|')
    parsed_terms_list=[]
    for row in terms:
        parsed_term_dict={}
        try:
                row=htmlparsetool.unescape(row).encode('utf-8')
        except:
                row=row.decode('latin-1')
                row=htmlparsetool.unescape(row).encode('utf-8')
        if row.strip()!='':
            try:
                       # print "query_term",query_term
                        # result=start_date_parse(query_term.strip())
                        result=parse_date(row,False,'')
                        # ed=re.sub('\(|\)|\'','',result.split(',')[0])
                        # ld=re.sub('\(|\)|\'','',result.split(',')[1])
                        ed=result[0]
                        ld=result[1]
                        # logic=",".join(result.split(',')[2:])
                        # logic=re.sub("'|\(|\)",'',logic)
                        logic=''
                        if ed!="" and ld!="":
                            parsed_term_dict['status']='Converted'
                            parsed_term_dict['query_term']=row
                            parsed_term_dict['Earliest Date']=int(ed)
                            parsed_term_dict['Latest Date']=int(ld)
                            parsed_term_dict['Logic']=logic
                        else:
                            parsed_term_dict['status']='Exception'
                            parsed_term_dict['query_term']=row
                            parsed_term_dict['Earliest Date']=ed
                            parsed_term_dict['Latest Date']=ld
                            parsed_term_dict['Logic']=logic
            except :
                        #print 'Exception',query_term
                        #traceback.print_exc(file=sys.stdout)
                        parsed_term_dict['status']='Exception'
                        parsed_term_dict['query_term']=row
                        parsed_term_dict['Earliest Date']=''
                        parsed_term_dict['Latest Date']=''
                        parsed_term_dict['Logic']=''
        else:
                        parsed_term_dict['status']='Null Value'
                        parsed_term_dict['query_term']=''
                        parsed_term_dict['Earliest Date']=''
                        parsed_term_dict['Latest Date']=''
                        parsed_term_dict['Logic']=''

        parsed_terms_list.append(parsed_term_dict)

    return parsed_terms_list






country_term_dict,country_id_dict=generate_country_dict(geography_map)
class_term_dict=generate_class_dict(classification_map)