/*
  © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
  License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define("budget_analysis_account_move_line.link_widget", function(require) {
"use strict";

var rpc = require("web.rpc");
var basicFields = require("web.basic_fields");
var AbstractField = require("web.AbstractField");

var BudgetAnalysisToMoveLines = basicFields.FieldFloat.extend({
    className: "o_field_float o_field_number o_budget_analysis_to_move_lines",
    tagName: "a",
    events: _.extend({}, AbstractField.prototype.events, {
        "click": "_onClick",
    }),
    /**
     * When clicking on the amount, trigger the action to display the list of move lines.
     */
    async _onClick(event){
        event.preventDefault();
        event.stopPropagation();
        var action = await rpc.query({
            model: "crossovered.budget.lines",
            method: "action_view_move_lines",
            args: [this.record.res_id],
            context: this.getSession().user_context,
        });
        this.do_action(action);
    },
    /**
     * Display the field as a clickable link.
     *
     * Because of bootstrap, <a> nodes without href do not appear as clickable links.
     */
    _render(){
        this._super.apply(this, arguments);
        this.$el.attr("href", "#");
    },
    /**
     * Fix the non-break spaces in amounts.
     *
     * When using an <a> node instead of a span, the non-break spaces
     * after or behind the currency symbol is displayed as "&nbsp;".
     *
     * This function replaces the "&nbsp;" with a real non-break space caracter.
     */
    _formatValue(value){
        var formattedValue = this._super.apply(this, arguments);
        return formattedValue.replace("&nbsp;", " ");
    },
});

var registry = require("web.field_registry");
registry.add("budget_analysis_to_move_lines", BudgetAnalysisToMoveLines);

});
