// chinh_pivot/static/src/js/pivot_view.js
odoo.define('custom_pivot_view.PivotViewAdjustments', function (require) {
    "use strict";
    var PivotView = require('web.PivotView');
    PivotView.include({
        _renderHeaderCell: function (header, colIndex, colspan) {
            var $th = this._super.apply(this, arguments);
            $th.addClass('o_pivot_header_cell');
            return $th;
        },
    });
    return PivotView;
});