import re
from datetime import *
import csv
# # from dateutil import *
# from dateutil.tz import *
from dateutil import parser


def remove_syms(date_string):
    symbols=['?','<','>','DESIGNED','PRINTED','MADE','ABOUT','MANUFACTURED','SPRING-SUMMER','SPRING','SUMMER','AUTUMN','WINTER']

    for sym in symbols:
        date_string=date_string.replace(sym,'')
    date_string=re.sub('A\.D\.|A\.D','AD',date_string)
    date_string=re.sub('B\.C\.|B\.C','BC',date_string)
    date_string=re.sub('\s+C\.\s+|\s+C\.$','CENTURY',date_string)
    date_string=re.sub('^C\.\s+','',date_string)
    date_string=re.sub('\s+BEG\s+|BEG\s+|BEG\.\s+','BEGINNING',date_string)
    date_string=re.sub('\s+OR\s+','-',date_string)

    return date_string


def detect_month_year_conflict(date_string):
    splits=re.split('-|\.',date_string)
    if len(re.search('\d+',splits[0]).group())!=len(re.search('\d+',splits[-1]).group()):
        return True
    else:
        return False

def parse_date(input_string):
    # date_string = input_string.upper().replace(' ','') #remove whitespaces
    date_string = input_string.upper()
    date_string = remove_syms(date_string)
    logic_string=''
    # print date_string
    # date_string=date_string.replace('?','')
    # date_string=date_string.replace('CIRCA','')
    # contains_s=_ends_with_s(date_string.replace(' ',''))
    is_month_day_year_format=_is_month_day_year_format(date_string)
    contains_forward_slash=_contains_forward_slash(date_string)
    # contains_date_with_words_and_hyp=_contains_date_with_words_and_hyp(date_string)
    # year_string = re.sub(r'\d+,\s', '', date_string) # Jan 26, 1960
    year_string = re.sub(r'\d.+ QUARTER', '', date_string)
    # contains_epoch_with_hyp=_contains_epoch_with_hyp(year_string)
    contains_complex_epoch=bool(re.search('^.+\d+.+(,).+\d+.+(CENTURY)$|^\d+.+(,)\d+.+(CENTURY)$|^.+\d+.+(,).+\d+.+(CENTURYAD)$|\d+.+(,).+\d+.+(CENTURYAD)$|.+\d+.+(,)\d+.+(CENTURY)',date_string))

    contains_dots_with_year=_contains_dots_with_year(date_string)
    # print 'is_range(year_string)',is_range(year_string),"bool(re.search('\d+S$',date_string))",bool(re.search('\d+S$',date_string))
    # contains_canadian_format=_contains_canadian_format(date_string)
    # print 'contains_dots_with_year',contains_dots_with_year
    # print is_month_day_year_format,contains_dots_with_year
    if is_month_day_year_format and contains_dots_with_year==False and date_string.find('CENTURY')==-1:
        conflict=detect_month_year_conflict(date_string)
        if conflict==False:
            pip_parser=find_date(date_string)
            logic_string='Simple month_day_year_format detected in '+input_string
            if int(pip_parser)>=datetime.now().year:
                logic_string='Unclear Format detected in '+input_string
                return '','',logic_string
            else:
                return pip_parser,pip_parser,logic_string
        else:
            logic_string='Unclear Format detected in '+input_string
            return '','',logic_string

        #
    elif is_range(year_string) and bool(re.search('\D+',year_string.replace('-','')))==False: #and contains_epoch_with_hyp==False and year_string.count('-')<2 and contains_date_with_words_and_hyp==False and contains_s==False:
        # print ' bc yahan q atey hou'
        return parse_ranges(year_string)
    elif is_range(year_string) and bool(re.search('\D+',year_string.replace('-','')))==True:
        # print 'mkc'
        date_string = input_string.upper()
        date_string=remove_syms(date_string)
        date_string=date_string.replace(' ','')
         #remove whitespaces
        if date_string.find('CA.')!=-1:
            date_string=date_string.replace('CA.','')
            if bool(re.search('(-)\d+(-)',date_string)):
                year_string=re.search('(-)\d+',date_string).group()
                return year_string,year_string
            elif bool(re.search('\d+(-)\d+',date_string)):
                year_string=date_string.split('-')
                return year_string[0],year_string[1]
            elif bool(re.search('(-)\d+(-)+\d+',date_string)):
                year_string=re.split('-\d+',date_string)
                return year_string[0],year_string[1]





        date_string=re.sub(r'AND|TO','-',date_string)
        logic_string='alphanumeric range detected in '+input_string
        # print date_string
        contains_s=_ends_with_s(date_string)
        contains_date_with_words_and_hyp=_contains_date_with_words_and_hyp(date_string)
        contains_epoch_with_hyp=_contains_epoch_with_hyp(date_string)
        contains_multiple_ranges=bool(re.search('\d+(-)\d+(,|;)\d+(-)\d+',date_string))




        if contains_multiple_ranges:
            dates=re.split(',|;',date_string)
            eds=start_date_parse(dates[0])
            lds=start_date_parse(dates[1])
            ed=eds.split(',')[0].replace('(','')
            ld=lds.split(',')[1]
            return ed,ld,'Multiple ranges detected'

        # print contains_date_with_words_and_hyp,contains_epoch_with_hyp
        if contains_s:
            date_string=date_string.replace('S','')
            if date_string.find('-')!=-1:
                date_string=date_string.split('-')
                if bool(re.search('\d+',date_string[0])):
                    ed=date_string[0]
                else:
                    date_string[1]=re.search('\d+',date_string[1]).group()
                    ed=date_string[1]
                z_count=date_string[1].count('0')
                trailing_n=''
                for c in range(z_count):
                    trailing_n+='9'
                ld=date_string[1][:-z_count]+trailing_n
                if len(ld)!=len(ed):
                    diff=len(ed)-len(ld)
                    ld=ed[:diff]+ld
                logic_string+='. "s" found appended to year, converted to range accordingly'
                return ed,ld,logic_string


            z_count=date_string.count('0')
            trailing_z=''
            trailing_n=''
            for c in range(z_count):
                trailing_z+='0'
                trailing_n+='9'
            ed=date_string[:-z_count]+trailing_z
            ld=date_string[:-z_count]+trailing_n
            logic_string+='. Simple date format without "-"found  converted to ED/LD accordingly'
            return ed,ld,logic_string


        elif contains_date_with_words_and_hyp:
            if bool(re.search('\D+\d+(-)\d+$|\d+(-)\d+',date_string)):
                res=start_date_parse(re.search('\d+(-)\d+',date_string).group())
                res+=', Date found containing words with "-", applied range logic to convert'
                return res
            elif bool(re.search('^\D+\d+(-)\D+\d+$|^\d+(-)\D+\d+$',date_string)):
                ed=re.sub('\D+','',date_string.split('-')[0])
                ld=re.sub('\D+','',date_string.split('-')[1])
                logic_string+='. Date found containing words with "-", applied range logic to convert'
                return ed,ld,logic_string
            elif bool(re.search('^\D+\d+\D+\d+(-)\D+\d+\D+\d+$',date_string)):
                ed=remove_string_elems(start_date_parse(input_string.split('-')[0]))[0]
                ld=remove_string_elems(start_date_parse(input_string.split('-')[1]))[0]
                logic_string+='. Date found containing words with "-", applied range logic to convert'
                return ed,ld,logic_string

            get_regex=re.compile(r'\d+$')
            ed=get_regex.search(date_string).group()
            ld=ed
            logic_string='Single date detected in alphanumeric, Earliest and Latest date will be same'
            return ed,ld,logic_string
        elif contains_epoch_with_hyp:
            year_string=date_string.replace(' ','')
            # print 'here'
            get_exact_string=re.compile(r'[A-Z]+\d+[A-Z][A-Z](CENTURY-)[A-Z]+\d+[A-Z][A-Z](CENTURY)')
            get_exact_string1=re.compile(r'[A-Z]+(-\d+[A-Z][A-Z]CENTURY)|[A-Z]+(-[A-Z]+\d+[A-Z][A-Z]CENTURY)|[A-Z]+(-\d+[A-Z]+\d+[A-Z]+CENTURY)|'
                                         r'([A-Z]+-+)+[A-Z]+\d+\D+CENTURY|\d+(-)\d+AD|[A-Z]+\d+[A-Z][A-Z](-[A-Z]+\d+[A-Z][A-Z]CENTURY)') #MID-19THCENTURY,MID-TOLATE19THCENTURY
            is_bc_date=re.compile(r'BC-|-BC|BC$')
            if bool(get_exact_string.search((year_string))):
                check_for_special_dates=bool(re.search('BEGINNING|EARLY|MID|LATE|END',year_string))
                if check_for_special_dates==False:
                    res=start_date_parse(get_exact_string.search(year_string).group().replace('-',','))
                else:
                    res=start_date_parse(year_string.replace('-',','))
                    res+='Special word '+re.search('BEGINNING|EARLY|MID|LATE|END',year_string).group()+' found in string.'
                res+=', Ranged epoch with multiple "CENTURY" keywords detected , parsing according to range rules'
                return res
            elif bool(get_exact_string1.search((year_string))):

                    if year_string.find('CENTURY')!=-1:
                        exp=re.search('\d+\D+(CENTURY)|^\d+(-)\d+|\d+\D+(-)\d+\D+(CENTURY)|\D+\d+\D+(-)\D+\d+\D+(CENTURY)',year_string)
                        # print start_date_parse(exp.group()),type(start_date_parse(exp.group()))
                        check_for_special_dates=bool(re.search('BEGINNING|EARLY|MID|LATE|END',year_string))
                        if check_for_special_dates==False:
                            if bool(is_bc_date.search(year_string))==False:
                                res=start_date_parse(exp.group().replace('-',','))
                            else:
                                res=start_date_parse(exp.group().replace('-',','))
                                res=res.split(',')
                                ed=int(re.sub('\(|\)','',res[0]))
                                ld=int(res[1].replace('(',''))

                                if  ed>ld:
                                    res[0]=str(int(re.sub('\(|\)','',res[0]))*-1-99)
                                    if crosses_bc_ad_boundary(year_string)==False:

                                        res[1]=str(int(res[1].replace('(',''))*-1+99)
                                    res=','.join(res)
                                else:

                                    res[0]=str(ld*-1)
                                    if crosses_bc_ad_boundary(year_string)==False:

                                        res[1]=str(ed*-1)
                                    res=','.join(res)



                        else:
                            res=start_date_parse(year_string.replace('-',','))
                            res+='Special word '+re.search('BEGINNING|EARLY|MID|LATE|END',year_string).group()+' found in string.'
                        res+=', Ranged epoch with  "CENTURY" keyword detected , parsing according to range rules'
                        return res
                    else:
                        if crosses_bc_ad_boundary(year_string):
                            exp=year_string.split('-')
                            ed=int(re.search('\d+',exp[0]).group())*-1
                            ld=int(re.search('\d+',exp[1]).group())
                            return ed,ld
                        res=start_date_parse(re.sub('AD|A.D.','',year_string))
                        return res

            elif bool(is_bc_date.search(year_string)):
                bc_ad=crosses_bc_ad_boundary(year_string)
                if bc_ad:
                    exp=year_string.split('-')
                    ed=int(re.search('\d+',exp[0]).group())*-1
                    ld=int(re.search('\d+',exp[1]).group())
                    return ed,ld
                exp=year_string.split('-')
                ed=int(re.search('\d+',exp[0]).group())*-1
                ld=int(re.search('\d+',exp[1]).group())*-1
                logic_string+='BC/AD Format detected,parsing to negative/positive numeric date accordingly'
                return ed,ld,logic_string




        else:
            # logic_string='No specific range format detected, applying simple range parser'
            return parse_ranges(date_string)

    elif contains_dots_with_year:
        logic_string='Date with dots detected,parsing to numeric format'
        get_year=re.sub('\d+\.\d+\.|\d+\.','',date_string)
        return get_year,get_year,logic_string

    # elif contains_canadian_format:
    #     years=date_string.split('-')
    #     ed=re.sub('\D+','',years[0])
    #     ld=re.sub('\D+','',years[1])
    #     if ed=='':
    #         ld='-'+ld
    #         ed=ld
    #     return ed,ld




    elif is_range(year_string)==None and bool(re.search('\d+S$',date_string))==True:
            date_string=date_string.replace('S','')
            date_string=re.sub('\D+','',date_string)
            z_count=date_string.count('0')
            trailing_z=''
            trailing_n=''
            for c in range(z_count):
                trailing_z+='0'
                trailing_n+='9'
            ed=date_string[:-z_count]+trailing_z
            ld=date_string[:-z_count]+trailing_n
            return ed,ld,'"s" found appended to '+input_string+'. Parsing into ED/LD'

    elif contains_forward_slash:
        date_string=date_string.split('/')
        if len(date_string[0].strip())==len(date_string[1].strip()):
            ed=date_string[0]
            ld=date_string[1]
        else:
            ed=date_string[0]
            ld=date_string[0][:(len(date_string[0])-len(date_string[1]))]+date_string[1]
        return ed,ld,'"/" found in '+input_string+' converting accordingly'
    elif contains_complex_epoch:
        years=re.split(',|-|/',date_string)
        t_ed=[]
        t_ld=[]
        epochs=[]
        for y in years:
            if bool(re.search('\d+',y)):
                if bool(re.search('BEGINNING|EARLY|MID|LATE|END',y)):
                    edo,ldo,logic=adjust_for_special_words(y)
                    t_ed.append(edo)
                    t_ld.append(ldo)
                else:
                    t_ed.append(0)
                    t_ld.append(0.99)

            epochs.append(re.sub('\D+','',y))

        if len(t_ed)<2 and len(t_ld)<2:
            ed=(int(epochs[0])-1)*calculate_year_multiplier(years[0]+' CENTURY')+(100*t_ed[0])
            ld=(int(epochs[1])-1)*calculate_year_multiplier(years[1])+(100*t_ld[0])
            ed=int(ed)
            ld=int(ld)
            logic_string='Complex epoch with '+logic+ ' detected in '+input_string
        else:
            ed=(int(epochs[0])-1)*calculate_year_multiplier(years[0]+' CENTURY')+(100*t_ed[0])
            ld=(int(epochs[1])-1)*calculate_year_multiplier(years[1])+(100*t_ld[-1])
            ed=int(ed)
            ld=int(ld)
            logic_string='Century epoch found with range in '+input_string+'. Parsing to range.'

        if len(str(ed))<5 and len(str(ld))<5:
            return ed,ld,logic_string
        else:
            return '','','Unclear Format detected in ',year_string

    else:
        year =re.sub('\D+', '', year_string)
        if len(year)>4:
            ed=year[0:(len(year)/2)]
            ld=year[(len(year)/2):]
            return '','','Unclear Format detected in ',year_string
        else:
            if date_string.find('CENTURY')!=-1:
                year=re.search('\d+[A-Z][A-Z]CENTURY',date_string.replace(' ','')).group()
                year=re.sub('\D+', '', year)
            year=int(year)
            year *= calculate_year_multiplier(date_string)
            if calculate_year_multiplier(date_string) == 100:
                check_for_special_dates=bool(re.search('BEGINNING|EARLY|MID|LATE|END',date_string))
                quarter,ls=adjust_for_quarters(date_string)
                logic_string+=ls+' Simple epoch detected in '+year_string

                if check_for_special_dates:
                    t_ed=[]
                    t_ld=[]
                    years=date_string.split(',')
                    years=[x for x in years if x.strip() is not '']
                    # print check_for_special_dates,date_string,years
                    for y in years:
                        edo,ldo,logic=adjust_for_special_words(y)
                        t_ed.append(edo)
                        t_ld.append(ldo)
                    # print t_ed,t_ld
                    if len(t_ed)<2 and len(t_ld)<2:
                        if not is_bc(date_string):
                            return int((year-100)+(100*t_ed[0])),int((year-100)+(100*t_ld[0])),logic_string+' '+logic
                        else:
                            return int(((int(year)) * -1)+(100*t_ed[0])), int(((int(year)) * -1)+(100*t_ld[0])),logic_string+' '+logic

                    else:
                        if t_ed[-1]!=0 and t_ld[-1]!=0:
                            if not is_bc(date_string):
                                return int((year-100)+(100*t_ed[0])),int((year-100)+(100*t_ld[-1])),logic_string+' '+logic
                            else:
                                return int(((int(year)) * -1)+(100*t_ed[0])), int(((int(year)) * -1)+(100*t_ld[-1])),logic_string+' '+logic
                        else:
                            if not is_bc(date_string):
                                return int((year-100)+(100*t_ed[0])),int((year-100)+(100*t_ld[0])),logic_string+' '+logic
                            else:
                                return int(((int(year)) * -1)+(100*t_ed[0])), int(((int(year)) * -1)+(100*t_ld[0])),logic_string+' '+logic
                else:
                    if ls.find('Quarter')!=-1:
                        return quarter + year - 100, quarter + year - 100+25,logic_string
                    elif ls.find('HALF')!=-1:
                        if quarter==0:
                            return year - 100, year - 50,logic_string
                        else:
                            return quarter+year - 100, year - 1,logic_string
                    else:
                        if not is_bc(date_string):
                            return year - 100, year - 1,logic_string
                        else:
                            return (int(year)) * -1, (int(year)-99) * -1,logic_string

            elif is_bc(date_string):
                if date_string.find('MILLION')==-1 and date_string.find('M')==-1 and calculate_year_multiplier(date_string)!=100:
                    year=re.sub('\D+','',date_string)
                    logic_string='BC date found,converting to negative numeric format'
                else:
                    million_digit=re.sub('\D+','',date_string)
                    year=int(million_digit)*1000000
                    logic_string='Million string detected,converting to negative numeric format'
                # print year,date_string
                return int(year) * -1, int(year) * -1,logic_string
            elif is_reverse_chronology(date_string):
                logic_string='Reverse Chronology format detected, converting to ED/LD'
                year = datetime.now().year - year
            return year, year,logic_string

