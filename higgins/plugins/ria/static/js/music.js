
Ext.onReady(function() {

    var artistStore = new Ext.data.JsonStore({
        url: '/ria/ajax/getArtists',
        root: 'artists',
        totalProperty: 'total',
        idProperty: 'id',
        fields: [{name: 'name'}]
    });

    var artists = new Ext.grid.GridPanel({
        store: artistStore,
        columns: [{id: 'name', header: 'Artist', sortable: true, dataIndex: 'name' }],
        unstyled: true,
        layout: 'fit',
        autoHeight: true,
        hideHeaders: true,
        border: false,
        viewConfig: {
            headersDisabled: true,
            autoFill: true,
            scrollOffset: 0
        },
        tbar: new Ext.PagingToolbar({
            pageSize: 10,
            store: artistStore,
            displayInfo: true,
            displayMsg: "Displaying Artists {0} - {1} of {2}",
            emptyMsg: "No Artists"
        })
    });

    artists.render('music-artist-table');

    artistStore.load({params:{start:0, limit:10}});
});
