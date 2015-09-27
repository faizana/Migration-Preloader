import re
from datetime import *
from dateutil import parser
from date_parser import start_date_parse
import math

if __name__ == "__main__":
    scenarios=[
                # "1920 (Taish_ 9), May",\
                #     "first quarter of the 18th century",\
                #     "mid-18th century or later",\
                #     "Late 16th-17th century or later",\
                # "late 1790s (mid Kansei era)",\
                #     "A.D. 90-96",\
                #       "1st half of the 1st century A.D.",\
                #       "1st or 2nd century A.D.",\
                #     "14th century (?)",\
                # "1627 (Kan'ei 4)",\
                #     "Early 1st century A.D.",\
                #     "3rd century A.D.",\
                #     "Second half of the 7th century A.D.",\
                #     "Late 3rd or early 4th century A.D.",\
                #     "about 600 B.C.",\
                #     "1400 B.C.",\
                #     "about 50 B.C.",\
                #     "Late 5th-early 4th century B.C.",\
                #     "2nd or 3rd century A.D.",\
                #     "Late 1st century B.C. or early 1st century A.D.",\
                #     "end of the 16th or early 17th century",\
                # "early 1770s",\
                # "designed 1945-46, made 1946-47",\
                # "datable to 1110s",\
                #     "about mid-1st century A.D.",\
                #     "Mid-to late 1st century B.C.",\
                # "mid-1860s",\
                # "mid 1830s",\
                # "about 30 B.C.-A.D. 70",\
                #     "about 40-20 B.C.",\
                #     "about 3rd century A.D.",\
                #     "late 1st century B.C. or 1st century A.D.",\
                #     "second half of the 11th century",\
                #     "19th century, style of Charles II",\
                #     "A.D. 14-37",\
                #     "3rd to early 4th century A.D.",\
                #     "11th century, with 12th century repairs",\
                #     "datable to the 1160s",\
                # "1715 (Sh_toku 5), 1st month",\
                #     "1st century B.C. or 1st century A.D.",\
                #     "first quarter of the 16th century",\
                #     "late 7th, early 8th century",\
                #     "20th century model of 17th century dwelling",\
                #     "June 24, 1939",\
                #     "Original construction in the 13th or 14th century; Damaged in the 17th century and rebuilt in the last quarter of the 17th century.",\
                #     "1/15/1938",\
                #     "about 1903-08",\
                #     "11.12.1868",\
                #     "1860s-70s",\
                #     "October 21, 1999 - January 21, 2000",\
                #     # "Drawn and etched about 1815-1816"
                #       "1225-1399 , 1479 CE",\
                #        "1496-97 CE"

    ]

def check_for_special_words(term):
    return bool(re.search(r'\bEARLY\b|\bMID\b|\bEND\b|\bSTART\b|\bBEGINNING\b|\bLATE\b|\bQUARTER\b|\bCENTURY\b|\bHALF\b',term))

def simple_date(string):
    formats=bool(re.search(r'\d+-\d+-\d+|\d+/\d+/\d+|\d+\.\d+\.\d+|.+,.+|\w+\s+\w+',string))
    if string.strip()!='' and formats:
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
        ed_factor=0.33
        ld_factor=0.66
    elif bool(re.search(r'\bLATE\b|\bEND\b',words)):
        ed_factor=0.66
        ld_factor=0.99
    elif 'QUARTER' in words:
        if re.search('1ST QUARTER|FIRST QUARTER',capitalized_string):
            ed_factor=0
            ld_factor=0.25
        elif re.search('2ND QUARTER|SECOND QUARTER',capitalized_string):
            ed_factor=0.25
            ld_factor=0.50
        elif re.search('3RD QUARTER|THIRD QUARTER',capitalized_string):
            ed_factor=0.50
            ld_factor=0.75
        else:
            ed_factor=0.75
            ld_factor=0.99
    elif words=='HALF':
        if re.search('1ST HALF|FIRST HALF',capitalized_string):
            ed_factor=0
            ld_factor=0.50
        elif re.search('2ND HALF|SECOND HALF',capitalized_string):
            ed_factor=0.50
            ld_factor=0.99
        elif re.search('LATTER HALF',capitalized_string):
            ed_factor=0.50
            ld_factor=0.99
    return ed_factor,ld_factor


