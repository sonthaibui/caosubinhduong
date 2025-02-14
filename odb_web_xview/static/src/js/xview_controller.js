odoo.define('odb_web_xview.Controller', function(require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    var core = require('web.core');
    var qweb = core.qweb;

    var XViewController = AbstractController.extend({
        custom_events: _.extend({}, AbstractController.prototype.custom_events, {// events from the Odoo JavaScript framework
            'tree_node_clicked': '_onTreeNodeClicked',
            'before_node_expand': '_onBeforeNodeExpand',
        }),
        events: _.extend({}, AbstractController.prototype.events, {//normal JavaScript events
            'keydown .search_item': '_onKeyDownSearchItem',
        }),
        _onKeyDownSearchItem:function(event){
            if (event.keyCode == 13){
                fuzzySearch(`xview_tree`, `#search_item`, null, true)
                document.getElementById('search_item').blur()
                document.getElementById('search_item').focus()
            }

        },
        renderButtons: function ($node) {
            //this.$buttons = $(qweb.render('XView.buttons', {}));
        },
        init: function(parent, model, renderer, params) {
            this.model = model;
            this.renderer = renderer;
            this._super.apply(this, arguments);
           
        },
        /**
         * @returns {Deferred}
         */
        start: function() {
            return this._super();
        },
        _onBeforeNodeExpand: function(event){
            this.model._beforeExpandData(event.data.node_id, event.data.id, event.data.model)
        },
        
        _onTreeNodeClicked: function(event) {
            var self = this;
            if (this.modelName == event.data.model) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: event.data.model,
                    view_type: 'form',
                    view_mode: 'form',
                    res_id: event.data.id,
                    target: 'new',
                    flags: {
                        mode: 'readonly'
                    },
                    views: [
                        [false, 'form']
                    ],
                }).then(function(data) {
                    document.getElementsByClassName('modal o_legacy_dialog o_technical_modal show')[0].className = "o_legacy_dialog o_technical_modal show"
                    document.getElementById('frm_xview').append(document.getElementsByClassName('o_legacy_dialog o_technical_modal show')[0])
                    document.getElementsByClassName('o_legacy_dialog o_technical_modal show')[0].setAttribute('tabindex', '');
                    document.getElementsByClassName('modal-title')[0].innerText = ""
                    document.getElementsByClassName('modal-dialog modal-lg')[0].className = ""
                    document.getElementsByClassName('modal-footer')[0].style = "position:absolute;top:0;left:-1%;margin-top:-1%"

                    if (document.getElementsByClassName('o_MessageList o_ThreadView_messageList')[0] !== undefined) {
                        var x = document.getElementsByClassName('clearfix position-relative o_form_sheet')[0].offsetHeight
                        var fx = x - x * 5 / 100
                        document.getElementsByClassName('o_MessageList o_ThreadView_messageList')[0].style = "height:" + fx + 'px'
                    }
                    var button = document.getElementsByClassName('modal-footer')[0]
                    button.className=""
                    button.style=""
                    document.getElementsByClassName('o_cp_buttons')[0].innerHTML=""
                    document.getElementsByClassName('o_cp_buttons')[0].append(button)
                    document.getElementsByClassName('modal-header')[0].style.display="none"
                });
            }
        }

    });

    return XViewController;

});