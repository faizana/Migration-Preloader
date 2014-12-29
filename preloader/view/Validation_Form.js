var download_url=''
var download_csv_url=''
var category='Country'
//var statusTextHTML='<tbody><tr id="statusArea-inputRow"><td id="statusArea-labelCell" style="" valign="top" halign="left" width="105" class="x-field-label-cell"><label id="statusArea-labelEl" for="statusArea-inputEl" class="x-form-item-label x-unselectable x-form-item-label-left" style="width:100px;margin-right:5px;" unselectable="on">Status:</label></td><td class="x-form-item-body " id="statusArea-bodyEl" colspan="2" role="presentation" style="width: 100%;"><textarea id="statusArea-inputEl" name="statusArea-inputEl" rows="4" cols="20" class="x-form-field x-form-text x-form-textarea" autocomplete="off" aria-invalid="false" data-errorqtip="" style="width: 100%;"></textarea></td></tr></tbody>'
var upload_form=Ext.create('Ext.form.Panel', {
    title: 'Preloader',
    bodyPadding: 5,
    width:600,
    x:200,
    y:300,

    // The form will submit an AJAX request to this URL when submitted
    url: '/upload_csv/',

    // Fields will be arranged vertically, stretched to full width
    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },

    // The fields
    defaultType: 'textfield',
    items: [{
        fieldLabel: 'Validate Column',
        name: 'validate_column',
        allowBlank: false
    },{
        fieldLabel: 'ID Column',
        name: 'id_column',
        allowBlank: false
    },{
        xtype: 'radiogroup',
        fieldLabel: 'Select Category',
        // Arrange radio buttons into two columns, distributed vertically
        columns: 2,
        vertical: true,
        items: [
            { boxLabel: 'Artstor Country', name: 'category', inputValue: 'Country' , checked: true},
            { boxLabel: 'Artstor Classification', name: 'category', inputValue: 'Classification'}
            
        ],
        listeners:{
            'change':function(combo, newValue, oldValue, eOpts ){

                if (category=='Country')
                    category=newValue
                else
                    category='Country'
            }
        }
    },
    {
        xtype: 'filefield',
        name: 'csvFile',
        fieldLabel: 'Select CSV File',
        labelWidth: 100,
        msgTarget: 'side',
        allowBlank: false,
        anchor: '100%',
        buttonText: 'Select file...',
//		listeners:{
//			'change':function(ta, value, eOpts){
//				Ext.getCmp('statusArea').update('')
//				
//			}
//		}
    },{
        xtype     : 'textareafield',
        grow      : true,
        autoScroll:true,
        fieldLabel: 'Status',
        // maxHeight: 100,
        anchor    : '100%',
        submitValue:false,
        id:'statusArea',
		
    }
            ],
        

    // Reset and Submit buttons
    buttons: [{
        text: 'Reset',
        handler: function() {
            this.up('form').getForm().reset();
        }
    }, {
        text: 'Submit',
        formBind: true, //only enabled once the form is valid
        disabled: true,
        handler: function() {
            var form = this.up('form').getForm();
            if (form.isValid()) {
                form.submit({
                    waitMsg:'Loading...',
                    success: function(form, action) {
                       csv_ref=action.result.csv_ref
                       download_url=''
                       download_csv_url=''
                       Ext.getCmp('reportDownload').disable()
                       Ext.getCmp('csvDownload').disable()
                       Ext.Function.defer(getStatus, 2000, this, [csv_ref]);

                       

                    },
                    failure: function(form, action) {
                        console.log(action)
                    }
                });
            }
        }
    },{
        text: 'Download Report',
        disabled: true,
        id:'reportDownload',
        handler: function(){
            try {
        Ext.destroy(Ext.get('downloadIframe'));
}
            catch(e) {
  // who you gonna call?  
}
      
Ext.DomHelper.append(document.body, {
  tag: 'iframe',
  id:'downloadIframe',
  frameBorder: 0,
  width: 0,
  height: 0,
  css: 'display:none;visibility:hidden;height: 0px;',
  src: download_url
});
            
        }
    },{
        text: 'Download Converted CSV',
        disabled: true,
        id:'csvDownload',
        handler: function(){
            try {
                if (download_csv_url!=false)
        Ext.destroy(Ext.get('downloadcsvIframe'));
                else{
                    alert('The required column does not exist in source csv')
                }
}
            catch(e) {
  // who you gonna call?  
}
      
Ext.DomHelper.append(document.body, {
  tag: 'iframe',
  id:'downloadcsvIframe',
  frameBorder: 0,
  width: 0,
  height: 0,
  css: 'display:none;visibility:hidden;height: 0px;',
  src: download_csv_url
});
            
        }
    }],
    //renderTo: Ext.getBody()
});


