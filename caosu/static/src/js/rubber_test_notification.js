/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { NotificationService } from "@web/core/notification_service";

patch(FormController.prototype, 'rubber_test_notification', {
    async _onFieldChanged(event) {
        this._super(event);
        if (event.data.changes.ctktup) {
            const notificationService = registry.category('services').get('notification');
            notificationService.add('CT úp has been changed and OC CT úp is set to True', {
                type: 'info',
                sticky: false,
            });
        }
    },
});