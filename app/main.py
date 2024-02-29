from fastapi import FastAPI
import os
import random
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
from fastapi.exceptions import HTTPException

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Replace with your Zoom OAuth credentials
CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID", default="your_client_id")
CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET", default="your_client_secret")
ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID", default="your_account_id")
ZOOM_TOKEN_ENDPOINT = "https://zoom.us/oauth/token"
ZOOM_USERS_ENDPOINT = "https://api.zoom.us/v2/users"

# APPLICATION SPECIFIC VARIABLES

MANDATORY_GROUP = os.environ.get("MANDATORY_GROUP", default="MANDATORY_GROUP_ID")
OPTIONAL_GROUP_1 = os.environ.get("OPTIONAL_GROUP_1", default="OPTIONAL_GROUP_1")
OPTIONAL_GROUP_2 = os.environ.get("OPTIONAL_GROUP_2", default="OPTIONAL_GROUP_2")

def get_zoom_oauth_token():
    response = requests.post(
        ZOOM_TOKEN_ENDPOINT,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "account_credentials", "account_id": ACCOUNT_ID}
    )

    if response.status_code == 200:
        # print(response.json())
        return response.json().get("access_token")
    else:
        return None


def generate_random_name():
    first_names = ['John', 'Jane', 'Chris', 'Sara', 'Mike', 'Laura', 'James', 'Mary', 'Robert', 'Patricia', 'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Jennifer', 'Joseph', 'Susan', 'Thomas', 'Jessica']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson']

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"jermainedotco+{first_name.lower()}.{last_name.lower()}.{random.randint(1000,9999)}@gmail.com"

    return {'first_name': first_name, 'last_name': last_name, 'email': email}


