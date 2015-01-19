var countryProxy={
			type: 'rest',
			timeout: 180000,
			url : '/get_artstor_country_list/',
			autoLoad: true,
			reader: {
				type: 'json',
				root:'countrydata',
				totalProperty :'total'
			}
	};
Ext.define('Preloader.store.ArtstorCountry.ListStore', {
    extend: 'Ext.data.Store',
    model: 'Preloader.model.ListModel',
    // fields:['countryName','tgn_id','region1','region2'],
    proxy:countryProxy 
            // data  : [
            //     {countryName: 'America',    tgn_id: '123',region1:'USA',region2:'USA'},
            //     {countryName: 'Pakistan',    tgn_id: '456',region1:'Islamic Republic of Pakistan',region2:'USA'}
            // ]
        }

        
);
