/*
    © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
    License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define("account_report_trial_balance", function (require) {
"use strict";

var core = require("web.core");
var framework = require("web.framework");
var rpc = require("web.rpc");
var AbstractAction = require("web.AbstractAction");

var QWeb = core.qweb;

var ReportAction = AbstractAction.extend({
    hasControlPanel: true,
    events: {
        "click .o_trial_balance__initialBalance": "initialBalanceClicked",
        "click .o_trial_balance__debit": "debitClicked",
        "click .o_trial_balance__credit": "creditClicked",
        "click .o_trial_balance__balance": "balanceClicked",
        "click .o_trial_balance__closingBalance": "closingBalanceClicked",
    },
    init(parent, action) {
        this._super.apply(this, arguments);
        this.controllerURL = action.context.url;
        this.reportId = action.context.active_id;
        this.controlPanelProps.cp_content = {$buttons: this.renderPrintButton()};
    },
    renderPrintButton(){
        var button = $(QWeb.render("accountReportTrialBalance.printButton", {}));
        button.bind("click", () => this.downloadPDF());
        return button;
    },
    async renderElement(){
        this._super(...arguments);
        var html = await this._rpc({
            model: "account.report.trial.balance",
            method: "get_html",
            args: [this.reportId],
            context: this.getSession().user_context,
        });
        this.$('.o_content').append(html);
    },
    downloadPDF(){
        framework.blockUI();
        this.getSession().get_file({
            url: "/web/account_report_trial_balance/" + this.reportId,
            complete: framework.unblockUI,
            error: (error) => this.call('crash_manager', 'rpc_error', error),
        });
    },
    initialBalanceClicked(event){
        this.drilldownAmount(event, "initial_balance_clicked")
    },
    debitClicked(event){
        this.drilldownAmount(event, "debit_clicked")
    },
    creditClicked(event){
        this.drilldownAmount(event, "credit_clicked")
    },
    balanceClicked(event){
        this.drilldownAmount(event, "balance_clicked")
    },
    closingBalanceClicked(event){
        this.drilldownAmount(event, "closing_balance_clicked")
    },
    async drilldownAmount(event, method){
        event.preventDefault();
        const accountId = getAccountId(event);
        const action = await this._rpc({
            model: "account.report.trial.balance",
            method: method,
            args: [this.reportId, accountId],
            context: this.getSession().user_context,
        })
        this.do_action(action);
    },
});

function getAccountId(event){
    var attributeNode = event.currentTarget.attributes["account-id"];
    return attributeNode ? parseInt(attributeNode.nodeValue) : false;
}

core.action_registry.add("account_report_trial_balance", ReportAction);
return {
    ReportAction,
};

});
