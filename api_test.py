import requests

def lookup_events(event_ids): 
    for event_id in event_ids:
        api_call = requests.get(f"https://www.thesportsdb.com/api/v1/json/801881/lookupevent.php?id={event_id}")
        storage = api_call.json()
        for event in storage["events"]:
            date_event = event["dateEvent"]
            home_team = event["strHomeTeam"]
            away_team = event["strAwayTeam"]
            print(f"{date_event}: {home_team} vs {away_team}")

def lookup_next(): 
    api_call = requests.get(f"https://www.thesportsdb.com/api/v1/json/801881/eventsnextleague.php?id=4335")
    storage = api_call.json()
    print(storage)
    # for event in storage["events"]:
    #     date_event = event["dateEvent"]
    #     home_team = event["strHomeTeam"]
    #     away_team = event["strAwayTeam"]
    #     print(f"{date_event}: {home_team} vs {away_team}")

def lookup_leagues(): 
    api_call = requests.get(f"https://www.thesportsdb.com/api/v1/json/801881/eventsnext.php?id=4335")
    storage = api_call.json()
    print(storage)
    # for event in storage["events"]:
    #     date_event = event["dateEvent"]
    #     home_team = event["strHomeTeam"]
    #     away_team = event["strAwayTeam"]
    #     print(f"{date_event}: {home_team} vs {away_team}")

event_ids = [2052711, 2052712, 2052713, 2052714]

# lookup_events(event_ids)

lookup_next()
