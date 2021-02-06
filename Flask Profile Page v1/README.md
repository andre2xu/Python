# **Flask Profile Page v1**
## **Description**
This project combines with and improves upon my previous flask authentication system. It is a blogging website that allows users to post blogs and save pictures in a personal account.

## **Features**
### *Version 1*
- Login system with an email, username and password field. Each one is verified with the user's info on the database.
- Register system with the same three fields but only the email and username are verified with the database.
- Both of the forms above come with flash error messages that appear when the user's inputs are incorrect.
- Cookies are created after successful authentication and will automatically log in the user when they click on the login button in the homepage.
- Sessions are provided to give the user permanent access to their account for a period of 3 days. 
- A system is in place that prevents users from accessing their account or someone else's if they do not have a session id and the valid cookies for authentication.
- Users can edit their account bio through their account settings. The user is given an option to change one, two or all three details about themselves which include their name, age and gender.
- Users are given a default profile picture which they can change in their settings.

