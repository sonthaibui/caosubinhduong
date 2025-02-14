odoo.define('odb_web_xview.View', function(require) {
    "use strict";

    var AbstractView = require('web.AbstractView');
    var view_registry = require('web.view_registry');
    var XViewController = require('odb_web_xview.Controller');
    var XViewModel = require('odb_web_xview.Model');
    var XViewRenderer = require('odb_web_xview.Renderer');


    var XView = AbstractView.extend({
        display_name: 'XView',
        icon: 'fa-tree',
        cssLibs: [
            '/odb_web_xview/static/src/libs/bootstrapStyle.css',
        ],
        jsLibs: [
            '/odb_web_xview/static/src/libs/jquery.xview.core.js',
            '/odb_web_xview/static/src/libs/jquery.xview.exhide.js',
            '/odb_web_xview/static/src/libs/jquery.ztree.excheck.js',
            '/odb_web_xview/static/src/js/xview_script.js',
            '/odb_web_xview/static/src/libs/fuzzySearch.js',
        ],
        config: _.extend({}, AbstractView.prototype.config, {
            Model: XViewModel,
            Controller: XViewController,
            Renderer: XViewRenderer,
        }),
        viewType: 'xview',
        groupable: false,
    
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);

            this.field_related = this.arch.attrs.field_related;
            this.parent_id = this.arch.attrs.parent_id;

            // Model Parameters
            this.loadParams.model = this.model;
            this.loadParams.fields = viewInfo.fields;
            this.loadParams.viewFields = viewInfo.viewFields;
            this.loadParams.field_related = this.field_related;
            this.loadParams.parent_id = this.parent_id;

            this.rendererParams.fields = this.loadParams.fields;
            this.rendererParams.modelName = this.loadParams.modelName;
            this.rendererParams.viewFields = this.loadParams.viewFields;

            this.rendererParams.field_related = this.field_related;
            this.rendererParams.parent_id = this.parent_id;

            // Controller Parameters
            // this.controllerParams.measures = _.omit(measures, '__count__');
        },

    });

    view_registry.add('xview', XView);
    return XView;
});