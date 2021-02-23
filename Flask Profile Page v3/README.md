# **Flask Profile Page v3**
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

### *Version 3*
> Added
- A gallery for saving pictures.
- Blogs can now be created to be displayed in the user's personal home page.
- The ability for users to follow & unfollow each other; the number of followers they have will be displayed just beneath their profile picture.
- Blogs, gallery pictures, and even accounts can now be deleted.
- A search bar for visiting other people's profile pages. Users are able to return to their own profile pages using a link in the navbar.
- Users can now view other people's profile pages (i.e. they can access them but not modify them). However, viewers have the ability to follow or unfollow the user they are viewing. 

> Changed
- Only the user's username is stored in the session now. Previously, emails were included but having them stored there posed a security risk.
- The 'home' and 'gallery' links in the navbar now work as intended. They both take the user to the desired destination depending on whether the user is viewing someone else's profile page or navigating around their own profile page.
- Usernames are now prefixed at the start of filenames to prevent them from being overwritten by different files with similar names belonging to other users.

> Removed
- Emails from sessions.