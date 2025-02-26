odoo.define('odb_account_dynamic_report.DynamicReports', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var Context = require('web.Context');
    var Dialog = require('web.Dialog');
    var datepicker = require('web.datepicker');
    var session = require('web.session');
    var field_utils = require('web.field_utils');
    var RelationalFields = require('web.relational_fields');
    var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
    var { WarningDialog } = require("@web/legacy/js/_deprecated/crash_manager_warning_dialog");
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var rpc = require("web.rpc");

	var balance_sheet_fields = {
		'name': 'Name',
		'debit': 'Debit',
		'credit': 'Credit',
		'balance': 'Balance',
        'analytic_account': 'Analytic Account',
	};
    var journals_audit_fields = {
        'move_id': 'Move',
        'date': "Date",
        'account_id': "Account",
        'partner_id': 'Partner',
        'name': 'Label',
        'analytic_account_id': 'Analytic Account',
        'debit': 'Debit',
        'credit': 'Credit',
    };

    var p_ledger_fields = {
        'date': 'Date',
        'code': 'JRNL',
        'a_code': 'Account',
        'displayed_name': 'Ref',
        'analytic_account_id': 'Analytic Account',
        'debit': 'Debit',
        'credit': 'Credit',
        'balance': 'Balance',
        'progress': 'Progress',
        'cumulated_balance': 'Cumulated Balance',
    };
    var g_ledger_fields = {
        'ldate': 'Date',
        'lcode': 'JRNL',
        'partner_name': 'Partner',
        'lref': 'Ref',
        'move_name': 'Move',
        'lname': 'Entry Label',
        'analytic_account_id': 'Analytic Account',
        'debit': 'Debit',
        'credit': 'Credit',
        'balance': 'Balance',
    };

    var trial_balance_fields = {
        'code': 'Code',
        'name': 'Account',
        'analytic_account_id': 'Analytic Account',
        'debit': 'Debit',
        'credit': 'Credit',
        'balance': 'Balance',
    };
    var aged_partner_fields = {
        'name': 'Partners',
        'direction': 'Not due',
        'l4': 'Credit',
        'l3': 'Balance',
        'l2': 'Balance',
        'l1': 'Balance',
        'l0': 'Balance',
        'total': 'Total',
    };
    var tax_report_fields = {
        'name': 'Partners',
        'net': 'Net',
        'tax': 'Tax'
    };

    var M2MFilters = Widget.extend(StandaloneFieldManagerMixin, {
        /**
         * @constructor
         * @param {Object} fields
         */
        init: function (parent, fields) {
            this._super.apply(this, arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.fields = fields;
            this.widgets = {};
        },
        /**
         * @override
         */
        willStart: function () {
            var self = this;
            var defs = [this._super.apply(this, arguments)];
            _.each(this.fields, function (field, fieldName) {
                defs.push(self._makeM2MWidget(field, fieldName));
            });
            return Promise.all(defs);
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var $content = $(QWeb.render("m2mWidgetTable", {fields: this.fields}));
            self.$el.append($content);
            _.each(this.fields, function (field, fieldName) {
                self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
            });
            return this._super.apply(this, arguments);
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * This method will be called whenever a field value has changed and has
         * been confirmed by the model.
         *
         * @private
         * @override
         * @returns {Promise}
         */
        _confirmChange: function () {
            var self = this;
            var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
            var data = {};
            _.each(this.fields, function (filter, fieldName) {
                data[fieldName] = self.widgets[fieldName].value.res_ids;
            });
            this.trigger_up('value_changed', data);
            return result;
        },
        /**
         * This method will create a record and initialize M2M widget.
         *
         * @private
         * @param {Object} fieldInfo
         * @param {string} fieldName
         * @returns {Promise}
         */
        _makeM2MWidget: function (fieldInfo, fieldName) {
            var self = this;
            var options = {};
            options[fieldName] = {
                options: {
                    no_create_edit: true,
                    no_create: true,
                }
            };
            return this.model.makeRecord(fieldInfo.modelName, [{
                fields: [{
                    name: 'id',
                    type: 'integer',
                }, {
                    name: 'display_name',
                    type: 'char',
                }],
                name: fieldName,
                relation: fieldInfo.modelName,
                type: 'many2many',
                value: fieldInfo.value,
            }], options).then(function (recordID) {
                self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                    fieldName,
                    self.model.get(recordID),
                    {mode: 'edit',}
                );
                self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
            });
        },
    });

    var DynamicReportAction = AbstractAction.extend({
        events: {
            'click .fetch_report_btn': '_getReportContent',
            'change select, input': 'onChangeReportData',
            'click tr.r_line': 'toggleReportLine',
            'click .js_account_report_foldable': 'fold_unfold',
            'click .report_buttons div': 'printReport',
            'click .o_account_reports_footnote_icons': 'delete_footnote',
            'click .js_account_reports_add_footnote': 'add_edit_footnote',
            'click .js_account_reports_get_analytic_entries': '_getAnalyticEntries',
            'click .display_currency_unit': 'onChangeSymbolCurrency',
        },
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.report_type = [];
            this.fixed_reports = [];
            this.journal_ids = [];
            this.analytic_account_ids = [];
            this.buttons = [];
            this.report_data = {};
            this.line_count = 0;
            this.current_level = 0;
            this.previous_level = 0;

            this.report_lines = {};
            this.report_line_ids = {};
            this.line_status = {};
            this.levels = {};
            this.currency_data = {};
            this.financial_id = false;
        },
        willStart: function () {
            var self = this;
            var def = [];
            var report_def = rpc.query({
                model: 'account.financial.report',
                method: 'search_read',
                fields: ['name'],
                domain: [['parent_id', '=', false]]
            }).then(function (result) {
                self.report_type = result;
                for (var i=0;i<result.length;i++) {
                    result[i].type = 'config';
                }

                var other_reports = self._fetchOtherReports();

                self.fixed_reports = $.map(other_reports, function(rec) {
                    return rec.id;
                });

                self.report_type = self.report_type.concat(other_reports);
            });

            var config_def = rpc.query({
                model: 'account.journal',
                method: 'search_read',
                fields: ['name']
            }).then(function (result) {
                self.journal_ids = result;
            });
            var config_analytic_account = rpc.query({
                model: 'account.analytic.account',
                method: 'search_read',
                fields: ['name']
            }).then(function (result) {
                self.analytic_account_ids = result;
            });
            return Promise.all([
                this._super.apply(this, arguments),
                report_def,config_def,config_analytic_account,
            ]);
            // return $.when($, report_def, config_def);
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments).then(function () {
                self._updateReportController();
            });
        },
        _updateReportController: function () {
            this.$el.html(
                QWeb.render('odb_account_dynamic_report.DynamicReports', {
                    'widget': this
                }
            ));

            this.$el.find('select').select2();

            this.$el.find('.report_buttons').hide();
            this.$el.find('.panel-bottom').hide()
        },
        /*events*/
        _fetchOtherReports: function () {
            return [{
                id: 'journals_audit',
                name: 'Journals Audit',
                type: 'fixed'
            }, {
                id: 'partner_ledger',
                name: 'Partner Ledger',
                type: 'fixed'
            }, {
                id: 'general_ledger',
                name: 'General Ledger',
                type: 'fixed'
            }, {
                id: 'trial_balance',
                name: 'Trial Balance',
                type: 'fixed'
            }, {
                id: 'aged_partner',
                name: 'Aged Partner Balance',
                type: 'fixed'
            }, {
                id: 'tax_report',
                name: 'Tax Report',
                type: 'fixed'
            }];
        },
        parse_reports_informations: function(values) {
            this.report_options = values.options;
            this.odoo_context = values.context;
            this.report_manager_id = values.report_manager_id;
            this.footnotes = values.footnotes;
            this.buttons = values.buttons;
    
            this.main_html = values.main_html;
            this.$searchview_buttons = $(values.searchview_html);

            this.odoo_context.model = 'account.analytic.report';
            if (values.context.id) {
                this.odoo_context.financial_id = values.context.id;
            }
            this.persist_options();
        },
        persist_options: function() {
            if ((this.ignore_session === 'write' || this.ignore_session === 'both') !== true) {
                var persist_key = 'report:'+this.report_model+':'+this.financial_id+':'+session.company_id;
                sessionStorage.setItem(persist_key, JSON.stringify(this.report_options));
            }
        },
        onChangeReportData: function (e) {
            var self = this;
            var active_el = $(e.currentTarget);

			this.strict_range = true;
			if (active_el.attr('name') == 'account_report_id') {
                if (!active_el.val()) {
                    this.report_data = {};
                    this.$el.find('.report_buttons').hide();
                }
                else {
                    this.report_data.account_report_id = [
                        active_el.val(),
                        this._getReportName(active_el.val())];
                    switch (active_el.val()) {
                        case 'journals_audit': {
                            this.$el.find('.ctrl_body').replaceWith($(QWeb.render('journals_audit', {widget: this})));
                            this.$el.find('.buttons_search').hide();
                            this.$el.find('.buttons_anlytic').hide();
                            this.addField('target_move', 'select');
                            this.addField('sort_selection', 'select');
                            this.addField('date_from', 'input');
                            this.addField('date_to', 'input');
                            this.addField('journal_ids', 'select');
                            this.addField('account_analytic_ids', 'select');

                            break;
                        };
                        case 'partner_ledger': {
                            this.$el.find('.ctrl_body').replaceWith($(QWeb.render('partner_ledger', {widget: this})));

                            this.addField('target_move', 'select');
                            this.addField('result_selection', 'select');
                            this.addField('reconciled', 'checkbox');
                            this.addField('date_from', 'input');
                            this.addField('date_to', 'input');
                            this.addField('journal_ids', 'select');

                            break;
                        };
                        case 'general_ledger': {
                            this.$el.find('.ctrl_body').replaceWith($(QWeb.render('general_ledger', {widget: this})));

                            this.addField('target_move', 'select');
                            this.addField('sortby', 'select');
                            this.addField('display_account', 'select');
                            this.addField('initial_balance', 'checkbox');
                            this.addField('date_from', 'input');
                            this.addField('date_to', 'input');
                            this.addField('journal_ids', 'select');
                            this.addField('account_analytic_ids', 'select');

                            break;
                        };
                        case 'trial_balance': {
                            this.$el.find('.ctrl_body').replaceWith($(QWeb.render('trial_balance', {widget: this})));

                            this.addField('target_move', 'select');
                            this.addField('display_account', 'select');
                            this.addField('date_from', 'input');
                            this.addField('date_to', 'input');
                            this.addField('account_analytic_ids', 'select');
                            break;
                        };
                        case 'aged_partner': {
                            this.$el.find('.ctrl_body').replaceWith($(QWeb.render('aged_partner', {widget: this})));

                            this.addField('target_move', 'select');
                            this.addField('result_selection', 'select');
                            this.addField('date_from', 'input');
                            this.addField('period_length', 'input');

                            this.$el.find('.ctrl_body .date_from').addClass('o_required');
                            this.$el.find('.ctrl_body .period_length').addClass('o_required');

                            break;
                        };
                        case 'tax_report': {
                            this.$el.find('.ctrl_body').replaceWith($(QWeb.render('tax_report', {widget: this})));
                            this.addField('date_from', 'input');
                            this.addField('date_to', 'input');
                            this.addField('target_move', 'select');
                            this.addField('account_analytic_ids', 'select');

							this.$el.find('.ctrl_body .date_from').addClass('o_required');
                            this.$el.find('.ctrl_body .date_to').addClass('o_required');

                            break;
                        };
                        
                        default: {
                            if (this._getReportName(active_el.val()) == 'Analytic Report') {
                                var pr_pos = $('.ctrl_body')
                                var ch_pos = pr_pos.find('.h_row')
                                if (pr_pos[0].childElementCount > 1){
                                    pr_pos[0].lastElementChild.remove();
                                }
                                for (var i = 0; i < ch_pos[0].childNodes.length; i++){
                                    if(i%2 != 0){
                                        ch_pos[0].childNodes[i].style.display = "none";
                                    }
                                }
                                ch_pos[0].childNodes[1].style.display = 'inline';
                                self.$el.find('.report_buttons').hide();
                            } else {
                                this.$el.find('.ctrl_body').replaceWith($(QWeb.render('profit_loss', {widget: this})));
                                this.$el.find('.buttons_search').hide()
                                this.$el.find('.buttons_anlytic').hide()
                                this.addField('target_move', 'select');
                                this.addField('debit_credit', 'checkbox');
                                this.addField('date_from', 'input');
                                this.addField('date_to', 'input');
                                this.addField('account_analytic_ids', 'select');
                            }
                        };
                    };

                    this.$el.find('select.account_report_id').val(this.report_data.account_report_id[0]);
                }
                this.$el.find('select').select2();
            }

			else {
	            /*caching the changed value*/
	            if (active_el.attr('type') == 'checkbox') {
	                this.report_data[active_el.attr('name')] = active_el.is(":checked");
	            }
	            else if (active_el.attr('name') == 'journal_ids') {
	                this.report_data[active_el.attr('name')] = [];
	                _.each(active_el.val(), function (val) {
	                    self.report_data[active_el.attr('name')].push(parseInt(val));
	                });
	            }
	            else {
	                this.report_data[active_el.attr('name')] = active_el.val();
	            }
            }
        },
        addField: function (name, type) {
            var self = this;
            if (name == 'journal_ids') {
                this.report_data[name] = [];
                _.each(this.$el.find('.dynamic_control_header select.journal_ids').val(), function (val) {
                    self.report_data[name].push(parseInt(val));
                });
            }
            else if (name == 'date_from' || name == 'date_to') {
                this.report_data[name] = this.$el.find('.dynamic_control_header .'+name).val();
            }
            else if (type == 'checkbox') {
                this.report_data[name] = this.$el.find('.dynamic_control_header .' + name).is(":checked");
            }
            else if (type == 'select') {
                this.report_data[name] = this.$el.find('.dynamic_control_header select.'+name).val();
            }
            else {
                this.report_data[name] = this.$el.find('.dynamic_control_header .'+name).val();
            }
        },
        toggleReportController: function (e) {
            this.$el.find('.dynamic_control_header .h_row').toggleClass('hidden');

            this.$el.find('.dynamic_control_header .h_row.ctrl').toggleClass('hidden ');

            var active_el = $(e.currentTarget);
            active_el.toggleClass('fa-angle-up');
            active_el.toggleClass('fa-angle-down');
        },
        toggleReportLine: function (e) {
            var active_el = $(e.currentTarget);

            var parent_id = parseInt(active_el.data('id'));

            /*child status*/
            if (this.line_status[parent_id] == 'open') {
                this.line_status[parent_id] = 'closed';

                this._hideChildren(parent_id);
            }
            else if (this.line_status[parent_id] == 'closed') {
                this.line_status[parent_id] = 'open';
                this._showChildren(parent_id);
            }

            if (active_el.attr('res_id')) {
                return this.openJournalItem(active_el.attr('res_id'));
            }
        },

        /*other methods*/
        openJournalItem: function (res_id) {
            if (isNaN(res_id) || parseInt(res_id) < 1) {
                return;
            }
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'account.move.line',
                views: [[false, 'form']],
                target: 'current',
                res_id: parseInt(res_id)
            });
        },
        _getReportName: function (r_id) {
            if (!r_id) {
                return "";
            }
            else {
                var r_name = "";

                for (var i=0;i<this.report_type.length;i++) {
                    if (this.report_type[i].id == r_id) {
                        r_name = this.report_type[i].name;
                        break;
                    }
                }

                return r_name;
            }
        },
        _showChildren: function (parent_id) {
            var child_ids = [];
            var line_length = this.line_count;
            this.toggleCaretIcon(parent_id);

            for (var i=parent_id + 1;i<=line_length;i++) {
                if (this.report_lines[i].parent == parent_id) {
                    child_ids.push(this.report_lines[i].id);

                    this.$el.find('tr[data-id="'+this.report_lines[i].id+'"]').show();

                }
            }
        },
        _hideChildren: function (parent_id) {
            var child_ids = [];
            var line_length = this.line_count;
            if (this.report_line_ids[parent_id]) {
                this.toggleCaretIcon(parent_id);
            }

            for (var i=parent_id + 1;i<=line_length;i++) {
                if (this.report_lines[i].parent == parent_id) {
                    child_ids.push(this.report_lines[i].id);

                    var $tr = this.$el.find('tr[data-id="'+this.report_lines[i].id+'"]');
                    $tr.hide();
                    /*check inner childs*/
                    if (this.line_status[this.report_lines[i].id] == 'open') {
                        this.line_status[this.report_lines[i].id] = 'closed';
                        this._hideChildren(this.report_lines[i].id);
                    }
                }
            }
        },
        toggleCaretIcon: function (parent_id) {
            var parent_el = this.$el.find("tr[data-id='"+parent_id+"']");
            var $td = $(parent_el.find('td')[0]);
            $td.find('i').toggleClass('fa-caret-right');
            $td.find('i').toggleClass('fa-caret-down');
            return;
        },
        _getReportContent: function (e) {
            var self = this;

            var data = this._getReportInput();
            self.current_report_data = Object.assign({}, {});
            if (data) {
                if (data.account_report_id[1] == 'Analytic Report') {
                    rpc.query({
                        model: 'dynamic.report.config',
                        method: 'check_report',
                        args: [data]
                    }).then(function (result) {
                        if ($('.table_r_content').length > 0) {
                            $('.report_buttons').hide();
                            $('.dynamic_report_body').hide();
                            $('.r_analytic').show();
                        }
                        $('.buttons_anlytic').show();
                        $('.buttons_search').show();
                        self.parse_reports_informations(result[0])
                        self.render()
                    });
                } else {
                    rpc.query({
                        model: 'dynamic.report.config',
                        method: 'check_report',
                        args: [data]
                    }).then(function (result) {
                        if ($('.r_analytic').length > 0 ){
                            $('.r_analytic').hide()
                            $('.col_body_options').hide()
                            $('.buttons_anlytic').hide();
                            $('.dynamic_report_body').show()
                        }
                        self.current_report_data = Object.assign({}, self.report_data);
                        self.currency_data = result[1];
                        self.updateReportBody(result[0]);
    
                        self.updateResizable();
    
                        self.$el.find('.report_buttons').show();

                        if ($('.display_currency_unit')[0].checked) {
                            $('.symbol_currency').show();
                        } else {
                            $('.symbol_currency').hide();
                        }
                    });
                }
            }
        },
        getCurrentReport: function () {
            if (!this.report_data.account_report_id) {
                alert("No report selected");
                return;
            }
            for (var i=0;i<this.report_type.length;i++) {
                if (this.report_type[i].id == this.report_data.account_report_id[0]) {
                    return this.report_type[i];
                }
            }

            alert("Error occurred, please try again");
            return;
        },
        checkRequiredFields: function () {
            var $el = this.$el.find('.dynamic_control_header .o_required');

			var fields_missing = false;
            for (var i=0;i<$el.length;i++) {
                var el_name = $($el[i]).attr('name');
                if (!el_name) {continue;}
                if (!$($el[i]).val()) {
                    fields_missing = true;
                    if ($($el[i]).hasClass('select_2')) {
                        this.$el.find('.dynamic_control_header .' + el_name).css('border', '1px solid red');
                    }
                    else {
                        $($el[i]).css('border', '1px solid red');
                    }
                }
                else {
                    if ($($el[i]).hasClass('select_2')) {
                        this.$el.find('.dynamic_control_header .' + el_name).css('border', '1px solid #aaa');
                    }
                    else {
                        $($el[i]).css('border', '1px solid #aaa');
                    }
                }
            }

            return fields_missing;
        },
        _getReportInput: function () {
            if (this.checkRequiredFields()) {
                return false;
            }

            var report = this.getCurrentReport();

            this.report_data.company_id = [1, 'YourCompany'];
            this.report_data.filter_cmp = 'filter_no';
            this.report_data.enable_filter = false;
            this.report_data.label_filter = false;

            this.report_data.date_from_cmp = false;
//            this.report_data.debit_credit = false;
            this.report_data.date_to_cmp = false;

            this.report_data.date_from = this.report_data.date_from ? this.report_data.date_from : false;
            this.report_data.date_to = this.report_data.date_to ? this.report_data.date_to : false;

            this.report_data.used_context = {
                'journal_ids': this.report_data.journal_ids,
                'state': this.report_data.target_move,
                'result_selection': this.report_data.result_selection,
                'reconciled': this.report_data.reconciled,
                'date_from': this.report_data.date_from,
                'date_to': this.report_data.date_to,
                'strict_range': this.strict_range,
                'company_id': this.report_data.company_id[0],
                'analytic_account': this.report_data.analytic_account,
            };

            if (report && report.type == 'config') {
                /*P & L or Balance sheet*/
                /*doing nothing right now*/
                this.report_data.report_type = 'config';
            }
            else {
                /*other reports*/
                this.report_data.report_type = 'fixed';
                this.report_data.amount_currency = true;
            }


            return this.report_data;
        },
        _findParent: function (index, req_type, o_index) {
            /*reverse parse the lines and find immediate parent*/
            if (index == 0 && !req_type) {
                return false;
            }
            else if (index == 0 && req_type == 'recursive') {
                return this.report_lines[0].id;
            }

            for(var i=index-1;i>=0;i--) {
                if (this.report_lines[i].level < this.report_lines[index].level &&
                        this.report_lines[i].level < this.report_lines[o_index].level) {
                    return this.report_lines[i].id;
                }
                else {
                    return this._findParent(i, 'recursive', o_index);
                }
            }

            return false;
        },
        _processData: function (report_lines, report_type) {
            this.report_lines = {};
            this.report_line_ids = {};
            this.line_count = 0;

            if (report_type == 'fixed') {
                var report_id = this.report_data.account_report_id[0];

                switch (report_id) {
                    case 'journals_audit': this._process_journals_audit(report_lines); break;
                    case 'partner_ledger': this._process_partner_ledger(report_lines); break;
                    case 'general_ledger': this._process_general_ledger(report_lines); break;
                    case 'trial_balance': this._process_trial_balance(report_lines); break;
                    case 'aged_partner': this._process_aged_partner(report_lines); break;
                    case 'tax_report': this._process_tax_report(report_lines); break;
                    default : {};
                };
            }
            else {
                for (var i=0;i<report_lines.length;i++) {
                    report_lines[i].id = i;
                    report_lines[i].level = parseInt(report_lines[i].level);

                    this.report_lines[i] = report_lines[i];
                }

                this.line_count = i > 0 ? (i -1) : 0;

                for (var i in this.report_lines) {
                    this.report_lines[i].parent = this._findParent(i, null, i);

                    /*keeping the hierarchy of ids as well, so that
                    we can handle easily*/
                    this.report_line_ids[report_lines[i].parent] = i;
                }
            }

            return;
        },
        _build_root_line: function (colspan) {
            this.report_lines[0] = {
                id: 0,
                parent: false,
                title: this.report_data.account_report_id[1],
                level:0,
                res_id: -1,
                colspan: colspan,
                line_type: 'root'
            };
            this.report_line_ids[false] = 0;
        },
        _process_trial_balance: function (report_lines) {
            this._build_root_line(2);
            /*sum of debit credit and balance columns*/
            this.report_lines[0] = Object.assign(this.report_lines[0], {
                analytic_account_id: '',
                debit: 0,
                credit: 0,
                balance: 0,
            });

            for (var l=0;l<report_lines.length;l++) {
                if (report_lines[l].line_type == 'total') {
                    this.report_lines[0]['analytic_account_id'] = report_lines[l].analytic_account_id;
                    this.report_lines[0]['debit'] = report_lines[l].total_debit;
                    this.report_lines[0]['credit'] = report_lines[l].total_credit;
                    this.report_lines[0]['balance'] = report_lines[l].total_balance;
                }
            }

            this.line_count++;
            this.report_lines[this.line_count] = Object.assign(
                {},
                trial_balance_fields)

            this.report_lines[this.line_count].id = this.line_count;
            this.report_lines[this.line_count].parent = 0;
            this.report_lines[this.line_count].level = 1;
            this.report_lines[this.line_count].res_id = -1;
            this.report_lines[this.line_count].line_type = 'section_heading';

            this.report_line_ids[0] = this.line_count;
			var parent_id = 0, l_id;
            for (var i=0;i<report_lines.length;i++) {
                this.line_count++;


                report_lines[i].id = this.line_count;


                this.report_lines[this.line_count] = report_lines[i];
                if (report_lines[i].level == 1) {
                    l_id = 	this.line_count;
                    report_lines[i].parent = parent_id;
                    this.report_line_ids[parent_id] = this.line_count;
                }
                else {
                    report_lines[i].parent = l_id;
                    this.report_line_ids[l_id] = this.line_count;
                }
            }
        },
        _process_aged_partner: function (report_lines) {
            this._build_root_line(8);

            for (var i=0;i<report_lines.length;i++) {
                this.line_count++;

                report_lines[i].level = 1;

                this.report_lines[this.line_count] = report_lines[i]
                this.report_line_ids[0] = this.line_count;
            }
        },
        _process_tax_report: function (report_lines) {
            this._build_root_line(3);

            for (var i=0;i<report_lines.length;i++) {
                this.line_count++;
                this.report_lines[this.line_count] = report_lines[i]
                this.report_line_ids[0] = this.line_count;
            }
        },
        _process_partner_ledger: function (report_lines) {
            this._build_root_line(7);

            this.line_count++;
            this.report_lines[this.line_count] = Object.assign(
                {},
                p_ledger_fields)

            /*because in the child lines, the field name is 'progress'*/
            delete this.report_lines[this.line_count].progress;

            this.report_lines[this.line_count].id = this.line_count;
            this.report_lines[this.line_count].line_type = 'font_bold';
            this.report_lines[this.line_count].parent = 0;
            this.report_lines[this.line_count].level = 0;
            this.report_lines[this.line_count].res_id = -1;

            this.report_line_ids[0] = this.line_count;

            var parent_id = 0;

            for (var i=0;i<report_lines.length;i++) {
                this.line_count++;

                if (report_lines[i].line_type == 'section_heading') {
                    report_lines[i].id = this.line_count;
                    report_lines[i].parent = 0;
                    report_lines[i].level = 0;
                    report_lines[i].res_id = -1;

                    this.report_lines[this.line_count] = report_lines[i]
                    this.report_line_ids[0] = this.line_count;

                    parent_id = this.line_count;
                }
                else {
                    report_lines[i].res_id = report_lines[i].id;
                    report_lines[i].id = this.line_count;
                    report_lines[i].parent = parent_id;
                    report_lines[i].level = 1;

                    this.report_lines[this.line_count] = report_lines[i]
                    this.report_line_ids[parent_id] = this.line_count;
                }
            }
        },
        _process_general_ledger: function (report_lines) {
            this._build_root_line(9);

            this.line_count++;
            this.report_lines[this.line_count] = Object.assign(
                {},
                g_ledger_fields)

            this.report_lines[this.line_count].id = this.line_count
            this.report_lines[this.line_count].parent = 0
            this.report_lines[this.line_count].level = 0
            this.report_lines[this.line_count].res_id = -1
            this.report_lines[this.line_count].line_type = 'font_bold'

            this.report_line_ids[0] = this.line_count;

            var parent_id = 0;

            for (var i=0;i<report_lines.length;i++) {
                this.line_count++;

				var temp_line = {
					id: this.line_count,
					parent: 0,
					level: 0,
					res_id: -1,
					line_type: "section_heading",
					ldate: report_lines[i].code + " " + report_lines[i].name,
                    analytic_account_id: '',
					debit: report_lines[i].debit,
					credit: report_lines[i].credit,
					balance: report_lines[i].balance
				};

                this.report_lines[this.line_count] = temp_line;
                this.report_line_ids[0] = this.line_count;

                parent_id = this.line_count;

                for (var j=0;j<report_lines[i]['move_lines'].length;j++) {
                    this.line_count++;
                    var temp = report_lines[i]['move_lines'][j];

                    for (var k in g_ledger_fields) {
                        if (temp[k] == null) {
                            temp[k] = '';
                        }
                    }

					temp.res_id = temp.lid;
                    temp.id = this.line_count;
                    temp.parent = parent_id;
                    temp.level = 1;

                    this.report_lines[this.line_count] = temp;
                    this.report_line_ids[parent_id] = this.line_count;
                }
            }
        },
        _process_journals_audit: function (report_lines) {
            this._build_root_line(7);

            for (var i in report_lines) {
                this.line_count++;
                this.report_lines[this.line_count] = {
                    id: this.line_count,
                    parent: 0,
                    move_id: this.getJournalName(i),
                    level: 0,
                    res_id: -1,
                    line_type: 'section_heading',
                };
                this.report_line_ids[0] = this.line_count;

                var parent_id = this.line_count;

                this.line_count++;
                this.report_lines[this.line_count] = Object.assign(
                    {},
                    journals_audit_fields);
                this.report_lines[this.line_count].id = this.line_count;
                this.report_lines[this.line_count].parent = parent_id;
                this.report_lines[this.line_count].level = 1;
                this.report_lines[this.line_count].line_type = 'section_heading';

                this.report_line_ids[parent_id] = this.line_count;

                for (var j=0;j<report_lines[i].length;j++) {
                    this.line_count++;
                    report_lines[i][j].id = this.line_count;
                    report_lines[i][j].parent = parent_id;
                    report_lines[i][j].level = 1;
                    this.report_lines[this.line_count] = report_lines[i][j];
                    this.report_line_ids[parent_id] = this.line_count;
                }
            }
            return;
        },
        updateReportBody: function (result) {
            /*process the report lines, setup parent - child relation*/
            if (this.report_data.report_type == 'config') {
                this._processData(result);
            }
            else {
                this._processData(result, 'fixed');
            }

            var report_body = this.build_report_lines();

            this.$el.find('.dynamic_report_body').html(report_body);

            this._updateAfterRender();

            return;
        },
        _updateAfterRender: function () {
            var $root_line = this.$el.find('.dynamic_report_body tr[data-id="0"]');

            $root_line.length > 0 ? $root_line.trigger('click') : null;

            this.$el.find('.h_row.ctrl > i').trigger('click');
        },
        build_report_lines: function () {
            var report_lines = "<div class='r_content'><table class='table_r_content'>";
            
			if (this.report_data.report_type == 'config') {
				report_lines += this._build_header();
			}

            var report_content = this.report_lines;

            for (var i in report_content) {
                /*loop through report lines*/

                var line_data = report_content[i];

                report_lines += this._build_line(line_data);
            }
            report_lines += "</table></div>";

            return report_lines;
        },
        getJournalName: function (journal) {
            for (var i=0;i<this.journal_ids.length;i++) {
                if (this.journal_ids[i].id == journal) {
                    return this.journal_ids[i].name;
                }
            }

            return "";
        },
        _build_header: function () {
            debugger
            var result = "<tr class='r_line font_bold' >";
            var report_id = this.report_data.account_report_id[0];

            switch (report_id) {
                case 'journals_audit': {
                    for (var i in journals_audit_fields) {
                        result += "<td name='"+i+"'>" +
                            journals_audit_fields[i] + "</td>";
                    }
                    break;
                }
                default: {
					for (var i in balance_sheet_fields) {
						if (this.report_data.debit_credit == false &&
							['debit', 'credit'].includes(i)) {
							continue;
						}
                        result += "<td name='"+i+"'>" +
                            balance_sheet_fields[i] + "</td>";
                    }
                }
            };

            result += "</tr>";
            return result;
        },
        _build_line: function (r_line) {
            /*based on the report type, we may need to use different
            mechanisms*/

            var line_html;
			if (this.report_data.report_type == 'config') {
				/*P & L and BS*/
				line_html = this._build_type_a(r_line);
			}
            else {
                /*other reports: journals audit, ...,*/
                var report_id = this.report_data.account_report_id[0];

				if (r_line.line_type == 'root') {
					line_html = this._build_root_line_html(r_line);
				}
                else if (report_id == 'journals_audit') {
                    line_html = this._build_type_b(r_line);
                }
                else if (report_id == 'partner_ledger') {
                    line_html = this._build_type_c(r_line);
                }
                else if (report_id == 'general_ledger') {
                    line_html = this._build_type_d(r_line);
                }
                else if (report_id == 'trial_balance') {
                    line_html = this._build_type_e(r_line);
                }
                else if (report_id == 'aged_partner') {
                    line_html = this._build_type_f(r_line);
                }
                else if (report_id == 'tax_report') {
                    line_html = this._build_type_g(r_line);
                }
            }

            /*opened or closed the child lines*/
            this.line_status[r_line.id] = 'open';

            return line_html;
        },
        _build_root_line_html: function (r_line) {
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id='0' level='0' parent='false'>";

            var first_col = true;
            result += this.build_row_col('title',
                                         r_line['title'],
                                         0,
                                         r_line.colspan ? r_line.colspan : 0,
                                         first_col == true ? r_line.id : null);
            first_col = false;
            var report_id = this.report_data.account_report_id[0];
            if (report_id == 'trial_balance') {
                var cols = ['analytic_account_id', 'debit', 'credit', 'balance'];
                for (var i in cols) {
                    result += this.build_row_col(cols[i],
                        r_line[cols[i]],
                        0,
                        1,
                        null);
                }

            }
            result += "</tr>";

            return result;
        },
        _build_type_a: function (r_line) {
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"'";

            if (r_line.line_id)
                result += " res_id=" + r_line.line_id;
            result += ">";

            var first_col = true;
            for (var i in balance_sheet_fields) {
                if (this.check_value(r_line[i])) {
                    result += this.build_row_col(i, r_line[i], r_line.level, 1,
                                                 first_col == true ? r_line.id : null);
                    first_col = false;
                }
            }
            result += "</tr>";

            return result;
        },
        _build_type_b: function (r_line) {
            /*journals audit*/
            var row_class = this.build_row_class(r_line);
            
            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"' res_id='"+r_line.res_id+"'>";

            var first_col = true;
			if (r_line.level == 0) {
				result += this.build_row_col(
                    'move_id',
                    r_line['move_id'],
                    r_line.level, 7, first_col == true ? r_line.id : null);
                first_col = false;
			}
			else {
	            for (var i in journals_audit_fields) {
	                if (this.check_value(r_line[i])) {
	                    result += this.build_row_col(i,
                        	                         r_line[i],
                        	                         r_line.level, 1,
                        	                         first_col == true ? r_line.id : null);
                        first_col = false;
	                }
	            }
	        }

            result += "</tr>";

            return result;
        },
        _build_type_c: function (r_line) {
            /*Partner ledger*/
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"' res_id='"+r_line.res_id+"'>";

            var first_col = true;
			if (r_line.line_type == 'section_heading') {
			    for (var i in p_ledger_fields) {
                    if (this.check_value(r_line[i])) {
                        var colspan = i == 'date' ? 4 : 1;
                        result += this.build_row_col(i,
                                                     r_line[i],
                                                     r_line.level,
                                                     colspan,
                                                     first_col == true ? r_line.id : null);
                        first_col = false;
                    }
                }
			}
			else {
			    for (var i in p_ledger_fields) {
                    if (this.check_value(r_line[i])) {
                        result += this.build_row_col(i,
                                                     r_line[i],
                                                     r_line.level, 1,
                                                     first_col == true ? r_line.id : null);
                        first_col = false;
                    }
                }
			}

            result += "</tr>";

            return result;
        },
        _build_type_d: function (r_line) {
            /* GL*/
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"' res_id='"+r_line.res_id+"'>";

            var first_col = true;
			if (r_line.line_type == 'section_heading') {
			    for (var i in g_ledger_fields) {
                    if (this.check_value(r_line[i])) {
                        var colspan = i == 'ldate' ? 6 : 1;
                        result += this.build_row_col(i,
                                                     r_line[i],
                                                     r_line.level,
                                                     colspan,
                                                     first_col == true ? r_line.id : null);
                        first_col = false;
                    }
                }
			}
			else {
			    for (var i in g_ledger_fields) {
                    if (this.check_value(r_line[i])) {
                        result += this.build_row_col(i,
                                                     r_line[i],
                                                     r_line.level, 1,
                                                     first_col == true ? r_line.id : null);
                        first_col = false;
                    }
                }
			}

            result += "</tr>";

            return result;
        },
        _build_type_e: function (r_line) {
			/*trial balance*/
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"' res_id='"+r_line.res_id+"'>";

            var first_col = true;
			for (var i in trial_balance_fields) {
                if (this.check_value(r_line[i])) {
                    result += this.build_row_col(i,
                                                 r_line[i],
                                                 r_line.level, 1,
                                                 first_col == true ? r_line.id : null,
                                                 r_line.line_type);
                    first_col = false;
                }
            }

            result += "</tr>";

            return result;
        },
        _build_type_f: function (r_line) {
			/*aged partner*/
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"' res_id='-1'>";

			var first_col = true;
			for (var i in aged_partner_fields) {
                if (this.check_value(r_line[i])) {
                    result += this.build_row_col(i,
                                                 r_line[i],
                                                 r_line.level, 1,
                                                 first_col == true ? r_line.id : null);
                    first_col = false;
                }
            }

            result += "</tr>";

            return result;
        },
        _build_type_g: function (r_line) {
			/*tax report*/
            var row_class = this.build_row_class(r_line);

            var result = "<tr class='"+row_class+
                "' data-id="+r_line.id+" level="+r_line.level+
                " parent='"+r_line.parent+"' res_id='-1'>";

			var first_col = true;
			for (var i in tax_report_fields) {
                if (this.check_value(r_line[i])) {
                    result += this.build_row_col(i,
                                                 r_line[i],
                                                 r_line.level,
                                                 1,
                                                 first_col == true ? r_line.id : null);
                    first_col = false;
                }
            }

            result += "</tr>";

            return result;
        },
        build_row_col: function (col_key, col_data, level, colspan, row_id, line_type) {
            var col_style = this.build_col_style(col_key, level);
            var col_class = this.build_col_class(col_key);
            var res = "<td class='" + col_class + "' " +
                "level='level_"+ level + "' " +
                "name='" + col_key + "' style='"+col_style + "'";
            res += colspan ? " colspan='" + colspan + "'" : "";
            res += ">";

            var display_value = line_type != 'section_heading' ? this.formatOutput(col_key, col_data) : col_data;
            res += this.buildIcon(col_key, row_id);
            res += "<span>"+display_value+"</span>";

            res += "</td>";

            return res;
        },
        formatOutput: function (col_key, value) {
            var result;
            var amount_cols = this.getAmountCols();

            if (amount_cols.includes(col_key)) {
                /*currency formatting needed*/

                /*set decimal places*/
                var decimal_places = this.currency_data && this.currency_data.decimal_places ? this.currency_data.decimal_places : 2;
                value = typeof value == 'number' ? value.toFixed(decimal_places) : value;

                result = value;

                if (value != '' && this.currency_data) {
                    if (this.currency_data.position == 'after') {
                        result = value + " " + "<span class='symbol_currency'>" + this.currency_data.symbol + "</span>";
                    }
                    else if (this.currency_data.position == 'before') {
                        result = this.currency_data.symbol + " " + value;
                    }
                }
            }
            else {
                result = value;
            }

            return result;
        },
        getAmountCols: function () {
            return ['debit', 'credit', 'balance', 'progress', 'cumulated_balance',
                     'net', 'tax', 'total', 'direction', 'l0', 'l1', 'l2', 'l3', 'l4'];
        },
        build_col_style: function (col_key, level) {
            var style_str = "";
            var report_id = this.report_data.account_report_id[0];

            switch (report_id) {
                case 'journals_audit': {
                    if (col_key == 'move_id') {
                        style_str += 'padding-left:' + (parseInt(level) * 6) + 'px';
                    }
                    break;
                };
                case 'partner_ledger': {
                    if (col_key == 'date') {
                        style_str += 'padding-left:' + (parseInt(level) * 6) + 'px';
                    }
                    break;
                };
                case 'general_ledger': {
                    if (col_key == 'ldate') {
                        style_str += 'padding-left:' + (parseInt(level) * 6) + 'px';
                    }
                    break;
                };
                case 'trial_balance': {
                    if (col_key == 'code') {
                        style_str += 'padding-left:' + (parseInt(level) * 6) + 'px';
                    }
                    break;
                };
                default: {
                    if (col_key == 'name') {
                        style_str += 'padding-left:' + (parseInt(level) * 6) + 'px';
                    }
                }
            };

            return style_str;
        },
        build_col_class: function (col_key) {
            var class_str = "";
            if (col_key == 'name') {
                class_str += 'col_name';
            }
            else if (col_key == 'balance') {
                class_str += 'col_balance';
            }

            return class_str;
        },
        buildIcon: function (col_key, row_id) {
            var res = "";
            if (this.report_line_ids[row_id]) {
                res = "<i class='fa fa-caret-down'/>";
            }
            return res;
        },
        build_row_class: function (r_line) {
            var r_class = 'r_line';

            if (['font_bold', 'root', 'section_heading'].includes(r_line.line_type)) {
                r_class += " " + r_line.line_type;
            }
            return r_class;
        },
        check_value: function (value) {
            return value == null ? false : true;
        },
        updateResizable: function () {
			$(".panel-top").resizable({
				handleSelector: ".splitter-horizontal",
				resizeWidth: false
			});
        },
        onChangeSymbolCurrency: function () {
            var inputSymbolCurrency = $(".display_currency_unit")
			if (inputSymbolCurrency[0].checked) {
                $(".symbol_currency").show();
            } else {
                $(".symbol_currency").hide();
            }
        },
        render_searchview_buttons: function() {
            var self = this;
            // bind searchview buttons/filter to the correct actions
            var $datetimepickers = this.$searchview_buttons.find('.js_account_reports_datetimepicker');
            var options = { // Set the options for the datetimepickers
                locale : moment.locale(),
                format : 'L',
                icons: {
                    date: "fa fa-calendar",
                },
            };
            // attach datepicker
            $datetimepickers.each(function () {
                var name = $(this).find('input').attr('name');
                var defaultValue = $(this).data('default-value');
                $(this).datetimepicker(options);
                var dt = new datepicker.DateWidget(options);
                dt.replace($(this)).then(function () {
                    dt.$el.find('input').attr('name', name);
                    if (defaultValue) { // Set its default value if there is one
                        dt.setValue(moment(defaultValue));
                    }
                });
            });
            // format date that needs to be show in user lang
            _.each(this.$searchview_buttons.find('.js_format_date'), function(dt) {
                var date_value = $(dt).html();
                $(dt).html((new moment(date_value)).format('ll'));
            });
            // fold all menu
            this.$searchview_buttons.find('.js_foldable_trigger').click(function (event) {
                $(self).toggleClass('o_closed_menu o_open_menu');
                self.$searchview_buttons.find('.o_foldable_menu[data-filter="'+$(this).data('filter')+'"]').toggleClass('o_closed_menu');
            });
            // render filter (add selected class to the options that are selected)
            _.each(self.report_options, function(k) {
                if (k!== null && k.filter !== undefined) {
                    self.$searchview_buttons.find('[data-filter="'+k.filter+'"]').addClass('selected');
                }
            });
            _.each(this.$searchview_buttons.find('.js_account_report_bool_filter'), function(k) {
                $(k).toggleClass('selected', self.report_options[$(k).data('filter')]);
            });
            _.each(this.$searchview_buttons.find('.js_account_report_choice_filter'), function(k) {
                $(k).toggleClass('selected', (_.filter(self.report_options[$(k).data('filter')], function(el){return ''+el.id == ''+$(k).data('id') && el.selected === true;})).length > 0);
            });
            $('.js_account_report_group_choice_filter', this.$searchview_buttons).each(function (i, el) {
                var $el = $(el);
                var ids = $el.data('member-ids');
                $el.toggleClass('selected', _.every(self.report_options[$el.data('filter')], function (member) {
                    // only look for actual ids, discard separators and section titles
                    if(typeof member.id == 'number'){
                        // true if selected and member or non member and non selected
                        return member.selected === (ids.indexOf(member.id) > -1);
                    } else {
                        return true;
                    }
                }));
            });
            _.each(this.$searchview_buttons.find('.js_account_reports_one_choice_filter'), function(k) {
                $(k).toggleClass('selected', ''+self.report_options[$(k).data('filter')] === ''+$(k).data('id'));
            });
            $(".buttons_search").html(this.$searchview_buttons);
            // click events
            this.$searchview_buttons.find('.js_account_report_date_filter').click(function (event) {
                self.report_options.date.filter = $(this).data('filter');
                var error = false;
                if ($(this).data('filter') === 'custom') {
                    var date_from = self.$searchview_buttons.find('.o_datepicker_input[name="date_from"]');
                    var date_to = self.$searchview_buttons.find('.o_datepicker_input[name="date_to"]');
                    if (date_from.length > 0){
                        error = date_from.val() === "" || date_to.val() === "";
                        self.report_options.date.date_from = field_utils.parse.date(date_from.val());
                        self.report_options.date.date_to = field_utils.parse.date(date_to.val());
                    }
                    else {
                        error = date_to.val() === "";
                        self.report_options.date.date_to = field_utils.parse.date(date_to.val());
                    }
                }
                if (error) {
                    new WarningDialog(self, {
                        title: _t("Odoo Warning"),
                    }, {
                        message: _t("Date cannot be empty")
                    }).open();
                } else {
                    self.reload();
                }
            });
            this.$searchview_buttons.find('.js_account_report_bool_filter').click(function (event) {
                var option_value = $(this).data('filter');
                self.report_options[option_value] = !self.report_options[option_value];
                if (option_value === 'unfold_all') {
                    self.unfold_all(self.report_options[option_value]);
                }
                self.reload();
            });
            $('.js_account_report_group_choice_filter', this.$searchview_buttons).click(function () {
                var option_value = $(this).data('filter');
                var option_member_ids = $(this).data('member-ids') || [];
                var is_selected = $(this).hasClass('selected');
                _.each(self.report_options[option_value], function (el) {
                    // if group was selected, we want to uncheck all
                    el.selected = !is_selected && (option_member_ids.indexOf(Number(el.id)) > -1);
                });
                self.reload();
            });
            this.$searchview_buttons.find('.js_account_report_choice_filter').click(function (event) {
                var option_value = $(this).data('filter');
                var option_id = $(this).data('id');
                _.filter(self.report_options[option_value], function(el) {
                    if (''+el.id == ''+option_id){
                        if (el.selected === undefined || el.selected === null){el.selected = false;}
                        el.selected = !el.selected;
                    } else if (option_value === 'ir_filters') {
                        el.selected = false;
                    }
                    return el;
                });
                self.reload();
            });
            var rate_handler = function (event) {
                var option_value = $(this).data('filter');
                if (option_value == 'current_currency') {
                    delete self.report_options.currency_rates;
                } else if (option_value == 'custom_currency') {
                    _.each($('input.js_account_report_custom_currency_input'), function(input) {
                        self.report_options.currency_rates[input.name].rate = input.value;
                    });
                }
                self.reload();
            }
            $(document).on('click', '.js_account_report_custom_currency', rate_handler);
            this.$searchview_buttons.find('.js_account_report_custom_currency').click(rate_handler);
            this.$searchview_buttons.find('.js_account_reports_one_choice_filter').click(function (event) {
                var option_value = $(this).data('filter');
                self.report_options[option_value] = $(this).data('id');
    
                if (option_value === 'tax_unit') {
                    // Change the currently selected companies depending on the chosen tax_unit option
                    // We need to do that to prevent record rules from accepting records that they shouldn't when generating the report.
    
                    var main_company = session.user_context.allowed_company_ids[0];
                    var companies = [main_company];
    
                    if (self.report_options['tax_unit'] != 'company_only') {
                        var unit_id = self.report_options['tax_unit'];
                        var selected_unit = self.report_options['available_tax_units'].filter(unit => unit.id == unit_id)[0];
                        companies = selected_unit.company_ids;
                    }
                    self.persist_options_for_company_reload(companies); // So that previous_options are kept after the reload performed by setCompanies
                    session.setCompanies(main_company, companies);
                }
                else {
                    self.reload();
                }
            });
            this.$searchview_buttons.find('.js_account_report_date_cmp_filter').click(function (event) {
                self.report_options.comparison.filter = $(this).data('filter');
                var error = false;
                var number_period = $(this).parent().find('input[name="periods_number"]');
                self.report_options.comparison.number_period = (number_period.length > 0) ? parseInt(number_period.val()) : 1;
                if ($(this).data('filter') === 'custom') {
                    var date_from = self.$searchview_buttons.find('.o_datepicker_input[name="date_from_cmp"]');
                    var date_to = self.$searchview_buttons.find('.o_datepicker_input[name="date_to_cmp"]');
                    if (date_from.length > 0) {
                        error = date_from.val() === "" || date_to.val() === "";
                        self.report_options.comparison.date_from = field_utils.parse.date(date_from.val());
                        self.report_options.comparison.date_to = field_utils.parse.date(date_to.val());
                    }
                    else {
                        error = date_to.val() === "";
                        self.report_options.comparison.date_to = field_utils.parse.date(date_to.val());
                    }
                }
                if (error) {
                    new WarningDialog(self, {
                        title: _t("Odoo Warning"),
                    }, {
                        message: _t("Date cannot be empty")
                    }).open();
                } else {
                    self.reload();
                }
            });
    
            // partner filter
            if (this.report_options.partner) {
                if (!this.M2MFilters) {
                    var fields = {};
                    if ('partner_ids' in this.report_options) {
                        fields['partner_ids'] = {
                            label: _t('Partners'),
                            modelName: 'res.partner',
                            value: this.report_options.partner_ids.map(Number),
                        };
                    }
                    if ('partner_categories' in this.report_options) {
                        fields['partner_categories'] = {
                            label: _t('Tags'),
                            modelName: 'res.partner.category',
                            value: this.report_options.partner_categories.map(Number),
                        };
                    }
                    if (!_.isEmpty(fields)) {
                        this.M2MFilters = new M2MFilters(this, fields);
                        this.M2MFilters.appendTo(this.$searchview_buttons.find('.js_account_partner_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find('.js_account_partner_m2m').append(this.M2MFilters.$el);
                }
            }
    
            // analytic filter
            if (this.report_options.analytic) {
                if (!this.M2MFilters) {
                    var fields = {};
                    if (this.report_options.analytic_accounts) {
                        fields['analytic_accounts'] = {
                            label: _t('Accounts'),
                            modelName: 'account.analytic.account',
                            value: this.report_options.analytic_accounts.map(Number),
                        };
                    }
                    if (this.report_options.analytic_tags) {
                        fields['analytic_tags'] = {
                            label: _t('Tags'),
                            modelName: 'account.analytic.tag',
                            value: this.report_options.analytic_tags.map(Number),
                        };
                    }
                    if (!_.isEmpty(fields)) {
                        this.M2MFilters = new M2MFilters(this, fields);
                        this.M2MFilters.appendTo(this.$searchview_buttons.find('.js_account_analytic_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find('.js_account_analytic_m2m').append(this.M2MFilters.$el);
                }
            }
        },
        format_date: function(moment_date) {
            var date_format = 'YYYY-MM-DD';
            return moment_date.format(date_format);
        },
        update_cp: function() {
            this.renderButtons();
            var status = {
                cp_content: {
                    $buttons: this.$buttons,
                    $searchview_buttons: this.$searchview_buttons,
                    $pager: this.$pager,
                    $searchview: this.$searchview,
                },
            };
            return this.updateControlPanel(status);
        },
        reload: function() {
            var self = this;
            return this._rpc({
                    model: 'account.analytic.report',
                    method: 'get_report_informations',
                    args: [self.financial_id, self.report_options],
                    context: self.odoo_context,
                })
                .then(function(result){
                    self.parse_reports_informations(result);
                    self.render()
                    return self.update_cp();
                });
        },
        render: function() {
            var self = this;
            $( ".r_analytic" ).html(self.main_html);
            $( ".buttons_anlytic" ).html(self.renderButtons());
            self.render_searchview_buttons();
            this.$('.js_account_report_foldable').each(function() {
                if(!$(this).data('unfolded')) {
                    self.fold($(this));
                }
            });
            this._add_line_classes();
        },
        unfold_all: function(bool) {
            var self = this;
            var lines = this.$el.find('.js_account_report_foldable');
            self.report_options.unfolded_lines = [];
            if (bool) {
                _.each(lines, function(el) {
                    self.report_options.unfolded_lines.push($(el).data('id'));
                });
            }
        },
        renderButtons: function() {
            var self = this;
            this.$buttons = $(QWeb.render("DynamicReports.buttons", {buttons: this.buttons}));
            // bind actions
            _.each(this.$buttons.siblings('button'), function(el) {
                $(el).click(function() {
                    self.$buttons.attr('disabled', true);

                    return self._rpc({
                            model: 'account.analytic.report',
                            method: $(el).attr('action'),
                            args: [self.financial_id, self.report_options],
                            context: self.odoo_context,
                        })
                        .then(function(result){
                            var doActionProm = self.do_action(result);
                            self.$buttons.attr('disabled', false);
                            return doActionProm;
                        })
                        .guardedCatch(function() {
                            self.$buttons.attr('disabled', false);
                        });
                });
            });
            return this.$buttons;
        },
        _getAnalyticEntries: function(event){
            var self = this;
            var analytic_account_id = $(event.target).attr('data-id');
            var params = {'id': analytic_account_id};
            return this._rpc({
                model: 'account.analytic.report',
                method: 'open_analytic_entries',
                args: [0, self.report_options, params],
                context: self.odoo_context,
            })
            .then(function(result){
                return self.do_action(result);
            });
        },
        render_footnotes: function() {
            var self = this;
            // First assign number based on visible lines
            var $dom_footnotes = self.$el.find('.js_account_report_line_footnote:not(.folded)');
            $dom_footnotes.html('');
            var number = 1;
            var footnote_to_render = [];
            _.each($dom_footnotes, function(el) {
                if ($(el).parents('.o_account_reports_filtered_lines').length > 0) {
                    return;
                }
                var line_id = $(el).data('id');
                var footnote = _.filter(self.footnotes, function(footnote) {return ''+footnote.line === ''+line_id;});
                if (footnote.length !== 0) {
                    $(el).html('<sup><b class="o_account_reports_footnote_sup"><a href="#footnote'+number+'">'+number+'</a></b></sup>');
                    footnote[0].number = number;
                    number += 1;
                    footnote_to_render.push(footnote[0]);
                }
            });
            // Render footnote template
            return this._rpc({
                    model: 'account.analytic.report',
                    method: 'get_html_footnotes',
                    args: [self.financial_id, footnote_to_render],
                    context: self.odoo_context,
                })
                .then(function(result){
                    return self.$el.find('.js_account_report_footnotes').html(result);
                });
        },
        add_edit_footnote: function(e) {
            // open dialog window with either empty content or the footnote text value
            var self = this;
            var line_id = $(e.target).data('id');
            // check if we already have some footnote for this line
            var existing_footnote = _.filter(self.footnotes, function(footnote) {
                return ''+footnote.line === ''+line_id;
            });
            var text = '';
            if (existing_footnote.length !== 0) {
                text = existing_footnote[0].text;
            }
            var $content = $(QWeb.render('accountReports.footnote_dialog', {text: text, line: line_id}));
            var save = function() {
                var footnote_text = $('.js_account_reports_footnote_note').val().replace(/[ \t]+/g, ' ');
                if (!footnote_text && existing_footnote.length === 0) {return;}
                if (existing_footnote.length !== 0) {
                    if (!footnote_text) {
                        return self.$el.find('.footnote[data-id="'+existing_footnote[0].id+'"] .o_account_reports_footnote_icons').click();
                    }
                    // replace text of existing footnote
                    return this._rpc({
                            model: 'report.accounting.footnote',
                            method: 'write',
                            args: [existing_footnote[0].id, {text: footnote_text}],
                            context: this.odoo_context,
                        })
                        .then(function(result){
                            _.each(self.footnotes, function(footnote) {
                                if (footnote.id === existing_footnote[0].id){
                                    footnote.text = footnote_text;
                                }
                            });
                            return self.render_footnotes();
                        });
                }
                else {
                    // new footnote
                    return this._rpc({
                            model: 'report.accounting.footnote',
                            method: 'create',
                            args: [{line: line_id, text: footnote_text, manager_id: self.report_manager_id}],
                            context: this.odoo_context,
                        })
                        .then(function(result){
                            self.footnotes.push({id: result, line: line_id, text: footnote_text});
                            return self.render_footnotes();
                        });
                }
            };
            new Dialog(this, {title: 'Annotate', size: 'medium', $content: $content, buttons: [{text: 'Save', classes: 'btn-primary', close: true, click: save}, {text: 'Cancel', close: true}]}).open();
        },
        delete_footnote: function(e) {
            var self = this;
            var footnote_id = $(e.target).parents('.footnote').data('id');
            return this._rpc({
                    model: 'report.accounting.footnote',
                    method: 'unlink',
                    args: [footnote_id],
                    context: this.odoo_context,
                })
                .then(function(result){
                    // remove footnote from report_information
                    self.footnotes = _.filter(self.footnotes, function(element) {
                        return element.id !== footnote_id;
                    });
                    return self.render_footnotes();
                });
        },
        fold_unfold: function(e) {
            var self = this;
            if ($(e.target).hasClass('caret') || $(e.target).parents('.o_account_reports_footnote_sup').length > 0){return;}
            e.stopPropagation();
            e.preventDefault();
            var line = $(e.target).parents('td');
            if (line.length === 0) {line = $(e.target);}
            var method = line[0].dataset.unfolded === 'True' ? this.fold(line) : this.unfold(line);
            Promise.resolve(method).then(function() {
                self.render_footnotes();
                self.persist_options();
            });
        },
        fold: function(line) {
            var self = this;
            var line_id = line.data('id');
            line.find('.o_account_reports_caret_icon .fa-caret-down').toggleClass('fa-caret-right fa-caret-down');
            line.toggleClass('folded');
            $(line).parent('tr').removeClass('o_js_account_report_parent_row_unfolded');
            var $lines_to_hide = this.$el.find('tr[data-parent-id="'+$.escapeSelector(String(line_id))+'"]');
            var index = self.report_options.unfolded_lines.indexOf(line_id);
            if (index > -1) {
                self.report_options.unfolded_lines.splice(index, 1);
            }
            if ($lines_to_hide.length > 0) {
                line[0].dataset.unfolded = 'False';
                $lines_to_hide.find('.js_account_report_line_footnote').addClass('folded');
                $lines_to_hide.hide();
                _.each($lines_to_hide, function(el){
                    var child = $(el).find('[data-id]:first');
                    if (child) {
                        self.fold(child);
                    }
                })
            }
            return false;
        },
        unfold: function(line) {
            var self = this;
            var line_id = line.data('id');
            line.toggleClass('folded');
            self.report_options.unfolded_lines.push(line_id);
            var $lines_in_dom = this.$el.find('tr[data-parent-id="'+$.escapeSelector(String(line_id))+'"]');
            if ($lines_in_dom.length > 0) {
                $lines_in_dom.find('.js_account_report_line_footnote').removeClass('folded');
                $lines_in_dom.show();
                line.find('.o_account_reports_caret_icon .fa-caret-right').toggleClass('fa-caret-right fa-caret-down');
                line[0].dataset.unfolded = 'True';
                this._add_line_classes();
                return true;
            }
            else {
                return this._rpc({
                        model: 'account.analytic.report',
                        method: 'get_html',
                        args: [self.financial_id, self.report_options, line.data('id')],
                        context: self.odoo_context,
                    })
                    .then(function(result){
                        $(line).parent('tr').replaceWith(result);
                        self._add_line_classes();
                        self.$('.js_account_report_foldable').each(function() {
                            if(!$(this).data('unfolded')) {
                                self.fold($(this));
                            }
                        });
                    });
            }
        },
        _init_line_popups: function(){
            /*
                Configure the popover used in the financial reports to display some details about the results given by
                the report lines like:
                - the code.
                - the formula with values.
                - the domain.
                - A button to show the account.move.lines.
            */
    
            var self = this;
            _.each(this.$('.o_account_report_popup'), function(popup){
                $(popup).popover({
                    html: true,
                    template: "<div class='popover' role='tooltip' style='max-width: 100%; margin-right:80px;'><div class='popover-body'></div></div>",
                    placement: 'left',
                    trigger: 'focus',
                    container: 'body',
                    delay: {show: 0, hide: 100},
                    content: function(){
                        var data = JSON.parse(popup.getAttribute('data'));
    
                        // Render the content.
                        var $content = $(QWeb.render(popup.getAttribute('template'), data));
    
                        // Bind the 'view journal items' button with the 'action_view_journal_entries' python method.
                        $content.find('.js_view_entries').on('click', function(event){
                            self._rpc({
                                model: 'account.financial.html.report.line',
                                method: 'action_view_journal_entries',
                                args: [$(event.target).data('id'), self.report_options, self.financial_id],
                                context: self.odoo_context,
                            })
                            .then(function(result){
                                return self.do_action(result);
                            })
                        });
    
                        // Bind the 'Accounts' button with the 'action_view_coa' python method.
                        $content.find('.js_view_coa').on('click', function(event){
                            self._rpc({
                                model: 'account.financial.html.report.line',
                                method: 'action_view_coa',
                                args: [$(event.target).data('id'), self.report_options],
                                context: self.odoo_context,
                            })
                            .then(function(result){
                                return self.do_action(result);
                            })
                        });
    
                        // Bind the 'Report Line Computation' button with the 'action_view_line_computation' python method.
                        $content.find('.js_view_line_computation').on('click', function(event){
                            self._rpc({
                                model: 'account.financial.html.report.line',
                                method: 'action_view_line_computation',
                                args: [$(event.target).data('id')],
                                context: self.odoo_context,
                            })
                            .then(function(result){
                                return self.do_action(result);
                            })
                        });
    
                        // Bind the 'view carryover lines' button with the 'action_view_carryover_lines' python method.
                        $content.find('.js_view_carryover_lines').on('click', function(event){
                            self._rpc({
                                model: 'account.tax.report.line',
                                method: 'action_view_carryover_lines',
                                args: [$(event.target).data('id'), self.report_options],
                                context: self.odoo_context,
                            })
                            .then(function(result){
                                return self.do_action(result);
                            })
                        });
    
                        // Highlight involved codes during formula evaluation.
                        _.each($content.find('.js_popup_formula'), function(element){
                            $(element).on("mouseenter", function(event){
                                $(element).addClass('o_financial_report_hover_popup');
                                self.$("[code='" + element.textContent + "']").addClass('o_financial_report_hover_popup');
                            });
                            $(element).on("mouseleave", function(event){
                                $(element).removeClass('o_financial_report_hover_popup');
                                self.$("[code='" + element.textContent + "']").removeClass('o_financial_report_hover_popup');
                            });
                        });
    
                        // Redirect to another report.
                        _.each($content.find('.js_popup_open_report'), function(element){
                            $(element).on("click", function(event){
                                var $target = $(event.target);
                                self._rpc({
                                    model: 'account.financial.html.report',
                                    method: 'action_redirect_to_report',
                                    args: [$target.data('id'), self.report_options, $target.data('target')],
                                    context: self.odoo_context,
                                })
                                .then(function(result){
                                    return self.do_action(result);
                                })
                            });
                        });
    
                        return $content;
                    }
                });
    
                // Triggered when the popup is closed without mouseleave event.
                $(popup).on("hidden.bs.popover", function(element){
                    self.$('.js_popup_formula').removeClass('o_financial_report_hover_popup');
                });
            });
        },
        _add_line_classes: function() {
            /* Pure JS to improve performance in very cornered case (~200k lines)
             * Jquery code:
             *  this.$('.o_account_report_line').filter(function () {
             *      return $(this).data('unfolded') === 'True';
             *  }).parent().addClass('o_js_account_report_parent_row_unfolded');
             */
            var el = this.$el[0];
            var report_lines = el.getElementsByClassName('o_account_report_line');
            for (var l=0; l < report_lines.length; l++) {
                var line = report_lines[l];
                var unfolded = line.dataset.unfolded;
                if (unfolded === 'True') {
                    line.parentNode.classList.add('o_js_account_report_parent_row_unfolded');
                }
            }
            // This selector is not adaptable in pure JS
            this.$('tr[data-parent-id]').addClass('o_js_account_report_inner_row');
    
            this._init_line_popups();
         },
        filter_accounts: function(e) {
            var self = this;
            var query = e.target.value.trim().toLowerCase();
            this.filterOn = false;
            this.$('.o_account_searchable_line').each(function(index, el) {
                var $accountReportLineFoldable = $(el);
                var line_id = $accountReportLineFoldable.find('.o_account_report_line').data('id');
                var $childs = self.$('tr[data-parent-id="'+$.escapeSelector(String(line_id))+'"]');
    
                // Only the direct text node, not text situated in other child nodes
                const lineContent = $accountReportLineFoldable.find('.account_report_line_name').contents();
                const lineText = lineContent.length > 0 ? lineContent.get(0).nodeValue.trim() : '';
    
                // The python does this too
                var queryFound = lineText.split(' ').some(function (str) {
                    return str.toLowerCase().startsWith(query);
                });
    
                $accountReportLineFoldable.toggleClass('o_account_reports_filtered_lines', !queryFound);
                $childs.toggleClass('o_account_reports_filtered_lines', !queryFound);
    
                if (!queryFound) {
                    self.filterOn = true;
                }
            });
            if (this.filterOn) {
                this.$('.o_account_reports_level1.total').hide();
            }
            else {
                this.$('.o_account_reports_level1.total').show();
            }
            this.report_options['filter_accounts'] = query;
            this.render_footnotes();
        },
        _onClickDropDownMenu: function (ev) {
            ev.stopPropagation();
        },
    });

    core.action_registry.add('dynamic_reports_view', DynamicReportAction);

    return DynamicReportAction;
});
