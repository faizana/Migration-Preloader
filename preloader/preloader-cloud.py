import cherrypy
from cherrypy.lib import static
import os
from dateutil.parser import parser
#from date_parser import start_date_parse
import csv
import simplejson
import os
import uuid
from multiprocessing import Process,Queue
import HTMLParser
import Queue as lq

htparser=HTMLParser.HTMLParser()
active_keys=[]
geography_map='controlled_list_map/country.csv'
classification_map='controlled_list_map/classification.csv'
global_status={}
conversion_queue=Queue()
result_paths_dict={}
# process_queue=lq.LifoQueue(maxsize=0)
process_queue=Queue(maxsize=0)
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
class preloader_interface(object):

#    def run_simple_date_parser(self,date_string):
        # print date_string
        # date_string=str(date_string)
#        result=start_date_parse(date_string)
#        return result
#    run_simple_date_parser.exposed=True


    def get_artstor_country_list(self,page,start,limit,_dc):
        geo_file=open(geography_map,'rU')
        geo_csv=csv.DictReader(geo_file,delimiter=',',dialect=csv.excel_tab)
        json_row=[]
        for row in geo_csv:
            # print type(row['Complete List of Nations'])
            try:
                json_row.append(dict(countryName=row['Source Geography Term'].decode('utf-8').strip(),tgn_id=row['TGN ID'].decode('utf-8').strip(),region1=row['Artstor Geography Term'].decode('utf-8').strip()))
            except:
                print row['Source Geography Term'],row['TGN ID'],row['Artstor Geography Term']

        response=simplejson.dumps(dict(countrydata=json_row,total=len(json_row)))
        return response

    get_artstor_country_list.exposed=True

    def get_artstor_class_list(self,page,start,limit,_dc):
        class_file=open(classification_map,'rU')
        class_csv=csv.DictReader(class_file,delimiter=',',dialect=csv.excel_tab)
        json_row=[]
        for row in class_csv:
            # print type(row['Complete List of Nations'])
            try:
                json_row.append(dict(countryName=row['Keyword'].decode('utf-8').strip(),tgn_id=row['Artstor Classification Term'].decode('utf-8').strip(),region1=row['AAT ID'].decode('utf-8').strip()))
            except:
                print row['Keyword'],row['TGN ID'],row['Artstor Classification Term']

        response=simplejson.dumps(dict(countrydata=json_row,total=len(json_row)))
        return response

    get_artstor_class_list.exposed=True


    def upload_csv(self,csvFile,category,validate_column,id_column):
        global active_keys
        out = """<html>
        <body>
            zipFile length: %s<br />
            zipFile filename: %s<br />
            zipFile mime-type: %s <br />

        </body>
        </html>"""

        # Although this just counts the file length, it demonstrates
        # how to read large files in chunks instead of all at once.
        # CherryPy reads the uploaded file into a temporary file;
        # myFile.file.read reads from that.
        size_csv = 0
        csv_data=''

        while True:
            data_zip= csvFile.file.read(8192)


            if not data_zip:
                break
            csv_data+=data_zip
            size_csv += len(data_zip)

            # print 'Success',size_xlsx
        # xsltFile,xlsxFile=unzip_files(zip_data)
        csv_file,csv_ref=self.save_csv(csv_data)
        # csv_path=os.path.abspath(csv_file)
        csv_ref=csv_ref.replace('.csv','')
        print 'key: ',csv_ref
        # print 'input_xlsx',xlsxFile,xsltFile
        # json_resp=simplejson.dumps(xls_to_dict(xlsxFile,xsltFile,username,password,newtransaction))

        global_status[csv_ref]={}
        global_status[csv_ref]['csv_path']=csv_file
        global_status[csv_ref]['total_rows']=self.get_total_rows(csv_file)
        active_keys.append(csv_ref)
        conversion_queue.put(global_status)
        # clear_queue()


        mapping_proc=Process(target = self.start_validation , args = (conversion_queue,process_queue,csv_ref,category,validate_column,id_column,geography_map,classification_map))
        mapping_proc.start()
        # mapping_proc.join()
        return simplejson.dumps(dict(success=True,message="Validation successfully started for "+csvFile.filename,csv_ref=csv_ref))
    upload_csv.exposed = True

    def get_mapping_status(self,csv_ref):
        global global_status
        global active_keys

        # print '\n mapping:',simplejson.dumps(process_queue.get()),process_queue.empty()
        if process_queue.empty()==False:
            mapping_status=process_queue.get()
            if csv_ref in mapping_status.keys():
                return return_resp(mapping_status,csv_ref)
                # data_obj=convert_dict_to_list(mapping_status[csv_ref]['result'])
                # if len(mapping_status[csv_ref]['result'].keys())<global_status[csv_ref]['total_rows']-1:
                #     return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='IN-PROGRESS'))
                # else:
                #     active_keys.remove(csv_ref)
                #     return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='COMPLETED'))
            elif csv_ref not in mapping_status.keys() and active_keys.index(csv_ref)==-1:
                response=mapping_status.keys()
                return simplejson.dumps(dict(message='The job you requested could not be found',code='NOT-FOUND',keys=response))
            elif csv_ref not in mapping_status.keys() and active_keys.index(csv_ref)!=-1:
                 mapping_status=process_queue.get()
                 while csv_ref not in mapping_status.keys():
                    mapping_status=process_queue.get()
                 return return_resp(mapping_status,csv_ref)


        else:
            return simplejson.dumps(dict(message='No jobs in process or completed',code='QUEUE-EMPTY'))
    get_mapping_status.exposed=True

    def download_report(self,csv_ref):
        global result_paths_dict
        path = result_paths_dict[csv_ref]['report']
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))
    download_report.exposed = True

    def download_csv(self,csv_ref):
        global result_paths_dict
        path = result_paths_dict[csv_ref]['csv']
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))
    download_csv.exposed = True

    def get_total_rows(self, csv_file):
        rows=''
        with open(csv_file,'rU') as fin:
            csvin = csv.reader(fin)
            rows = sum(1 for row in csvin)
            fin.close()
        return rows




    def save_csv(self,csv_data):
        filename=str(uuid.uuid4())+'.csv'
        csv_file=open('/home/ana/faizan/preloader_csvs/'+filename,'w')
        csv_file.write(csv_data)
        csv_file.close()
        csv_file=os.path.abspath('/home/ana/faizan/preloader_csvs/'+filename)
        return csv_file,filename

    def generate_country_dict(self,csv_dict):
        country_term_dict={}
        country_id_dict={}
        for row in csv_dict:
            country_term_dict[row['Source Geography Term'].lower()]=dict(artstor_term=row['Artstor Geography Term'],tgn_id=row['TGN ID'])
            country_id_dict[row['TGN ID']]=dict(artstor_term=row['Artstor Geography Term'],source_term=row['Source Geography Term'])
        return country_term_dict,country_id_dict


    def start_validation(self,conversion_queue,process_queue,csv_ref,category,validate_column,id_column,geography_map,classification_map):
        global_status=conversion_queue.get()
        csv_path=global_status[csv_ref]['csv_path']
        csv_file=open(csv_path,'rU')
        csv_dict=csv.DictReader(csv_file,delimiter=',')
        mapping_status={}
        result_dict={}
        if category=='Country':
            geography_map=open(geography_map,'rU')
            geography_map=csv.DictReader(geography_map,delimiter=',',dialect=csv.excel_tab)
            country_term_dict,country_id_dict=self.generate_country_dict(geography_map)
            c=0
            mapping_status[csv_ref]={}
            for row in csv_dict:
                result_dict[row[id_column]]={}
                c+=1
                sm=0
                query_val=row[validate_column].split(',')
                # print 'counter',c
                for qv in query_val:

                    # print qv
                    if qv.strip()!='' and qv.isdigit()==True and qv.strip() in country_id_dict.keys():
                        result_dict[row[id_column]]['query_term']=' '.join(query_val)
                        result_dict[row[id_column]]['artstor_country']=country_id_dict[qv]['artstor_term']
                        result_dict[row[id_column]]['tgn_id']=qv
                        result_dict[row[id_column]]['source_term']=country_id_dict[qv]['source_term']
                        result_dict[row[id_column]]['status']='Matched'
                        sm=1
                        break
                        # continue

                    elif qv.strip()!='' and qv.isdigit()==False and qv.lower().strip() in country_term_dict.keys():

                        result_dict[row[id_column]]['query_term']=' '.join(query_val)

                        result_dict[row[id_column]]['artstor_country']=country_term_dict[qv.lower().strip()]['artstor_term']

                        result_dict[row[id_column]]['tgn_id']=country_term_dict[qv.lower().strip()]['tgn_id']

                        result_dict[row[id_column]]['status']='Matched'

                        sm=1
                        break
                        # continue

                if sm==0 and query_val[0]!='':
                    result_dict[row[id_column]]['status']='Not Matched'
                    result_dict[row[id_column]]['query_term']=' '.join(query_val)
                elif sm==0 and query_val[0]=='':
                    result_dict[row[id_column]]['status']='null'
                    result_dict[row[id_column]]['query_term']=''


                # global_status[csv_ref]['result']=result_dict
                mapping_status[csv_ref]['result']=result_dict
                mapping_status[csv_ref]['category']=category
                if 'artstor country' in [x.lower().strip() for x in row.keys() if x is not None]:
                    mapping_status[csv_ref]['converted_csv']=write_modified_csv(row,result_dict[row[id_column]],os.path.basename(csv_path),category,c,validate_column)
                else:
                    mapping_status[csv_ref]['converted_csv']=False
                process_queue.put(mapping_status)
        elif category=='Classification':
            classification_map=open(classification_map,'rU')
            classification_map=csv.DictReader(classification_map,delimiter=',',dialect=csv.excel_tab)
            class_term_dict=self.generate_class_dict(classification_map)
            c=0
            mapping_status[csv_ref]={}
            for row in csv_dict:
                result_dict[row[id_column]]={}
                c+=1
                sm=0
                query_val=row[validate_column].split(',')
                for qv in query_val:
                    # print qv.strip(),class_term_dict.keys()
                    if qv.strip()!='' and qv.strip().lower() in class_term_dict.keys():
                        result_dict[row[id_column]]['query_term']=' '.join(query_val)
                        result_dict[row[id_column]]['artstor_classification']=class_term_dict[qv.lower().strip()]['artstor_term']
                        result_dict[row[id_column]]['status']='Matched'
                        sm=1
                        break
                if sm==0 and query_val[0]!='':
                    result_dict[row[id_column]]['status']='Not Matched'
                    result_dict[row[id_column]]['query_term']=' '.join(query_val)
                elif sm==0 and query_val[0]=='':
                    result_dict[row[id_column]]['status']='null'
                    result_dict[row[id_column]]['query_term']=''

                mapping_status[csv_ref]['result']=result_dict
                mapping_status[csv_ref]['category']=category
                if 'artstor classification' in [x.lower().strip() for x in row.keys() if x is not None]:
                    mapping_status[csv_ref]['converted_csv']=write_modified_csv(row,result_dict[row[id_column]],os.path.basename(csv_path),category,c,validate_column,id_column)
                else:
                    mapping_status[csv_ref]['converted_csv']=False
                process_queue.put(mapping_status)







        print 'succesful end of validation',len(result_dict.keys())

    def generate_class_dict(self,csv_dict):
        class_term_dict={}
        for row in csv_dict:
            class_term_dict[row['Keyword'].lower()]=dict(artstor_term=row['Artstor Classification Term'])
        return class_term_dict


