// wait until the DOM is loaded, the execute the JavaScript code
jQuery(document).ready(function() {


    var clipboardNode = null;
    var pasteMode = null;


//var tree_services = window.location.protocol + "//" + window.location.host + "/" +"admin/fancytree/fancytree/change_tree/"
// var tree_json_url = window.location.protocol + "//" + window.location.host + "/" +"admin/fancytree/fancytree/tree_json/"


// get the Server url to POST to in order to consume the data services
// get it from
// e.g.   <div id="tree"    tree_model= "{{ tree_model_name }}"   tree_json_url="{{ tree_json_url }}"    tree_services= "{{ tree_services_url }}"  />
    var tree_services = $("div#tree").attr('tree_Services')

// Get the url where to get the tree data
    var tree_json_url = $("div#tree").attr('tree_json_url')

    var tree_model =    $("div#tree").attr('tree_model')



    window.new_title =    $("div#tree").attr('new_title')

    var data_save_state=  $("div#tree").attr('data-save_state')
    var data_auto_open=  $("div#tree").attr('data-auto_open')


//var has_add_permission=
//var  grid_url=
//var has_add_permission=
//var cl=
//var media =



    var  tree_changerequest = {
        source_nodes : [ {}],
        target_node : {},
        method : "",
        new_id : 0,
        response : "" }

    tree_changerequest_JSON = ""



    function copyPaste(action, node) {
        switch( action ) {
            case "cut":
            case "copy":
                clipboardNode = node;
                pasteMode = action;
                break;
            case "paste":
                if( !clipboardNode ) {
                    alert("Clipoard is empty.");
                    break;
                }
                if( pasteMode == "cut" ) {


//               Cut mode: check for recursion and remove source
                    var cb = clipboardNode.toDict(true);
                    if( node.isDescendantOf(cb) ) {
                        alert("Cannot move a node to it's sub node.");
                        return;
                    }
                    node.addChildren(cb);
                    node.render();
                    clipboardNode.remove();
                } else {
                    // Copy mode: prevent duplicate keys:
                    var cb = clipboardNode.toDict(true, function(dict){

                        delete dict.key; // Remove key, so a new one will be created
                    });


                    var newnode = {title:"new" }
                    newnode = node.addNode(newnode,'child');

                    newnode.applyPatch(cb);
                }
                clipboardNode = pasteMode = null;
                break;
            default:
                alert("Unhandled clipboard action '" + action + "'");
        }
    };


    $("#tree").fancytree({


        extensions: ['contextMenu','edit','dnd'],


        activeVisible: true, // Make sure, active nodes are visible (expanded).
        aria: false, // Enable WAI-ARIA support.
        autoActivate: true, // Automatically activate a node when it is focused (using keys).
        autoCollapse: false, // Automatically collapse all siblings, when a node is expanded.
        autoScroll: false, // Automatically scroll nodes into visible area.
        clickFolderMode: 4, // 1:activate, 2:expand, 3:activate and expand, 4:activate (dblclick expands)
        checkbox: true, // Show checkboxes.

        dblclick: function(event,data) {



//            alert(data.node.title+' was selected ( primary key value = '+data.node.key+' )')

            opener.dismissRelatedLookupPopup(window,data.node.key)



//            data.node.toggleSelected();
        },
        debugLevel: 2, // 0:quiet, 1:normal, 2:debug
        disabled: false, // Disable control
        generateIds: false, // Generate id attributes like <span id='fancytree-id-KEY'>
        idPrefix: "ft_", // Used to generate node id´s like <span id='fancytree-id-<key>'>.
        icons: true, // Display node icons.
        keyboard: true, // Support keyboard navigation.
        keyPathSeparator: "/", // Used by node.getKeyPath() and tree.loadKeyPath().
        minExpandLevel: 1, // 1: root node is not collapsible
        selectMode: 2, // 1:single, 2:multi, 3:multi-hier
        tabbable: true, // Whole tree behaves as one single control
        titlesTabbable: false,// Node titles can receive keyboard focus

        contextMenu: {

            menu: {
                'add': { 'name': 'Add', 'icon': 'add' },
                'cut': { 'name': 'Cut', 'icon': 'cut' },
                'copy': { 'name': 'Copy', 'icon': 'copy' },
                'paste': { 'name': 'Paste', 'icon': 'paste' },
                'delete': { 'name': 'Delete', 'icon': 'delete', 'disabled': false },
                'deselect': { 'name': 'Unselect All', 'icon': 'selectnone' },
                'selectall': { 'name': 'Select all', 'icon': 'selectall' },
                'sep1': '---------',
                'rebuild': { 'name': 'Rebuild', 'icon': 'rebuild' },
                'help': { 'name': 'Help', 'icon': 'help' }

            },

            actions: function(node, action, options) {


                switch( action ) {


                    case "delete":

                        tree_changerequest = {
                            source_nodes: [
                                {node_id: 0, node_title: ""}
                            ],
                            target_node: { node_id: node.key, node_title: node.title},
                            method: "DELETE",
                            hitmode: "",
                            new_id: 0,
                            response: "hold" }

                        tree_changerequest_JSON = JSON.stringify(tree_changerequest);

                        $.ajax({
                            url:  tree_services,
                            type: 'POST',
                            async: false,
                            data: tree_changerequest_JSON,
                            datatype: 'json',


                            beforeSend: function (xhr, settings) {
                                // Set Django csrf token
                                var csrftoken = jQuery.cookie('csrftoken');
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            },

                            success: function (data) {


                                node.remove();


                            },
                            error: function (request, status, error) {

                                alert('fout' + request.responseText);

                            }

                        });


                        break;

                    case "add":


                        tree_changerequest = {
                            source_nodes: [
                                {node_id: 0, node_title: new_title}
                            ],
                            target_node: { node_id: node.key, node_title: node.title},
                            method: "ADD",
                            hitmode: "",
                            new_id: 0,
                            response: "hold" }


                        tree_changerequest_JSON = JSON.stringify(tree_changerequest);


                        $.ajax({
                            url: tree_services,
                            type: 'POST',
                            async: false,
                            data: tree_changerequest_JSON,
                            datatype: 'json',


                            beforeSend: function (xhr, settings) {
                                // Set Django csrf token
                                var csrftoken = jQuery.cookie('csrftoken');
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            },

                            success: function (data) {


                                // In the backend, the new node was already saved to the database, now make the UI represent this change
                                Data = JSON.parse(data)


                                var newnode = {title:new_title }

                                newnode = node.addNode(newnode,'child');



                                // Set the node id to the primary key that was obtained from the back end
                                newnode.key = Data.new_id

                                newnode.setActive()
                                //                              newnode.editStart()


                            },
                            error: function (request, status, error) {

                                alert('fout' + request.responseText);

                            }

                        });





                        break;



                    case "selectall":

                        $("#tree").fancytree("getTree").visit(function(node) {  node.setSelected(true)  }) ;

                        // jQuery select the HTML division in the template with id = tree
                        $("#tree").fancytree("getTree").visit(function(node) {  node.setSelected(true)  }) ;

                        break;

                    case "help":



                        "f2",  "shift+click", "mac+enter"



                        window.alert('To edit the node use F2, shift+click or mac+enter' +
                            '\nTo select the node, double click'+
                                '\nRebuild is used to rebuild corrupted mptt tree data '

                        )

                        break;


                    case "rebuild":

                        tree_changerequest = {
                            source_nodes: [
                                {node_id: 0, node_title: ''}
                            ],
                            target_node: { node_id: node.key, node_title: node.title},
                            method: "REBUILD",
                            hitmode: "",
                            new_id: 0,
                            response: "hold" }


                        tree_changerequest_JSON = JSON.stringify(tree_changerequest);


                        $.ajax({
                            url: tree_services,
                            type: 'POST',
                            async: false,
                            data: tree_changerequest_JSON,
                            datatype: 'json',

                            beforeSend: function (xhr, settings) {
                                // Set Django csrf token
                                var csrftoken = jQuery.cookie('csrftoken');
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            },

                            success: function (data) {

                            },
                            error: function (request, status, error) {

                                alert('fout' + request.responseText);

                            }

                        });



                        break;

                    case "deselect":

                        $("#tree").fancytree("getTree").visit(function(node){  node.setSelected(false)  });
                        break;



                    case "cut":

                        copyPaste(action,node);
                        break;

                    case "copy":



                        var  tree_changerequest = {
                            source_nodes : [ {node_id: 2,node_title: "titel 2"},{node_id: 3, node_title:"titel 3"}],
                            target_node : {node_id: 1,node_title: "titel 1"},
                            method : "COPY",
                            hitmode: "",
                            new_id : 999,
                            response : "hold" }


                        var tree_changerequest_JSON = JSON.stringify(tree_changerequest);



                        $.ajax({
                            url:    tree_services,
                            type: 'POST',
                            async: false,
                            data: tree_changerequest_JSON ,
                            datatype: 'json',


                            beforeSend: function(xhr, settings)
                            {
                                // Set Django csrf token
                                var csrftoken = jQuery.cookie('csrftoken');
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            },

                            success: function(data)
                            {

                            },
                            error: function (request, status, error)
                            {

                                alert('fout'+request.responseText);

                            }

                        });



                    case "paste":


                        if( pasteMode == "cut" ) {


                            // Cut mode: check for recursion and remove source
                            var cb = clipboardNode.toDict(true);
                            if (node.isDescendantOf(cb)) {
                                alert("Cannot move a node to it's sub node.");
                                return;
                            }


                            tree_changerequest = {
                                source_nodes: [
                                    {node_id: clipboardNode.key, node_title: clipboardNode.title}
                                ],
                                target_node: { node_id: node.key, node_title: node.title},
                                method: "PASTE",
                                hitmode: "",
                                new_id: 0,
                                response: "hold" }


                            tree_changerequest_JSON = JSON.stringify(tree_changerequest);


                            $.ajax({
                                url: tree_services,
                                type: 'POST',
                                async: false,
                                data: tree_changerequest_JSON,
                                datatype: 'json',


                                beforeSend: function (xhr, settings) {
                                    // Set Django csrf token
                                    var csrftoken = jQuery.cookie('csrftoken');
                                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                                },

                                success: function (data) {


                                },
                                error: function (request, status, error) {

                                    alert('fout' + request.responseText);

                                }

                            });

                            copyPaste(action, node)
                        }


                        else

                        {alert("copy paste functionnality still to be implemented")}
                        break;

                    default:
                        greeting = "Good evening";
                }
            }
        },


        edit: {
            triggerStart: ["f2",  "shift+click", "mac+enter"],
//            triggerStart: ["f2", "dblclick", "shift+click", "mac+enter"],
            beforeClose: function(event, data){
                // Return false to prevent cancel/save (data.input is available)
            },
            beforeEdit: function(event, data){
                // Return false to prevent edit mode
            },
            close: function(event, data){
                // Editor was removed
            },
            edit: function(event, data){
                // Editor was opened (available as data.input)
            },
            save: function(event, data){
                // Save data.input.val() or return false to keep editor open




                tree_changerequest = {
                    source_nodes : [ {}],
                    target_node : {node_id: data.node.key ,node_title: data.value},
                    method : "CHANGETITLE",
                    hitmode: "",
                    new_id : 0,
                    response : "" }

                tree_changerequest_JSON = JSON.stringify(tree_changerequest);



                $.ajax({
                    url:    tree_services,
                    type: 'POST',
                    async: false,
                    data: tree_changerequest_JSON ,
                    datatype: 'json',


                    beforeSend: function(xhr, settings)
                    {
                        // Set Django csrf token
                        var csrftoken = jQuery.cookie('csrftoken');
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },

                    success: function(data)
                    {

                    },
                    error: function (request, status, error)
                    {

                        alert('fout'+request.responseText);

                    }

                });



            }
        },



        dnd: {
            preventVoidMoves: true, // Prevent dropping nodes 'before self', etc.
            preventRecursiveMoves: true, // Prevent dropping nodes on own descendants
            autoExpandMS: 400,
            dragStart: function(node, data) {
                /** This function MUST be defined to enable dragging for the tree.
                 *  Return false to cancel dragging of node.
                 */
                return true;
            },
            dragEnter: function(node, data) {
                /** data.otherNode may be null for non-fancytree droppables.
                 *  Return false to disallow dropping on node. In this case
                 *  dragOver and dragLeave are not called.
                 *  Return 'over', 'before, or 'after' to force a hitMode.
                 *  Return ['before', 'after'] to restrict available hitModes.
                 *  Any other return value will calc the hitMode from the cursor position.
                 */
                // Prevent dropping a parent below another parent (only sort
                // nodes under the same parent)



//
//
//           if(node.parent !== data.otherNode.parent){
//                 return false;
//                 }
//                 // Don't allow dropping *over* a node (would create a child)
//                 return ["before", "after"];








                return true;
            },
            dragDrop: function(node, data) {
                /** This function MUST be defined to enable dropping of items on
                 *  the tree.
                 */


                    // data.otherNode.moveTo(node, data.hitMode);


                tree_changerequest = {
                    source_nodes: [
                        {node_id: data.otherNode.key, node_title: data.otherNode.title}
                    ],
                    target_node: { node_id: node.key, node_title: node.title},
                    method: "DROP",
                    hitmode: data.hitMode,
                    new_id: 0,
                    response: "hold" }


                tree_changerequest_JSON = JSON.stringify(tree_changerequest);


                $.ajax({
                    url: tree_services,
                    type: 'POST',
                    async: false,
                    data: tree_changerequest_JSON,
                    datatype: 'json',


                    beforeSend: function (xhr, settings) {
                        // Set Django csrf token
                        var csrftoken = jQuery.cookie('csrftoken');
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    },

                    success: function (data) {



                    },
                    error: function (request, status, error) {

                        alert('fout' + request.responseText);

                    }

                });

                data.otherNode.moveTo(node, data.hitMode);





            }
        },


//          source: {
//            url: "{{ tree_json_url }}" ,
//            cache:false
//        },

        source: {
            url: tree_json_url ,
            cache:false
        },


        select: function(event, data)
        {

            $("#echoSelected").text($.map(data.tree.getSelectedNodes(), function(node){ return  node.key ;  }).join(", "));

        }

    })


});







//function initTree($tree, auto_open) {
//    var error_node = null;
//
//    function createLi(node, $li) {
//        // Create edit link
//        var $title = $li.find('.jqtree-title');
//        $title.after('<a href="'+ node.url +'" class="edit">(edit)</a>');
//    }
//
//
//
//    function handleMove(e) {
//
//    }
//
//    function handleLoadFailed(response) {
//
//    }
//
//}
//


//
//
//jQuery(function() {
//    var $tree = jQuery('#tree');
//    var auto_open = $tree.data('auto_open');
//
//    initTree($tree, auto_open);
//});


//    $tree.tree({
//        autoOpen: auto_open,
//        dragAndDrop: true,
//        onCreateLi: createLi,
//        saveState: $tree.data('save_state'),
//        useContextMenu: false,
//        onLoadFailed: handleLoadFailed
//    });
//
//    $tree.bind('tree.move', handleMove);
