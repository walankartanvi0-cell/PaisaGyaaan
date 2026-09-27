# =========================================================
# PAISAGYAAN
# Financial Literacy & Awareness Platform
#
# Flask Backend + SQLite Database
# =========================================================


# =========================================================
# 1. IMPORTS
# =========================================================

import os
import sqlite3
from functools import wraps
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# 2. FLASK APPLICATION
# =========================================================

app = Flask(__name__)

# Secret key is used for Flask sessions.
# For development, this fallback works.
# Later, we can move it into an environment variable.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "paisa-gyaan-development-secret-key-change-later"
)


# =========================================================
# 3. DATABASE CONFIGURATION
# =========================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "database.db"
)

SCHEMA_FILE = os.path.join(
    BASE_DIR,
    "schema.sql"
)


# =========================================================
# 4. DATABASE CONNECTION
# =========================================================

def get_db_connection():
    """
    Create and return a SQLite database connection.

    sqlite3.Row allows us to access columns like:

        user["first_name"]

    instead of:

        user[0]
    """

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    # Enable foreign key support.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# =========================================================
# 5. DATABASE INITIALIZATION
# =========================================================

def initialize_database():
    """
    Create the SQLite database and all required tables
    using schema.sql.
    """

    connection = sqlite3.connect(DATABASE)

    connection.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as schema:
        connection.executescript(schema.read())

    connection.commit()
    connection.close()

    print("==============================================")
    print("PaisaGyaan database initialized successfully.")
    print("Database:", DATABASE)
    print("==============================================")


# =========================================================
# 6. LOGIN REQUIRED DECORATOR
# =========================================================

def login_required(function):
    """
    Protect routes that require a logged-in user.

    If the user is not logged in, they are redirected
    to the login page.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login to access this page.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return decorated_function


# =========================================================
# 7. HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# 8. PUBLIC EDUCATIONAL PAGES
# =========================================================

@app.route("/learn")
def learn():

    return render_template(
        "learn.html"
    )


@app.route("/investments")
def investments():

    return render_template(
        "investments.html"
    )


@app.route("/loans")
def loans():

    return render_template(
        "loans.html"
    )


@app.route("/safety")
def safety():

    return render_template(
        "safety.html"
    )


@app.route("/scams")
def scams():

    return render_template(
        "scams.html"
    )


# =========================================================
# 9. COMMUNITY
# =========================================================

@app.route("/community")
def community():

    connection = get_db_connection()

    posts = connection.execute(
        """
        SELECT
            community_posts.id,
            community_posts.title,
            community_posts.content,
            community_posts.category,
            community_posts.created_at,
            users.first_name,
            users.last_name
        FROM community_posts
        JOIN users
            ON community_posts.user_id = users.id
        ORDER BY community_posts.created_at DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "community.html",
        posts=posts
    )


