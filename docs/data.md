# RecoverOS Synthetic Payment Dataset

RecoverOS uses a synthetic payment environment for development,
testing and evaluation.

## Generated entities

- Merchants
- Customers
- Transactions
- Recovery actions

## Transactions

Each transaction contains:

- transaction ID
- merchant
- customer
- timestamp
- amount
- payment method
- transaction type
- payment status
- failure reason
- attempt number
- recoverability label
- review requirement

## Important

This dataset is synthetic and does not contain real customer,
payment or financial information.

The ground-truth recoverability labels are used for evaluating
the future ML and recovery decision systems.