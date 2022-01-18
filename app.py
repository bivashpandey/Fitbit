'''
    @author: Bivash Pandey

    This program gets the input from the webpage, fetch the data from fitbit,
    and exports the steps, sleep, heart rate data into excel files
'''

# import libraries
from flask import Flask, render_template, request

from conversiontools import ConversionClient
import requests
from pprint import pprint
import json
import pandas as pd

app = Flask(__name__)

# before every api call this url is attached
FITBIT_URL = "https://api.fitbit.com"

# your tokens from conversiontools website
CONVERSION_TOKEN1 = "DEMO-eyJhbGciOiJIUzI1NiI9.eyJpZCI6IjJmMzNkYzAxOTA2MjQ0NT2IxIiwiaWF0IjoxNjMxMzkzMTgwfQ.TESTING"
CONVERSION_TOKEN2 = "DEMO-eyJhbGciOiJIUzI1NiI9.eyJpZCI6IjJmMzNkYzAxOTA2MjQ0NT2IxIiwiaWF0IjoxNjMxMzkzMTgwfQ.TESTING"

# get the participant id and token from id_token.xlsx file
id_token = pd.read_excel('id_token.xlsx')

# convert participant id and token into list
ids = id_token['id'].to_list()
token = id_token['token'].to_list()


def get_steps_all(start_date, end_date):
    '''
    This function exports the steps data of all participants into excel file

    Parameters:
    ----------
    start_date (string): The starting date of the data
    end_date (string): The final date of the data
    '''

    # loop through all the participants
    for i in range(len(ids)):
        # requesting the steps data of each user from the fitbit API
        activity_request_steps = requests.get(FITBIT_URL+'/1/user/' + ids[i]+'/activities/steps/date/' + start_date + "/" + end_date + '.json',
                                              headers={'Authorization': "Bearer " + token[i]})

        # dynamic file names
        filename = "steps" + ids[i]

        # converting the reponse from fitbit to json
        steps_json = activity_request_steps.json()

        # print data from fitbit api in nice format
        # pprint(steps_json)

        # Check for the permission by searching the key in json
        if "activities-steps" not in steps_json:
            print(filename)
        else:
            # converting json data into dataframe
            df = pd.DataFrame(steps_json['activities-steps'])

            # data in the values column are string, so converting it into number
            df['value'] = df['value'].apply(lambda x: int(x))

            # show first 5 rows of the data
            #print(df.head())

            # saving the data into json file
            #with open('./data/steps/json/'+filename+'.json', 'w') as f:
            #    json.dump(steps_json, f)

            # saving the data into excel file
            df.to_excel('./data/steps/' +
                        filename + '.xlsx', index=None)



def get_heart_rate_all(start_date, end_date):
    '''
    This function exports the heart rate data of all participants into excel file

    Parameters:
    ----------
    start_date (string): The starting date of the data
    end_date (string): The final date of the data
    '''

    # loop through all the participants
    for i in range(len(ids)):

        # requesting the heart rate data of each user from the fitbit API
        activity_request_heart_rate = requests.get(FITBIT_URL+'/1/user/' + ids[i]+'/activities/heart/date/' + start_date + "/" + end_date + '.json',
                                                   headers={'Authorization': "Bearer " + token[i]})
        # dynamic file names
        filename = "heart" + ids[i]
        
        # converting the reponse from fitbit to json
        heart_rate_json = activity_request_heart_rate.json()

        # print data from fitbit api in nice format
        # pprint(heart_rate_json)

        # Check for the permission by searching the key in json
        if "activities-heart" not in heart_rate_json:
            print(filename)
        else:
            # create an empty dataframe
            df = pd.DataFrame()

            for j in range(len(heart_rate_json['activities-heart'])):
                df1 = pd.DataFrame(
                    heart_rate_json['activities-heart'][j]['value']['heartRateZones'])
                df1.insert(0, 'dateTime', [
                    heart_rate_json['activities-heart'][j]['dateTime'], '', '', ''], True)

                # if there is caloriesOut data not present, insert a column with empty values
                if "caloriesOut" not in heart_rate_json['activities-heart'][j]['value']['heartRateZones'][0]:
                    df1.insert(1, 'caloriesOut', ['', '', '', ''], True)

                # if there is minutes data not present, insert a column with empty values
                if "minutes" not in heart_rate_json['activities-heart'][j]['value']['heartRateZones'][0]:
                    df1.insert(4, 'minutes', ['', '', '', ''], True)

                # for restingHeartRate data. If present put data in last column else put empty values
                if "restingHeartRate" in heart_rate_json['activities-heart'][j]['value']:
                    df1.insert(6, 'restingHeartRate', [
                        heart_rate_json['activities-heart'][j]['value']['restingHeartRate'], '', '', ''], True)
                else:
                    df1.insert(6, 'restingHeartRate', ['', '', '', ''], True)

                df = pd.concat([df, df1], ignore_index=True)

            # saving the data into json file
            # with open('./data/heart_rate/json/'+filename+'.json', 'w') as f:
            #     json.dump(heart_rate_json, f)

            # saving the data into excel file
            df.to_excel('./data/heart_rate/' + filename + '.xlsx', index=None)