# =========================================================
# 10. REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # If already logged in, don't show registration page.
    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        first_name = request.form.get(
            "first_name",
            ""
        ).strip()

        last_name = request.form.get(
            "last_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not first_name:
            flash(
                "Please enter your first name.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if not last_name:
            flash(
                "Please enter your last name.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if not email:
            flash(
                "Please enter your email address.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if not password:
            flash(
                "Please enter a password.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        connection = get_db_connection()

        # -------------------------------------------------
        # Check existing email
        # -------------------------------------------------

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            connection.close()

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = generate_password_hash(
            password
        )

        # -------------------------------------------------
        # Create user
        # -------------------------------------------------

        connection.execute(
            """
            INSERT INTO users
            (
                first_name,
                last_name,
                email,
                password_hash
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                first_name,
                last_name,
                email,
                password_hash
            )
        )

        connection.commit()

        connection.close()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# 11. LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter your email and password.",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if user is None:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        # -------------------------------------------------
        # Create session
        # -------------------------------------------------

        session.clear()

        session["user_id"] = user["id"]
        session["user_email"] = user["email"]

        flash(
            f"Welcome back, {user['first_name']}!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# 12. LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# =========================================================
# 13. GET CURRENT USER
# =========================================================

def get_current_user():

    if "user_id" not in session:
        return None

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return user


# =========================================================
# 14. DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    connection = get_db_connection()

    # -----------------------------------------------------
    # User
    # -----------------------------------------------------

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    # -----------------------------------------------------
    # Total Income
    # -----------------------------------------------------

    income_result = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        AND transaction_type = 'income'
        """,
        (user_id,)
    ).fetchone()

    total_income = income_result["total"]

    # -----------------------------------------------------
    # Total Expenses
    # -----------------------------------------------------

    expense_result = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        AND transaction_type = 'expense'
        """,
        (user_id,)
    ).fetchone()

    total_expenses = expense_result["total"]

    # -----------------------------------------------------
    # Total Investments
    # -----------------------------------------------------

    investment_result = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        AND transaction_type = 'investment'
        """,
        (user_id,)
    ).fetchone()

    total_investments = investment_result["total"]

    # -----------------------------------------------------
    # Current Savings / Balance
    #
    # Savings =
    # Income - Expenses - Investments
    # -----------------------------------------------------

    savings = (
        total_income
        - total_expenses
        - total_investments
    )

    # -----------------------------------------------------
    # Savings Goals Count
    # -----------------------------------------------------

    goals_result = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM savings_goals
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    savings_goals_count = goals_result["total"]

    # -----------------------------------------------------
    # Recent Transactions
    # -----------------------------------------------------

    recent_transactions = connection.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY
            transaction_date DESC,
            id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    # -----------------------------------------------------
    # Savings Goals
    # -----------------------------------------------------

    savings_goals = connection.execute(
        """
        SELECT *
        FROM savings_goals
        WHERE user_id = ?
        ORDER BY target_date ASC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",

        user=user,

        total_income=total_income,
        total_expenses=total_expenses,
        total_investments=total_investments,

        savings=savings,

        savings_goals_count=savings_goals_count,

        recent_transactions=recent_transactions,
        savings_goals=savings_goals
    )


# =========================================================
# 15. PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    user = get_current_user()

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
        )

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# 16. TRACKER
# =========================================================

@app.route("/tracker")
@login_required
def tracker():

    user_id = session["user_id"]

    connection = get_db_connection()

    # -----------------------------------------------------
    # Financial totals
    # -----------------------------------------------------

    income_result = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        AND transaction_type = 'income'
        """,
        (user_id,)
    ).fetchone()

    expense_result = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        AND transaction_type = 'expense'
        """,
        (user_id,)
    ).fetchone()

    investment_result = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        AND transaction_type = 'investment'
        """,
        (user_id,)
    ).fetchone()

    total_income = income_result["total"]
    total_expenses = expense_result["total"]
    total_investments = investment_result["total"]

    savings = (
        total_income
        - total_expenses
        - total_investments
    )

    # -----------------------------------------------------
    # Recent transactions
    # -----------------------------------------------------

    transactions = connection.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY
            transaction_date DESC,
            id DESC
        """,
        (user_id,)
    ).fetchall()

    # -----------------------------------------------------
    # Savings goals
    # -----------------------------------------------------

    savings_goals = connection.execute(
        """
        SELECT *
        FROM savings_goals
        WHERE user_id = ?
        ORDER BY target_date ASC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "tracker.html",

        total_income=total_income,
        total_expenses=total_expenses,
        total_investments=total_investments,
        savings=savings,

        transactions=transactions,
        savings_goals=savings_goals
    )


# =========================================================
# 17. ADD TRANSACTION
# =========================================================

@app.route(
    "/tracker/add",
    methods=["POST"]
)
@login_required
def add_transaction():

    user_id = session["user_id"]

    transaction_type = request.form.get(
        "transaction_type",
        ""
    ).strip().lower()

    amount_text = request.form.get(
        "amount",
        ""
    ).strip()

    category = request.form.get(
        "category",
        ""
    ).strip()

    transaction_date = request.form.get(
        "transaction_date",
        ""
    ).strip()

    note = request.form.get(
        "note",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate transaction type
    # -----------------------------------------------------

    allowed_types = {
        "income",
        "expense",
        "investment"
    }

    if transaction_type not in allowed_types:

        flash(
            "Please select a valid transaction type.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    # -----------------------------------------------------
    # Validate amount
    # -----------------------------------------------------

    try:

        amount = float(amount_text)

    except (TypeError, ValueError):

        flash(
            "Please enter a valid amount.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    if amount <= 0:

        flash(
            "Amount must be greater than zero.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    # -----------------------------------------------------
    # Validate category
    # -----------------------------------------------------

    if not category:

        flash(
            "Please select a category.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    # -----------------------------------------------------
    # Validate date
    # -----------------------------------------------------

    if not transaction_date:

        transaction_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    # -----------------------------------------------------
    # Insert transaction
    # -----------------------------------------------------

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO transactions
        (
            user_id,
            transaction_type,
            amount,
            category,
            transaction_date,
            note
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            transaction_type,
            amount,
            category,
            transaction_date,
            note
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Transaction added successfully.",
        "success"
    )

    return redirect(
        url_for("tracker")
    )


# =========================================================
# 18. DELETE TRANSACTION
# =========================================================

@app.route(
    "/tracker/delete/<int:transaction_id>",
    methods=["POST"]
)
@login_required
def delete_transaction(transaction_id):

    user_id = session["user_id"]

    connection = get_db_connection()

    transaction = connection.execute(
        """
        SELECT id
        FROM transactions
        WHERE id = ?
        AND user_id = ?
        """,
        (
            transaction_id,
            user_id
        )
    ).fetchone()

    if transaction is None:

        connection.close()

        flash(
            "Transaction not found.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    connection.execute(
        """
        DELETE FROM transactions
        WHERE id = ?
        AND user_id = ?
        """,
        (
            transaction_id,
            user_id
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Transaction deleted.",
        "success"
    )

    return redirect(
        url_for("tracker")
    )


# =========================================================
# 19. ADD SAVINGS GOAL
# =========================================================

@app.route(
    "/goals/add",
    methods=["POST"]
)
@login_required
def add_goal():

    user_id = session["user_id"]

    goal_name = request.form.get(
        "goal_name",
        ""
    ).strip()

    target_amount_text = request.form.get(
        "target_amount",
        ""
    ).strip()

    target_date = request.form.get(
        "target_date",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate name
    # -----------------------------------------------------

    if not goal_name:

        flash(
            "Please enter a goal name.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    # -----------------------------------------------------
    # Validate amount
    # -----------------------------------------------------

    try:

        target_amount = float(
            target_amount_text
        )

    except (TypeError, ValueError):

        flash(
            "Please enter a valid target amount.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    if target_amount <= 0:

        flash(
            "Target amount must be greater than zero.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    # -----------------------------------------------------
    # Insert goal
    # -----------------------------------------------------

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO savings_goals
        (
            user_id,
            goal_name,
            target_amount,
            target_date,
            current_amount
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            goal_name,
            target_amount,
            target_date,
            0
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Savings goal created successfully.",
        "success"
    )

    return redirect(
        url_for("tracker")
    )


# =========================================================
# 20. DELETE SAVINGS GOAL
# =========================================================

@app.route(
    "/goals/delete/<int:goal_id>",
    methods=["POST"]
)
@login_required
def delete_goal(goal_id):

    user_id = session["user_id"]

    connection = get_db_connection()

    goal = connection.execute(
        """
        SELECT id
        FROM savings_goals
        WHERE id = ?
        AND user_id = ?
        """,
        (
            goal_id,
            user_id
        )
    ).fetchone()

    if goal is None:

        connection.close()

        flash(
            "Savings goal not found.",
            "danger"
        )

        return redirect(
            url_for("tracker")
        )

    connection.execute(
        """
        DELETE FROM savings_goals
        WHERE id = ?
        AND user_id = ?
        """,
        (
            goal_id,
            user_id
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Savings goal deleted.",
        "success"
    )

    return redirect(
        url_for("tracker")
    )


# =========================================================
# 21. ADD COMMUNITY POST
# =========================================================

@app.route(
    "/community/add",
    methods=["POST"]
)
@login_required
def add_community_post():

    user_id = session["user_id"]

    title = request.form.get(
        "title",
        ""
    ).strip()

    content = request.form.get(
        "content",
        ""
    ).strip()

    category = request.form.get(
        "category",
        "General"
    ).strip()

    if not title:

        flash(
            "Please enter a post title.",
            "danger"
        )

        return redirect(
            url_for("community")
        )

    if not content:

        flash(
            "Please enter some content.",
            "danger"
        )

        return redirect(
            url_for("community")
        )

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO community_posts
        (
            user_id,
            title,
            content,
            category
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            title,
            content,
            category
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Your community post has been published.",
        "success"
    )

    return redirect(
        url_for("community")
    )


# =========================================================
# 22. ADD COMMUNITY COMMENT
# =========================================================

@app.route(
    "/community/comment/<int:post_id>",
    methods=["POST"]
)
@login_required
def add_comment(post_id):

    user_id = session["user_id"]

    content = request.form.get(
        "content",
        ""
    ).strip()

    if not content:

        flash(
            "Comment cannot be empty.",
            "danger"
        )

        return redirect(
            url_for("community")
        )

    connection = get_db_connection()

    # -----------------------------------------------------
    # Check that post exists
    # -----------------------------------------------------

    post = connection.execute(
        """
        SELECT id
        FROM community_posts
        WHERE id = ?
        """,
        (post_id,)
    ).fetchone()

    if post is None:

        connection.close()

        flash(
            "That post no longer exists.",
            "danger"
        )

        return redirect(
            url_for("community")
        )

    # -----------------------------------------------------
    # Add comment
    # -----------------------------------------------------

    connection.execute(
        """
        INSERT INTO community_comments
        (
            post_id,
            user_id,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            post_id,
            user_id,
            content
        )
    )

    connection.commit()

    connection.close()

    flash(
        "Comment added.",
        "success"
    )

    return redirect(
        url_for("community")
    )


# =========================================================
# 23. DATABASE TEST ROUTE
# =========================================================

@app.route("/database-test")
def database_test():

    connection = get_db_connection()

    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    table_names = [
        table["name"]
        for table in tables
    ]

    return jsonify(
        {
            "database": "SQLite",
            "status": "connected",
            "tables": table_names
        }
    )


# =========================================================
# 24. CURRENT USER API TEST
# =========================================================

@app.route("/api/current-user")
@login_required
def current_user_api():

    user = get_current_user()

    if user is None:

        return jsonify(
            {
                "logged_in": False
            }
        )

    return jsonify(
        {
            "logged_in": True,
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "created_at": user["created_at"]
            }
        }
    )


# =========================================================
# 25. 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PaisaGyaan - Page Not Found</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background: #faf8f1;
                color: #20312b;
                min-height: 100vh;
                display: grid;
                place-items: center;
                text-align: center;
                padding: 20px;
            }

            h1 {
                font-size: 4rem;
                margin-bottom: 10px;
            }

            a {
                color: #176b55;
                font-weight: bold;
                text-decoration: none;
            }
        </style>
    </head>

    <body>

        <div>

            <h1>404</h1>

            <h2>Page not found</h2>

            <p>
                The page you're looking for doesn't exist.
            </p>

            <br>

            <a href="/">
                ← Back to PaisaGyaan
            </a>

        </div>

    </body>
    </html>
    """, 404


# =========================================================
# 26. APPLICATION STARTUP
# =========================================================

if __name__ == "__main__":

    initialize_database()

    print("")
    print("==============================================")
    print("           PAISAGYAAN IS RUNNING")
    print("==============================================")
    print("Local URL:")
    print("http://127.0.0.1:5000")
    print("")
    print("Database:")
    print(DATABASE)
    print("")
    print("Press CTRL + C to stop the server.")
    print("==============================================")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )