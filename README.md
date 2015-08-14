# LainBot
A Lainchan thread monitoring bot

## Usage

Run the script as python 
~~~
LainBot.py --board <board url here> --database <sqlite3 database file path> 
~~~
to start analyzing every thread on the supplied board.


LainBot downloads every file that finds, and stores links, magnets and comment body on a sqlite3 database.

## Dependencies
  * Requests
  * simplejson
  * sqlite3

## Future work
  * Add a database creation feature
  * Implement an image viewer to see downloaded media
  * Use the comment body store as data for training 