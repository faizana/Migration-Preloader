var download_url=''
var download_csv_url=''
var category='Country'
var upload_form=Ext.create('Ext.form.Panel', {
    title: 'Preloader',
    bodyPadding: 5,
    width:600,
	height:320,
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
            { boxLabel: 'Artstor Classification', name: 'category', inputValue: 'Classification'},
			{ boxLabel: 'Artstor Date', name: 'category', inputValue: 'Date'}

        ],
        listeners:{
            'change':function(combo, newValue, oldValue, eOpts ){

//                if (category=='Country')
//                    category=newValue
//                else
//                    category='Country'
                  category=newValue['category']
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
        buttonText: 'Select file...'
    },{
        xtype     : 'textareafield',
        grow      : true,
        autoScroll:true,
        fieldLabel: 'Status',
		height:120,
        // maxHeight: 100,
        anchor    : '100%',
        submitValue:false,
        id:'statusArea'
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
			Ext.getCmp('statusArea').setRawValue('');
            if (form.isValid()) {
                form.submit({
                    waitMsg:'Loading...',
                    success: function(form, action) {
                       csv_ref=action.result.csv_ref
                       download_url=''
                       download_csv_url=''
                       Ext.getCmp('reportDownload').disable()
                       Ext.getCmp('csvDownload').disable()
					   Ext.getBody().mask('<div style="border-style:none;" class="x-mask-loading"><div style="border-style:none;">Processing</div></div>');
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
    url: '/get_mapping_status/'+csv_ref,
//    params: {
//        csv_ref: csv_ref
//    },
    success: function(response){
		Ext.getBody().unmask();
        var text = response.responseText;
        data=Ext.decode(text)
		if (category!='Date'){
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
           statusString=' Countries Matched: '+addCommas(matched)+';\n Countries Unmatched: '+addCommas(unmatched)+'\n Empty Source Values : '+ addCommas(emptyVals)+';\n Total Source Values:'+addCommas(total)+' \n '+pct.toFixed(2)+'% Complete'
        }
        else {
            pct=((matched+unmatched+emptyVals)/total)*100
           statusString=' Classifications Matched: '+addCommas(matched)+';\n Classifications Unmatched: '+addCommas(unmatched)+'\n Empty Source Values : '+ addCommas(emptyVals)+';\n Total Source Values:'+addCommas(total)+' \n '+pct.toFixed(2)+'% Complete'
        }

        var statusArea=Ext.getCmp('statusArea')
		statusArea.setFieldStyle('font-weight:normal;color:black;')
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
                        statusString=' Countries Matched: '+addCommas(matched)+';\n Countries Unmatched: '+addCommas(unmatched)+';\n Empty Source Values : '+ addCommas(emptyVals)+';\n Total Source Values: '+addCommas(total)+' \n '+pct.toFixed(2)+'% Complete'





        }
        else {
                        pct=((matched+unmatched+emptyVals)/total)*100
                        statusString=' Classifications Matched: '+addCommas(matched)+';\n Classifications Unmatched: '+addCommas(unmatched)+';\n Empty Source Values : '+ addCommas(emptyVals)+';\n Total Source Values: '+addCommas(total)+' \n '+pct.toFixed(2)+'% Complete'

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
        else if (data['code']=='ERROR-COLUMN' ){
            Ext.Msg.alert('Error','The entered ID or Validate Column/s could not be found, check for case sensitivity and whitespaces.');
            return;
        }
        // Ext.getCmp('statusArea').setRawValue
        // process server response here
                }
                else{
                        var statusString=''
                        var converted=0
                        var exceptions=0;
                var emptyVals=0;
                var total=data['total']
                        for (var i=0;i<parseInt(data['count']);i++){
                                        if (data['data'][i][1]['status']=='Converted'){
                                                converted+=1
                                        }
                                        else if (data['data'][i][1]['status']=='Exception'){
                                                exceptions+=1
                                        }
                                        else{
                                                emptyVals+=1
                                        }
                                }
                        pct=((converted+exceptions+emptyVals)/total)*100
            statusString=' Dates Parsed: '+addCommas(converted)+';\n Parsing Exceptions: '+addCommas(exceptions)+'\n Empty Source Values : '+ addCommas(emptyVals)+';\n Total Source Values:'+addCommas(total)+' \n '+pct.toFixed(2)+'% Complete'
                        var statusArea=Ext.getCmp('statusArea')
                        if (data['code']=='IN-PROGRESS'){

                                statusArea.setFieldStyle('font-weight:normal;color:black;')
                        statusArea.setRawValue(statusString)
                        getStatus(csv_ref)
                        }

                        else if (data['code']=='COMPLETED' || data['code']=='QUEUE-EMPTY'){
                                download_url=data['result_file_url']
                        download_csv_url=data['result_csv_url']
                        Ext.getCmp('reportDownload').enable()
                        Ext.getCmp('csvDownload').enable()
                                if (pct==100)
                                statusArea.setFieldStyle('font-weight:bold;color:green;')
                                else
                                statusArea.setFieldStyle('font-weight:bold;color:red;')
                                statusArea.setRawValue(statusString)
                        }

                         else if (data['code']=='ERROR-COLUMN' ){
                Ext.Msg.alert('Error','The entered ID or Validate Column/s could not be found, check for case sensitivity and whitespaces.');
                return;
        }


                }

    }
});
}

var addPanelSwitchButton=function (){
    var newDiv = document.createElement('div');
    newDiv.id='switchDiv';
    newDiv.innerHTML='<ul id="switchElem" style="margin-left:20px;margin-top:20px;"> <li><a href="#">Artstor Country</li><li class="on"><a href="#">Artstor Classification</li></ul>'
    document.body.appendChild(newDiv);

}

var addCommas=function (nStr) {
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
            x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}