"""
EventLedger - Event Budget and Vendor Payment Tracker (CP-070)

An organiser sets budget heads (venue, food, ...), records vendor quotes
per head, selects one quote, pays it in milestones (advance, balance),
and sees budget vs committed vs paid, with alerts when a head goes over.
"""

# ---------------------------------------------------------------
# DATA DESIGN
# One dictionary holds everything. Each key is a head name, and
# each value is a small dictionary describing that head:
#
# heads = {
#     "Venue": {
#         "budget": 50000.0,
#         "quotes": [ {"vendor": "ABC Hall", "amount": 45000.0, "rating": 4.5} ],
#         "selected": 0,       # index of the chosen quote in "quotes", or None
#         "payments": [ {"label": "Advance", "amount": 10000.0} ],
#     }
# }
#
# Committed = amount of the selected quote (0 if none selected yet)
# Paid      = sum of all payments for the head
# Balance   = committed - paid
# ---------------------------------------------------------------
heads = {}


# ---------------- small helper functions ----------------

def money(amount):
    """Format a number like 1,25,000.00 -> 125,000.00"""
    return f"{amount:,.2f}"


def read_amount(prompt):
    """Keep asking until the user types a positive number."""
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print("  Please enter a number, for example 25000.")
            continue
        if value <= 0:
            print("  Amount must be greater than zero.")
            continue
        return value


def read_choice(prompt, low, high):
    """Keep asking until the user types a whole number from low to high."""
    while True:
        text = input(prompt).strip()
        if not text.isdigit():
            print(f"  Please enter a whole number from {low} to {high}.")
            continue
        number = int(text)
        if number < low or number > high:
            print(f"  Please enter a number from {low} to {high}.")
            continue
        return number


def read_rating(prompt):
    """Rating from 1 to 5, or just press Enter to skip (returns None)."""
    while True:
        text = input(prompt).strip()
        if text == "":
            return None
        try:
            value = float(text)
        except ValueError:
            print("  Please enter a rating from 1 to 5, or press Enter to skip.")
            continue
        if value < 1 or value > 5:
            print("  Rating must be between 1 and 5.")
            continue
        return value


def get_committed(head):
    """Amount of the selected quote, or 0 if no quote is selected."""
    if head["selected"] is None:
        return 0.0
    return head["quotes"][head["selected"]]["amount"]


def get_paid(head):
    """Total of all payments made for this head."""
    total = 0.0
    for payment in head["payments"]:
        total += payment["amount"]
    return total


def pick_head():
    """Show numbered heads and return the chosen head name (or None)."""
    if len(heads) == 0:
        print("  No heads yet. Add one first (option 1).")
        return None
    names = list(heads.keys())
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    number = read_choice("Choose head number: ", 1, len(names))
    return names[number - 1]


# ---------------- Core Feature 1: budget heads ----------------

def add_head():
    """Set a budget head such as Venue, Food, Decoration or Sound."""
    name = input("Head name (e.g. Venue, Food, Decoration, Sound): ").strip()
    if name == "":
        print("  Name cannot be empty.")
        return
    for existing in heads:
        if existing.lower() == name.lower():
            print(f"  A head called '{existing}' already exists.")
            return
    budget = read_amount(f"Budget for {name}: ")
    heads[name] = {
        "budget": budget,
        "quotes": [],
        "selected": None,
        "payments": [],
    }
    print(f"  Added head '{name}' with budget {money(budget)}")


def view_heads():
    """List all heads and their budgets."""
    if len(heads) == 0:
        print("  No heads yet. Add one first (option 1).")
        return
    print("\n  Head                 Budget")
    print("  " + "-" * 32)
    for name in heads:
        print("  " + name.ljust(18) + money(heads[name]["budget"]).rjust(14))


# ---------------- Core Feature 2: quotes ----------------

