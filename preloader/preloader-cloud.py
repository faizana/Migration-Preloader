import cherrypy
from cherrypy.lib import static
import os
from dateutil.parser import parser
from date_parser import start_date_parse
import csv
import simplejson
import os
import uuid
from multiprocessing import Process,Queue
import HTMLParser
import Queue as lq
import traceback

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.response import FileResponse
from paste.httpserver import serve


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

@view_config(route_name='artstor_country_list', renderer='json')
def get_artstor_country_list(request):
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
        return Response(response)

@view_config(route_name='artstor_class_list', renderer='json')
def get_artstor_class_list(request):
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
        return Response(response)

@view_config(route_name='upload_csv', renderer='json')
def upload_csv(request):
        global active_keys
        filename=request.POST['csvFile'].filename
        input_file = request.POST['csvFile'].file
        input_file.seek(0)
        csv_data=''
        while True:
            data = input_file.read(2<<16)
            if not data:
                break
            csv_data+=data



        csv_file,csv_ref=save_csv(csv_data)
        csv_ref=csv_ref.replace('.csv','')
        print 'key: ',csv_ref
        # print 'input_xlsx',xlsxFile,xsltFile
        # json_resp=simplejson.dumps(xls_to_dict(xlsxFile,xsltFile,username,password,newtransaction))

        global_status[csv_ref]={}
        global_status[csv_ref]['csv_path']=csv_file
        global_status[csv_ref]['total_rows']=get_total_rows(csv_file)
        active_keys.append(csv_ref)
        conversion_queue.put(global_status)
        # clear_queue()
        category=request.POST['category']
        validate_column=request.POST['validate_column']
        id_column=request.POST['id_column']


        mapping_proc=Process(target = start_validation , args = (conversion_queue,process_queue,csv_ref,category,validate_column,id_column,geography_map,classification_map))
        mapping_proc.start()
        # mapping_proc.join()
        response=simplejson.dumps(dict(success=True,message="Validation successfully started for "+filename,csv_ref=csv_ref))
        return Response(response)

@view_config(route_name='get_mapping_status', renderer='json')
def get_mapping_status(request):
        global global_status
        global active_keys
        csv_ref=request.matchdict['csv_ref']
        # print '\n mapping:',simplejson.dumps(process_queue.get()),process_queue.empty()
        if process_queue.empty()==False:
            mapping_status=process_queue.get()
            if csv_ref in mapping_status.keys():
                return Response(return_resp(mapping_status,csv_ref))
                # data_obj=convert_dict_to_list(mapping_status[csv_ref]['result'])
                # if len(mapping_status[csv_ref]['result'].keys())<global_status[csv_ref]['total_rows']-1:
                #     return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='IN-PROGRESS'))
                # else:
                #     active_keys.remove(csv_ref)
                #     return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='COMPLETED'))
            elif csv_ref not in mapping_status.keys() and active_keys.index(csv_ref)==-1:
                response=mapping_status.keys()
                return Response(simplejson.dumps(dict(message='The job you requested could not be found',code='NOT-FOUND',keys=response)))
            elif csv_ref not in mapping_status.keys() and active_keys.index(csv_ref)!=-1:
                 mapping_status=process_queue.get()
                 while csv_ref not in mapping_status.keys():
                    mapping_status=process_queue.get()
                 return Response(return_resp(mapping_status,csv_ref))


        else:
            return Response(simplejson.dumps(dict(message='No jobs in process or completed',code='QUEUE-EMPTY')))  
            
@view_config(route_name='download_report', renderer='json')
def download_report(request):
        global result_paths_dict
        csv_ref=request.matchdict['csv_ref']
        path = result_paths_dict[csv_ref]['report']
        response = FileResponse(
        path,
        request=request,
        content_type='text/csv'
        )
        return response

        # return static.serve_file(path, "application/x-download",

        #                          "attachment", os.path.basename(path))

