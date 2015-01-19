import re
from datetime import *
# # from dateutil import *
# from dateutil.tz import *
from dateutil import parser


def remove_syms(date_string):
    symbols=['?',';','<','>']

    for sym in symbols:
        date_string=date_string.replace(sym,'')
    return date_string


def parse_date(input_string):
    # date_string = input_string.upper().replace(' ','') #remove whitespaces
    date_string = input_string.upper()
    date_string = remove_syms(date_string)
    # print date_string
    # date_string=date_string.replace('?','')
    # date_string=date_string.replace('CIRCA','')
    # contains_s=_ends_with_s(date_string.replace(' ',''))
    is_month_day_year_format=_is_month_day_year_format(date_string)
    contains_forward_slash=_contains_forward_slash(date_string)
    # contains_date_with_words_and_hyp=_contains_date_with_words_and_hyp(date_string)
    year_string = re.sub(r'\d+,\s', '', date_string) # Jan 26, 1960
    year_string = re.sub(r'\d.+ QUARTER', '', date_string)
    # contains_epoch_with_hyp=_contains_epoch_with_hyp(year_string)
    contains_complex_epoch=bool(re.search('^.+\d+.+(,).+\d+.+(CENTURY)$',date_string))
    contains_dots_with_year=_contains_dots_with_year(date_string)
    # print 'is_range(year_string)',is_range(year_string),"bool(re.search('\d+S$',date_string))",bool(re.search('\d+S$',date_string))
    # contains_canadian_format=_contains_canadian_format(date_string)
    # print 'contains_dots_with_year',contains_dots_with_year
    # print is_month_day_year_format,contains_dots_with_year
    if is_month_day_year_format and contains_dots_with_year==False:
        pip_parser=find_date(date_string)
        return pip_parser,pip_parser

        #
    elif is_range(year_string) and bool(re.search('\D+',year_string.replace('-','')))==False: #and contains_epoch_with_hyp==False and year_string.count('-')<2 and contains_date_with_words_and_hyp==False and contains_s==False:
        # print ' bc yahan q atey hou'
        return parse_ranges(year_string)
    elif is_range(year_string) and bool(re.search('\D+',year_string.replace('-','')))==True:
        # print 'mkc'
        date_string = input_string.upper().replace(' ','') #remove whitespaces
        date_string=date_string.replace('?','')
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





        date_string=re.sub(r';|AND|TO','-',date_string)
        # print date_string
        contains_s=_ends_with_s(date_string.replace(' ',''))
        contains_date_with_words_and_hyp=_contains_date_with_words_and_hyp(date_string)
        contains_epoch_with_hyp=_contains_epoch_with_hyp(date_string)

        print contains_date_with_words_and_hyp,contains_epoch_with_hyp
        if contains_s:
            date_string=date_string.replace('S','')
            if date_string.find('-')!=-1:
                date_string=date_string.split('-')
                ed=date_string[0]
                z_count=date_string[1].count('0')
                trailing_n=''
                for c in range(z_count):
                    trailing_n+='9'
                ld=date_string[1][:-z_count]+trailing_n
                return ed,ld


            z_count=date_string.count('0')
            trailing_z=''
            trailing_n=''
            for c in range(z_count):
                trailing_z+='0'
                trailing_n+='9'
            ed=date_string[:-z_count]+trailing_z
            ld=date_string[:-z_count]+trailing_n
            return ed,ld


        elif contains_date_with_words_and_hyp:
            if bool(re.search('\D+\d+(-)\d+$',date_string)):
                ed,ld=start_date_parse(re.sub('[A-Z]+','',date_string))
                return ed,ld
            elif bool(re.search('^\D+\d+(-)\D+\d+$|^\d+(-)\D+\d+$',date_string)):
                ed=re.sub('\D+','',date_string.split('-')[0])
                ld=re.sub('\D+','',date_string.split('-')[1])
                return ed,ld

            get_regex=re.compile(r'\d+$')
            ed=get_regex.search(date_string).group()
            ld=ed
            return ed,ld
        elif contains_epoch_with_hyp:
            year_string=date_string.replace(' ','')
            print 'here'
            get_exact_string=re.compile(r'[A-Z]+\d+[A-Z][A-Z](CENTURY-)[A-Z]+\d+[A-Z][A-Z](CENTURY)')
            get_exact_string1=re.compile(r'[A-Z]+(-\d+[A-Z][A-Z]CENTURY)|[A-Z]+(-[A-Z]+\d+[A-Z][A-Z]CENTURY)|[A-Z]+(-\d+[A-Z]+\d+[A-Z]+CENTURY)|'
                                         r'([A-Z]+-+)+[A-Z]+\d+\D+CENTURY|\d+(-)\d+AD') #MID-19THCENTURY,MID-TOLATE19THCENTURY
            is_bc_date=re.compile(r'BC-|-BC|BC$')
            if bool(get_exact_string.search((year_string))):
                ed,ld=start_date_parse(get_exact_string.search(year_string).group().replace('-',','))
                return ed,ld
            elif bool(get_exact_string1.search((year_string))):
                # print year_string
                exp=re.search('\d+\D+(CENTURY)$|^\d+(-)\d+',year_string)
                ed,ld=start_date_parse(exp.group())
                return ed,ld
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
                return ed,ld




        else:
            return parse_ranges(date_string)

    elif contains_dots_with_year:
        get_year=re.sub('\d+\.\d+\.|\d+\.','',date_string)
        return get_year,get_year

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
            z_count=date_string.count('0')
            trailing_z=''
            trailing_n=''
            for c in range(z_count):
                trailing_z+='0'
                trailing_n+='9'
            ed=date_string[:-z_count]+trailing_z
            ld=date_string[:-z_count]+trailing_n
            return ed,ld

    elif contains_forward_slash:
        date_string=date_string.split('/')
        if len(date_string[0].strip())==len(date_string[1].strip()):
            ed=date_string[0]
            ld=date_string[1]
        else:
            ed=date_string[0]
            ld=date_string[0][:(len(date_string[0])-len(date_string[1]))]+date_string[1]
        return ed,ld
    elif contains_complex_epoch:
        years=date_string.split(',')
        epochs=[]
        for y in years:
            epochs.append(re.sub('\D+','',y))
        ed=(int(epochs[0])-1)*calculate_year_multiplier(years[0]+' CENTURY')
        ld=(int(epochs[1])-1)*calculate_year_multiplier(years[1])+99
        return ed,ld

    else:

        year = int(re.sub('\D+', '', year_string))
    year *= calculate_year_multiplier(date_string)
    if not is_bc(date_string) and calculate_year_multiplier(date_string) == 100:
        return adjust_for_quarters(date_string) + year - 100, year - 1
    elif is_bc(date_string):
        year=re.sub('\D+','',date_string)
        # print year,date_string
        return int(year) * -1, int(year) * -1
    elif is_reverse_chronology(date_string):
        year = datetime.now().year - year
    # elif contains_s:
    #     date_string=date_string.replace('S','')
    #     if date_string.find('-')!=-1:
    #         date_string=date_string.split('-')
    #         ed=date_string[0]
    #         z_count=date_string[1].count('0')
    #         trailing_n=''
    #         for c in range(z_count):
    #             trailing_n+='9'
    #         ld=date_string[1][:-z_count]+trailing_n
    #         return ed,ld
    #
    #
    #     z_count=date_string.count('0')
    #     trailing_z=''
    #     trailing_n=''
    #     for c in range(z_count):
    #         trailing_z+='0'
    #         trailing_n+='9'
    #     ed=date_string[:-z_count]+trailing_z
    #     ld=date_string[:-z_count]+trailing_n
    #     return ed,ld
    # elif contains_forward_slash:
    #     date_string=date_string.split('/')
    #     if len(date_string[0].strip())==len(date_string[1].strip()):
    #         ed=date_string[0]
    #         ld=date_string[1]
    #     else:
    #         ed=date_string[0]
    #         ld=date_string[0][:(len(date_string[0])-len(date_string[1]))]+date_string[1]
    #     return ed,ld
    # elif year_string.count('-')>=2:
    #     year_string=year_string.replace('-','')
    #     year_string = find_date(year_string)
    #     return year_string[0],year_string[0]
    # elif contains_date_with_words_and_hyp:
    #     get_regex=re.compile(r'\d+$')
    #     ed=get_regex.search(date_string).group()
    #     ld=ed
    #     return ed,ld
    # elif contains_epoch_with_hyp:
    #     get_exact_string=re.compile(r'[A-Z]+\d+[A-Z][A-Z](CENTURY-)[A-Z]+\d+[A-Z][A-Z](CENTURY)')
    #     get_exact_string1=re.compile(r'[A-Z]+(-\d+[A-Z][A-Z]CENTURY)|[A-Z]+(-[A-Z]+\d+[A-Z][A-Z]CENTURY)|[A-Z]+(-\d+[A-Z]+\d+[A-Z]+CENTURY)') #MID-19THCENTURY,MID-TOLATE19THCENTURY
    #     if bool(get_exact_string.search((year_string))):
    #         ed,ld=start_date_parse(get_exact_string.search(year_string).group().replace('-',','))
    #     elif bool(get_exact_string1.search((year_string))):
    #         exp=re.sub(r'^\D+\d+[A-Z][A-Z](CENTURY)$|^\D+\d+[A-Z]+\d+[A-Z]+(CENTURY)$',r'\d+[A-Z][A-Z](CENTURY)',year_string)
    #         ed,ld=start_date_parse(exp)
    #     return ed,ld








    return year, year

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
                                       r'\d+(-)\d+(AD|BC)|'
                                       r'\d+(AD|BC)-\d+(AD|BC)')
    # print val, contains_epoch_with_hyp.search(val).group()
    return bool(contains_epoch_with_hyp.search(val))

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
    century = re.search('CENT$| C. $| C $|C$|CENTURY$', date_string)
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
    print date_string
    start, end = re.split('-|;|\sAND\s|\sTO\s', date_string)
    # start=re.sub(r'\D+','',start)
    # end=re.sub(r'\D+','',end)
    if start=='':
        end='-'+end
        start=end
    if int(end) < 100:
        end = (int(start[:2]) * 100) + int(end)

    return int(start), int(end)
    