def add_quote():
    """Record a vendor quote under a head."""
    name = pick_head()
    if name is None:
        return
    head = heads[name]
    vendor = input("Vendor name: ").strip()
    if vendor == "":
        print("  Vendor name cannot be empty.")
        return
    for quote in head["quotes"]:
        if quote["vendor"].lower() == vendor.lower():
            print(f"  '{quote['vendor']}' already has a quote under {name}.")
            return
    amount = read_amount("Quote amount: ")
    rating = read_rating("Vendor rating 1-5 (press Enter to skip): ")
    head["quotes"].append({"vendor": vendor, "amount": amount, "rating": rating})
    print(f"  Recorded quote from {vendor} for {name}: {money(amount)}")


def select_quote():
    """Select one quote for a head. Its amount becomes the committed amount."""
    name = pick_head()
    if name is None:
        return
    head = heads[name]
    if len(head["quotes"]) == 0:
        print("  No quotes for this head yet. Add one first (option 3).")
        return
    if len(head["payments"]) > 0:
        print("  Payments already exist for this head, so the quote cannot be changed.")
        return
    for i, quote in enumerate(head["quotes"], 1):
        print(f"  {i}. {quote['vendor']}  -  {money(quote['amount'])}")
    number = read_choice("Select quote number: ", 1, len(head["quotes"]))
    head["selected"] = number - 1
    chosen = head["quotes"][head["selected"]]
    print(f"  Selected {chosen['vendor']}. Committed: {money(chosen['amount'])}")
    check_alert(name)


# ---------------- Core Feature 3: payments ----------------

def record_payment():
    """Record a payment milestone (advance, balance, ...) for a head."""
    name = pick_head()
    if name is None:
        return
    head = heads[name]
    if head["selected"] is None:
        print("  No quote selected for this head yet. Select one first (option 4).")
        return
    committed = get_committed(head)
    paid = get_paid(head)
    remaining = committed - paid
    if round(remaining, 2) <= 0:
        print("  This head is fully paid. Nothing left to pay.")
        return
    vendor = head["quotes"][head["selected"]]["vendor"]
    print(f"  Vendor: {vendor} | Committed: {money(committed)} | "
          f"Paid: {money(paid)} | Left to pay: {money(remaining)}")
    print("  Milestone:  1. Advance   2. Balance   3. Other")
    kind = read_choice("Choose milestone: ", 1, 3)
    if kind == 1:
        label = "Advance"
    elif kind == 2:
        label = "Balance"
    else:
        label = input("Milestone name: ").strip()
        if label == "":
            print("  Milestone name cannot be empty.")
            return
    amount = read_amount("Payment amount: ")
    if round(amount, 2) > round(remaining, 2):
        print(f"  Rejected: that is more than the {money(remaining)} still owed.")
        return
    head["payments"].append({"label": label, "amount": amount})
    print(f"  Recorded {label} of {money(amount)}. "
          f"Left to pay: {money(remaining - amount)}")


# ---------------- Core Feature 4: report ----------------

def status_text(head):
    """Short status for the report: No quote / OK / OVER by X."""
    if head["selected"] is None:
        return "No quote"
    over = get_committed(head) - head["budget"]
    if over > 0:
        return "OVER by " + money(over)
    return "OK"


def show_report():
    """Budget vs committed vs paid per head."""
    if len(heads) == 0:
        print("  No heads yet. Add one first (option 1).")
        return
    print("\n" + "Head".ljust(14) + "Budget".rjust(13) + "Committed".rjust(13)
          + "Paid".rjust(13) + "Balance".rjust(13) + "  Status")
    print("-" * 80)
    total_budget = 0.0
    total_committed = 0.0
    total_paid = 0.0
    for name in heads:
        head = heads[name]
        committed = get_committed(head)
        paid = get_paid(head)
        print(name[:13].ljust(14) + money(head["budget"]).rjust(13)
              + money(committed).rjust(13) + money(paid).rjust(13)
              + money(committed - paid).rjust(13) + "  " + status_text(head))
        total_budget += head["budget"]
        total_committed += committed
        total_paid += paid
    print("-" * 80)
    print("TOTAL".ljust(14) + money(total_budget).rjust(13)
          + money(total_committed).rjust(13) + money(total_paid).rjust(13)
          + money(total_committed - total_paid).rjust(13))


