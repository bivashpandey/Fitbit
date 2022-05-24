# Fitbit
This program fetches the data from fitbit and save into excel/csv files. The program uses conversiontools api to convert one category of json data into excel file. Please update the CONVERSION_TOKEN1 and CONVERSION_TOKEN2 with your own API Token in the app.py file. <br/>
To receive your own API Token, sign up for conversiontools https://conversiontools.io/. <br/>
After downloading the code, create a virtual environment inside the Fitbit-main folder and install the required packages. 

<h3>Setup</h3>

a) Create a virtual environment <br/>
`python -m venv env` <br/>

b) Activate the virtual environment <br/>
(Mac): `source env/bin/activate` <br/>
(Windows): `.\env\Scripts\activate` <br/>

c) Install the packages <br/>
`pip install flask` <br/>
`pip install pandas` <br/>
`pip install openpyxl` <br/>
`pip install conversiontools` <br/>

d) Run the program <br/>
`flask run` <br/>
