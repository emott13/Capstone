class TaxService:

    @staticmethod
    def calculate_tax(order_items, state, taxable_amount):

        tax_rate = TaxService.get_tax_rate(state)

        return int(taxable_amount * tax_rate)


    @staticmethod
    def get_tax_rate(state):

        rates = {
            "PA": 0.06,
            "CA": 0.0725,
            "NY": 0.04
        }

        return rates.get(state, 0.05)