def _contains_canadian_format(val):
    val=val.replace(' ','')
    canadians=re.compile(r'(CA\.)\d+(-)(CA\.)\d+|(CA\.)-\d+-(CA\.)')
    return bool(canadians.search(val))
def _contains_epoch_with_hyp(val):
    val=val.replace(' ','')
    contains_epoch_with_hyp=re.compile(r'[A-Z]+\d+[A-Z][A-Z](CENTURY-)[A-Z]+\d+[A-Z][A-Z](CENTURY)|'
                                       r'[A-Z]+(-\d+[A-Z][A-Z]CENTURY)|'
                                       r'[A-Z]+(-[A-Z]+\d+[A-Z][A-Z]CENTURY)|'
                                       r'[A-Z]+(-\d+[A-Z]+\d+[A-Z]+CENTURY)|'
                                       r'([A-Z]+-+)+[A-Z]+\d+\D+CENTURY|'
                                       r'[A-Z]+\d+[A-Z][A-Z](-[A-Z]+\d+[A-Z][A-Z]CENTURY)|'
                                       r'\d+(-)\d+(AD|BC|A.D.|B.C.)|'
                                       r'\d+(AD|BC)-\d+(AD|BC)')
    # print val, contains_epoch_with_hyp.search(val).group()
    return bool(contains_epoch_with_hyp.search(val))

