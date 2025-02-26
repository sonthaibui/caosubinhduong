/** @odoo-module */

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

async function executeAccountReportDownload({ env, action }) {
    env.services.ui.block();
    const url = "/odb_account_analytic_report";
    const data = action.data;
    try {
      await download({ url, data });
    } finally {
      env.services.ui.unblock();
    }
}

registry
    .category("action_handlers")
    .add('ir_actions_account_report_download', executeAccountReportDownload);
