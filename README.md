# YOUR PROJECT TITLE
#### Video Demo:  https://youtu.be/d38aszMiWBM
#### Description:
This project creates a web application called FinMan which is an easy and convenient way to manage your own finances. It has multiple features such as allowing users to view graphical representations of their finances, message other people using the app with the feed option and also check prices of stocks.

The file app.py contains functions built using the library flask that allow it to manage what the user sees when they visit any of the links. It is the backend of the app and contains all the logic required to run the pages.

helpers.py contain some functions that have been abstracted away but ensure the proper functioning of the app such as the function needed to check current stock prices.

database.db contains the sqlite database containing user information like username, posts etc and post information.

The folder static contains the styles.css file which is used to ensure the web pages look visually appealing through css.

templates contain the html templates that are called in app.py. layout.html contains the basic layout all the other html files follow.

The pages login.html and register.html contain forms to allow users to login and register.

The pages add-entry.html, finance.html, analysis.html are the files that display user info related to their finances. feed and post contain pages that allow the user to view and post messages respectively. stocks and stock-price allow them to search and view stock prices.
