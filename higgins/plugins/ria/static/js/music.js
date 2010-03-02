Ext.onReady(function() {

    var songStore = new Ext.data.JsonStore({
        url: '/ria/ajax/getSongs',
        root: 'songs',
        totalProperty: 'total',
        idProperty: 'id',
        fields: [{name: 'name'}, {name: 'id'}]
    });

    var songs = new Ext.grid.GridPanel({
        id: 'songs-grid',
        store: songStore,
        columns: [{id: 'name', header: 'Song Title', sortable: true, dataIndex: 'name' }],
        unstyled: true,
        layout: 'fit',
        autoHeight: true,
        hideHeaders: true,
        border: false,
        viewConfig: {
            headersDisabled: true,
            autoFill: true,
            forceFit: true,
            scrollOffset: 0
        },
        tbar: new Ext.PagingToolbar({
            pageSize: 10,
            store: songStore,
            displayInfo: true,
            displayMsg: "Displaying Songs {0} - {1} of {2}",
            emptyMsg: "No Songs"
        })
    });

    var albumStore = new Ext.data.JsonStore({
        url: '/ria/ajax/getAlbums',
        root: 'albums',
        totalProperty: 'total',
        idProperty: 'id',
        fields: [{name: 'name'}, {name: 'id'}]
    });

    var albums = new Ext.grid.GridPanel({
        id: 'albums-grid',
        store: albumStore,
        columns: [{id: 'name', header: 'Album', sortable: true, dataIndex: 'name' }],
        unstyled: true,
        layout: 'fit',
        autoHeight: true,
        hideHeaders: true,
        border: false,
        viewConfig: {
            headersDisabled: true,
            autoFill: true,
            forceFit: true,
            scrollOffset: 0
        },
        tbar: new Ext.PagingToolbar({
            pageSize: 10,
            store: albumStore,
            displayInfo: true,
            displayMsg: "Displaying Albums {0} - {1} of {2}",
            emptyMsg: "No Albums"
        })
    });

    var artistStore = new Ext.data.JsonStore({
        url: '/ria/ajax/getArtists',
        root: 'artists',
        totalProperty: 'total',
        idProperty: 'id',
        fields: [{name: 'name'}, {name: 'id'}]
    });

    var artists = new Ext.grid.GridPanel({
        id: 'artists-grid',
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
            forceFit: true,
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

    var layout = new Ext.Panel({
        id: 'layout-panel',
        layout: 'card',
        region: 'center',
        activeItem: 0,
        border: false,
        items: [ artists, albums, songs ],
        renderTo: 'music-body'
    });

    var crumbs = new Array({method: loadArtists, id: 0, prev: '', curr: 'Artists'});

    function loadArtists() {
        artistStore.setBaseParam('id', crumbs[0].id);
        artistStore.load({params:{start: 0, limit: 10}});
        artists.hide();
        layout.layout.setActiveItem('artists-grid');
        Ext.get('music-crumbs').update('');
        Ext.get('music-info').update(crumbs[0].curr);
        artists.getEl().slideIn('l', {stopFX: true, duration: .3});
    }

    function loadArtist() {
        albumStore.setBaseParam('id', crumbs[0].id);
        albumStore.load({params:{start: 0, limit: 10}});
        albums.hide();
        layout.layout.setActiveItem('albums-grid');
        Ext.get('music-crumbs').update('<a href="#" id="music-prev-link">&#171; ' + crumbs[0].prev + '</a>');
        Ext.get('music-info').update(crumbs[0].curr);
        albums.getEl().slideIn('l', {stopFX: true, duration: .3});
    };

    function loadAlbum() {
        songStore.setBaseParam('id', crumbs[0].id);
        songStore.load({params:{start: 0, limit: 10}});
        songs.hide();
        layout.layout.setActiveItem('songs-grid');
        Ext.get('music-crumbs').update('<a href="#" id="music-prev-link">&#171; ' + crumbs[0].prev + '</a>');
        Ext.get('music-info').update(crumbs[0].curr);
        songs.getEl().slideIn('l', {stopFX: true, duration: .3});
    };

    artists.on('cellclick', function(grid, rowIndex, columnIndex, e) {
        var record = grid.getStore().getAt(rowIndex);
        var id = record.get('id');
        var name = record.get('name');
        crumbs.unshift({method: loadArtist, id: id, prev: crumbs[0].curr, curr: name});
        loadArtist();
    });

    albums.on('cellclick', function(grid, rowIndex, columnIndex, e) {
        var record = grid.getStore().getAt(rowIndex);
        var id = record.get('id');
        var name = record.get('name');
        crumbs.unshift({method: loadAlbum, id: id, prev: crumbs[0].curr, curr: name});
        loadAlbum();
    });

    Ext.get('music-crumbs').on('click', function(ev, el, options) {
        crumbs.shift();
        crumbs[0].method();
    });

    loadArtists();
    artists.show();
});