def get_sleep_all(start_date, end_date):
    '''
    This function exports the sleep data of all participants into excel file

    Parameters:
    ----------
    start_date (string): The starting date of the data
    end_date (string): The final date of the data
    '''

    # divide data into 2, one for conversion token 1 and another for conversion token 2
    for i in range(len(ids)):
        # requesting the sleep data of each user from the fitbit API
        activity_request_sleep = requests.get(FITBIT_URL+'/1.2/user/' + ids[i] + '/sleep/date/' + start_date + "/" + end_date + '.json',
                                              headers={'Authorization': "Bearer " + token[i]})

        # dynamic file names
        filename = "sleep" + ids[i]

        # converting the reponse from fitbit to json
        sleep_json = activity_request_sleep.json()

        # print data from fitbit api in nice format
        # pprint(sleep_json)

        # Check for the permission by searching the key in json
        if "sleep" not in sleep_json:
            print(filename)
            with open('./data/sleep/json/'+filename+'.json', 'w') as f:
                json.dump(sleep_json, f)
        else:
            # save into a json file
            with open('./data/sleep/json/'+filename+'.json', 'w') as f:
                json.dump(sleep_json, f)

            # input json file and this api will convert to excel file
            fileInput = './data/sleep/json/'+filename+'.json'
            fileOutput = './data/sleep/'+filename+'.xlsx'

            # half of the data are using CONVERSION_TOKEN1 and remaining half are
            # using CONVERSION_TOKEN2
            if i <= len(ids)//2:
                client = ConversionClient(CONVERSION_TOKEN1)
            else:
                client = ConversionClient(CONVERSION_TOKEN2)

            try:
                client.convert('convert.json_to_excel', fileInput,
                               fileOutput, {'delimiter': 'tabulation'})
            except Exception as error:
                print(error)



def get_steps_of_one(participant_id, start_date, end_date):
    '''
    This function exports the steps data of a participant into excel file

    Parameters:
    ----------
    participant_id (string): The client ID of a participant
    start_date (string): The starting date of the data
    end_date (string): The final date of the data
    '''

    # create a string for the api call
    steps_api_call = FITBIT_URL+'/1/user/' + participant_id + \
    '/activities/steps/date/' + start_date + "/" + end_date + '.json'

    # get the participant token with the help of participant id
    participant_token = token[ids.index(participant_id)]

    # requesting the step data of a user from the fitbit
    activity_request_steps = requests.get(
        steps_api_call, headers={'Authorization': "Bearer " + participant_token})

    # dynamic file names so that each file name has client id attached to it
    filename = "steps" + participant_id

    # converting the reponse from fitbit to json
    steps_json = activity_request_steps.json()

    # print data from fitbit api in nice format
    #pprint(steps_json)

    # converting the json into dataframe using pandas
    df = pd.DataFrame(steps_json['activities-steps'])

    # data in the values column are string, so converting it into number
    df['value'] = df['value'].apply(lambda x: int(x))

    # show first 5 rows of the data
    #print(df.head())

    # saving the data into excel file
    df.to_excel('./data/steps/' + filename + '.xlsx', index=None)



