"""Baseline user display implementation with multiple inefficiencies.

This module is intentionally naive and inefficient. It is designed
to serve as a starting point for refactoring and architectural
improvements.
"""

import time


def display_users(users, show_all=True, verbose=False):
    """
    Display all users in a single large string.

    This implementation is intentionally inefficient:
    - Uses string concatenation in a loop
    - Sleeps on every user to simulate slow processing
    - Repeats field extraction for each user
    - Has no error handling or logging
    """
    result = ""
    processed_count = 0

    for user in users:
        if verbose:
            print("Processing user:", user["id"])

        # Repeated extraction of fields
        user_id = user["id"]
        user_name = user["name"]
        user_email = user["email"]
        user_role = user["role"]
        user_status = user["status"]
        user_join_date = user["join_date"]
        user_last_login = user["last_login"]

        # Inefficient string building and fixed formatting
        line = "ID: " + str(user_id)
        line += " | Name: " + user_name
        line += " | Email: " + user_email
        line += " | Role: " + user_role
        line += " | Status: " + user_status
        line += " | Join Date: " + user_join_date
        line += " | Last Login: " + user_last_login

        result += line + "\n"
        processed_count += 1

        # Artificial delay
        time.sleep(0.01)

    if show_all:
        result += "\nTotal users processed: " + str(processed_count) + "\n"

    return result


def get_user_by_id(users, user_id):
    """
    Linear search for a user by ID.

    Inefficient for large lists, and does not handle missing keys.
    """
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def filter_users(users, criteria):
    """
    Filter users based on a simple criteria dictionary.

    This implementation:
    - Uses nested, repetitive condition checks
    - Is hard to extend
    - Does not support case sensitivity control or advanced rules
    """
    filtered = []

    for user in users:
        include = True

        if "role" in criteria:
            if "role" not in user or user["role"] != criteria["role"]:
                include = False

        if "status" in criteria:
            if "status" not in user or user["status"] != criteria["status"]:
                include = False

        if "name" in criteria:
            name_value = user.get("name", "")
            search_value = criteria["name"]
            # Always case-insensitive, hard-coded behavior
            if search_value.lower() not in name_value.lower():
                include = False

        if "email" in criteria:
            email_value = user.get("email", "")
            search_email = criteria["email"]
            if search_email.lower() not in email_value.lower():
                include = False

        if include:
            filtered.append(user)

    return filtered


def export_users_to_string(users):
    """
    Export users to a multi-line string.

    This implementation:
    - Builds multiple temporary strings
    - Has fixed formatting that cannot be customized
    - Does not handle missing fields
    """
    output = "USER_EXPORT_START\n"
    output += "=" * 80 + "\n"

    for user in users:
        temp = ""
        temp += "User ID: " + str(user["id"]) + "\n"
        temp += "  Name: " + user["name"] + "\n"
        temp += "  Email: " + user["email"] + "\n"
        temp += "  Role: " + user["role"] + "\n"
        temp += "  Status: " + user["status"] + "\n"
        temp += "  Join Date: " + user["join_date"] + "\n"
        temp += "  Last Login: " + user["last_login"] + "\n"
        temp += "-" * 80 + "\n"

        output += temp

    output += "USER_EXPORT_END\n"
    return output


# Sample data for manual testing and demonstration
sample_users = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "role": "Admin",
        "status": "Active",
        "join_date": "2023-01-15",
        "last_login": "2025-11-26",
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "role": "User",
        "status": "Inactive",
        "join_date": "2023-06-20",
        "last_login": "2025-11-20",
    },
    {
        "id": 3,
        "name": "Bob Johnson",
        "email": "bob@example.com",
        "role": "Moderator",
        "status": "Active",
        "join_date": "2024-02-10",
        "last_login": "2025-11-25",
    },
    {
        "id": 4,
        "name": "Alice Williams",
        "email": "alice@example.com",
        "role": "User",
        "status": "Active",
        "join_date": "2024-05-12",
        "last_login": "2025-11-26",
    },
    {
        "id": 5,
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "role": "User",
        "status": "Active",
        "join_date": "2024-08-03",
        "last_login": "2025-11-24",
    },
]


if __name__ == "__main__":
    print("Baseline Implementation Output")
    print("=" * 80)
    text = display_users(sample_users, show_all=True, verbose=False)
    print(text)

    print("Single user lookup (id=3)")
    print(get_user_by_id(sample_users, 3))

    print("Filter users by role=User and status=Active")
    filtered_list = filter_users(sample_users, {"role": "User", "status": "Active"})
    print(export_users_to_string(filtered_list))
