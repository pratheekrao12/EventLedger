# EventLedger: Event Budget and Vendor Payment Tracker

**Capstone problem:** CP-070 (Intermediate, Food, Hospitality and Events)
**Language:** Python 3 (console, menu-driven, no external libraries)

## Problem

Event organisers lose track of quotes, advances and balances across many
vendors and overshoot the budget. EventLedger keeps every budget head, vendor
quote and payment in one place and warns as soon as a head goes over budget.

## Features

### Core features (all 5)
1. **Budget heads:** set heads such as Venue, Food, Decoration and Sound, each with a budget.
2. **Vendor quotes:** record quotes per head and select one. The selected quote becomes the *committed* amount.
3. **Payment milestones:** record Advance, Balance or a custom milestone against the selected quote.
4. **Budget report:** budget vs committed vs paid vs balance for every head, with totals.
5. **Over-budget alerts:** warns when a head's committed amount is above its budget, both when a quote is selected and on demand.

### Stretch feature
- **Compare vendors:** quotes for a head sorted by price, with rating and the difference from the cheapest.

## How to run

```
python eventledger.py
```

Requires Python 3.6 or newer. No installation needed.

## Menu

```
1. Add budget head
2. View budget heads
3. Add vendor quote
4. Select a quote for a head
5. Record payment
6. Budget report
7. Over-budget alerts
8. Compare vendors
0. Exit
```

## Data design

All data lives in one dictionary, `heads`. Each head is itself a dictionary:

```python
heads = {
    "Venue": {
        "budget": 50000.0,
        "quotes": [{"vendor": "Grand Hall", "amount": 55000.0, "rating": 4.5}],
        "selected": 0,        # index of the chosen quote, or None
        "payments": [{"label": "Advance", "amount": 20000.0}],
    }
}
```

- **Committed** = amount of the selected quote (0 if none selected)
- **Paid** = sum of the head's payments
- **Balance** = committed - paid
- **Over budget** = committed > budget

## Wrong input handled

| Situation | What the program does |
|---|---|
| Text or empty input where a number is expected | Asks again |
| Zero or negative amount | Rejected, asks again |
| Menu or list choice out of range | Rejected, asks again |
| Invalid menu option | "Invalid choice" message |
| Empty or duplicate head name (any capitalisation) | Rejected |
| Empty or duplicate vendor name under the same head | Rejected |
| Rating outside 1 to 5 | Rejected, asks again |
| Using a feature before any head exists | Tells the user to add a head first |
| Selecting a quote when the head has no quotes | Tells the user to add a quote first |
| Paying before a quote is selected | Rejected |
| Paying more than what is still owed | Rejected, shows the amount owed |
| Paying a head that is already fully paid | Rejected |
| Changing the selected quote after payments exist | Rejected |

## Sample run

```
Head                 Budget    Committed         Paid      Balance  Status
--------------------------------------------------------------------------------
Venue             50,000.00    55,000.00    55,000.00         0.00  OVER by 5,000.00
Food              30,000.00    28,000.00    10,000.00    18,000.00  OK
--------------------------------------------------------------------------------
TOTAL             80,000.00    83,000.00    65,000.00    18,000.00

*** ALERT: Venue is OVER BUDGET by 5,000.00 (budget 50,000.00, committed 55,000.00) ***
```

## Test cases

| # | Test | Expected result | Result |
|---|---|---|---|
| 1 | Add head "Venue" with budget 50000 | Head added | Pass |
| 2 | Add head "venue" again | Duplicate rejected | Pass |
| 3 | Budget typed as `abc` | Asks again | Pass |
| 4 | Budget typed as `-5` or `0` | Asks again | Pass |
| 5 | Add the same vendor twice under one head | Second one rejected | Pass |
| 6 | Select a quote costing more than the budget | Over-budget alert shown | Pass |
| 7 | Pay before selecting a quote | Rejected | Pass |
| 8 | Pay 20000 advance on a 55000 quote | Left to pay 35000 | Pass |
| 9 | Pay 40000 when only 35000 is owed | Rejected | Pass |
| 10 | Pay exactly the remaining 35000 | Left to pay 0 | Pass |
| 11 | Pay again on a fully paid head | Rejected | Pass |
| 12 | Change the quote after payments exist | Rejected | Pass |
| 13 | Report with no heads | Asks to add a head first | Pass |
| 14 | Type `abc` at the main menu | Invalid choice message | Pass |
| 15 | Compare vendors with a vendor that has no rating | Shows `-` for rating | Pass |

## Possible improvements

- Save and load data from a CSV file so it survives closing the program
- List pending payments by due date
- Edit or delete heads and quotes

