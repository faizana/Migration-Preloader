# -*- coding: utf-8 -*-
import re
from datetime import *
from dateutil import parser
from date_parser import start_date_parse,simple_epoch_conversion

import math

if __name__ == "__main__":
    scenarios=[





             "3rd millennium C.E."






    ]




def check_for_special_words(term):
    return bool(re.search(r'\bEARLY\b|\bMID\b|\bEND\b|\bSTART\b|\bBEGINNING\b|\bLATE\b|\bQUARTER\b|\bCENTURY\b|\bHALF\b',term))

def simple_date(string):
    formats=bool(re.search(r'\d+-\d+-\d+|\d+/\d+/\d+|\d+\.\d+\.\d+|.+,.+',string))
    contains_era_term=bool(re.search(r'AD|A\.D\.',string))
    if string.strip()!='' and formats and not contains_era_term:
        try:
            simple=parser.parse(string,fuzzy=False)
            year=simple.year
            return year,year
        except:
            return '',''
    else:
        return '',''

def special_word_factors(words,capitalized_string):
    ed_factor=''
    ld_factor=''
    if bool(re.search(r'\bEARLY\b|\bBEGINNING\b|\bSTART\b',words)):
        ed_factor=0
        ld_factor=0.33
    elif 'MID' in words:
        ed_factor=0.34
        ld_factor=0.66
    elif bool(re.search(r'\bLATE\b|\bEND\b',words)):
        ed_factor=0.67
        ld_factor=0.99
    elif 'QUARTER' in words:
        if re.search('1ST QUARTER|FIRST QUARTER',capitalized_string):
            ed_factor=0
            ld_factor=0.24
        elif re.search('2ND QUARTER|SECOND QUARTER',capitalized_string):
            ed_factor=0.25
            ld_factor=0.49
        elif re.search('3RD QUARTER|THIRD QUARTER',capitalized_string):
            ed_factor=0.50
            ld_factor=0.74
        elif re.search('4TH QUARTER|FOURTH QUARTER',capitalized_string):
            ed_factor=0.75
            ld_factor=0.99
    elif words=='HALF':
        if re.search('1ST HALF|FIRST HALF',capitalized_string):
            ed_factor=0
            ld_factor=0.49
        elif re.search('2ND HALF|SECOND HALF',capitalized_string):
            ed_factor=0.50
            ld_factor=0.99
        elif re.search('LATTER HALF|LATER HALF',capitalized_string):
            ed_factor=0.50
            ld_factor=0.99
    return ed_factor,ld_factor

def contains_AD_BC_term(string):
    return bool(re.search(r'\bBC\b|\bB.C\b|\bB.C.\b|\bBCE\b|\bB\.C\.E\.\b|\bAD\b|\bA\.D\b|\bA\.D\.\b|\bCE\b|\b[^B\.]C\.E\.',string))

def generate_factors(words):
    factors=[]
    for word in words:
        if word=='FIRST' or word=='1ST':
            factors.append('EARLY')
        elif word=='SECOND' or word=='2ND':
            factors.append('MID')
        elif word=='LAST':
            factors.append('LATE')
    return factors




def get_era(term):
    contains_bc=bool(re.search(r'\bBC\b|\bB.C\b|\bB.C.\b|\bBCE\b|\bB\.C\.E\.\b',term))
    contains_ad=bool(re.search(r'\bAD\b|\bA\.D\b|\bA\.D\.\b|\bCE\b|\b[^B\.]C\.E\.',term))

    if contains_bc and not contains_ad:
        return 'BC'
    elif contains_ad and not contains_bc:
        return 'AD'
    elif contains_ad and contains_bc:
        return 'MULTIPLE'
    else:
        return 'AD'

def check_for_range(capitalized_string):
    range_words=bool(re.search(r'.+-{1}.+|\bTO\b|\bAND\b|\bOR\b|.+(/){1}.+|\d+.+,{1}.+\d+',capitalized_string))
    decision=False
    if range_words:
        terms=re.split(r'-|\bTO\b|\bAND\b|\bOR\b|/|,|\(.+\)',capitalized_string)
        for term in terms:
            contains_digits=bool(re.search(r'\d+',term))
            if contains_digits==False:
                contains_special_words=check_for_special_words(term)
                if contains_special_words:
                    decision=True
            else:
                decision=True
    return decision

def remove_irrelevant_words(string):
    irrelevant=['ABOUT','_']

    for words in irrelevant:
        string=string.replace(words,' ')

    return string.strip()

def check_for_special_cases(case):
    truth_list=[]
    check_for_appeneded_s_range=bool(re.search(r'\d+s(-)\d+s|\d+s(to)\d+s|\d+s(,)\d+s|\d+s(/)\d+s',case))
    truth_list.append(check_for_appeneded_s_range)
    check_for_complete_date_range=bool(re.search(r'\w+\s+\d+,\s+\d+\s+-\s+\w+\s+\d+',case))
    truth_list.append(check_for_complete_date_range)

    if True in truth_list:
        return True
    else:
        return False

