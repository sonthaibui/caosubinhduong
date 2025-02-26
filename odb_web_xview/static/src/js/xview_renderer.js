odoo.define('odb_web_xview.Renderer', function (require) {
    "use strict";

    var AbstractRenderer = require('web.BasicRenderer');
    var core = require('web.core');
    var qweb = core.qweb;

    var XViewRenderer = AbstractRenderer.extend({
        events: _.extend({}, AbstractRenderer.prototype.events, {
            // 'click .o_search_web_report': '_xViewOnClick',
        }),
        // INNER_GROUP_COL: 2,
        // OUTER_GROUP_COL: 2,
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.fields = params.fields;
            this.field_related = params.field_related;
            this.parent_id = params.parent_id;

            this.viewFields = params.viewFields;
            this.className = '';
            this.modelName = params.modelName;
            this.idsForLabels = {};

        },
        _render: function () {
            this.$el.html(qweb.render('xview.Template', {}))
            document.body.style = "overflow-x:hidden"
            var self = this
            self.$el.css({
                //'display': "flex",
                'margin-left': '0.5%',
                'height': '100%'
                // 'margin-right':'1%',
            });
            self.$el[0].parentNode.style = "overflow-x:hidden"
            self.$el[0].className = "row"
            var xViewObj
            var setting = {
                callback: {
                    beforeExpand: self._xViewOnBeforeExpand.bind(self),
                    onClick: self._xViewOnClick.bind(self),
                },
                check: {
                    enable: false, //checkbox
                    chkStyle: "checkbox",
                    chkboxType: { "Y" : "", "N" : "" }
                },
                edit: {
                    enable: true,
                    editNameSelectAll: false
                },
                data: {
                    simpleData: {
                        enable: true
                    }
                }
            },
            xViewObj = $.fn.zTree.init(self.$el.children().eq(0), setting, self.state.xViewNodes);
            if(document.getElementById('search_item') === null){
                var input = document.createElement("input");
                input.setAttribute('type','text')
                input.setAttribute('placeholder','Filter')
                input.id = "search_item"
                input.className="form-control border border-primary search_item"
                input.style="height: 3.5% !important; position:sticky;top:0;z-index:2"
                var list = self.$el.children().eq(0)[0];
                list.insertBefore(input, list.childNodes[0]);
            }
        },
        _xViewOnDrag: function (event, treeId, treeNode) {
            alert('Drag')
        },
        _xViewOnClick: function (event, treeId, treeNode) {
            this.trigger_up('tree_node_clicked', {
                id: treeNode.id,
                model: treeNode.model,
            });
        },
        _xViewOnBeforeExpand: function (treeId, treeNode) {
            this.trigger_up('before_node_expand', {
                id: treeNode.id,
                model: treeNode.model,
                node_id: event.target.id
            });
        },
        _onExpand: function (event, treeId, treeNode) {
            this.trigger_up('expand_node', {
                treeNode: treeNode
            });
        }

    });

    return XViewRenderer;

});