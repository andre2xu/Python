# **Flask Social Network Website**
## **Description**
The website is called Cliq. It is a social networking platform that allows users to create profile pages based on their interests - this is done through a system known as 'cliques'. The cliques determine what type of content the user can or cannot post and each one provides a unique profile page layout that is suited for the content it allows. There are only three at the moment: one for text-based content like blogs, another for posting images and videos only, and the third for those seeking to find jobs or promote their business.

*I made this for my continuous assessment project in the first semester of my first year in college. It is only meant to showcase my skills and is not intended to be an actual social media platform!*

## **Features**
- Three different profile page layouts to choose from.
- Unauthorized access protection for accounts.
- Profile pages have a separate copy called a 'view' that allows other users to look at someone's profile page without the ability to make changes to it.
- A searchbar that uses JQuery's AJAX to send requests to and from Flask without forms. It displays the usernames of others based on what has currently been entered in the search's input field.
- Users are given multiple ways to customize their profile bio, these include: A profile picture & background cover, a brief description of the user, a 'niche' that summarizes the user in one word and what content they will be posting, and a list for user's website URLs. 
- All the cliques share a common settings page which keeps track of the user's clique and displays the appropriate settings for that clique.
- Users can change their credentials and delete their account through the settings page.
- The website uses an image processing library called 'Pillow' to resize images and reduce their file size for better performance.
- There is an RSS feed in one of the cliques which displays news around the world in real time (**DISCLAIMER: I DID NOT make the JavaScript for it, the credit belongs to https://surfing-waves.com**).
- Only viewers who have registered and are currently logged in can like or rate someone's post. The liking/rating system also uses AJAX to make the necessary changes.
- The database I used for the website is SQLite which comes with Flask. All the tables can be found in the schema provided.
- All SVG Icons belong to https://fontawesome.com/ and are licensed under MIT, SIL OFL, and CC BY licenses.