def crosses_bc_ad_boundary(date_string):
    if is_bc(date_string):
        if re.search(r'AD|A\.D\.|CE', date_string) is not None:
            return True
    return False

def _is_month_day_year_format(date_string):
        try:
            parser.parse(date_string,fuzzy=True)
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
    print year
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
    if re.search('2ND\sQUARTER|SECOND QUARTER', date_string):
        return 25
    elif re.search('3RD\sQUARTER|THIRD QUARTER', date_string):
        return 50
    elif re.search('4TH\sQUARTER|FOURTH QUARTER', date_string):
        return 75
    else:
        return 0
    

if __name__ == "__main__":
    tests = ["2004",\
        "1920 C.E.",\
        "19th Century",\
        "400BC",\
        "1 million years ago",\
        "30 years ago",\
        "3rd quarter of the 18th century",\
        "1920-25",\
        "1920-1925",\
        "1920 to 1965",\
        "1320-45",\
        "1926-32",\
        "unknown, possibly 1st century",\
        "late 7th century",\
        "early 8th century",\
        "late 7th, early 8th century",\
        "600BC",\
        "20th century model of 17th century dwelling",\
        "1926-32",\
        "ca. 1870, 1892, 1898, 1941",\
        "Construction began on June 24, 1939 (opening ceremony March 24, 1940)",\
        "1920s",\
        "1938/47",\
        "01 March1912",\
        "1650-1660",\
        "1847-48",\
        "20-May-1918",\
        "7-8 December 1868",\
        "19th century",\
        "01 March 2014",\
        "600/47",\
        "1920?",\
        "late 19th century-early 20th century",\
        "early to mid 19th century",\
        "l875-1897",\
        "mid-to-late 18th century",\
        "600-700 AD",\
        "180-145 BC",\
        "Feb 1916-Sep1917",\
        "1915-Feb 1916",\
        "11.12.1868",\
        "ca. -3000 - ca.",\
        "ca. 1500 - ca. 1600",\
        "ca. -2000 - ca. -1000",\
        "3 BC - 6 AD"

    ]


def start_date_parse(date_string):
    result=parse_date(date_string)
    return str(result)






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
