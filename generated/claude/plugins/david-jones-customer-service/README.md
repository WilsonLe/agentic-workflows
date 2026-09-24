# David Jones Customer Service

An instruction-only Agentic Workflows plugin for customer-service procedures at David
Jones. The first workflow is the **Till Sale — EFTPOS (No Cash)**, an internal
working name for completing a customer purchase at a David Jones till.

## First workflow

The `david-jones-till-sales` skill covers:

- preparing and signing in to an authorized till without exposing employee credentials;
- asking for a David Jones Rewards card and, if needed, trying the customer's phone number;
- scanning each item and allowing the till time to register it;
- detagging authorized merchandise and checking for the detagging beep;
- selecting the card/EFTPOS no-cash route, taking payment at the terminal, and printing the receipt;
- offering a suitable bag, placing the folded receipt and items inside, and closing courteously.

This package records no employee passwords, customer phone numbers, rewards profiles,
payment-card data, or POS state. Exact till labels and exceptions must follow the
current store training and supervisor instructions. Returns, refunds, cash,
split payments, discounts, price overrides, gift cards, and other processes are
outside this first release.

Start with:

```text
Guide me through the David Jones till sale process one step at a time.
```
