import random

qty = 3
die = 20
mod = +2

# Set qty to 1 if none given, else make int
if not qty:
    qty = 1
else:
    qty = int(qty)

# Set mod to 0 if none given, else make int
if not mod:
    mod = 0
else:
    mod = int(mod)

# Initalize list for all rolls
rolls = []

# Initialize list for rolls plus mod
totals = []

# Loop once for each die roll
for i in range(qty):

    # Append roll result to list
    rolls.append(random.randint(1, die))

    # Add modifier, append to totals list
    total = rolls[i] + mod
    totals.append(total)

    # Testing, print results
    print(f"Roll {i}: {rolls[i]} + {mod} = {rolls[i] + mod}")

# Testing, print lists
print(rolls)
print(totals)