# ---------------- Core Feature 5: alerts ----------------

def check_alert(name):
    """Print a warning if this head's committed amount is above its budget."""
    head = heads[name]
    over = get_committed(head) - head["budget"]
    if over > 0:
        print(f"  *** ALERT: {name} is OVER BUDGET by {money(over)} "
              f"(budget {money(head['budget'])}, committed {money(get_committed(head))}) ***")
        return True
    return False


def show_alerts():
    """Check every head and print all over-budget warnings."""
    if len(heads) == 0:
        print("  No heads yet. Add one first (option 1).")
        return
    found = False
    for name in heads:
        if check_alert(name):
            found = True
    if not found:
        print("  All heads are within budget.")


# ---------------- Stretch feature: compare vendors ----------------

def get_amount(quote):
    """Sort key: the amount of a quote."""
    return quote["amount"]


def compare_vendors():
    """Compare quotes for a head on price and rating, cheapest first."""
    name = pick_head()
    if name is None:
        return
    head = heads[name]
    if len(head["quotes"]) == 0:
        print("  No quotes for this head yet. Add one first (option 3).")
        return
    ordered = sorted(head["quotes"], key=get_amount)
    cheapest = ordered[0]["amount"]
    print("\n" + "Vendor".ljust(18) + "Quote".rjust(13) + "Rating".rjust(9)
          + "Vs cheapest".rjust(14) + "  Note")
    print("-" * 70)
    for quote in ordered:
        rating = "-" if quote["rating"] is None else str(quote["rating"])
        note = ""
        if head["selected"] is not None and quote is head["quotes"][head["selected"]]:
            note = "SELECTED"
        print(quote["vendor"][:17].ljust(18) + money(quote["amount"]).rjust(13)
              + rating.rjust(9) + money(quote["amount"] - cheapest).rjust(14)
              + "  " + note)


# ---------------- demo helper: sample data ----------------

def load_sample_data():
    """Fill an empty tracker with example heads and quotes, so a demo
    can skip the typing. No quote is selected and no payment is made."""
    if len(heads) > 0:
        print("  Sample data can only be loaded when there are no heads yet.")
        return
    # head name -> (budget, [(vendor, amount, rating), ...])
    sample = {
        "Venue": (50000.0, [("Grand Hall", 55000.0, 4.5),
                            ("Royal Lawn", 45000.0, None)]),
        "Food": (30000.0, [("Spice Kitchen", 28000.0, None),
                           ("Tasty Bites", 32000.0, 3.5)]),
        "Sound": (10000.0, [("DJ Beats", 8000.0, 4.0)]),
    }
    for name in sample:
        budget = sample[name][0]
        heads[name] = {"budget": budget, "quotes": [], "selected": None, "payments": []}
        for vendor, amount, rating in sample[name][1]:
            heads[name]["quotes"].append(
                {"vendor": vendor, "amount": amount, "rating": rating})
    print("  Loaded sample data: 3 heads (Venue, Food, Sound) with quotes.")
    print("  No quote is selected yet and no payments are recorded.")


# ---------------- main menu ----------------

def show_menu():
    print("\n===== EventLedger =====")
    print("1. Add budget head")
    print("2. View budget heads")
    print("3. Add vendor quote")
    print("4. Select a quote for a head")
    print("5. Record payment")
    print("6. Budget report")
    print("7. Over-budget alerts")
    print("8. Compare vendors")
    print("9. Load sample data (for demo)")
    print("0. Exit")


def main():
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_head()
        elif choice == "2":
            view_heads()
        elif choice == "3":
            add_quote()
        elif choice == "4":
            select_quote()
        elif choice == "5":
            record_payment()
        elif choice == "6":
            show_report()
        elif choice == "7":
            show_alerts()
        elif choice == "8":
            compare_vendors()
        elif choice == "9":
            load_sample_data()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    main()
