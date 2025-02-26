odoo.define('odb_web_list_sequence.ListRenderer', function(require) {
"use strict";

var ListRenderer = require('web.ListRenderer');

ListRenderer.include({
    /**
     * Render all rows. This method should only called when the view is not
     * grouped.
     *
     * @private
     * @returns {jQueryElement[]} a list of <tr>
     */
    _renderRows: function () {
        var rows = this._super.apply(this, arguments);
        this._addSequence(rows);
        return rows;
    },
    _createSeqCell: function(seq){
        var tdClassName = 'oe_read_only o_list_number';
        var $td = $('<td>', { class: tdClassName, tabindex: -1 }).html(seq);
        return $td;
    },
    _addSequence: function(rows){
        var k = 0;
        for(var i=0; i < rows.length; ++i) {
            var j = i + this.state.offset + 1 - k;
            if (rows[i].hasClass('o_is_line_note') || rows[i].hasClass('o_is_line_section')){
                j = '';
                k += 1;
            }
            var $td = this._createSeqCell(j);
            rows[i].prepend($td);
        }
    },
    _renderHeader: function () {
        var $thead = this._super.apply(this, arguments);
        $thead.find('tr').prepend($('<th class="oe_read_only o_list_seq_th">#</th>'));
        return $thead;
    },
    _renderEmptyRow: function(){
        var $tr = this._super.apply(this, arguments);
        if (!this.editable){
            $tr.prepend($('<td class="oe_read_only"/>'));
        }
        return $tr;
    },
    _renderFooter: function(){
        var $tfoot = this._super.apply(this, arguments);
        if (!this.editable){
            $tfoot.find('tr').prepend($('<td class="oe_read_only"/>'));
        }
        return $tfoot;
    },
});
});