def rearrange_columns(hl,vc,idc,category):
    removed=False
    if category=='Country':
        hl.remove(idc)
        hl.remove(vc)
        if 'Artstor Country' in hl:
            removed=True
            hl.remove('Artstor Country')
        hl.sort()
        if removed:
            hl.insert(0,'Artstor Country')
        hl.insert(0,vc)
        hl.insert(0,idc)
        return hl
    elif category=='Classification':
        hl.remove(idc)
        hl.remove(vc)
        if 'Artstor Classification' in hl:
            removed=True
            hl.remove('Artstor Classification')
        hl.sort()
        if removed:
            hl.insert(0,'Artstor Classification')
        hl.insert(0,vc)
        hl.insert(0,idc)
        return hl

def write_modified_csv(row,rd,fname,category,counter,vc,idc):
    f_path='/home/ana/faizan/preloader_csvs/converted_csvs/'+'converted-'+fname
    f=open(f_path,'a')
    csv_writer=csv.writer(f,dialect='excel',delimiter=',')
    hl=row.keys()
    if counter==1:
        #hl=rearrange_columns(hl,vc,idc,category)
        csv_writer.writerow(hl)
    new_row=[]
    if category=='Country':
        for heads in hl:
            if heads.lower().strip()=='artstor country' and 'artstor_country' in rd.keys():
                new_row.append(rd['artstor_country'])
            else:
                new_row.append(row[heads])
        # for k,v in row.items():
        #     if k.lower().strip()=='artstor country' and 'artstor_country' in rd.keys():
        #         new_row.append()
        #     else:
        #         new_row.append(v)

    elif category=='Classification':
         for heads in hl:
            if heads.lower().strip()=='artstor classification' and 'artstor_classification' in rd.keys():
                new_row.append(rd['artstor_classification'])
            else:
                new_row.append(row[heads])

    csv_writer.writerow(new_row)
    return os.path.abspath(f_path)


