# Budget

#### Video Demo: https://youtu.be/UKKA5UmcKGo

#### Structure:

`app.py`: Contains the Flask application and every route that can be accessed on the webpage. Also makes sure correct authentication for each route and ownership checks.

`databse.py`: Defines the SQLAlchemy models. Creates 2 tables, Users and Expenses, with attributes (id, username, hash) and (id, user_id, amount, category, desc, time), respectively.

`helpers.py`: Holds code that is shared across routes, such as the login_required decorator, to make sure a user is logged in before moving forward, taken from the CS50 Finance problem. It also has the datetimefmt template filter, convert which calls the API to convert currencies, and the loan_cost calculator.

`templates/`: Contains all the Jinja HTML pages, all of which extend `layout.html`

`static/`: Contains `sort.js` for table sorting, `main.js` which stores the prefered currency symbol in memory, `styles.css` which has all the CSS styles defined

`budget.db`: Contains the database which is used for the website. Created automatically if it doesn't exist!

`.env`: Contains the `SECRET_KEY`, which is also defined in `example.env`, but as a placeholder value instead.

#### Design Decisions:

**Money as Floats**: Money is handles as floats and rounded to two decimal places using round. This is done for simplicity, though floats can't represent every decimal exactly, and for that reason "Decimal" might be better.

**UTC Timestamps**: Times are stored in UTC for simplicity. The timestamp is labeled as such on the tables as well.

**Ownership Check and login_required**: Every edit and remove makes sure to check that the currently selected expense is "owned" by the current user accessing it. login_required makes sure that the user is logged in before accessing resources that require log in.

**Client-side Sorting**: The sorting done on the dashboard table headers is done through JavaScript rather than server-side using SQL as it is faster and does not require reloading. However, if the table had pages, it would be preferable to move to the server.

**One Page for Account Management**: Rather than having different templates for both changing password and deleting the account, the experience is instead unified in `manage.html` where you can choose to change the password or delete the account, after which it will load the form to do so in the same page based on the post request action.

**Converter API**: Conversion uses the [Frankfurter API](https://frankfurter.dev/), which is updated daily using ECB data, is free and doesn't require an API key. This is fine for a personal tracker but it may be better to use a paid API if minute exchange rates are required.

#### Prerequisites:

- Python 3.10 or newer
- All packages in `requirements.txt`
- Internet connection required for currency converter API (Using Frankfurter API, no API key needed)
- Insert SECRET_KEY in .env (example.env is provided)

#### Dependencies:

Dependencies can be installed using:
```
pip install -r /src/requirements.txt
```

#### Description:

This is a budget and expense tracker made using Flask, Python, SQL, HTML, CSS, JS, and other libraries within those languages.

For the basis of the website, there was inspiration taken and adapted from the CS50 Finance Problem, as will be visible. Unlike in the CS50 problem, this website instead uses Flask-SQLAlchemy rather than CS50s own implementation of SQL.

There will be no database provided initially, SQLAlchemy will create one by itself when it recognises there is no database.

To run the program, you can type:
```bash
flask run
```
And that's it. Give it a second and it should whir up a locally hosted dynamic website on address: `127.0.0.1:5000`

`127.0.0.1:5000/register`:
From there on, you can click the Register button from the navbar to register an account. There are no pre-populated expenses.

`127.0.0.1:5000/add`:
To add an expense, you can click the Add button from the navbar which will take you to a page where you can add expenses.
The time at which the expense is added is by default the time at which you clicked the submit button, however the time can be changed from the edit page, if need be.
Categories are self defined. You can add whatever categories you deem fit, and if you change your mind, you can always edit them.

`127.0.0.1:5000/remove`:
You can likewise remove an expense by going to the Remove page from the navbar.

`127.0.0.1:5000/edit`:
You may also edit an expense, such as its amount, category, description, etc, by clicking the Edit webpage from the navbar.

`127.0.0.1:5000/insights`:
You can view all spenditure insights from the Insights page from the navbar. This groups the expenses by category so you can see how much you have spent per category. It will also show you the total amount of transactions you have made in each category and in total.

`127.0.0.1:5000/`:
From the Dashboard, you can access many functions, such as changing the currency. Note that this is not a converter, it is only a quality of life feature for if you could like to change the currency you track expenses in. However, a currency converter is available. Furthermore, clicking on any headers on the table allows you to sort by any of the columns in the table

`127.0.0.1:5000/converter`:
In the Converter page, which can be accessed through the navbar, you are able to convert between currencies using a free "Frankfurter" API, no API key needed. Currently, only conversion between GBP, USD and EUR can be made.

`127.0.0.1:5000/calculator`:
In the Calculator page, you can calculate a loan amount. The required inputs are the loan amount, the yearly interest rate as a float, and the term, which can be in years or months, with a maximum term of 50 years.

`127.0.0.1:5000/manage`:
From the manage page, you can manage your account details, such as change your password or entirely delete the account. You will be asked for the confirmation before deleting your account.

`127.0.0.1:5000/credits`:
There is also a credits page, where you can access all the places from where I got code or inspiration, or any other assets from.

#### AI Use Disclosure:

AI was used to help in certain parts of the code. Use of AI is documented throughout where it was used.