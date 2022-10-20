odoo.define("mis_builder_automated_report.widget", function (require) {
    "use strict";

    var MisReportWidget = require("mis_builder.widget");

    var MisReportAutoWidget = MisReportWidget.include({
        events: _.extend({}, MisReportWidget.prototype.events, {
            "click .oe_mis_builder_automated_export": "autoExportXls",
        }),

        init: function () {
            var self = this;
            self._super.apply(self, arguments);
        },

        autoExportXls: function () {
            var self = this;
            var context = self.getParent().state.context;
            context['automated_edition'] = true
            this._rpc({
                model: "mis.report.instance",
                method: "export_xls",
                args: [this._instanceId()],
                context: context,
            }).then(function (result) {
                self.do_action(result);
            });
        },
    });

    return MisReportAutoWidget;
});
