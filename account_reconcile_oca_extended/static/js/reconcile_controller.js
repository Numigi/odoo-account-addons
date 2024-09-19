/** @odoo-module */
const {onMounted, onWillStart, useState, useSubEnv} = owl;
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {View} from "@web/views/view";
import {formatMonetary} from "@web/views/fields/formatters";
import {useService} from "@web/core/utils/hooks";

export class ReconcileController extends KanbanController {

    async updateJournalInfo() {
        var journalId = this.journalId;
        if (!journalId) {
            return;
        }
        if (this.props.context.active_model == "account.move") {
            var move_id = await this.orm.call("account.move", "read", [
                [journalId],
                ["journal_id"],
            ]);
            journalId = move_id[0].journal_id[0];
        }
        var result = await this.orm.call("account.journal", "read", [
            [journalId],
            ["current_statement_balance", "currency_id", "company_currency_id"],
        ]);
        this.state.journalBalance = result[0].current_statement_balance;
        this.state.currency = (result[0].currency_id ||
            result[0].company_currency_id)[0];
    }

ReconcileController.components = {
    ...ReconcileController.components,
    View,
};

ReconcileController.template = "account_reconcile_oca_extended.ReconcileController";
ReconcileController.defaultProps = {};