def adjust_for_special_words(year_s):
    s_list=dict(BEGINNING='0-0.33',EARLY='0-0.33',MID='0.33-0.67',LATE='0.67-0.99',END='0.67-0.99')
    ted=''
    tld=''
    for s in s_list.keys():
        if year_s.find(s)!=-1:
            ted=float(s_list[s].split('-')[0])
            tld=float(s_list[s].split('-')[1])
            logic_string='Special Word '+s+' found, adjusting to '+s_list[s]+' accordingly'
    if ted=='':
        ted=0
        tld=0
        logic_string=''
    return ted,tld,logic_string


def _contains_dots_with_year(val):
    dots=re.compile(r'\d+[.]\d+[.]\d+|\d+[.]\d+')
    return bool(dots.search(val))
def _ends_with_s(val):
    endswith_s=re.compile(r'\d+(S-)\d+(S)|\d+(S)')
    return bool(endswith_s.search(val))

def _contains_forward_slash(val):
    forward_slash=re.compile(r'\d+(/)\d+|\d+\s+(/)\s+\d+')
    return bool(forward_slash.search(val))

def _contains_date_with_words_and_hyp(val):
    contains_date_with_words_and_hyp=re.compile(r'\d+(-)\d+[A-Z]+\d+|^\d+[A-Z]+\d+$|\D+\d+(-)\d+|\D+\d+-\D+\d+|\d+(-)\D+\d+')
    return bool(contains_date_with_words_and_hyp.search(val))