def convert_dict_to_list(dt):
    dictlist=[]
    temp=''
    for k,v in dt.items():
        temp = [k,v]
        dictlist.append(temp)
    return dictlist

def return_resp(mapping_status,csv_ref):
    global active_keys
    global result_paths_dict
    data_obj=convert_dict_to_list(mapping_status[csv_ref]['result'])
    if len(mapping_status[csv_ref]['result'].keys())<global_status[csv_ref]['total_rows']-1:
        return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='IN-PROGRESS'))
    else:
        result_paths_dict[csv_ref]={}
        active_keys.remove(csv_ref)
        result_file=generate_result_csv(data_obj,csv_ref,mapping_status[csv_ref]['category'])
        result_paths_dict[csv_ref]['report']=result_file
        result_paths_dict[csv_ref]['csv']=mapping_status[csv_ref]['converted_csv']
        result_csv_url='download_csv?csv_ref='+csv_ref
        if result_paths_dict[csv_ref]['csv']==False:
            result_csv_url=False
        return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='COMPLETED',result_file_url='download_report?csv_ref='+csv_ref,result_csv_url=result_csv_url))



def generate_result_csv(data_obj,csv_ref,category):
    path='/home/ana/faizan/preloader/result_file/'+csv_ref+'.csv'
    f=open(path,'a')
    csv_writer=csv.writer(f,delimiter=',')
    hl=[]
    if category=='Country':
        hl=['ID','Query Term','Logic','Status','Artstor Country','TGN ID']
        csv_writer.writerow(hl)
        for vals in data_obj:
            if vals[1]['status']=='Matched':
                id=vals[0]
                status=vals[1]['status']
                ac=vals[1]['artstor_country']
                qt=vals[1]['query_term']
                tgn_id=vals[1]['tgn_id']
                logic='An exact match of the term '+ac+' was found in the query term string'
            else:
                id=vals[0]
                status=vals[1]['status']
                ac=''
                qt=vals[1]['query_term']
                tgn_id=''
                logic=''
            csv_writer.writerow([id,qt,logic,status,ac,tgn_id])
    else:
        hl=['ID','Query Term','Logic','Status','Artstor Classification']
        csv_writer.writerow(hl)
        for vals in data_obj:
            if vals[1]['status']=='Matched':
                id=vals[0]
                status=vals[1]['status']
                ac=vals[1]['artstor_classification']
                qt=vals[1]['query_term']
                logic='The keyword '+qt+' maps directly to the term '+ac
            else:
                id=vals[0]
                status=vals[1]['status']
                ac=''
                qt=vals[1]['query_term']
                logic=''

            csv_writer.writerow([id,qt,logic,status,ac])


    # print data_obj[0]


        # csv_writer.writerow([id,status,ac,qt,tgn_id])
    return path






if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().

    cherrypy.quickstart(preloader_interface(), config=tutconf)

else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(preloader_interface(), config=tutconf)