def remove_unwanted_brackets(capitalized_string):
    bracket=bool(re.search('^\(.*\)$',capitalized_string))
    if bracket:
        capitalized_string=re.sub('^\(|\)$','',capitalized_string)
    capitalized_string=capitalized_string.replace('–','-')
    return capitalized_string




def check_for_composite_epochs(capitalized_string):
    #period_terms=['FIRST','SECOND','THIRD','FOURTH','LAST','1ST','2ND','3RD','4TH']
    pattern_check=bool(re.search(r'([A-Z]+\s+(?:THIRD|3RD)|\d{1}[A-Z]+\s+(?:THIRD|3RD))\s+([A-Z]*\s*[A-Z]*\s*)*\d+([A-Z]{2}\s+C.*|[A-Z]{2}C.*)',capitalized_string))
    return pattern_check


def parse_date(original_string,recursive,era):

    capitalized_string=original_string.upper()
    capitalized_string=remove_unwanted_brackets(capitalized_string)
    # capitalized_string=remove_irrelevant_words(capitalized_string)
    if era=='' or era=='MULTIPLE':
        era=get_era(capitalized_string)
    is_range=check_for_range(capitalized_string)

    if is_range:
        check_for_simple=simple_date(capitalized_string)
        if check_for_special_cases(original_string):
            try:
                result=start_date_parse(capitalized_string)
                ed=int(re.sub('\(|\)|\'','',result.split(',')[0]).strip())
                ld=int(re.sub('\(|\)|\'','',result.split(',')[1]).strip())
                return ed,ld
            except:
                pass
        if '' in check_for_simple:
            contains_epoch=bool(re.search(r'CENTUR|[^\.]C\.$|[^\.]C\.\s+|[^\.]C\.[\W+]',capitalized_string))
            split_terms=re.split(r'-|\bTO\b|\bAND\b|\bOR\b|/|,|\(.+\)',capitalized_string)
            if capitalized_string.find('(')!=-1:
                split_ranges=re.findall(r'\(.+\)',capitalized_string)
                split_terms=list(set(split_ranges) | set(split_terms) )
            # contains_non_digits=[ True for x in split_terms if bool(re.search('\D+',x))==True ]
            edld=[]
            for term in split_terms:
                # if True in contains_non_digits:
                    if contains_epoch and not contains_AD_BC_term(term):
                        term=term+' CENTURY'
                    ans=parse_date(term,True,era)
                    if '' not in ans and 'NA' not in ans:
                        edld.append(int(ans[0]))
                        edld.append(int(ans[1]))
                    elif '' in ans and 'NA' not in ans:
                        ans=parse_date(re.sub(r'-|\bTO\b|\bAND\b|\bOR\b|/|,|\(.+\)',' ',capitalized_string),True,era)
                        if ans[0]!='' and ans[1]!='':
                            edld.append(ans[0])
                            edld.append(ans[1])
                        else:

                            # capitalized_string=re.sub(r'-|\bTO\b|\bAND\b|\bOR\b|/|,|\(.+\)',' ',capitalized_string)
                            if era=='AD':
                                result=start_date_parse(capitalized_string)
                                try:
                                    ed=int(re.sub('\(|\)|\'','',result.split(',')[0]).strip())
                                    ld=int(re.sub('\(|\)|\'','',result.split(',')[1]).strip())
                                    if type(ed)==int and type(ld)==int:
                                        edld.append(int(ed))
                                        edld.append(int(ld))
                                except:
                                    start=re.search(r'\d+',split_terms[0]).group()
                                    end=re.search(r'\d+',split_terms[-1]).group()
                                    if int(start)>int(end):
                                        end=start[:-len(end)]+end
                                    edld.append(start)
                                    edld.append(end)
                            elif era=='BC':
                                result=start_date_parse(capitalized_string)
                                ed=re.sub('\(|\)|\'','',result.split(',')[0])
                                ld=re.sub('\(|\)|\'','',result.split(',')[1])
                                if bool(re.search('\d+',ed)) and bool(re.search('\d+',ld)):
                                    edld.append(int(ed))
                                    edld.append(int(ld))

                            elif era=='MULTIPLE':
                                bc_date=re.search(r'\d+',re.search(r'\d+\s+BC|BC\s+\d+',re.sub(r'BC|B\.C\.|BCE|B\.C','BC',capitalized_string)).group()).group()
                                ad_date=re.search(r'\d+',re.search(r'\d+\s+AD|AD\s+\d+',re.sub(r'AD|A\.D\.|CE|A\.D|C\.E\.','AD',capitalized_string)).group()).group()
                                edld.append(-int(bc_date))
                                edld.append(int(ad_date))

                        break
                # else:
                #     break
            # if True not in contains_non_digits:
            #     start=split_terms[0]
            #     end=split_terms[-1]
            #     if int(start)>int(end):
            #         end=start[:-len(end)]+end
            #
            #
            #     edld.append(start)
            #     edld.append(end)
            ed=min(edld)
            ld=max(edld)
            if ed<=ld:
                return ed,ld
            else:
                '',''
        else:
            return check_for_simple
    else:


        check_for_simple=simple_date(capitalized_string)
        if '' in check_for_simple:
            contains_digits=bool(re.search(r'\d+',capitalized_string))
            if contains_digits:
                contains_epoch=bool(re.search(r'CENT|MILLENNIUM|[^\.B]C\.*$|[^\.B]C\.*\s+|[^\.B]C\.[\W+]',capitalized_string))
                contains_special_words=bool(re.search(r'\bEARLY\b|\bMID\b|\bEND\b|\bSTART\b|\bBEGINNING\b|\bLATE\b|\bQUARTER\b|\bHALF\b',capitalized_string))
                contains_s=bool(re.search(r'\b\d+S\b|\b\d+\'S\b',capitalized_string))
                contains_composite_epoch=check_for_composite_epochs(capitalized_string)
                if contains_epoch and not contains_special_words and not contains_s and not contains_composite_epoch:
                    return simple_epoch_conversion(capitalized_string,era)
                elif contains_epoch and contains_special_words and not contains_s:
                    special_words=re.findall(r'\bEARLY\b|\bMID\b|\bEND\b|\bSTART\b|\bBEGINNING\b|\bLATE\b|\bQUARTER\b|\bHALF\b',capitalized_string)
                    ed_factor=''
                    ld_factor=''
                    ed_list=[]
                    ld_list=[]
                    for words in special_words:
                        ed_factor,ld_factor=special_word_factors(words,capitalized_string)
                        ed_list.append(ed_factor)
                        ld_list.append(ld_factor)
                    # numeric_terms=re.findall('\d+',re.search('\d+\D+\s+C.*',capitalized_string).group())
                    if len(special_words)<2:
                        numeric_terms=re.findall(r'\d+[A-Z][A-Z]\s*(?:CENT|C\.*$|C\.*\s+|[^\.]C\.[\W+])',capitalized_string)
                    else:
                        numeric_terms=re.findall(r'\d+[A-Z][A-Z]\s*(?:CENT|C\.*$|C\.*\s+|[^\.]C\.[\W+])*',capitalized_string)
                    numeric_terms=[re.sub('\D+','',x) for x in numeric_terms if bool(re.search('\d+',x))==True]
                    if len(numeric_terms)>0:
                        if era=='AD':
                            i=0
                            epoch_ed_ld_list=[]
                            for numeric_term in numeric_terms:
                                if len(numeric_terms)!=len(ed_list):
                                    ed=(int(numeric_term)-1)*100+min(ed_list)*100
                                    ld=(int(numeric_term)-1)*100+max(ld_list)*100
                                    epoch_ed_ld_list.append(ed)
                                    epoch_ed_ld_list.append(ld)
                                else:
                                    ed=(int(numeric_term)-1)*100+ed_list[i]*100
                                    ld=(int(numeric_term)-1)*100+ld_list[i]*100
                                    i+=1
                                    epoch_ed_ld_list.append(ed)
                                    epoch_ed_ld_list.append(ld)
                            return min(epoch_ed_ld_list),max(epoch_ed_ld_list)


                        else:
                            i=0
                            epoch_ed_ld_list=[]
                            for numeric_term in numeric_terms:
                                if len(numeric_terms)!=len(ed_list):
                                    ed=(int(numeric_term))*100*-1+min(ed_list)*100
                                    ld=(int(numeric_term))*100*-1+max(ld_list)*100
                                    epoch_ed_ld_list.append(ed)
                                    epoch_ed_ld_list.append(ld)
                                else:
                                    ed=(int(numeric_term))*100*-1+ed_list[i]*100
                                    ld=(int(numeric_term))*100*-1+ld_list[i]*100
                                    i+=1
                                    epoch_ed_ld_list.append(ed)
                                    epoch_ed_ld_list.append(ld)

                            return min(epoch_ed_ld_list),max(epoch_ed_ld_list)
                    else:
                        return 'NA','NA'
                elif contains_s:
                    s_ed_ld_list=[]
                    date=capitalized_string.split(' ')
                    for d in date:
                        trailing_z=''
                        trailing_n=''
                        if bool(re.search('\d+S|\d+\'S',d)) and check_for_special_words(date[date.index(d)-1])==False  :
                            d=re.sub('\D+','',d)
                            z_s=d.count('0')
                            for c in range(z_s):
                                trailing_z+='0'
                                trailing_n+='9'
                            ed=d[:-z_s]+trailing_z
                            s_ed_ld_list.append(int(ed))
                            ld=d[:-z_s]+trailing_n
                            s_ed_ld_list.append(int(ld))


                    if bool(re.search('\s+\d+[^S]\s+|\s+\d+[^\'S]\s+',capitalized_string)):
                        try:
                            other_date=re.findall('\s+\d+[^S]\s+|\s+\d+[^\'S]\s+',capitalized_string)
                            date_list=[int(x.strip()) for x in other_date]
                            date_list.append(int(ed))
                            date_list.append(int(ld))
                            ed=min(date_list)
                            ld=max(date_list)
                            s_ed_ld_list.append(ed)
                            s_ed_ld_list.append(ld)
                        except:
                            pass

                    if contains_special_words:
                        ed=re.findall(r'\bEARLY\s+\d+|\bMID\s+\d+|\bEND\s+\d+|\bSTART\s+\d+|\bBEGINNING\s+\d+|\bLATE\s+\d+|\bQUARTER\s+\d+|\bHALF\s+\d+',capitalized_string)
                        for dates in ed:
                            z_count=dates.count('0')
                            ed_factor,ld_factor=special_word_factors(re.search(r'[A-Z]+\s+\d+',dates).group(),capitalized_string)
                            new_ed=int(re.sub('\D+','',dates))+(10**z_count)*ed_factor
                            ld=int(re.sub('\D+','',dates))+(10**z_count)*ld_factor
                            s_ed_ld_list.append(math.floor(new_ed))
                            s_ed_ld_list.append(math.floor(ld))


                    return min(s_ed_ld_list),max(s_ed_ld_list)
                elif contains_special_words and not contains_epoch:
                    term=capitalized_string+' CENTURY '+era
                    ed,ld=parse_date(term,True,era)
                    return ed,ld

                elif contains_composite_epoch:
                    range_words=re.findall(r'FIRST|SECOND|THIRD|FOURTH|LAST|1ST|2ND|3RD',capitalized_string)
                    factors=generate_factors(range_words)
                    custom_date_string=re.sub('^FIRST\s+(?:[A-Z]+|\d{1}[A-Z]+)|^SECOND\s+(?:[A-Z]+|\d{1}[A-Z]+)|^THIRD\s+(?:[A-Z]+|\d{1}[A-Z]+)|^FOURTH\s+(?:[A-Z]+|\d{1}[A-Z]+)|^LAST\s+(?:[A-Z]+|\d{1}[A-Z]+)|^1ST\s+(?:[A-Z]+|\d{1}[A-Z]+)|^2ND\s+(?:[A-Z]+|\d{1}[A-Z]+)|^3RD\s+(?:[A-Z]+|\d{1}[A-Z]+)'," ".join(factors),capitalized_string)
                    ed,ld=parse_date(custom_date_string,True,era)
                    return ed,ld

                else:
                    if recursive:
                        if not contains_special_words and not contains_AD_BC_term(capitalized_string) and not contains_epoch and not contains_s:
                            return '',''
                        else:
                            result=start_date_parse(capitalized_string,era)
                            ed=int(re.sub('\(|\)|\'','',result.split(',')[0]).strip())
                            ld=int(re.sub('\(|\)|\'','',result.split(',')[1]).strip())
                            return ed,ld

                    else:
                        if bool(re.search('\D+\s+\d+\s+\(\D+\s+\d+\)',capitalized_string)):
                            # xxxx #### (xxxx ####)
                            try:
                                ed=re.search('\d+',capitalized_string.split('(')[0]).group()
                                ld=re.search('\d+',capitalized_string.split('(')[1]).group()
                                return int(ed),int(ld)
                            except:
                                ed='NA'
                                ld='NA'
                                return ed,ld


                        else:
                            year=re.findall('\d+',capitalized_string)
                            year=[int(x) for x in year]
                            if era=='AD':
                                return min(year),max(year)
                            elif era=='BC':
                                return max(year)*-1,min(year)*-1



            else:
                contains_special_words=bool(re.search(r'\bEARLY\b|\bMID\b|\bEND\b|\bSTART\b|\bBEGINNING\b|\bLATE\b|\bQUARTER\b|\bHALF\b',capitalized_string))
                if contains_special_words:
                    return '',''
                else:
                    return 'NA','NA'
        else:
            return check_for_simple







# for test in scenarios:
#     print "input: %s"%test
#     print "output:", parse_date(test,False,'')
#     # try:
#     #     print "output:", parse_date(test)
#     # except:
#     #     print "exception"
#     print ""