---
description: Seed realistic dummy expenses for a specific user
argument-hint: "<user_id> <count> <months>"
allowed-tools: Read, Bash(python3:*)
---

Read database/db.py to understand:
- the expenses table schema
- the users table schema
- the database connection pattern
- the database file name/path

User input: $ARGUMENTS

## Step 1 — Parse arguments

Extract from $ARGUMENTS:

- user_id — integer
- count — integer, number of expenses to create
- months — integer, how many past months to spread them across

If any argument is missing or not a valid integer, stop and say exactly:

"Usage: /seed-expenses <user_id> <count> <months>
Example: /seed-expenses 1 50 6"

Do not modify the database if the arguments are invalid.

## Step 2 — Verify user exists

Before generating anything, confirm that the given user_id exists in the users table.

If not, stop and say:

"No user found with id <user_id>."

Do not insert anything.

## Step 3 — Generate and insert expenses

Write and run a Python script that:

1. Generates exactly <count> expenses.

2. Spreads their dates randomly across the past <months> months.

3. Uses these categories with realistic Indian descriptions and amounts in INR:

   - Food: ₹50–₹800
   - Transport: ₹20–₹500
   - Bills: ₹200–₹3000
   - Health: ₹100–₹2000
   - Entertainment: ₹100–₹1500
   - Shopping: ₹200–₹5000
   - Other: ₹50–₹1000

4. Distributes categories roughly proportionally:
   - Food should be most common
   - Transport and Shopping should be moderately common
   - Bills and Other should be moderately less common
   - Health and Entertainment should be least common

5. Generates realistic Indian expense descriptions appropriate to each category.

6. Every expense must belong to the specified user_id.

7. Uses the database connection pattern from database/db.py.

8. Do NOT hardcode the database filename.

9. Use parameterised SQL queries only.

10. Do NOT modify or delete existing expenses.

11. Do NOT modify or delete users.

12. Do NOT call seed_db().

13. Insert all generated expenses in ONE database transaction.

14. If any insert fails, roll back the entire transaction so that none of the new expenses are inserted.

15. Commit only after all <count> expenses have been successfully inserted.

## Step 4 — Confirm

After successful insertion, print:

- Number of expenses inserted
- User ID
- Date range of the inserted expenses
- A sample of 5 inserted records showing:
  - id
  - category
  - description
  - amount
  - date