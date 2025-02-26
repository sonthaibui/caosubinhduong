odoo.define("mana_dashboard.template_widget", function (require) {
    "use strict";
    
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var filed_registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var config = require('web.config')

    var qweb = core.qweb;

    var template_widget = AbstractField.extend({

        events: _.extend({}, AbstractField.prototype.events, {
            'click .o_menu_item': '_onItemClick',
        }),

        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            if (!this.nodeOptions.template) {
                console.log(
                    "the template for template widget is undfined, please set the template attrs"
                );
            }
        },

        trigger_button: function (e) {
            e.stopPropagation();
            e.preventDefault();

            var self = this;
            var controller = this.getParent().getParent();

            if (controller._callButtonAction) {
                var param = {
                    type: $(e.currentTarget).attr("type"),
                    name: $(e.currentTarget).attr("name")
                };
                if ($(e.currentTarget).attr("context")) {
                    param.context = JSON.parse($(e.currentTarget).attr("context"));
                }
                controller._callButtonAction(param, this.record).then(function (rst) {
                    if (!rst) {
                        self.trigger_up("reload");
                    } else if (rst.reload_domain) {
                        controller.reload({ "domain": rst.reload_domain })
                    }
                });
            } else {
                self.trigger_up("button_clicked", {
                    attrs: {
                        type: $(e.currentTarget).attr("type"),
                        name: $(e.currentTarget).attr("name")
                    },
                    record: this.record
                });
            }
        },

        start: function () {
            return this._super.apply(this, arguments).then(() => {
                this.$("button").on("click", this._button_clicked.bind(this))
            });
        },

        _button_clicked: function (event) {
            var confirm = $(event.currentTarget).attr("confirm")
            if (confirm) {
                event.stopPropagation();
                Dialog.confirm(this, confirm, {
                    confirm_callback: () => {
                        this.trigger_button(event)
                        this.destroy()
                    }
                });
            } else {
                this.trigger_button(event)
            }
        },

        isSet: function () {
            return true
        },

        _render: function () {
            var $el = undefined;
            if (this.nodeOptions.template) {
                $el = $(qweb.render(this.nodeOptions.template, { widget: this, record: this.record, debug: config.debug }));
                this._replaceElement($el);
            } else {
                $el = this._super.apply(this)
            }
            this.$('.dropdown-toggle').dropdown()
        },

        _onItemClick: function (event) {
            event.preventDefault();
            event.stopPropagation();
        },
    });

    filed_registry.add("template_widget", template_widget);
    return template_widget
});