def get_era(term):
    contains_bc=bool(re.search(r'\bBC\b|\bB.C\b|\bB.C.\b|\bBCE\b',term))
    contains_ad=bool(re.search(r'\bAD\b|\bA.D\b|\bA.D.\b|\bCE\b|\bC.E.\b',term))

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



def parse_date(original_string,recursive,era):

    capitalized_string=original_string.upper()
    # capitalized_string=remove_irrelevant_words(capitalized_string)
    if era=='' or era=='MULTIPLE':
        era=get_era(capitalized_string)
    is_range=check_for_range(capitalized_string)

    if is_range:
        check_for_simple=simple_date(capitalized_string)
        if check_for_special_cases(original_string):
            result=start_date_parse(capitalized_string)
            ed=int(re.sub('\(|\)|\'','',result.split(',')[0]).strip())
            ld=int(re.sub('\(|\)|\'','',result.split(',')[1]).strip())
            return ed,ld
        if '' in check_for_simple:
            contains_epoch=bool(re.search(r'CENTURY',capitalized_string))
            split_terms=re.split(r'-|\bTO\b|\bAND\b|\bOR\b|/|,|\(.+\)',capitalized_string)
            # contains_non_digits=[ True for x in split_terms if bool(re.search('\D+',x))==True ]
            edld=[]
            for term in split_terms:
                # if True in contains_non_digits:
                    if contains_epoch:
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
                contains_epoch=bool(re.search(r'CENTURY',capitalized_string))
                contains_special_words=bool(re.search(r'\bEARLY\b|\bMID\b|\bEND\b|\bSTART\b|\bBEGINNING\b|\bLATE\b|\bQUARTER\b|\bHALF\b',capitalized_string))
                contains_s=bool(re.search(r'\b\d+S\b',capitalized_string))
                if contains_epoch and not contains_special_words and not contains_s:
                    numeric_term=re.findall(r'\d+',capitalized_string)
                    eds=[]
                    lds=[]
                    for ts in numeric_term:
                        if era=='AD':
                            ed=(int(ts)-1)*100
                            ld=ed+99
                            eds.append(ed)
                            lds.append(ld)

                        else:
                            ed=(int(ts))*100*-1
                            ld=ed+99
                            eds.append(ed)
                            lds.append(ld)
                    return min(eds),max(lds)
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
                    numeric_term=re.search('\d+',capitalized_string).group()
                    if era=='AD':

                        ed=(int(numeric_term)-1)*100+min(ed_list)*100
                        ld=(int(numeric_term)-1)*100+max(ld_list)*100
                        return int(ed),int(ld)
                    else:
                        ed=(int(numeric_term))*100*-1+min(ed_list)*100
                        ld=(int(numeric_term))*100*-1+max(ld_list)*100
                        return ed,ld
                elif contains_s:
                    date=re.search('\d+',capitalized_string).group()
                    z_count=date.count('0')
                    trailing_z=''
                    trailing_n=''
                    for c in range(z_count):
                        trailing_z+='0'
                        trailing_n+='9'
                    ed=date[:-z_count]+trailing_z
                    ld=date[:-z_count]+trailing_n
                    if contains_special_words:
                        ed_factor,ld_factor=special_word_factors(re.search(r'[A-Z]+\s+\d+',capitalized_string).group(),capitalized_string)
                        new_ed=int(ed)+(10**z_count)*ed_factor
                        ld=int(ed)+(10**z_count)*ld_factor
                        return int(math.floor(new_ed)),int(math.floor(ld))

                    return ed,ld
                elif contains_special_words and not contains_epoch:
                    term=capitalized_string+' CENTURY '+era
                    ed,ld=parse_date(term,True,era)
                    return ed,ld
                else:
                    if recursive:
                        return '',''
                    else:
                        year=re.search('\d+',capitalized_string).group()
                        if era=='AD':
                            return int(year),int(year)
                        elif era=='BC':
                            return int(year)*-1,int(year)*-1



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









