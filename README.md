# FAB
FAB
FUT 2020 Bot This project is all about automating FUT actions, performing time consuming actions like trading, searching and listing items on the market.
This project is the server side to the project FAB-Client - that enables the user to control all these actions with a convinient UI via his mobile (both are under development).
Final functionality (Not all of these are implemented yet):
• Each user is authenticated with his credentials and has its own personal area
• The bot presents several options to the user including:
  * Trading items with specific filters - club/nation/type etc...
  * Trading items based on user's predefined price / price that is calculated according to the market
  * Buying and selling items
  * Checking items prices according to latest updated prices on the market
  * Searching most updated items according to Futbin, including special ,regular items and consumables
  * Buying and selling desired players
  * Performing Login and Logout from several accounts at the same time, as well as opertaing them simultaneously - accounts can be remembered with cookies storing
  * Viewing account activity that include the best deals found etc...
  * Scanning the market to find 59min deals and snipe them
# Versions and additional information
• Current version is using python-requests,Flask and mongoDB for storing users,accounts and items data.
• Last release used Selenium insead of actual requests to EA servers. It automated user's actions with actualy mocking a real user by doing all
if this stuff mentioned above, without searching for special items -as this is not possible via the Web App(For that reason the next release will
implement python-requests to perform actions that require data that is not presented in the WebApp current UI(20).
This version also uses Flask, but doesn't have UI - all actions have to be performed using curl/postman.
