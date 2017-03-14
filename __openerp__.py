# -*- encoding: utf-8 -*-
##############################################################################
##############################################################################

{   
    "name"        : "Fleet Management",
    "version"     : "1.0",
    "category"    : "Logistic",
    'complexity'  : "Alta",
    "author"      : "Alejandro Rodriguez",
    "depends"     : ["hr", "account_voucher", "purchase","sale", "fleet"],
    "summary"     : "Management System for Carriers, Trucking companies and other freight companies",
    "data" : [
#        'security/tms_security.xml',
        #'views/sale_shop_view.xml',
#        'security/ir.model.access.csv',
        #'views/product_view.xml',
        #'views/ir_config_parameter.xml',
        #'views/ir_sequence_view.xml',
        #'views/account_view.xml',
        #'views/hr_view.xml',
        #'views/partner_view.xml',
        'views/sale_view.xml',
		"views/transportista_view.xml",
        #'views/tms_view.xml',
        #'views/tms_travel_view.xml',
        #'views/tms_advance_view.xml',
        #'views/tms_fuelvoucher_view.xml',
        #'views/tms_waybill_view.xml',
        #'views/tms_expense_view.xml',
        #'views/tms_factor_view.xml',
        #'views/tms_history_view.xml',
        #'views/tms_operation_view.xml',
        #'views/tms_expense_loan_view.xml',
        ],
    "application": True,
    "installable": True
}
