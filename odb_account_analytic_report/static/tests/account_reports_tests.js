odoo.define('odb_account_analytic_report/static/tests/account_reports_tests', function (require) {
    "use strict";

    const ControlPanel = require('web.ControlPanel');
    const testUtils = require("web.test_utils");
    const { patch, unpatch } = require("web.utils");
    const { createWebClient, doAction } = require('@web/../tests/webclient/helpers');
    const { legacyExtraNextTick } = require("@web/../tests/helpers/utils");

    const { dom } = testUtils;

    QUnit.module('Account Reports', {}, () => {
        QUnit.test("mounted is called once when returning on 'Account Reports' from breadcrumb", async assert => {
            // This test can be removed as soon as we don't mix legacy and owl layers anymore.
            assert.expect(7);

            let mountCount = 0;

            patch(ControlPanel.prototype, 'test.ControlPanel', {
                mounted() {
                    mountCount = mountCount + 1;
                    this.__uniqueId = mountCount;
                    assert.step(`mounted ${this.__uniqueId}`);
                    this.__superMounted = this._super.bind(this);
                    this.__superMounted(...arguments);
                },
                willUnmount() {
                    assert.step(`willUnmount ${this.__uniqueId}`);
                    this.__superMounted(...arguments);
                }
            });

            const models = {
                partner: {
                    fields: {
                        display_name: { string: "Displayed name", type: "char" },
                    },
                    records: [
                        {id: 1, display_name: "Genda Swami"},
                    ],
                }
            };
            const views = {
                'partner,false,form': '<form><field name="display_name"/></form>',
                'partner,false,search': '<search></search>',
            };
            const actions = {
                42: {
                    id: 42,
                    name: "Account reports",
                    tag: 'account_report',
                    type: 'ir.actions.client',
                }
            };
            const serverData = { models, views, actions };
            const webClient = await createWebClient({
                serverData,
                mockRPC: function (route) {
                    if (route === '/web/dataset/call_kw/account.report/get_report_informations') {
                        return Promise.resolve({
                            options: {},
                            buttons: [],
                            main_html: '<a action="go_to_details">Go to detail view</a>',
                        });
                    } else if (route === '/web/dataset/call_kw/account.report/go_to_details') {
                        return Promise.resolve({
                            type: "ir.actions.act_window",
                            res_id: 1,
                            res_model: "partner",
                            views: [
                                [false, "form"],
                            ],
                        });
                    } else if (route === '/web/dataset/call_kw/account.report/get_html_footnotes') {
                        return Promise.resolve("");
                    }
                },
            });

            await doAction(webClient, 42);
            await dom.click($(webClient.el).find('a[action="go_to_details"]'));
            await legacyExtraNextTick();
            await dom.click($(webClient.el).find('.breadcrumb-item:first'));
            await legacyExtraNextTick();
            webClient.destroy();

            assert.verifySteps([
                'mounted 1',
                'willUnmount 1',
                'mounted 2',
                'willUnmount 2',
                'mounted 3',
                'willUnmount 3',
            ]);

            unpatch(ControlPanel.prototype, 'test.ControlPanel');
        });
    });

});
