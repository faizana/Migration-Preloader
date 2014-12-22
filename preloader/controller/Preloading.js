Ext.define('Preloader.controller.Preloading', {
    extend: 'Ext.app.Controller',
     views: [
        'ArtstorCountry.ListView'
    ],
    stores: [
        'ArtstorCountry.ListStore'
    ],
    models:[
    'ListModel'
    ],
   
    init: function() {
        console.log(this.getArtstorCountryListStoreStore())
        this.control({
            'viewport > panel': {
                render: this.onPanelRendered
            }
        });
},

   onPanelRendered: function() {
        // console.log(this.getApplication().getController('Preloading').store())
        this.getArtstorCountryListStoreStore().load()
        // addSwitchListener()
    },

    onswitchchangeclass: function(action){
        this.getArtstorCountryListStoreStore().setProxy({
            type: 'rest',
            timeout: 180000,
            url : 'http://localhost:9090/get_artstor_class_list/',
            autoLoad: true,
            reader: {
                type: 'json',
                root:'countrydata',
                totalProperty :'total'
            }
        })
       this.getArtstorCountryListStoreStore().load()
       Ext.getCmp('countryGrid').columns[0].setText('Keyword')
       Ext.getCmp('countryGrid').columns[1].setText('Artstor Classification Term')
       Ext.getCmp('countryGrid').columns[2].setText('AAT ID')
       // this.getArtstorCountryListViewView().columns
       // this.getArtstorCountryListViewView().columns
    },
    onswitchchangecountry:function(){
        this.getArtstorCountryListStoreStore().setProxy({
            type: 'rest',
            timeout: 180000,
            url : 'http://localhost:9090/get_artstor_country_list/',
            autoLoad: true,
            reader: {
                type: 'json',
                root:'countrydata',
                totalProperty :'total'
            }
        })
        this.getArtstorCountryListStoreStore().load()
       Ext.getCmp('countryGrid').columns[0].setText('Source Geography Term')
       Ext.getCmp('countryGrid').columns[1].setText('TGN ID')
       Ext.getCmp('countryGrid').columns[2].setText('Artstor Geography Term')

    }
    
});



