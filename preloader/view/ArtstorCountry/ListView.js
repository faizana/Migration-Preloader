// Ext.define('Preloader.view.ArtstorCountry.ListView' ,{
//     extend: 'Ext.grid.Panel',
//     alias: 'widget.artstorcountrylist',
//     store: 'ArtstorCountry.ListStore',
//     title: 'All Countries',

//     initComponent: function() {
        

//         this.columns = [
//             {header: 'Artstor Geography Term',  dataIndex: 'countryName',  flex: 1},
//             {header: 'TGN ID', dataIndex: 'tgn_id', flex: 1},
//             {header: 'Artstor Region 1', dataIndex: 'region1', flex: 1},
//             {header: 'Artstor Region 2', dataIndex: 'region2', flex: 1}
//         ];

//         this.callParent(arguments);
//     }
// });

Ext.define('Preloader.view.ArtstorCountry.ListGrid', {
    extend: 'Ext.grid.Panel',
    // requires: ['Preloader.view.ArtstorCountry.SearchTrigger'],
    alias: 'widget.artstorcountrylist',
    store: 'ArtstorCountry.ListStore',
    initComponent: function() {
        

        this.columns = [
            {header: 'Source Geography Term',  dataIndex: 'countryName',  flex: 1},
            {header: 'TGN ID', dataIndex: 'tgn_id', flex: 1},
            {header: 'Artstor Geography Term', dataIndex: 'region1', flex: 1},
            
        ];

        this.callParent(arguments);
    },
    //header:false,
    // items:[{
    //     xtype: 'searchtrigger',
    //     autoSearch: true
    // }]
});

Ext.define('Preloader.view.ArtstorCountry.ListView', {
    extend: 'Ext.panel.Panel',
    requires: ['Preloader.view.ArtstorCountry.SearchTrigger'],
    alias: 'widget.artstorcountrycont',
    layout: {
        type: 'fit'
    },
    // store: 'ArtstorCountry.ListStore',
    // initComponent: function() {
        

    //     this.columns = [
    //         {header: 'Source Geography Term',  dataIndex: 'countryName',  flex: 1},
    //         {header: 'TGN ID', dataIndex: 'tgn_id', flex: 1},
    //         {header: 'Artstor Geography Term', dataIndex: 'region1', flex: 1},
            
    //     ];

    //     this.callParent(arguments);
    // },
    items:[{
        xtype:'artstorcountrylist',
        id:'countryGrid'
    }
    


    ]
    //header:false,
    // items:[{
    //     xtype: 'searchtrigger',
    //     autoSearch: true
    // }]
});