@view_config(route_name='download_csv', renderer='json')
def download_csv(request):
        global result_paths_dict
        csv_ref=request.matchdict['csv_ref']
        path = result_paths_dict[csv_ref]['csv']
        response = FileResponse(
        path,
        request=request,
        content_type='text/csv'
        )
        return response   

def get_total_rows(csv_file):
        rows=''
        with open(csv_file,'rU') as fin:
            csvin = csv.reader(fin)
            rows = sum(1 for row in csvin)
            fin.close()
        return rows




def save_csv(csv_data):
    filename=str(uuid.uuid4())+'.csv'
    csv_file=open('/home/ana/faizan/preloader_csvs/'+filename,'w')
    csv_file.write(csv_data)
    csv_file.close()
    csv_file=os.path.abspath('/home/ana/faizan/preloader_csvs/'+filename)
    return csv_file,filename

def generate_country_dict(csv_dict):
    country_term_dict={}
    country_id_dict={}
    for row in csv_dict:
        country_term_dict[row['Source Geography Term'].lower()]=dict(artstor_term=row['Artstor Geography Term'],tgn_id=row['TGN ID'])
        country_id_dict[row['TGN ID']]=dict(artstor_term=row['Artstor Geography Term'],source_term=row['Source Geography Term'])
    return country_term_dict,country_id_dict


def start_validation(conversion_queue,process_queue,csv_ref,category,validate_column,id_column,geography_map,classification_map):
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
                    result_dict[row[id_column]]['keyword']=qv.lower()
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

    elif category=='Date':
        c=0
        mapping_status[csv_ref]={}
        for row in csv_dict:
            result_dict[row[id_column]]={}
            c+=1
            query_term=str(row[validate_column])
            if query_term.strip()!='':
                try:
                    ed,ld,logic=start_date_parse(query_term)
                    result_dict[row[id_column]]['status']='Converted'
                    result_dict[row[id_column]]['query_term']=query_term
                    result_dict[row[id_column]]['Earliest Date']=ed
                    result_dict[row[id_column]]['Latest Date']=ld
                    result_dict[row[id_column]]['Logic']=logic
                except:
                    traceback.print_exc(file=sys.stdout)
                    result_dict[row[id_column]]['status']='Exception'
                    result_dict[row[id_column]]['query_term']=query_term
                    result_dict[row[id_column]]['Earliest Date']=''
                    result_dict[row[id_column]]['Latest Date']=''
                    result_dict[row[id_column]]['Logic']=''
            else:
                    result_dict[row[id_column]]['status']='Null Value'
                    result_dict[row[id_column]]['query_term']=''
                    result_dict[row[id_column]]['Earliest Date']=''
                    result_dict[row[id_column]]['Latest Date']=''
                    result_dict[row[id_column]]['Logic']=''

            mapping_status[csv_ref]['result']=result_dict
            mapping_status[csv_ref]['category']=category
            if 'artstor earliest date' and 'artstor latest date' in [x.lower().strip() for x in row.keys() if x is not None]:
                mapping_status[csv_ref]['converted_csv']=write_modified_csv(row,result_dict[row[id_column]],os.path.basename(csv_path),category,c,validate_column,id_column)
            else:
                mapping_status[csv_ref]['converted_csv']=False
            process_queue.put(mapping_status)

    print 'succesful end of validation',len(result_dict.keys())

def generate_class_dict(csv_dict):
    class_term_dict={}
    for row in csv_dict:
        class_term_dict[row['Keyword'].lower()]=dict(artstor_term=row['Artstor Classification Term'])
    return class_term_dict

