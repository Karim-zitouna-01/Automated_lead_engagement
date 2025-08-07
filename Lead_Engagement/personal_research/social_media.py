import json
from apify_client import ApifyClient
import http.client

APIFY_KEY="apify_api_8Tshzy61AFMoqcD9O2fnxODpgAH9CK4oDuVu"
RAPID_API_KEY="30f0a8d6e4msh13d82afdd7da410p195c0ejsn41d7f2805fb1"


def linkedinsearch(username):

    if username:
        client = ApifyClient(APIFY_KEY)
        run_input = {
            "username": f"{username}",
            "page_number": 1,
            "limit": 5,
        }
        run = client.actor("LQQIXN9Othf8f7R5n").call(run_input=run_input)
        data = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
        return data

def twittersearch(username):

    if username:
        conn = http.client.HTTPSConnection("twitter-api45.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPID_API_KEY,
            'x-rapidapi-host': "twitter-api45.p.rapidapi.com"
        }
        conn.request("GET", f"/timeline.php?screenname={username}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

def instasearch(username):

    if username:
        conn = http.client.HTTPSConnection("instagram-api-fast-reliable-data-scraper.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': RAPID_API_KEY,
            'x-rapidapi-host': "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"
        }
        conn.request("GET", f"/profile?username={username}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

def search_all(linkedin_username, twitter_username, insta_username):
    return {
        "linkedin": linkedinsearch(linkedin_username),
        "twitter": twittersearch(twitter_username),
        "instagram": instasearch(insta_username)
    }


# if __name__ == "__main__":
#     linkedin_username = "imen-ayari-1b1bb811"
#     twitter_username = "imennayari"
#     insta_username = "imenyari"

#     result = search_all(linkedin_username, twitter_username, insta_username)

#     # # Pretty print the result as JSON
#     # import json
#     # print(json.dumps(result, indent=2, ensure_ascii=False))


#     # Write the result to a JSON file
#     import json
#     with open("output.json", "w", encoding="utf-8") as f:
#         json.dump(result, f, indent=2, ensure_ascii=False)

#     print("Results written to output.json")
