# Budget

#### Video Demo:

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

`127.0.0.1:5000/history`:
You can view all historical expenses from the History page from the navbar.

`127.0.0.1:5000/`:
From the Dashboard, you can access many functions, such as changing the currency. Note that this is not a converter, it is only a quality of life feature for if you could like to change the currency you track expenses in.

`127.0.0.1:5000/manage`:
From the manage page, you can manage your account details, such as change your password or entirely delete the account.

`127.0.0.1:5000/credits`:
There is also a credits page, where you can access all the places from where I got code or inspiration, or any other assets from.