def add_user_to_group(token, group_id, user_ids, batch_size=30):
    """
    Adds users to a Zoom group in batches due to the API's limit.

    :param token: Your Zoom JWT or OAuth token
    :param group_id: The ID of the group to which the users will be added
    :param user_ids: A list of user IDs to add to the group
    :param batch_size: The maximum number of users to add in a single request (default: 30)
    """
    url = f"https://api.zoom.us/v2/groups/{group_id}/members"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Function to divide user_ids into chunks of batch_size
    def chunked_user_ids(seq, size):
        for i in range(0, len(seq), size):
            yield seq[i:i + size]

    # Iterate over the user IDs in chunks
    for batch in chunked_user_ids(user_ids, batch_size):
        data = {
            "members": [{"id": user_id} for user_id in batch]
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            print(f"Batch of users successfully added to group {group_id}.")
        else:
            print(f"Failed to add batch of users to group {group_id}. Status code: {response.status_code}, Response: {response.text}")


def remove_user_from_group(token, group_id, user_id):
    """
    Removes a user from a Zoom group.

    :param token: Your Zoom JWT or OAuth token
    :param group_id: The ID of the group from which the user will be removed
    :param user_id: The ID of the user to remove from the group
    """
    url = f"https://api.zoom.us/v2/groups/{group_id}/members/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"User {user_id} successfully removed from group {group_id}.")
    else:
        print(f"Failed to remove user {user_id} from group {group_id}. Status code: {response.status_code}, Response: {response.text}")


@app.get("/zoom-users")
def list_zoom_users():
    token = get_zoom_oauth_token()
    if not token:
        raise HTTPException(status_code=400, detail="Failed to get OAuth token")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # response = requests.get(ZOOM_USERS_ENDPOINT, headers=headers)
    # response = requests.get("https://api.zoom.us/v2/users/me", headers=headers)
    # response = requests.get("https://api.zoom.us/v2/users", headers=headers)
    users = []  # Initialize an empty list to store all user data
    next_page_token = ''  # Initialize pagination token
    base_url = f"https://api.zoom.us/v2/users"

    while True:
        # Include the next_page_token in the request if it exists
        response = requests.get(f"{base_url}?page_size=30&next_page_token={next_page_token}", headers=headers)
        if response.status_code != 200:
            # Handle error responses from the API
            raise HTTPException(status_code=response.status_code, detail="Error fetching Zoom group members")

        data = response.json()
        users.extend(data.get('users', []))  # Add the users from the current page to the list

        next_page_token = data.get('next_page_token', None)
        if not next_page_token:
            break  # Exit the loop if there's no next page
    basic_user_group_users_ids = [user['id'] for user in users]

    print(len(basic_user_group_users_ids))

    return users

    # return response.json()


@app.get("/group-members/{group_id}")
def get_group_members(group_id: str):
    token = get_zoom_oauth_token()
    if not token:
        raise HTTPException(status_code=400, detail="Failed to get OAuth token")

    zoom_endpoint = f"https://api.zoom.us/v2/groups/{group_id}/members"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(zoom_endpoint, headers=headers)
    if response.status_code != 200:
        print(response.json())
        raise HTTPException(status_code=response.status_code, detail="Error fetching group members")

    if response.status_code == 204:
        return {"message": "No members found"}

    num_of_pages = response.json().get("page_count")
    page_num = response.json().get("page_number")

    while num_of_pages - page_num != 0:
        response = requests.get(zoom_endpoint, headers=headers)
        print("did not run second time")
        num_of_pages -= 1

    return response.json()


@app.get("/check-zoom-groups")
def check_zoom_groups():
    basic_user_group_id = MANDATORY_GROUP
    recorded_user_group_id = OPTIONAL_GROUP_1
    recorded_and_chat_user_group_id = OPTIONAL_GROUP_2

    users = []
    basic_user = []
    recorded_user = []
    recorded_and_chat_user = []

    token = get_zoom_oauth_token()
    if not token:
        raise HTTPException(status_code=400, detail="Failed to get OAuth token")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    ####### ALL USERS #######
    next_page_token = ''  # Initialize pagination token
    base_url = f"https://api.zoom.us/v2/users"

    while True:
        # Include the next_page_token in the request if it exists
        response = requests.get(f"{base_url}?page_size=30&next_page_token={next_page_token}", headers=headers)
        if response.status_code != 200:
            # Handle error responses from the API
            raise HTTPException(status_code=response.status_code, detail="Error fetching Zoom group members")

        data = response.json()
        users.extend(data.get('users', []))  # Add the users from the current page to the list

        next_page_token = data.get('next_page_token', None)
        if not next_page_token:
            break  # Exit the loop if there's no next page
    all_users_id = [user['id'] for user in users]



    ####### BASIC USER GROUP #######
    next_page_token = ''  # Initialize pagination token
    base_url = f"https://api.zoom.us/v2/groups/{basic_user_group_id}/members"

    while True:
        # Include the next_page_token in the request if it exists
        response = requests.get(f"{base_url}?page_size=30&next_page_token={next_page_token}", headers=headers)
        if response.status_code != 200:
            # Handle error responses from the API
            raise HTTPException(status_code=response.status_code, detail="Error fetching Zoom group members")

        data = response.json()
        basic_user.extend(data.get('members', []))  # Add the users from the current page to the list

        next_page_token = data.get('next_page_token', None)
        if not next_page_token:
            break  # Exit the loop if there's no next page

    basic_user_group_users_ids = [user['id'] for user in basic_user]

    ####### RECORDED USER GROUP #######
    next_page_token = ''
    base_url = f"https://api.zoom.us/v2/groups/{recorded_user_group_id}/members"

    while True:
        response = requests.get(f"{base_url}?page_size=30&next_page_token={next_page_token}", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching Zoom group members")

        data = response.json()
        recorded_user.extend(data.get('members', []))

        next_page_token = data.get('next_page_token', None)
        if not next_page_token:
            break

    recorded_user_group_users_ids = [user['id'] for user in recorded_user]

    ####### RECORDED AND CHAT USER GROUP #######
    next_page_token = ''
    base_url = f"https://api.zoom.us/v2/groups/{recorded_and_chat_user_group_id}/members"

    while True:
        response = requests.get(f"{base_url}?page_size=30&next_page_token={next_page_token}", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching Zoom group members")

        data = response.json()
        recorded_and_chat_user.extend(data.get('members', []))

        next_page_token = data.get('next_page_token', None)
        if not next_page_token:
            break

    recorded_and_chat_user_group_users_ids = [user['id'] for user in recorded_and_chat_user]

    # Convert lists to sets for efficient operations
    all_users_set = set(all_users_id)
    basic_user_group_set = set(basic_user_group_users_ids)  # ToDo - Remove this
    recorded_user_group_set = set(recorded_user_group_users_ids)
    recorded_and_chat_user_group_set = set(recorded_and_chat_user_group_users_ids)

    # Find users that need to be added to the basic user group (not in recorded_user_group_set or recorded_and_chat_user_group_set)
    users_tobe_added_to_basic_user_set = all_users_set - (recorded_user_group_set | recorded_and_chat_user_group_set)
    print(len(users_tobe_added_to_basic_user_set))
    users_tobe_added_to_basic_user_set = users_tobe_added_to_basic_user_set - basic_user_group_set
    print(len(users_tobe_added_to_basic_user_set))
    users_tobe_added_to_basic_user = list(users_tobe_added_to_basic_user_set)
    print(len(users_tobe_added_to_basic_user))

    add_user_to_group(token, basic_user_group_id, users_tobe_added_to_basic_user)

    # Find users that need to be removed from the basic user group (in recorded_user_group_set or recorded_and_chat_user_group_set)
    users_tobe_removed_from_basic_user_set = basic_user_group_set & (recorded_user_group_set | recorded_and_chat_user_group_set)
    users_tobe_removed_from_basic_user = list(users_tobe_removed_from_basic_user_set)

    for user_id in users_tobe_removed_from_basic_user:
        remove_user_from_group(token, basic_user_group_id, user_id)







    return {
        "users_tobe_added_to_basic_user": users_tobe_added_to_basic_user,
        "users_tobe_removed_from_basic_user": users_tobe_removed_from_basic_user,
        "all_users_id": all_users_id,
        "basic_user_group_users_ids": basic_user_group_users_ids,
        "recorded_user_group_users_ids": recorded_user_group_users_ids,
        "recorded_and_chat_user_group_users_ids": recorded_and_chat_user_group_users_ids
    }


@app.get("/create_dummy_user/{count:int}")
def create_dummy_user(count: int):
    if count < 1:
        raise HTTPException(status_code=400, detail="Count must be greater than 0")
    token = get_zoom_oauth_token()
    if not token:
        raise HTTPException(status_code=400, detail="Failed to get OAuth token")

    for i in range(count):
        user_info = generate_random_name()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        body = {
            "action": "create",
            "user_info": {
                "email": user_info['email'],
                "first_name": user_info['first_name'],
                "last_name": user_info['last_name'],
                "display_name": user_info['first_name'] + " " + user_info['last_name'],
                "password": "if42!LfH@",
                "type": 1
            }
        }

        response = requests.post("https://api.zoom.us/v2/users/", headers=headers, json=body)
        print(response.json())


    # response = requests.get(ZOOM_USERS_ENDPOINT, headers=headers)


    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail="Error fetching Zoom users")

    return response.json()