# class preloader_interface(object):

    # def run_simple_date_parser(self,date_string):
    #     print date_string
    #     date_string=str(date_string)
    #     result=start_date_parse(date_string)
    #     return result
    # run_simple_date_parser.exposed=True


    

    # get_artstor_country_list.exposed=True

    

    # get_artstor_class_list.exposed=True


    # def upload_csv(self,csvFile,category,validate_column,id_column):
    #     global active_keys
    #     out = """<html>
    #     <body>
    #         zipFile length: %s<br />
    #         zipFile filename: %s<br />
    #         zipFile mime-type: %s <br />

    #     </body>
    #     </html>"""

    #     # Although this just counts the file length, it demonstrates
    #     # how to read large files in chunks instead of all at once.
    #     # CherryPy reads the uploaded file into a temporary file;
    #     # myFile.file.read reads from that.
    #     size_csv = 0
    #     csv_data=''

    #     while True:
    #         data_zip= csvFile.file.read(8192)


    #         if not data_zip:
    #             break
    #         csv_data+=data_zip
    #         size_csv += len(data_zip)

    #         # print 'Success',size_xlsx
    #     # xsltFile,xlsxFile=unzip_files(zip_data)
    #     csv_file,csv_ref=self.save_csv(csv_data)
    #     # csv_path=os.path.abspath(csv_file)
    #     csv_ref=csv_ref.replace('.csv','')
    #     print 'key: ',csv_ref
    #     # print 'input_xlsx',xlsxFile,xsltFile
    #     # json_resp=simplejson.dumps(xls_to_dict(xlsxFile,xsltFile,username,password,newtransaction))

    #     global_status[csv_ref]={}
    #     global_status[csv_ref]['csv_path']=csv_file
    #     global_status[csv_ref]['total_rows']=self.get_total_rows(csv_file)
    #     active_keys.append(csv_ref)
    #     conversion_queue.put(global_status)
    #     # clear_queue()


    #     mapping_proc=Process(target = self.start_validation , args = (conversion_queue,process_queue,csv_ref,category,validate_column,id_column,geography_map,classification_map))
    #     mapping_proc.start()
    #     # mapping_proc.join()
    #     return simplejson.dumps(dict(success=True,message="Validation successfully started for "+csvFile.filename,csv_ref=csv_ref))
    # upload_csv.exposed = True

    # def get_mapping_status(self,csv_ref):
    #     global global_status
    #     global active_keys

    #     # print '\n mapping:',simplejson.dumps(process_queue.get()),process_queue.empty()
    #     if process_queue.empty()==False:
    #         mapping_status=process_queue.get()
    #         if csv_ref in mapping_status.keys():
    #             return return_resp(mapping_status,csv_ref)
    #             # data_obj=convert_dict_to_list(mapping_status[csv_ref]['result'])
    #             # if len(mapping_status[csv_ref]['result'].keys())<global_status[csv_ref]['total_rows']-1:
    #             #     return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='IN-PROGRESS'))
    #             # else:
    #             #     active_keys.remove(csv_ref)
    #             #     return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='COMPLETED'))
    #         elif csv_ref not in mapping_status.keys() and active_keys.index(csv_ref)==-1:
    #             response=mapping_status.keys()
    #             return simplejson.dumps(dict(message='The job you requested could not be found',code='NOT-FOUND',keys=response))
    #         elif csv_ref not in mapping_status.keys() and active_keys.index(csv_ref)!=-1:
    #              mapping_status=process_queue.get()
    #              while csv_ref not in mapping_status.keys():
    #                 mapping_status=process_queue.get()
    #              return return_resp(mapping_status,csv_ref)


    #     else:
    #         return simplejson.dumps(dict(message='No jobs in process or completed',code='QUEUE-EMPTY'))
    # get_mapping_status.exposed=True

    # def download_report(self,csv_ref):
    #     global result_paths_dict
    #     path = result_paths_dict[csv_ref]['report']
    #     return static.serve_file(path, "application/x-download",
    #                              "attachment", os.path.basename(path))
    # download_report.exposed = True

    # def download_csv(self,csv_ref):
    #     global result_paths_dict
    #     path = result_paths_dict[csv_ref]['csv']
    #     return static.serve_file(path, "application/x-download",
    #                              "attachment", os.path.basename(path))
    # download_csv.exposed = True

    




