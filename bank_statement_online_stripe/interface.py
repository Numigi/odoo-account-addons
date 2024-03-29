import stripe

TRANSACTION_BATCH_LIMIT = 100


class BalanceTransactionInterface:
    def __init__(
        self,
        datetime_from,
        datetime_to,
        api_key,
        currency,
    ):
        self._timestamp_from = self._get_timestamp(datetime_from)
        self._timestamp_to = self._get_timestamp(datetime_to)
        self._api_key = api_key
        self._currency = currency.lower()

    def get_start_balance(self):
        return self._get_balance_at(self._timestamp_from)

    def get_end_balance(self):
        return self._get_balance_at(self._timestamp_to)

    def _get_balance_at(self, timestamp):
        current_balance = self._get_current_balance()
        created = {
            "gte": timestamp,
        }
        transactions = self._iter_transactions(created=created)
        balance = current_balance - sum(
            t.get("amount", 0) - t.get("fee", 0) for t in transactions
        )
        return balance / 100

    def _get_current_balance(self):
        payload = stripe.Balance.retrieve(api_key=self._api_key)
        balance = next(
            (b for b in payload["pending"] if b["currency"] == self._currency)
        )
        return balance["amount"]

    def list_transactions(self):
        created = {
            "gte": self._timestamp_from,
            "lt": self._timestamp_to,
        }
        return [t for t in self._iter_transactions(created=created)]

    def _iter_transactions(self, created):
        for items in self._walk_transaction_batches(created):
            yield from iter(items)

    def _walk_transaction_batches(self, created, starting_after=None):
        payload = stripe.BalanceTransaction.list(
            created=created,
            limit=TRANSACTION_BATCH_LIMIT,
            currency=self._currency,
            api_key=self._api_key,
            starting_after=starting_after,
            expand=["data.source.billing_details"],
        )
        items = payload["data"]
        yield items

        if payload["has_more"]:
            last_item_id = items[-1]["id"]
            yield from self._walk_transaction_batches(
                created=created, starting_after=last_item_id
            )

    @staticmethod
    def _get_timestamp(datetime_):
        return int(datetime_.timestamp())
