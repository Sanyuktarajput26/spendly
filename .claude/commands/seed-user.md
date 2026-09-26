---
description: Create a single dummy user in the existing database
allowed-tools: Read, Bash(python3:*)
---

Read database/db.py to understand the users table schema and the get_db() helper.

Then write and run a Python script using Bash that:

1. Generates ONE realistic random Indian user using common Indian first and last names across different regions.

   - Name: realistic Indian first name + last name
   - Email: derived from the name with a random 2-3 digit number suffix, for example:
     rahul.sharma91@gmail.com
   - Password: exactly "password123", hashed using Werkzeug's generate_password_hash
   - created_at: current datetime

2. Check whether the generated email already exists in the users table.

3. If the email already exists, generate another random email and check again until the email is unique.

4. Insert the new user into the EXISTING database using the same get_db() pattern found in database/db.py.

5. Do NOT delete, replace, or recreate the existing database.

6. Do NOT call seed_db().

7. Do NOT modify or delete the existing Demo User.

8. Do NOT insert any expenses.

9. Add exactly ONE new user.

10. Commit the transaction.

11. Print confirmation:
    - id
    - name
    - email