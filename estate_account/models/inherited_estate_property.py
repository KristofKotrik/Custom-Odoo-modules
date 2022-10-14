from odoo import Command, models


class Property(models.Model):
    _inherit = "estate.property"

    # FIXED error when trying to sell a property -> "Missing required account on accountable invoice line."
    def action_state_sold(self):
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()

        # DONE add actual property price to line_ids?
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'journal_id': journal.id,
            'line_ids': [
                Command.create({
                    "name": self.name,
                    "quantity": 1,
                    "price_unit": self.selling_price,
                    "account_id": 1,  # TODO find out why this needs to be here
                }),
                Command.create({
                    "name": "Provision",
                    "quantity": 1,
                    "price_unit": self.selling_price * 6/100,
                    "account_id": 1,  # TODO find out why this needs to be here
                }),
                Command.create({
                    "name": "Administrative fees",
                    "quantity": 1,
                    "price_unit": 100,
                    "account_id": 1,  # TODO find out why this needs to be here
                })
            ]
        }
        self.env['account.move'].with_context(
            default_move_type='out_invoice',
            check_move_validity=False  # TODO find out why this needs to be here
        ).create(invoice_vals)
        return super().action_state_sold()