def is_bc(date_string):
    return re.search('^-|BC|B\.C\.|BCE|MILLION|M\.', date_string)

def is_reverse_chronology(date_string):
    return re.search('BP|YEARS AGO', date_string)

def calculate_year_multiplier(date_string):
    million = re.search('MILLION|M\.', date_string)
    # century = re.search('CENT$| C. $| C $|C$|CENTURY$', date_string)
    century = re.search('CENT$| C. $|CENTURY', date_string)
    if million:
        return 1000000
    elif century:
        return 100
    else:
        return 1

def is_range(date_string):
    # print re.search('.+-.+|;|\sAND\s|\sTO\s', date_string).group()
    return re.search('.+-.+|;|\sAND\s|\sTO\s', date_string)
    
def parse_ranges(date_string):
    """Split date ranges based on: (-,;,and,to)"""
    # print date_string
    start, end = re.split('-|;|\sAND\s|\sTO\s', date_string)

    start=re.sub(r'\D+','',start)
    end=re.sub(r'\D+','',end)
    if start=='':
        end='-'+end
        start=end
    if int(end) < 100 and len(start)!=len(end):
        end = (int(start[:2]) * 100) + int(end)

    if is_bc(date_string):
        return -int(start), -int(end),'Numeric year range detected in '+date_string

    return int(start), int(end),'Numeric year range detected in '+date_string