def get_heart_rate_of_one(participant_id, start_date, end_date):
    '''
    This function exports the heart rate data of a participant into excel file

    Parameters:
    ----------
    participant_id (string): The client ID of a participant
    start_date (string): The starting date of the data
    end_date (string): The final date of the data
    '''

    # create a string for the api call
    heart_rate_api_call = FITBIT_URL+'/1/user/' + \
    participant_id + '/activities/heart/date/' + start_date + "/" + end_date + '.json'

    # get the participant token with the help of participant id
    participant_token = token[ids.index(participant_id)]

    # requesting the heart rate data of a user from the fitbit API
    activity_request_heart_rate = requests.get(heart_rate_api_call, headers={
                                               'Authorization': "Bearer " + participant_token})

    # converting the reponse from fitbit to json
    heart_rate_json = activity_request_heart_rate.json()
    pprint(heart_rate_json)
    print(participant_id)

    # dynamic file names so that each file name has client id attached to it
    filename = "heart" + participant_id

    # Empty dataframe
    df = pd.DataFrame()
    for j in range(len(heart_rate_json['activities-heart'])):
        df1 = pd.DataFrame(
            heart_rate_json['activities-heart'][j]['value']['heartRateZones'])
        df1.insert(0, 'dateTime', [
            heart_rate_json['activities-heart'][j]['dateTime'], '', '', ''], True)

        # if there is caloriesOut data not present, insert a column with empty values
        if "caloriesOut" not in heart_rate_json['activities-heart'][j]['value']['heartRateZones'][0]:
            df1.insert(1, 'caloriesOut', ['', '', '', ''], True)

        # if there is minutes data not present, insert a column with empty values
        if "minutes" not in heart_rate_json['activities-heart'][j]['value']['heartRateZones'][0]:
            df1.insert(4, 'minutes', ['', '', '', ''], True)

        # for restingHeartRate data. If present put data in last column else put empty values
        if "restingHeartRate" in heart_rate_json['activities-heart'][j]['value']:
            df1.insert(6, 'restingHeartRate', [
                heart_rate_json['activities-heart'][j]['value']['restingHeartRate'], '', '', ''], True)
        else:
            df1.insert(6, 'restingHeartRate', ['', '', '', ''], True)

        # merge the dataframes
        df = pd.concat([df, df1], ignore_index=True)

    # print the dataframe
    #print(df)

    # save the dataframe into excel using pandas
    df.to_excel('./data/heart_rate/' + filename + '.xlsx', index=None)



def get_sleep_of_one(participant_id, start_date, end_date):
    '''
    This function exports the sleep data of a participant into excel file

    Parameters:
    ----------
    participant_id (string): The client ID of a participant
    start_date (string): The starting date of the data
    end_date (string): The final date of the data
    '''

    # create a string for the api call
    sleep_api_call = FITBIT_URL+'/1.2/user/' + \
    participant_id + '/sleep/date/' + start_date + "/" + end_date + '.json'

    # get the participant token with the help of participant id
    participant_token = token[ids.index(participant_id)]

    # requesting the sleep data of a user from the fitbit API
    activity_request_sleep = requests.get(
        sleep_api_call, headers={'Authorization': "Bearer " + participant_token})

    # dynamic file names
    filename = "sleep" + participant_id

    # converting the reponse from fitbit to json
    sleep_json = activity_request_sleep.json()

    # print data from fitbit api in nice format
    #pprint(sleep_json)

    # save into a json file
    with open('./data/sleep/json/'+filename+'.json', 'w') as f:
        json.dump(sleep_json, f)

    # name of input and output file
    fileInput = './data/sleep/json/'+filename+'.json'
    fileOutput = './data/sleep/'+filename+'.xlsx'

    # convert the json into excel using API
    client = ConversionClient(CONVERSION_TOKEN1)
    try:
        client.convert('convert.json_to_excel', fileInput,
                       fileOutput, {'delimiter': 'tabulation'})
    except Exception as error:
        print(error)



@app.route('/', methods=['POST', 'GET'])
def index():
    participant_type, participant_id, data_type, start_date, end_date = "", "", "", "", ""

    # if the length of request from website is greater than zero
    if len(request.form) > 0:

        # Get the data from the website
        participant_type = request.form.get('oneOrAll')
        participant_id = request.form.get('participant')
        data_type = request.form.get('data')
        start_date = request.form.get('startdate')
        end_date = request.form.get('enddate')
        
        # when user selects single participant and doesn't provide an ID
        # display the error message and render the home page
        if participant_type == "one" and len(participant_id) == 0:
            print("\nERROR: Please enter a participant ID for individual data...\n")
            return render_template('index.html')

        # when user selects single participant and provides an invalid ID
        # display the error message and render the home page
        if participant_type == "one" and participant_id not in ids:
            print("\nERROR: Please provide a valid participant ID...\n")
            return render_template('index.html')
            
        # call the get_steps_of_one method
        if participant_type == "one" and data_type == "steps":
            get_steps_of_one(participant_id, start_date, end_date)
        # call the get_heart_rate_of_one method
        elif participant_type == "one" and data_type == 'heartRate':
            get_heart_rate_of_one(participant_id, start_date, end_date)
        # call the get_sleep_of_one method
        elif participant_type == "one" and data_type == "sleep":
            get_sleep_of_one(participant_id, start_date, end_date)
        # call the get_steps_all method
        elif participant_type == "all" and data_type == "steps":
            get_steps_all(start_date, end_date)
        # call the get_heart_rate_all method
        elif participant_type == "all" and data_type == "heartRate":
            get_heart_rate_all(start_date, end_date)
        # call the get_sleep_all method
        elif participant_type == "all" and data_type == "sleep":
            get_sleep_all(start_date, end_date)

        # redirect user to the success page once after submitting data
        return render_template('success.html')

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)