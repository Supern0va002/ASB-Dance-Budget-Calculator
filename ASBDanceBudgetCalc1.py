"""
ASB Dance Ticket Price Calculator
Calculates the base ticket price needed to break even on a dance budget.
 
Ticket Tiers:
  - Activity sticker + Early:    x
  - Activity sticker + Late:     x + $5
  - No sticker + Early:          x + $5
  - No sticker + Late:           x + $10
"""
 
import math
 
# ── Attendance per dance, edit numbers to reflect past average attendance ──────────
ATTENDANCE = {
    "homecoming":     100,
    "winter formal":  100,
    "tolo":           100,
    "prom":           100,
}
 
# ── Ticket distribution percentages, edit according to expected percentages. Must add to 100, don't use decimals ──────────────────────
PERCENTAGES = {
    "sticker_early":    25,   # Activity sticker, bought early
    "sticker_late":     25,   # Activity sticker, bought late
    "no_sticker_early": 25,   # No sticker, bought early
    "no_sticker_late":  25,   # No sticker, bought late
}
 
 
def get_dance_choice():
    """Prompt the user to select a dance and return its name."""
    dances = list(ATTENDANCE.keys())
    print("\nWhich dance are you calculating for?")
    for i, dance in enumerate(dances, 1):
        print(f"  {i}. {dance.title()}")
 
    while True:
        choice = input("\nEnter the number of the dance: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(dances):
            return dances[int(choice) - 1]
        print("  Please enter a valid number from the list.")
 
 
def get_budget():
    """Prompt the user to enter the dance budget."""
    while True:
        raw = input("Enter the dance budget: ").strip().lstrip("$").replace(",", "")
        try:
            budget = float(raw)
            if budget <= 0:
                print("  Budget must be greater than $0.")
                continue
            return budget
        except ValueError:
            print("  Please enter a valid dollar amount (e.g. 10,000).")
 
 
def get_profit_goal():
    """Prompt the user to enter the desired profit."""
    while True:
        raw = input("Enter the desired profit: ").strip().lstrip("$").replace(",", "")
        try:
            profit = float(raw)
            if profit < 0:
                print("  Profit can't be negative. Enter 0 if you don't want any profit.")
                continue
            return profit
        except ValueError:
            print("  Please enter a valid dollar amount (e.g. 500).")
 
 
def validate_percentages(pcts):
    """Check that the tier percentages add up to 100."""
    total = sum(pcts.values())
    if abs(total - 100) > 0.01:
        raise ValueError(
            f"Ticket distribution percentages must add to 100, but they add to {total}. "
            "Update the PERCENTAGES dictionary at the top of the script."
        )
 
 
def calculate_base_price(target, attendance, pcts):
    """
    Solve for base price x so that total revenue == target.
 
    'target' is whatever revenue goal you're solving for — pass in the
    budget alone to find the break-even price, or budget + profit to
    find the price needed to also clear that much profit.
 
    Revenue formula:
      n_SE * x  +  n_SL * (x+5)  +  n_NE * (x+5)  +  n_NL * (x+10)  =  target
      x * (n_SE + n_SL + n_NE + n_NL)  +  5*n_SL  +  5*n_NE  +  10*n_NL  =  target
      x  =  (target - fixed_add) / total_students
    """
    n_se = attendance * (pcts["sticker_early"]    / 100)
    n_sl = attendance * (pcts["sticker_late"]     / 100)
    n_ne = attendance * (pcts["no_sticker_early"] / 100)
    n_nl = attendance * (pcts["no_sticker_late"]  / 100)
 
    fixed_add = 5 * n_sl + 5 * n_ne + 10 * n_nl
    total_students = n_se + n_sl + n_ne + n_nl
 
    if total_students == 0:
        raise ValueError("Total student attendance cannot be zero.")
 
    x_raw = (target - fixed_add) / total_students
    # Round UP to the nearest whole dollar so students never need change,
    # and so the rounded price still meets (or slightly exceeds) the target.
    x = math.ceil(x_raw)
    return x, n_se, n_sl, n_ne, n_nl
 
 
def print_results(dance, budget, profit_goal, attendance,
                   x_breakeven, x_profit,
                   n_se, n_sl, n_ne, n_nl):
    """Print a formatted breakdown comparing break-even and profit-goal pricing."""
    col = 32
 
    print()
    print("=" * 70)
    print(f"  {dance.title()} — Ticket Price Breakdown")
    print("=" * 70)
    print(f"  {'Budget:':<{col}} ${budget:>10,.2f}")
    print(f"  {'Desired profit:':<{col}} ${profit_goal:>10,.2f}")
    print(f"  {'Historical attendance:':<{col}} {attendance:>10}")
    print()
 
    def tier_breakdown(x, label):
        price_se = x
        price_sl = x + 5
        price_ne = x + 5
        price_nl = x + 10
 
        rev_se = n_se * price_se
        rev_sl = n_sl * price_sl
        rev_ne = n_ne * price_ne
        rev_nl = n_nl * price_nl
        total_rev = rev_se + rev_sl + rev_ne + rev_nl
        surplus = total_rev - budget
 
        print(f"  --- {label} (base price = ${x:.0f}) ---")
        print(f"  {'Tier':<28} {'Students':>8}  {'Price':>8}  {'Revenue':>10}")
        print(f"  {'-'*28}  {'-'*8}  {'-'*8}  {'-'*10}")
 
        tiers = [
            ("Sticker + Early",    n_se, price_se, rev_se),
            ("Sticker + Late",     n_sl, price_sl, rev_sl),
            ("No Sticker + Early", n_ne, price_ne, rev_ne),
            ("No Sticker + Late",  n_nl, price_nl, rev_nl),
        ]
        for tlabel, n, price, rev in tiers:
            print(f"  {tlabel:<28} {round(n):>8}  ${price:>7.0f}  ${rev:>9,.2f}")
        print()  # blank line after each tier table
 
    tier_breakdown(x_breakeven, "BREAK-EVEN (profit = $0)")
 
    if profit_goal > 0:
        tier_breakdown(x_profit, f"PROFIT GOAL (profit = ${profit_goal:,.2f})")
 
    print("=" * 70)
    print(f"  PRICE TO BREAK EVEN:            ${x_breakeven:.0f}  "
          f"(range ${x_breakeven:.0f} – ${x_breakeven+10:.0f})")
    if profit_goal > 0:
        print(f"  PRICE TO PROFIT ${profit_goal:,.2f}:".ljust(41) +
              f"${x_profit:.0f}  (range ${x_profit:.0f} – ${x_profit+10:.0f})")
    print("=" * 70)
    print()
 
 
def main():
    print()
    print("╔══════════════════════════════════════╗")
    print("║   ASB Dance Ticket Price Calculator  ║")
    print("╚══════════════════════════════════════╝")
 
    try:
        validate_percentages(PERCENTAGES)
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        return
 
    dance = get_dance_choice()
    budget = get_budget()
    profit_goal = get_profit_goal()
    attendance = ATTENDANCE[dance]
 
    try:
        x_breakeven, n_se, n_sl, n_ne, n_nl = calculate_base_price(budget, attendance, PERCENTAGES)
        x_profit = x_breakeven
        if profit_goal > 0:
            x_profit, _, _, _, _ = calculate_base_price(budget + profit_goal, attendance, PERCENTAGES)
    except ValueError as e:
        print(f"\nError: {e}")
        return
 
    print_results(dance, budget, profit_goal, attendance,
                   x_breakeven, x_profit,
                   n_se, n_sl, n_ne, n_nl)
 
    # Ask if the user wants to run another calculation
    again = input("Calculate for another dance? (y/n): ").strip().lower()
    if again == "y":
        main()
 
 
if __name__ == "__main__":
    main()