getStatus=function(csv_ref){
Ext.Ajax.request({
    url: '/get_mapping_status/',
    params: {
        csv_ref: csv_ref
    },
    success: function(response){
        var text = response.responseText;
        data=Ext.decode(text)
        var statusString=''
        var matched=0;
        var unmatched=0;
        var emptyVals=0;
        var total=data['total']
        if (data['code']=='IN-PROGRESS'){
            for (var i=0;i<parseInt(data['count']);i++){
                if (data['data'][i][1]['status']=='Matched'){
                    matched+=1;
                }
                
                else if (data['data'][i][1]['status']=='Not Matched'){
                    unmatched+=1;
                }
            else{
                    emptyVals+=1;
            }


            }
        if (category=='Country'){
		   pct=((matched+unmatched+emptyVals)/total)*100
           statusString=' Countries Matched: '+matched+',\n Countries Unmatched: '+unmatched+'\n Empty Values : '+ emptyVals+',\n Total:'+total+' \n '+pct+'% Complete'
        }
        else {
            pct=((matched+unmatched+emptyVals)/total)*100
           statusString=' Classifications Matched: '+matched+',\n Classifications Unmatched: '+unmatched+'\n Empty Values : '+ emptyVals+',\n Total:'+total+' \n '+pct+'% Complete'
        }

        var statusArea=Ext.getCmp('statusArea')
		statusArea.setFieldStyle('font-weight:normal')
        statusArea.setRawValue(statusString)
        getStatus(csv_ref)
            
        }

        else if (data['code']=='COMPLETED' || data['code']=='QUEUE-EMPTY'){

           for (var i=0;i<parseInt(data['count']);i++){
                if (data['data'][i][1]['status']=='Matched'){
                    matched+=1;
                }
                
                else if (data['data'][i][1]['status']=='Not Matched'){
                    unmatched+=1;
                }
            else{
                    emptyVals+=1;
            }


            }
        if (category=='Country'){
			
			pct=((matched+unmatched+emptyVals)/total)*100
			statusString=' Countries Matched: '+matched+',\n Countries Unmatched: '+unmatched+',\n Empty Values : '+ emptyVals+',\n Total: '+total+' \n '+pct+'% Complete'	
			
			
			
           
        }
        else {
			pct=((matched+unmatched+emptyVals)/total)*100
			statusString=' Classifications Matched: '+matched+',\n Classifications Unmatched: '+unmatched+',\n Empty Values : '+ emptyVals+',\n Total: '+total+' \n '+pct+'% Complete'
            
        }
        download_url=data['result_file_url']
        download_csv_url=data['result_csv_url']
        Ext.getCmp('reportDownload').enable()
        Ext.getCmp('csvDownload').enable()
        var statusArea=Ext.getCmp('statusArea')
		pct=((matched+unmatched+emptyVals)/total)*100
		if (pct==100)
		statusArea.setFieldStyle('font-weight:bold;color:green;')
		else
		statusArea.setFieldStyle('font-weight:bold;color:red;')
        statusArea.setRawValue(statusString)
        
        }
        // Ext.getCmp('statusArea').setRawValue
        // process server response here
    }
});
}

var addPanelSwitchButton=function (){
    var newDiv = document.createElement('div');
    newDiv.id='switchDiv';
    newDiv.innerHTML='<ul id="switchElem" style="margin-left:20px;margin-top:20px;"> <li><a href="#">Artstor Country</li><li class="on"><a href="#">Artstor Classification</li></ul>'
    document.body.appendChild(newDiv);

}
