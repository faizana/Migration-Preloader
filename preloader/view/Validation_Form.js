var download_url=''
var category='Country'
var upload_form=Ext.create('Ext.form.Panel', {
    title: 'Preloader',
    bodyPadding: 5,
    width:600,
    x:200,
    y:300,

    // The form will submit an AJAX request to this URL when submitted
    url: 'http://localhost:9090/upload_csv/',

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
        buttonText: 'Select file...'
    },{
        xtype     : 'textareafield',
        grow      : false,
        autoScroll:true,
        fieldLabel: 'Status',
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
            if (form.isValid()) {
                form.submit({
                    success: function(form, action) {
                       csv_ref=action.result.csv_ref
                       download_url=''
                       Ext.getCmp('reportDownload').disable()
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
    }],
    //renderTo: Ext.getBody()
});


getStatus=function(csv_ref){
Ext.Ajax.request({
    url: 'http://localhost:9090/get_mapping_status/',
    params: {
        csv_ref: csv_ref
    },
    success: function(response){
        var text = response.responseText;
        Ext.getCmp('statusArea').setRawValue('')
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
           statusString='<b> Countries Matched: '+matched+', Countries Unmatched: '+unmatched+' Empty Values : '+ emptyVals+', Total:'+total +' </b>'
        }
        else {
            statusString=' <b> Classifications Matched: '+matched+', Classifications Unmatched: '+unmatched+' Empty Values : '+ emptyVals+', Total:'+total +' </b>'
        }

        var statusArea=Ext.getCmp('statusArea')
        statusArea.setRawValue(statusString)
        getStatus(csv_ref)
            
        }

        else if (data['code']=='COMPLETED'){

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
           statusString='<b> Countries Matched: '+matched+', Countries Unmatched: '+unmatched+' Empty Values : '+ emptyVals+', Total:'+total +' </b>'
        }
        else {
            statusString=' <b> Classifications Matched: '+matched+', Classifications Unmatched: '+unmatched+' Empty Values : '+ emptyVals+', Total:'+total +' </b>'
        }
        download_url=data['result_file_url']
        Ext.getCmp('reportDownload').enable()
        var statusArea=Ext.getCmp('statusArea')
        statusArea.update(statusString)
        
        }
        // Ext.getCmp('statusArea').setRawValue
        // process server response here
    }
});
}

var addPanelSwitchButton=function (){
    var newDiv = document.createElement('div');
    newDiv.id='switchDiv';
    newDiv.innerHTML='<ul id="switchElem" style="margin-left:20px;margin-top:20px;"> <li><a href="#">Artstor Country</a></li><li class="on"><a href="#">Artstor Classification</a></li></ul>'
    document.body.appendChild(newDiv);

}