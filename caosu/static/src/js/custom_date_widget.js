odoo.define('caosu.CustomDateWidget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var CustomDateWidget = AbstractField.extend({
        supportedFieldTypes: ['date'],
        
        _render: function () {
            if (!this.value) {
                this.$el.text('');
                return;
            }
            var formatted = moment(this.value).format('DD.MM');
            this.$el.text(formatted);
        }
    });

    field_registry.add('custom_date', CustomDateWidget);
    return CustomDateWidget;
});