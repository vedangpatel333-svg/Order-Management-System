# Storing and Retrieving JSON with Oracle

This is a web app for managing customer orders for an online outdoor store. It's built with Flask and uses an Oracle database. The interesting part is how it handles the data: instead of only splitting everything into separate tables, it also saves each whole order as a JSON document inside Oracle, and can search through that JSON directly.

I built this for my Advanced Database course. The part I worked on was the Python side: getting Flask talking to the Oracle database and writing the code that saves and loads the orders.

## What you can do with it

It's a simple dashboard in the browser. You can add a new order and see it turned into JSON before you save it, look at all your orders in a table, edit one, search through them, or delete one (it asks you to confirm first).

## The Oracle JSON part

Each order gets stored in two ways at once. The normal details go into regular tables (`ORDERS` and `ORDER_ITEMS`), and the full order also gets saved as a JSON document in an `OUTDOOR_ORDERS` table.

Oracle checks that the JSON is actually valid before it lets it in, so junk data gets rejected right away. On top of that, there are special indexes on a few fields inside the JSON (like status and category) so searches stay fast without Oracle having to read through the whole document every time.

There are two safety nets for bad input: the database itself blocks broken JSON and duplicate order IDs, and the Python code catches those errors and shows a clear message instead of a scary technical one.

## How the code is laid out

I kept the code organised using the MVC pattern, so each folder has one job:

- `app/models` — describes what an order looks like
- `app/repositories` — all the Oracle database code lives here
- `app/services` — the logic, like checking the form and adding up totals
- `app/controllers` — the web page routes
- `app/templates` and `app/static` — the front end (pages and styling)

## What it's built with

- Python and Flask
- Oracle Database 23ai Free, using the `oracledb` library
- HTML, CSS, and JavaScript for the pages
- Written in Visual Studio Code

## How to run it

1. Download the project.
2. Set up a virtual environment and install what it needs:
   ```
   pip install -r requirements.txt
   ```
3. Have an Oracle database running with the `ORDERS`, `ORDER_ITEMS`, and `OUTDOOR_ORDERS` tables set up.
4. Put your database login details into environment variables (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SERVICE`).
5. Start it:
   ```
   python run.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

## Author

Vedang Patel
