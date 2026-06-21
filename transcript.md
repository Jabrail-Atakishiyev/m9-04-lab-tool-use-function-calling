# Transcript — Tool Use / Function Calling Lab



## 1. Two-tool question

**Question:** "For order A1001, what would the total be if I bought three of them?"

```
======================================================================
QUESTION: For order A1001, what would the total be if I bought three of them?
======================================================================
  [tool call] lookup_order({'order_id': 'A1001'})
  [tool result] {'found': True, 'order_id': 'A1001', 'item': 'laptop', 'price': 1200, 'purchased': '2026-05-20', 'warranty_months': 12}
  [tool call] calculate({'expression': '1200 * 3'})
  [tool result] {'result': 3600}

FINAL ANSWER: If you bought three of order A1001 (laptop, $1200 each), the total would be $3600.
```

## 2. No-tool question

**Question:** "What can you help me with?"

```
======================================================================
QUESTION: What can you help me with?
======================================================================

FINAL ANSWER: I can help you look up order details (item, price, purchase date, warranty) using an order ID, and perform arithmetic calculations. For example, I can tell you what an order would cost if you bought multiple units.
```

## 3. Optional stretch — non-existent order

**Question:** "What's the price for order A9999?"

```
======================================================================
QUESTION: What's the price for order A9999?
======================================================================
  [tool call] lookup_order({'order_id': 'A9999'})
  [tool result] {'found': False, 'error': "Order 'A9999' not found."}

FINAL ANSWER: I couldn't find an order with ID A9999. Please double-check the order ID and try again.
```