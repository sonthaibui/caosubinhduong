$(window).resize(function() {
    if (screen.width > window.innerWidth) { //zoom In
        if (document.getElementById('search_obj') && document.getElementsByClassName('o_searchview_input')) {
            var browser_height = $(window).height()
            var nav_height = document.getElementsByClassName('o_main_navbar')[0].offsetHeight
            var control_height = document.getElementsByClassName('o_control_panel')[0].offsetHeight
            var chk_height = document.getElementsByClassName('o_searchview_input')[0].offsetHeight

            document.getElementById('search_obj').style.height = (chk_height + 'px')
            var tree_height = browser_height - nav_height - control_height - document.getElementById('search_obj').height + 'px'
            var top = nav_height + control_height + chk_height + 'px'
            document.getElementById('xview_obj').style = 'width:23%;overflow-x: scroll;overflow-y: scroll; position:fixed;bottom:0;left:3%;top:' + top + ';height:' + tree_height
        }
    }
    if (screen.width < window.innerWidth) { // zoom out
        if (document.getElementById('search_obj') && document.getElementsByClassName('o_searchview_input')) {
            var browser_height = $(window).height()
            var nav_height = document.getElementsByClassName('o_main_navbar')[0].offsetHeight
            var control_height = document.getElementsByClassName('o_control_panel')[0].offsetHeight
            var chk_height = document.getElementsByClassName('o_searchview_input')[0].offsetHeight
            document.getElementById('search_obj').style.height = (chk_height + 'px')
            var tree_height = browser_height - nav_height - control_height - document.getElementById('search_obj').height + 'px'
            var top = nav_height + control_height + chk_height + 'px'
            document.getElementById('xview_obj').style = 'width:23%;overflow-x: scroll;overflow-y: scroll; position:fixed;bottom:0;left:3%;top:' + top + ';height:' + tree_height
        }
    }
    if (screen.width == window.innerWidth) { // zoom in => normal // zoom out => normal
        if (document.getElementById('search_obj') && document.getElementsByClassName('o_searchview_input')) {
            var browser_height = $(window).height()
            var nav_height = document.getElementsByClassName('o_main_navbar')[0].offsetHeight
            var control_height = document.getElementsByClassName('o_control_panel')[0].offsetHeight
            var chk_height = document.getElementsByClassName('o_searchview_input')[0].offsetHeight
            document.getElementById('search_obj').style.height = (chk_height + 'px')
            var tree_height = browser_height - nav_height - control_height - document.getElementById('search_obj').height + 'px'
            var top = nav_height + control_height + chk_height + 'px'
            document.getElementById('xview_obj').style = 'width:23%;overflow-x: scroll;overflow-y: scroll; position:fixed;bottom:0;left:3%;top:' + top + ';height:' + tree_height
        }
    }
})

function handleKeyUp() {
    if (document.getElementById('search_obj').value.length == 0) {
        document.getElementById('search_obj').blur()
    }
    fuzzySearch(`xview_obj`, `#search_obj`, null, true)
    document.getElementById('search_obj').blur()
    document.getElementById('search_obj').focus()
}