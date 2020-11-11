# Zoom Dashboard

## Overview

This objective of this project is to have a visual tool to monitor the stability of Zoom connections. This is specially useful for schools or other institutions that lately rely heavily on Zoom and that host a big amount of users and sessions at the same time. 
The current version of the project is a collection of python methods that extract and store meetings information using Zoom API in order to manually upload said information to a dashboard in Zoho Analytics.

## Background

Empirical observation during the last few months has led me to beleive that, as several teachers say, Zoom does have good days and bad days. This is, meeting participants will be randomly disconnected from the session regardless of their internet speed and in some days it gets worse.
I have also noticed that Zoom's in-built dashboard will sometimes indicate that many participants in a meeting were disconnected due to network errors at exactly the same time even when they were not in the same place.

## Structure

There are two main variables to be observed:

1) Individual disconnections. Useful for follow up with specific users that may need help with their internet connections.
2) Collective disconnections. Useful for situational awareness or possible Zoom problems and follow up with Zoom support.

The file apis.py, so far, does the following:

- Downloads and stores the meeting information for all meetings in a date range.
- Filters the meetings and stores only those that are of monitoring interest (only class sessions).
- For the filtered meetings, downloads and stores all the participants information.
- Extracts all the cases where participants were disconnected for network errors and stores it in a format that Zoho Analytics can understand.
- Groups the individual disconnections by time and meeting ID to detect collective disconnections and stores in a Zoho compatible format.

## Next steps

- Create a Django app to receive Zoom webhooks on meetings ending, extract and filter participant information, and upload it to Zoho using their API.
- Add data and reports to use Zoom's built-in meeting issues webhooks.

