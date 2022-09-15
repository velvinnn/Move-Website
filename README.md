# Move-Website

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#playing-the-game">Playing the game</a></li>
    <li><a href="#managing-cards">Managing cards</a></li>
    <li><a href="#modifying-or-reading-information-in-the-past-week">Modifying or reading information in the past week</a></li>
    <li><a href="#adding-a-new-participant">Adding a new participant</a></li>
    <li><a href="#Adding-a-new-team">Adding a new team</a></li>
  </ol>
</details>

### Prerequisites
Please install the following packages before using this website.
* pandas
* random
* numpy
* os
* flask
* flask_util_js
* matplotlib
* requests
* datetime
* json


Please put the `user info.csv` file under the folder `player`.



### Playing the game
1. Launch the python program `app_cookie.py`.
2. In the program console, there should be a website link provided as following. In your browser, go to this website link.
   ```sh
   Running on http://YOUR_IP_ADDRESS:5000/ (Press CTRL+C to quit)
   ```
3. Log in with the `username` as 12, `password` as 123



### Managing cards
#### Managing cards drawn
The cards are drawn randomly from the folder `team/card_image`. The cards are drawn by a fixed order. Adding new cards, removing cards, or renaming cards will change this order.

To add a new card, please make sure that it is in the `.png` format, and placed under the same folder `team/card_image`.



#### Managing the action cards in the drop-down selection box
Add/remove/modify a row in the `static/cards.csv` file.



### Modifying and reading information in past weeks
When making changes to previous information, please only modify individual cells in the `.csv` file. Please not to add new lines or spaces or cells in those information files. Otherwise, it could break this website.

1. Player miles: `player/miles/PLAYER_ID.csv`
2. Player commitment cards: `static/commitment_cards/(PLAYER_ID)_week(WEEK_NUMBER).csv`
3. Team progress(location, points,miles,cards): `team/TEAM_ID.csv`
4. Team basic information(team member,name, game start date): `team/team info.csv`



### Adding a new participant
Add a new row for the participant in the file `player/user info.csv`. The required fields are the following:
* user_id
* first_name
* last_name
* permanent_token, which is token to retrieve fitbit data, and generated by the same approach as the Motivate Walking study.



### Adding a new team
1. Add a new row for the team in the file `team/team info.csv`. All fields are required for the team.
2. Make a copy of the file `team/template.csv`, rename it as `team/TEAM_ID.csv`, where `TEAM_ID` is the same as the team_id field in the `team/team info.csv` file.
