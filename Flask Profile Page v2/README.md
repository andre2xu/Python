# **Flask Profile Page v2**
## **Description**
This project combines with and improves upon my previous flask authentication system. It is a blogging website that allows users to post blogs and save pictures in a personal account.

## **Features**
### *Version 1*
> Added
- Login system with an email, username and password field. Each one is verified with the user's info on the database.
- Register system with the same three fields but only the email and username are verified with the database.
- Both of the forms above come with flash error messages that appear when the user's inputs are incorrect.
- Cookies are created after successful authentication and will automatically log in the user when they click on the login button in the homepage.
- Sessions are provided to give the user permanent access to their account for a period of 3 days. 
- A system is in place that prevents users from accessing their account or someone else's if they do not have a session id and the valid cookies for authentication.
- Users can edit their account bio through their account settings. The user is given an option to change one, two or all three details about themselves which include their name, age and gender.
- Users are given a default profile picture which they can change in their settings.

### *Version 2*
> Added
- Background covers for the profile page.
- Users can now write more descriptive biographies for their profile page, they aren't limited to just age and gender anymore.
- New flash error messages for some of the forms which return the conditions for a valid form submission. 
- Pre-existing files are now deleted first from the server before being replaced by new ones whenever the user makes a change to their profile picture or background cover.

> Changed
- The website's appearance has been changed to accomodate the new features.
- The new navbar is borrowed from bootstrap.

> Removed
- Cookies are not used anymore for auto-login and for verifying the user's ownership of a profile page (it is not as reliable and secure as sessions); only sessions are used now: Once the user successfully logs in to their account for the first time, their email and username are stored in a session that lasts for 3 days. These credentials, moreso the email, is verified with a profile page owner's database info whenever the user enters a route that renders profile pages; this prevents users who have logged in successfully from entering another person's profile.