odoo.define('custom_module.CustomSum', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderFooter: function (isGrouped) {
            var $footer = this._super.apply(this, arguments);
            var $sumCell = $footer.find('tfoot .o_list_number.o_field_float');

            if ($sumCell.length) {
                // Customize the sum text
                $sumCell.html($sumCell.html() + ' - Custom Text');
            }

            return $footer;
        },
    });
});