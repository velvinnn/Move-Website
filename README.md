# Move-Website

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#playing-the-game">Playing the game</a></li>
    <li><a href="#adding-a-new-participant">Adding a new participant</a></li>
    <li><a href="#Adding-a-new-team">Adding a new team</a></li>
    <li><a href="#managing-cards">Managing cards</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
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
   Running on http://192.168.0.110:5000/ (Press CTRL+C to quit)
   ```
3. Log in with the `username` as 12, `password` as 123

### Adding a new participant
Add a new row for the participant in the file `player/user info.csv`. The required fields are the following:
* user_id
* first_name
* last_name
* permanent_token, which is generated by the same approach as the Motivate Walking study.

### Adding a new team
1. Add a new row for the team in the file `team/team info.csv`. All fields are required for the team.
2. Make a copy of the file `team/template.csv`, rename it as `team/TEAM_ID.csv`, where `TEAM_ID` is the same as the team_id field in the `team/team info.csv` file.

### Managing cards
#### Managing cards drawn
The cards are drawn randomly from the folder `team/card_image`. The cards are drawn by a fixed order. Adding new cards, removing cards, or renaming cards will change this order.

To add a new card, please make sure that it is in the `.png` format, and placed under the same folder `team/card_image`.

#### Managing the action cards in the drop-down selection box
Add/remove/modify a row in the `static/cards.csv` file.