def crosses_bc_ad_boundary(date_string):
    if is_bc(date_string):
        if re.search(r'AD|A\.D\.', date_string) is not None:
            return True
    return False

def _is_month_day_year_format(date_string):
        try:
            parser.parse(date_string)
            return True
        except:
            return False
    # return re.search('\d{1,2}/\d{1,2}/\d{2,4}', date_string)


def find_date(string):
    # print string,'find_date'
    dateString=parser.parse(string,fuzzy=True)
    year = dateString.year
    # month = dateString.month
    # day = dateString.day
    # return (year, month, day)
    # print year
    return year


        # string = reduce_string(string)

    # return None

def reduce_string(string):
    i = len(string) - 1
    while string[i] >= '0' and string[i] < '9':
        i -= 1
    while string[i] < '0' or string[i] > '9':
        i -= 1
    return string[:i + 1]

def adjust_for_quarters(date_string):
    date_string=date_string.replace(' ','')
    if re.search('2NDQUARTER|SECONDQUARTER', date_string):
        return 25,'Quarter keyword found'

    elif re.search('1STQUARTER|FIRSTQUARTER', date_string):
        return 0,'Quarter keyword found'

    elif re.search('3RDQUARTER|THIRDQUARTER', date_string):
        return 50,'Quarter keyword found'
    elif re.search('4THQUARTER|FOURTHQUARTER', date_string):
        return 75,'Quarter keyword found'
    elif re.search('1STHALF|FIRSTHALF', date_string):
        return 0,'HALF keyword found'
    elif re.search('2NDHALF|SECONDHALF', date_string):
        return 50,'HALF keyword found'
    else:
        return 0,''


