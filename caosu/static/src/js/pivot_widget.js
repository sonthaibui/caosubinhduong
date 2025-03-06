/** @odoo-module **/

import { PivotModel } from "@web/views/pivot/pivot_model";

// Monkey-patch PivotModel to force zero decimals when digits[1] = 0
const originalGetFormattedValue = PivotModel.prototype._getFormattedValue;
PivotModel.prototype._getFormattedValue = function (value, measure, group) {
    const formattedValue = originalGetFormattedValue.call(this, value, measure, group);
    const measureInfo = this.measures[measure];
    if (!measureInfo || !measureInfo.field) return formattedValue;

    const field = measureInfo.field;
    console.log("[DEBUG] Field:", field.name, "Digits:", field.digits); // Debugging

    // Force zero decimals if digits[1] is explicitly 0
    if (Array.isArray(field.digits) && field.digits[1] === 0) {
        return this.env.session.formatFloat(value, {
            digits: [field.digits[0], // Omit decimal places entirely
            thousandSeparator: true,
        }).replace(/\.?0+$/, ""); // Remove trailing decimals
    }
    return formattedValue;
};