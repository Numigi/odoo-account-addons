# -*- coding: utf-8 -*-
# Part of Creyox Technologies

{
    "name": (
        "Stripe Auto Debit Subscription for Odoo | Stripe Recurring Payments and "
        "Billing Pro | Stripe Odoo Subscription Auto Pay | Stripe Automated "
        "Payment and Subscription Billing"
    ),
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "mailto:support@creyox.com",
    "category": "Accounting",
    "description": """
        This module automates subscription payments in Odoo using Stripe. It
        automatically charges customers on their billing dates, reducing manual
        work and ensuring timely payments. Businesses can set up different
        subscription plans, track payment status in real-time, and handle failed
        payments with automatic retries. The module also syncs with Odoo
        Accounting for accurate financial records. It supports multiple currencies
        and provides a smooth, hassle-free experience for both businesses and
        customers.

        Resize the Sidebar – Adjust the width of the panel to fit your screen.

        Automatic Payments – Charges customers automatically on their billing dates.

        Easy Stripe Integration – Connects Odoo with Stripe for smooth payment processing.

        Recurring Billing – Supports monthly, yearly, or custom subscription plans.

        Real-Time Payment Updates – Instantly tracks payment success or failure.

        Failed Payment Handling – Automatically retries failed payments and sends alerts.

        Odoo Accounting Integration – Syncs all transactions with Odoo’s financial system.

        Multi-Currency Support – Accepts payments in different currencies.

        User-Friendly Setup – Simple configuration with minimal effort.

        Secure Transactions – Uses Stripe’s encryption and PCI-compliant security.

        Better Customer Experience – Hassle-free payments without manual renewals.

        Stripe Auto Debit Subscription
        Stripe Odoo Auto Payment
        Stripe Recurring Payments Pro
        Stripe Subscription Billing
        Stripe Smart Subscription Billing
        Stripe Auto Debit for Odoo
        Stripe Seamless Recurring Payments
        Stripe Odoo Subscription Pay
        Stripe Automated Payments
        Stripe Auto Charge for Odoo
        Stripe Odoo Subscription Auto Pay
        Stripe Easy Recurring Payments
        Stripe Smart Billing
        Stripe Auto Charge Pro for Odoo
        Stripe Odoo Subscription Debit
        Stripe Payment Automation
        Stripe Recurring Billing for Odoo
        Stripe Odoo PayFlow
        Stripe AutoPay for Odoo Subscriptions

        How to set auto payments in Odoo?

        Can Odoo use Stripe for subscriptions?

        How does auto debit work in Odoo?

        Why use Stripe for Odoo payments?

        How to check failed payments in Odoo?

        Can I set different billing times in Odoo?

        How to link Stripe with Odoo?

        Does this module support many currencies?

        How does this module save time?

        Is Stripe payment safe in Odoo?

        How to make Stripe charge customers automatically?

        Can Odoo handle monthly payments?

        How to stop a subscription in Odoo?

        Does Odoo send payment failure alerts?

        Can customers update their payment details?

        How to see payment history in Odoo?

        Does this module work in all countries?

        Can I use Stripe with different Odoo versions?

        How to add multiple payment methods in Odoo?

        Does this module create invoices automatically?
    """,
    "license": "OPL-1",
    "version": "14.0.1.0.0",
    "summary": """
        This module automates subscription payments in Odoo using Stripe. It
        automatically charges customers on their billing dates, reducing manual
        work and ensuring timely payments. Businesses can set up different
        subscription plans, track payment status in real-time, and handle failed
        payments with automatic retries. The module also syncs with Odoo
        Accounting for accurate financial records. It supports multiple currencies
        and provides a smooth, hassle-free experience for both businesses and
        customers.

        Resize the Sidebar – Adjust the width of the panel to fit your screen.

        Automatic Payments – Charges customers automatically on their billing dates.

        Easy Stripe Integration – Connects Odoo with Stripe for smooth payment processing.

        Recurring Billing – Supports monthly, yearly, or custom subscription plans.

        Real-Time Payment Updates – Instantly tracks payment success or failure.

        Failed Payment Handling – Automatically retries failed payments and sends alerts.

        Odoo Accounting Integration – Syncs all transactions with Odoo’s financial system.

        Multi-Currency Support – Accepts payments in different currencies.

        User-Friendly Setup – Simple configuration with minimal effort.

        Secure Transactions – Uses Stripe’s encryption and PCI-compliant security.

        Better Customer Experience – Hassle-free payments without manual renewals.

        Stripe Auto Debit Subscription
        Stripe Odoo Auto Payment
        Stripe Recurring Payments Pro
        Stripe Subscription Billing
        Stripe Smart Subscription Billing
        Stripe Auto Debit for Odoo
        Stripe Seamless Recurring Payments
        Stripe Odoo Subscription Pay
        Stripe Automated Payments
        Stripe Auto Charge for Odoo
        Stripe Odoo Subscription Auto Pay
        Stripe Easy Recurring Payments
        Stripe Smart Billing
        Stripe Auto Charge Pro for Odoo
        Stripe Odoo Subscription Debit
        Stripe Payment Automation
        Stripe Recurring Billing for Odoo
        Stripe Odoo PayFlow
        Stripe AutoPay for Odoo Subscriptions

        How to set auto payments in Odoo?

        Can Odoo use Stripe for subscriptions?

        How does auto debit work in Odoo?

        Why use Stripe for Odoo payments?

        How to check failed payments in Odoo?

        Can I set different billing times in Odoo?

        How to link Stripe with Odoo?

        Does this module support many currencies?

        How does this module save time?

        Is Stripe payment safe in Odoo?

        How to make Stripe charge customers automatically?

        Can Odoo handle monthly payments?

        How to stop a subscription in Odoo?

        Does Odoo send payment failure alerts?

        Can customers update their payment details?

        How to see payment history in Odoo?

        Does this module work in all countries?

        Can I use Stripe with different Odoo versions?

        How to add multiple payment methods in Odoo?

        Does this module create invoices automatically?
    """,
    "depends": [
        "base",
        "mail",
        "payment_stripe",
        "sale",
    ],
    "data": [
        "views/account_move_views.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": [
        "static/description/banner.png"
    ],
    "price": 40,
    "currency": "USD",
}
