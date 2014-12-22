Ext.require('Ext.container.Viewport');
var app=Ext.application({
    name: 'Preloader',
    appFolder: 'preloader',
    controllers: [
        'Preloading'
    ],
    launch: function() {
        Ext.create('Ext.container.Viewport', {
            layout: 'absolute',
            items: [
    Ext.create('Ext.form.Panel', {
    title: 'Field Filter',
    // bodyPadding: 5,
    width: 800,
    height:50,
    x:200,
    y:20,
    // renderTo: Ext.getBody(),
    items:[{
        xtype: 'searchtrigger',
        autoSearch: true,
        fieldLabel: 'Search Term',
        
    }]
}),
        //     {
        //     xtype      : 'fieldcontainer',
        //     region     :   'north',
        //     fieldLabel : 'Choose category',
        //     defaultType: 'radiofield',
        //     defaults: {
        //         flex: 0.5
        //     },
        //     layout: 'hbox',
        //     items: [
        //         {
        //             boxLabel  : 'Artstor Country',
        //             name      : 'artcountry',
        //             inputValue: 'country',
        //             id        : 'radio1'
        //         }, {
        //             boxLabel  : 'Artstor Classification',
        //             name      : 'class',
        //             inputValue: 'true',
        //             id        : 'radio2'
        //         }
        //     ]
        // },

                {
                    xtype: 'artstorcountrycont',
                    height:200,
                    width:800,
                    x:200,
                    y:70
                                         
                    
                },
                upload_form,{
                    xtype:'container',
                    x:-20,
                    y:20,
                    height:30,
                    width:150,
                    id:'switchComp',
                    items:[{
                        xtype:'container',
                        html:'<ul id="switchElem"> <li class="on"><a href="#">Artstor Country</a></li><li><a href="#">Artstor Classification</a></li></ul>',
                        listeners:{
                            'afterrender':function(cont,epts){
                                Ext.get(Ext.query("ul li")).on('click', function(e, t, eOpts) { 
                                var el = Ext.get(this),
                                    p;
                                el.addCls("on");
                                if((p = el.next())) {
                                    p.removeCls("on");
                                    Preloader.app.getController('Preloading').onswitchchangecountry()
                                    
                                } else if ((p = el.prev())){
                                    p.removeCls("on");
                                    Preloader.app.getController('Preloading').onswitchchangeclass()
                                    // preloadClassStore()
                                }
                            });
                            
                            }
                        }
                    }]
                }
            ]
        });
    }
});