def remove_string_elems(string):
    string=string.split(',')
    string[0]=re.sub('\D+','',string[0])
    string[1]=re.sub('\D+','',string[1])
    return string[0],string[1]


def out_of_the_box_cases(date_string):
    date_string=date_string.replace(' ','')
    accept_list=['EARLY','MID','LATE','BEGINNING','END','STCENTURY','NDCENTURY','THCENTURY']
    components=re.split(';|,|\.',date_string)
    date_vals=[]
    for comp in components:
        comp_string=''
        for words in accept_list:
            if comp.find(words)!=-1:
                comp_string=re.sub('\D+','',comp)
                comp_string+=words
        if comp_string!='':
            comp_string=start_date_parse(comp_string)
            ed,ld=remove_string_elems(comp_string)
            date_vals.append(int(ed))
            date_vals.append(int(ld))
        else:
            if(bool(re.search('\d+',comp))):
                comp=re.sub('\D+','',comp)
                comp_string=start_date_parse(comp)
                ed,ld=remove_string_elems(comp_string)
                date_vals.append(int(ed))
                date_vals.append(int(ld))



    # print date_vals
    ed=sorted(date_vals)[0]
    ld=sorted(date_vals)[-1]
    return ed,ld,'Multiple dates found,selecting lowest and highest values for ed/ld'








