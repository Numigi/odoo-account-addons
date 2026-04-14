odoo.define('account_reconciliation_default_payment.ReconciliationModel', function (require) {
"use strict";

    // Import the original model
    var ReconciliationModel = require('account.ReconciliationModel');

    // Override the StatementModel
    ReconciliationModel.StatementModel.include({

        /**
         * Override default mode to prioritize match_other (Outstanding payments)
         * over match_rp (Customer/Vendor Matching).
         */
        _getDefaultMode: function (handle) {
            var line = this.getLine(handle);
            if (
                line.balance.amount === 0 &&
                (!line.st_line.mv_lines_match_rp ||
                    line.st_line.mv_lines_match_rp.length === 0) &&
                (!line.st_line.mv_lines_match_other ||
                    line.st_line.mv_lines_match_other.length === 0)
            ) {
                return "inactive";
            }

            // LOGIC CHANGE HERE : Prioritize match_other instead of match_rp
            if (line.mv_lines_match_other && line.mv_lines_match_other.length) {
                return "match_other";
            }
            if (line.mv_lines_match_rp && line.mv_lines_match_rp.length) {
                return "match_rp";
            }

            return "create";
        },
    });
});