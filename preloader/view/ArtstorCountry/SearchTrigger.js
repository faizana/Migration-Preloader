Ext.define('Preloader.view.ArtstorCountry.SearchTrigger', {
    extend: 'Ext.form.field.Trigger',
    alias: 'widget.searchtrigger',
    // triggerCls: 'x-form-clear-trigger',
    // trigger2Cls: 'x-form-search-trigger',
    onTriggerClick: function() {
        this.setValue('')
        this.setFilter(this.up().dataIndex, '')
    },
    // onTrigger2Click: function() {
    //     this.setFilter(this.up().dataIndex, this.getValue())
    // },
    setFilter: function(filterId, value){
        var store = this.up('viewport').down('grid').getStore();
        console.log(filterId, value)
        if(value){
            store.removeFilter(filterId, false)
            var filter = {id: filterId, property: filterId, value: value};
            if(this.anyMatch) filter.anyMatch = this.anyMatch
            if(this.caseSensitive) filter.caseSensitive = this.caseSensitive
            if(this.exactMatch) filter.exactMatch = this.exactMatch
            if(this.operator) filter.operator = this.operator
            console.log(this.anyMatch, filter)
            store.addFilter(filter)
        } else {
            // store.filters.removeAtKey(filterId)
            // console.log(originalCountryList)
            store.clearFilter()
            // store.setProxy(countryProxy)
            store.load()
        }
    },
    listeners: {
        render: function(){
            var me = this;
            me.ownerCt.on('resize', function(){
                me.setWidth(this.getEl().getWidth())
            })
        },
        change: function() {
            console.log(this.getValue())
            // if (typeof(this.getValue())
            if (isNaN(this.getValue())){
               if(this.autoSearch) this.setFilter('countryName', this.getValue()) 
            }
            else{
               if(this.autoSearch) this.setFilter('tgn_id', this.getValue())  
            }
        }
    }
});