# if __name__ == "__main__":
#     tests = ["2004",\
#         "1920 C.E.",\
#         "19th Century",\
#         "400BC",\
#         "1 million years ago",\
#         "30 years ago",\
#         "1920-25",\
#         "1920-1925",\
#         "1920 to 1965",\
#         "1320-45",\
#         "1926-32",\
#         "unknown, possibly 1st century",\
#         "late 7th century",\
#         "early 8th century",\
#         "late 7th, early 8th century",\
#         "600BC",\
#         "20th century model of 17th century dwelling",\
#         "1926-32",\
#         "ca. 1870, 1892, 1898, 1941",\
#         # "Construction began on June 24, 1939 (opening ceremony March 24, 1940)",\
#         "1920s",\
#         "1938/47",\
#         "01 March1912",\
#         "1650-1660",\
#         "1847-48",\
#         "20-May-1918",\
#         "7-8 December 1868",\
#         "19th century",\
#         "01 March 2014",\
#         "600/47",\
#         "1920?",\
#         "late 19th century-early 20th century",\
#         "early to mid 19th century",\
#         "l875-1897",\
#         "mid-to-late 18th century",\
#         "600-700 AD",\
#         "180-145 BC",\
#         "Feb 1916-Sep1917",\
#         "1915-Feb 1916",\
#         "11.12.1868",\
#         "ca. -3000 - ca.",\
#         "ca. 1500 - ca. 1600",\
#         "ca. -2000 - ca. -1000",\
#         "3 BC - 6 AD",\
#         "Jan 26, 1960",\
#         "mid-3rd century",\
#         "8th-9th century BC",\
#         "9TH,8THCENTURY",\
#         "A.D. 918-1392",\
#         "1956, printed 1979",\
#         "designed 1951; made 1953",\
#         "designed 1945-46, made 1946-47",\
#         "designed 1948-50; made about 1950-53",\
#         "designed 1951-52; made 1953-about 1960",\
#         "first half of 20th century",\
#         "5th-3rd century B.C.",\
#         "1860s-70s",\
#         "Late 18th Century",\
#         "2002-03",\
#         "October 21, 1999 - January 21, 2000",\
#         "about 1903-08",\
#         "6th Century B.C.",\
#         "1/15/1938",\
#         "late 6th century BC",\
#         "July 1, 1941"
#         # "3rd quarter of the 18th century",\
#         # "Original construction in the 13th or 14th century; Damaged in the 17th century and rebuilt in the last quarter of the 17th century."
#
#     ]


def start_date_parse(date_string):
    result=parse_date(date_string)
    return str(result)





# f=open('/Users/naveed/Documents/Preloader demo/MFABostonAddl_L02_PL20120204_enhanced_legal_qc.csv','rU')
# fr=open('/Users/naveed/Documents/Preloader demo/MFABostonAddl_L02_PL20120204_enhanced_legal_qc-test.csv','a')
# csv_reader=csv.DictReader(f,delimiter=',')
# csv_writer=csv.writer(fr,delimiter=',')
# i=0
# all_forms=[]
# for row in csv_reader:
#     new_row=[]
#     i+=1
#     print i
#     if row['Object Date'].strip()!='':
#         print "input: %s"%row['Object Date']
#         if row['Object Date'] not in all_forms:
#             all_forms.append(row['Object Date'])
#             new_row.append(row['Object Date'])
#             try:
#                 print "output:",start_date_parse(row['Object Date'])
#                 new_row.append(start_date_parse(row['Object Date']))
#             except:
#                  print "exception!"
#                  new_row.append('exception')
#             print ""
#             csv_writer.writerow(new_row)


# for test in tests:
#     print "input: %s"%test
#     print "output:", start_date_parse(test)
#     # try:
#     #     print "output:", start_date_parse(test)
#     # except:
#     #     print "exception"
#     print ""




"""
Comments

UUID: 224a1895-050c-4ae4-9ec6-0927b4bf89b5; SSID: 4902416
Date=20th century model of 17th century dwelling
Earliest Date=null
Latest Date=null.

They are migrated to SS IMATA as below:
Date=20th century model of 17th century dwelling
Earliest Date=2017 (1600)
Latest Date=2017  (1699)

UUID: a1354011-f67c-458c-b196-7587efc20b3d; SSID: 4884003
Date=ca. 1870, 1892, 1898, 1941
Earliest Date=null
Latest Date=null.

They are migrated to SS IMATA as below:
Date=ca. 1870, 1892, 1898, 1941
Earliest Date=1870189218981941 (1870)
Latest Date=1870189218981941  (1941)

UUID: ad53d2bb-8e82-44da-a9ed-ccc4f1cf5943; SSID: 4904579
Date=Construction began on June 24, 1939 (opening ceremony March 24, 1940)
Earliest Date=null
Latest Date=null.

They are migrated to SS IMATA as below:
Date=Construction began on June 24, 1939 (opening ceremony March 24, 1940)
Earliest Date=241939241940 (1939)
Latest Date=241939241940 (1940)"""
