/*
  © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
  License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define("budget_analysis_account_move_line.link_widget", function(require) {
"use strict";

var ShowPaymentLineWidget = require("account.payment").ShowPaymentLineWidget;

ShowPaymentLineWidget.include({
    events: _.extend({
        "click .o_account_payment_widget_link": "_onPaymentItemClicked",
    }, ShowPaymentLineWidget.prototype.events),
    _getOriginRecordFormViewAction(moveLineId){
        return this._rpc({
            model: "account.move.line",
            method: "get_payment_widget_link_action",
            args: [moveLineId],
        });
    },
    async _onPaymentItemClicked(event){
        event.preventDefault();
        event.stopPropagation();
        var moveLineId = parseInt($(event.target).attr("data-id"));
        var action = await this._getOriginRecordFormViewAction(moveLineId);
        this.trigger_up("do_action", {action});
    },
    _render() {
        this._super.apply(this, arguments);
        this.$el.addClass("o_outstanding_credits_debits_widget");
    }
});

});
