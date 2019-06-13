odoo.define("budget_analysis_account_move_line.pivot", function (require) {
"use strict";

var PivotView = required("web.PivotView");
var PivotController = required("web.PivotController");

var BudgetAnalysisPivotController = PivotController.extend({
    _onCellClick(event){
    	var a = 1;
        return this._super.apply(this, arguments);
    },
});

var BudgetAnalysisPivot = PivotView.extend({
	config: Object.assign({}, PivotView.config, {
		'Controller': BudgetAnalysisPivotController,
	}),
});

});
