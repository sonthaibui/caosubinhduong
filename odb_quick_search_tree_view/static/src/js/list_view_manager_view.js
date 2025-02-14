odoo.define('odb_quick_search_tree_view.ks_lvm_view', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({

        getRenderer: function () {
            this.rendererParams = _.extend({},{'ks_lvm_data':this.fieldsView.ks_lvm_user_data || false},this.rendererParams);
            return this._super.apply(this, arguments);
        },

        getController: function () {
            this.controllerParams = _.extend({},{'ks_lvm_data':this.fieldsView.ks_lvm_user_data || false},this.controllerParams);
            return this._super.apply(this, arguments);
        },

    });

});