def write_modified_csv(row,rd,fname,category,counter,vc,idc):
    f_path='/home/ana/faizan/preloader_csvs/converted_csvs/'+'converted-'+fname
    f=open(f_path,'a')
    csv_writer=csv.writer(f,dialect='excel',delimiter=',')
    hl=row.keys()
    if counter==1:
        hl.sort()
        # hl=rearrange_columns(hl,vc,idc,category)
        csv_writer.writerow(hl)
    new_row=[]
    if category=='Country':
        for heads in hl:
            if heads.lower().strip()=='artstor country' and 'artstor_country' in rd.keys():
                index=[x.lower() for x in hl].index(heads.lower().strip())
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
    elif category=='Date':
        for heads in hl:
            if heads.lower().strip()=='earliest date' and 'Earliest Date' in rd.keys():
                new_row.append(rd['Earliest Date'])
            elif heads.lower().strip()=='latest date' and 'Latest Date' in rd.keys():
                new_row.append(rd['Latest Date'])
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
        result_csv_url='download_csv/'+csv_ref
        if result_paths_dict[csv_ref]['csv']==False:
            result_csv_url=False
        return simplejson.dumps(dict(data=data_obj,count=len(mapping_status[csv_ref]['result'].keys()),total=int(global_status[csv_ref]['total_rows'])-1,code='COMPLETED',result_file_url='download_report/'+csv_ref,result_csv_url=result_csv_url))



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
    elif category=='Classification':
        hl=['ID','Query Term','Logic','Status','Artstor Classification']
        csv_writer.writerow(hl)
        for vals in data_obj:
            if vals[1]['status']=='Matched':
                id=vals[0]
                status=vals[1]['status']
                ac=vals[1]['artstor_classification']
                qt=vals[1]['query_term']
                qv=vals[1]['keyword']
                logic='The keyword '+qv+' maps directly to the term '+ac
            else:
                id=vals[0]
                status=vals[1]['status']
                ac=''
                qt=vals[1]['query_term']
                logic=''

            csv_writer.writerow([id,qt,logic,status,ac])
    else:
        hl=['ID','Query Term','Logic','Status','Earliest Date','Latest Date']
        csv_writer.writerow(hl)
        for vals in data_obj:
            if vals[1]['status']=='Converted':
                id=vals[0]
                status=vals[1]['status']
                ed=vals[1]['Earliest Date']
                ld=vals[1]['Latest Date']
                qt=vals[1]['query_term']
                logic=vals[1]['Logic']
            else:
                id=vals[0]
                status=vals[1]['status']
                ed=''
                ld=''
                qt=vals[1]['query_term']
                logic=''
            csv_writer.writerow([id,qt,logic,status,ed,ld])





    # print data_obj[0]


        # csv_writer.writerow([id,status,ac,qt,tgn_id])
    return path



def main():
    config = Configurator()
    config.add_route('artstor_country_list', '/get_artstor_country_list/')
    config.add_route('artstor_class_list', '/get_artstor_class_list/')
    config.add_route('upload_csv', '/upload_csv/')
    config.add_route('get_mapping_status', '/get_mapping_status/{csv_ref}')
    config.add_route('download_report', '/download_report/{csv_ref}')
    config.add_route('download_csv', '/download_csv/{csv_ref}')
    config.add_view(get_artstor_country_list, route_name='artstor_country_list')
    config.add_view(get_artstor_class_list, route_name='artstor_class_list')
    config.add_view(upload_csv, route_name='upload_csv')
    config.add_view(get_mapping_status, route_name='get_mapping_status')
    config.add_view(download_report, route_name='download_report')
    config.add_view(download_csv, route_name='download_csv')
    app = config.make_wsgi_app()
    return app


if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8888, app)
    print ('Starting up server on http://localhost:8888')
    server.serve_forever()
