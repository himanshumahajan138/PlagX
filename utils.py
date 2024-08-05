import os 
import sys
import urllib
import json
from random import choice
import time 
from tqdm import tqdm
import glob
import zipfile
import requests
import pandas as pd
import csv
import base64
from datetime import datetime, timezone, timedelta

headers1 = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"126.0.6478.127"',
    "sec-ch-ua-full-version-list": '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.127", "Google Chrome";v="126.0.6478.127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

headers2 = headers1.copy()
headers2["referer"] = "https://leetcode.com/contest/"

def create_directories(contest):
    lang_list = ["c","cpp","cs","dart","erl","ex","go","java","js","kt","php","py","rb","rkt","rs","scala","swift","ts"]
    # create folder
    try:
        os.mkdir("plagiarism")
        os.mkdir("plag_report")
        os.mkdir("contests")
    except:
        pass
    try:
        os.mkdir(contest)
        os.mkdir("plag_report/"+contest.split('/')[-1])
    except:
        pass
    try:
        os.mkdir(contest + "/Q3")
    except:
        pass
    try:
        os.mkdir(contest + "/Q4")
    except:
        pass
    for i in lang_list:
        try:
            os.mkdir(contest + "/Q3/" + i)
        except:
            pass
        try:
            os.mkdir(contest + "/Q4/" + i)
        except:
            pass

def questions_information(contest_url):
    ## get question_id
    Q = []

    status = 0
    for _ in range(10):
        try:
            req = urllib.request.Request(
                contest_url, headers=choice([headers1, headers2])
            )
            r = urllib.request.urlopen(req)
            response = json.loads(r.read())
        except urllib.error.HTTPError as e:
            print(type(e.code))
            status = e.code
        except:
            pass
        else:
            break
    else:
        print("Status", status, contest_url)
        sys.exit()

    for question in response["questions"]:
        Q.append(str(question["question_id"]))
        print(question["question_id"], question["credit"], question["title"])
    return Q


# Function to get file extension based on language
def lang_ext(lang):
    return {
        "cpp": "cpp",
        "python3": "py",
        "python": "py",
        "java": "java",
        "csharp": "cs",
        "javascript": "js",
        "golang": "go",
        "kotlin": "kt",
        "rust": "rs",
        "swift": "swift",
        "php": "php",
        "ruby": "rb",
        "scala": "scala",
        "racket": "rkt",
        "erlang": "erl",
        "dart": "dart",
        "typescript": "ts",
        "c": "c",
        "elixir": "ex",
    }.get(lang, lang)


# Function to make a request with retries
def make_request(url, headers, retries=10, backoff=1):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except urllib.error.URLError as e:
            print(f"Attempt {i+1} failed: {e.reason}")
            if i < retries - 1:
                time.sleep(backoff * (2**i))
            else:
                raise
        except urllib.error.HTTPError as e:
            print(f"HTTP error: {e.code}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

def contest_crawler(contest,contest_url,start_page,end_page):
    
    Q=questions_information(contest_url)
    # Iterate through pages
    for pagination in tqdm(range(start_page, end_page + 1)):
        contest_api = f"{contest_url}?pagination={pagination}&region=global"
        response = make_request(contest_api, choice([headers1, headers2]))

        for i in tqdm(range(25)):
            if response["total_rank"][i]["data_region"] == "CN":
                continue

            ra = str(response["total_rank"][i]["rank"])
            user = str(response["total_rank"][i]["user_slug"])
            sub3 = str(response["submissions"][i].get(Q[2], {}).get("submission_id", ""))
            sub4 = str(response["submissions"][i].get(Q[3], {}).get("submission_id", ""))

            if sub3:
                sub3_url = f"https://leetcode.com/api/submissions/{sub3}"
                sub3_code = make_request(sub3_url, choice([headers1, headers2]))
                codepath3 = f"{contest}/Q3/{lang_ext(sub3_code['lang'])}/{ra};{user};{sub3}.{lang_ext(sub3_code['lang'])}"

                with open(codepath3, "w", encoding="utf-8") as code3:
                    try:
                        code3.write(sub3_code["code"])
                    except Exception as e:
                        print(f"Failed for {user} in question 3: {e}")

            if sub4:
                sub4_url = f"https://leetcode.com/api/submissions/{sub4}"
                sub4_code = make_request(sub4_url, choice([headers1, headers2]))
                codepath4 = f"{contest}/Q4/{lang_ext(sub4_code['lang'])}/{ra};{user};{sub4}.{lang_ext(sub4_code['lang'])}"

                with open(codepath4, "w", encoding="utf-8") as code4:
                    try:
                        code4.write(sub4_code["code"])

                    except Exception as e:
                        print(f"Failed for {user} in question 4: {e}")
                        


def zip_directory(directory_path):
    support_list = ["c", "cpp", "cs", "js", "java", "php", "py", "ts"]
    for root, _, files in os.walk(directory_path):
        folder_type = root.split(sep="/")[-1]
        if folder_type in support_list:
            zips_to_del = glob.glob(os.path.join(root, "*.zip")) + glob.glob(
                os.path.join(root, "*.csv")
            )
            list(map(os.remove, zips_to_del))
            if len(files) > 1 and len(files) <= 750:
                with zipfile.ZipFile(
                    f"{root}/{(root.split(sep='/'))[-1]}.zip", "w", zipfile.ZIP_DEFLATED
                ) as zipf:
                    for file in files:
                        if str(file).endswith(f"{(root.split(sep='/'))[-1]}"):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, file)

            elif len(files) > 1:
                if len(files) % 750 == 0:
                    lim = len(files) // 750
                else:
                    lim = (len(files) // 750) + 1
                start = 0
                end = 750
                for i in range(lim):
                    with zipfile.ZipFile(
                        f"{root}/{(root.split(sep='/'))[-1]}_{i+1}.zip",
                        "w",
                        zipfile.ZIP_DEFLATED,
                    ) as zipf:
                        for i in range(start, end, 1):
                            try:
                                file = files[i]
                                if str(file).endswith(f"{(root.split(sep='/'))[-1]}"):
                                    file_path = os.path.join(root, file)
                                    zipf.write(file_path, file)
                            except:
                                break
                    start += 750
                    end += 750

def zip_questions(contest):
    directory_paths = [f"{contest}/Q3/", f"{contest}/Q4/"]
    for directory_path in directory_paths:
        zip_directory(directory_path)


def submit_to_dolos(name, zipfile_path):
    """
    Submit a ZIP-file to the Dolos API for plagiarism detection
    and return the URL where the resulting HTML report can be found.
    """
    response = requests.post(
        "https://dolos.ugent.be/api/reports",
        files={"dataset[zipfile]": open(zipfile_path, "rb")},
        data={"dataset[name]": name},
    )
    json = response.json()
    return json


# Example usage
def list_required_files(main_directory,type):
    if(type=="zip"):
        extension=".zip"
    elif(type=="csv"):
        extension=".csv"
    else:
        extension=""
        
    final_list = []
    support_list = ["c", "cpp", "cs", "js", "java", "php", "py", "ts"]

    # Walk through the directory
    for root, dirs, files in os.walk(main_directory):
        folder_type = root.split(sep="/")[-1]
        if folder_type in support_list:
            for file in files:
                if file.lower().endswith(extension):
                    # Create full file path and add to the list
                    full_path = os.path.join(root, file)
                    final_list.append(full_path)
    return final_list



def final_submit_to_dolos(l):
    d = list()
    for i in l:
        data = submit_to_dolos(f"{(i.split('\\'))[-1]}", i)
        dic = {
            "path": i,
            "url": f"https://dolos.ugent.be/api/reports/{data['id']}/data/pairs.csv",
        }
        d.append(dic)
        print(
            f"{i} done, please wait 5 seconds before next request, Link: {data['html_url']}"
        )
        time.sleep(5)
    return d

def preprocess_zips_for_dolos(contest):
    q3_zips = list_required_files(f"{contest}/Q3/","zip")
    q4_zips = list_required_files(f"{contest}/Q4/","zip")
    print("Pre-Processing Done !!!")
    print("Final Submitting Files !!!")
    q3_dict = final_submit_to_dolos(q3_zips)
    q4_dict = final_submit_to_dolos(q4_zips)
    print("Files Submitted !!!")
    print("please wait for 30 sec  after submiting files")
    for i in tqdm(range(30)):
        time.sleep(1)
    
    return q3_dict,q4_dict

def check_status_and_download(
    api_url,
    download_url,
    download_path,
    initial_wait=30,
    min_wait=5,
    decay_factor=0.9,
    max_retries=10,
):
    """
    Continuously checks the status of an API endpoint and downloads the file once status is 200.
    The wait time starts longer and decreases with each check.

    :param api_url: The URL to check for status.
    :param download_url: The URL to download the file from once status is 200.
    :param download_path: The local path where the downloaded file will be saved.
    :param initial_wait: Initial wait time in seconds before the first retry.
    :param min_wait: Minimum wait time in seconds between retries.
    :param decay_factor: Factor by which the wait time decreases after each retry.
    :param max_retries: The maximum number of status checks before giving up.
    """
    wait_time = initial_wait
    print("Processing...")

    with tqdm(total=max_retries, desc="Checking status", unit="check") as pbar:
        for _ in range(max_retries):
            try:
                # Check the status of the API endpoint
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an error for HTTP error codes

                if response.status_code == 200:
                    print("Status is 200. Starting download...")

                    # Download the file
                    download_response = requests.get(download_url, stream=True)
                    download_response.raise_for_status()  # Raise an error for HTTP error codes

                    with open(download_path, "wb") as file:
                        for chunk in download_response.iter_content(chunk_size=8192):
                            file.write(chunk)

                    print(f"File downloaded successfully and saved to {download_path}")
                    break  # Exit the loop once the download is complete

                else:
                    pbar.update(1)
                    print(
                        f"Status is {response.status_code}. Checking again in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)

                    # Decrease the wait time with decay factor, but ensure it does not go below min_wait
                    wait_time = max(min_wait, wait_time * decay_factor)

            except requests.RequestException as e:
                print(f"An error occurred: {e}")
                pbar.update(1)
                time.sleep(wait_time)
                wait_time = max(min_wait, wait_time * decay_factor)

        else:
            print("Max retries reached. The status did not become 200.")


def download_report(l):
    for i in l:
        print(f"starting for {i['path']}")
        path = f"{i['path'].split('.')[0]}.csv"
        print(path)
        check_status_and_download(i["url"], i["url"], path)


def download_final_reports(contest):
    q3_dict,q4_dict=preprocess_zips_for_dolos(contest)
    print("Downloading Reports !!!")
    download_report(q3_dict)
    download_report(q4_dict)
    print("Reports Downloaded !!!")


def combine_csv(csv_files, path):
    # Initialize an empty list to hold DataFrames
    dfs = []
    # Loop through the list of CSV files and read them into DataFrames
    for file in csv_files:
        df = pd.read_csv(file)

        # Drop unnecessary columns
        drp = [
            "id",
            "leftFileId",
            "rightFileId",
            "totalOverlap",
            "longestFragment",
            "leftCovered",
            "rightCovered",
        ]
        df = df.drop(
            columns=drp, errors="ignore"
        )  # Use errors='ignore' to handle cases where columns might not exist

        # Process columns
        df["leftFilePath"] = df["leftFilePath"].apply(
            lambda x: str(x).split(sep="/")[-1]
        )
        df["rightFilePath"] = df["rightFilePath"].apply(
            lambda x: str(x).split(sep="/")[-1]
        )
        df["similarity"] = df["similarity"].apply(lambda x: int(round(x, 2) * 100))

        # Append the DataFrame to the list
        dfs.append(df)

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv(path, index=False)


def combine_reports(contest):
    q3_csv = list_required_files(f"{contest}/Q3/","csv")
    q4_csv = list_required_files(f"{contest}/Q4/","csv")

    combine_csv(q3_csv, f"{contest}/Q3/Q3_Result.csv")
    combine_csv(q4_csv, f"{contest}/Q4/Q4_Result.csv")


def result(df_path, path, threshold=50):
    combined_df = pd.read_csv(df_path)
    # Perform the existing processing logic on the combined DataFrame
    combined_df = combined_df.loc[
        combined_df.groupby("leftFilePath")["similarity"].idxmax()
    ]
    combined_df = combined_df.reset_index(drop=True)

    # Identify missing `leftFilePath` values
    missing_right_paths = set(combined_df["rightFilePath"]) - set(
        combined_df["leftFilePath"]
    )

    # Create new rows with reversed paths for missing `rightFilePath`
    new_rows = []
    for right_path in missing_right_paths:
        # Get the rows in the original DataFrame where `rightFilePath` matches `leftFilePath`
        match_rows = combined_df[combined_df["rightFilePath"] == right_path]
        for _, row in match_rows.iterrows():
            new_row = {
                "leftFilePath": right_path,
                "rightFilePath": row["leftFilePath"],
                "similarity": row["similarity"],
            }
            new_rows.append(new_row)

    # Convert new rows to DataFrame
    new_df = pd.DataFrame(new_rows)
    # Concatenate original DataFrame with new DataFrame
    combined_df = pd.concat([combined_df, new_df], ignore_index=True)

    combined_df = combined_df[combined_df["similarity"] >= threshold]
    combined_df.sort_values(
        by=["leftFilePath", "similarity", "rightFilePath"], inplace=True
    )
    combined_df = combined_df.reset_index(drop=True)
    combined_df.sort_values(
        by=["leftFilePath", "similarity", "rightFilePath"],
        ascending=[True, False, True],
        inplace=True,
    )

    combined_df.drop_duplicates(subset="leftFilePath", keep="first", inplace=True)

    # save the final DataFrame
    combined_df.to_csv(path, index=False)  # Uncomment to save to a CSV file


def final_result(path,user_link,contest_sub):
    # Sample DataFrame including the similarity column
    df = pd.read_csv(path)
    if df.empty:
        print(f"No Plagiarism in {path.split('/')[-2]}")
        return

    # Split 'leftFilePath' into subcolumns
    left_split = df["leftFilePath"].str.split(";", expand=True)
    left_split.columns = ["left_rank", "left_username", "left_submission_id"]

    # Split 'rightFilePath' into subcolumns
    right_split = df["rightFilePath"].str.split(";", expand=True)
    right_split.columns = ["right_rank", "right_username", "right_submission_id"]

    # Combine the DataFrames
    df_combined = pd.concat([left_split, right_split, df["similarity"]], axis=1)
    df_combined.rename(
        columns={
            "left_rank": "cheater1_rank",
            "left_username": "cheater1_username",
            "left_submission_id": "cheater1_submission_id",
            "right_rank": "cheater2_rank",
            "right_username": "cheater2_username",
            "right_submission_id": "cheater2_submission_id",
            "similarity": "similarity_percentage",
        },
        inplace=True,
    )

    df_combined["cheater1_username"] = user_link + df_combined["cheater1_username"]
    df_combined["cheater2_username"] = user_link + df_combined["cheater2_username"]
    df_combined["cheater1_submission_id"] = contest_sub + df_combined[
        "cheater1_submission_id"
    ].apply(lambda x: x.split(".")[0])
    df_combined["cheater2_submission_id"] = contest_sub + df_combined[
        "cheater2_submission_id"
    ].apply(lambda x: x.split(".")[0])
    df_combined["cheater1_rank"] = df_combined["cheater1_rank"].astype("int")
    df_combined["cheater2_rank"] = df_combined["cheater2_rank"].astype("int")
    df_combined.sort_values(by="cheater1_rank", inplace=True)
    df_combined = df_combined[
        (df_combined["cheater1_rank"] > 250) | (df_combined["cheater2_rank"] > 250)
    ]
    df_combined = df_combined[df_combined['cheater1_rank']>df_combined['cheater2_rank']]
    print(f"{df_combined.shape[0]} Plagiarism Cases in {path.split('/')[-2]}")
    df_combined.to_csv(path, index=False)
    print(f"Report saved at this path : {path}")


def final_report_results(contest,user_link,contest_sub):
    
    result(f"{contest}/Q3/Q3_Result.csv", f"{contest}/Q3/Q3_Final_Result.csv")
    result(f"{contest}/Q4/Q4_Result.csv", f"{contest}/Q4/Q4_Final_Result.csv")

    final_result(f"{contest}/Q3/Q3_Final_Result.csv",user_link,contest_sub)
    final_result(f"{contest}/Q4/Q4_Final_Result.csv",user_link,contest_sub)


def convert_to_json(csv_file_path):
    data = []
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    output = {"data": data}
    split_path = csv_file_path.split("/")
    json_file_path = (
        "plag_report/"
        + split_path[1]
        + "/"
        + split_path[-1].split(sep=".")[0]
        + ".json"
    )

    with open(json_file_path, "w") as json_file:
        json.dump(output, json_file, indent=4)

    print("CSV to JSON conversion completed!")
    print(f"file saved at {json_file_path}")

def convert_reports_to_json(contest):
    convert_to_json(f"{contest}/Q3/Q3_Final_Result.csv")
    convert_to_json(f"{contest}/Q4/Q4_Final_Result.csv")



def get_latest_files(folder_path):
    """Get the list of all files in the specified folder, including subdirectories"""
    latest_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            latest_files.append(full_path)
    return latest_files


def upload_file_to_github(file_path, repo, branch, token):
    """Upload a single file to GitHub"""
    with open(file_path, "rb") as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode()
    file_path = file_path.replace("\\", "/")
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Get the current timestamp for the commit message
    timestamp = datetime.now(timezone.utc).isoformat()

    data = {
        "message": f"Upload {file_path} at {timestamp}",
        "content": encoded_content,
        "branch": branch,
    }

    # Check if the file already exists to get its SHA
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
        data["sha"] = sha
        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"Successfully updated {file_path} on GitHub.")
        else:
            print(f"Failed to update {file_path}. Response: {response.json()}")
    elif response.status_code == 404:
        # File does not exist, create a new one
        response = requests.put(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Successfully uploaded {file_path} to GitHub.")
        else:
            print(f"Failed to upload {file_path}. Response: {response.json()}")
    else:
        print(f"Failed to fetch SHA for {file_path}. Response: {response.json()}")


def get_contest_data(api):
    response= requests.get(api)
    return response.json()
    
def check_and_get_file_content(repo, path, branch):
        url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
        response = requests.get(url)
        if response.status_code == 200:
            content = response.json()['content']
            return json.loads(base64.b64decode(content).decode('utf-8'))
        return None

def create_data_file_content(directory,clist_api,contest_name,repo,branch):
    contest_data = get_contest_data(clist_api)['objects']
    data = []
    
    data_file_path="contests/data.json"
    existing_content = check_and_get_file_content(repo, data_file_path, branch)
    if existing_content and 'data' in existing_content:
        data = existing_content['data']
    
    for root, dirs, files in os.walk(directory):
        if files != []:
            contest_web_link = f"https://leetcode.com/contest/{contest_name}"
            name=contest_name.replace('-',' ').title()
            contest_date=None
            for doc in contest_data:
                if doc['event'] == name:
                    contest_date=doc['start']
                    contest_date= (datetime.fromisoformat(contest_date) + timedelta(hours=5, minutes=30)).strftime('%B %d, %Y, %I:%M %p')
                    break
            
            dic = {
                "contest_name": f"{contest_web_link}",
                "contest_date":f"{contest_date}",
                "question_3": f"{root}/{files[0]}",
                "question_4": f"{root}/{files[1]}",
            }
            # Check if the entry already exists in data
            entry_exists = False
            for entry in data:
                if entry["contest_name"].lower() == dic["contest_name"].lower():
                    entry.update(dic)  # Update the existing entry
                    entry_exists = True
                    break
            
            if not entry_exists:
                data.append(dic)  # Add new entry if it does not exist
                
    output = {"data": data}
    return output


def save_to_json(data, output_file):
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)


def upload_json_results(local_folder_path,github_repo,branch,github_token):
    latest_files = get_latest_files(local_folder_path)
    print(latest_files)
    for file_path in latest_files:
        print(file_path)
        upload_file_to_github(file_path, github_repo, branch, github_token)


def upload_data_file(contest_name,directory,output_file,contest_data_path,github_repo,branch,github_token,clist_api):

    directory_structure = create_data_file_content(directory,clist_api,contest_name,github_repo,branch)

    save_to_json(directory_structure, output_file)

    print(f"Directory structure saved in json at {output_file}")
        
    latest_contest_data = get_latest_files(contest_data_path)
    for file_path in latest_contest_data:
        upload_file_to_github(file_path, github_repo, branch, github_token)

def upload_web_files(web_path,github_repo,branch,github_token):
    latest_contest_data = get_latest_files(web_path)
    for file_path in latest_contest_data:
        upload_file_to_github(file_path, github_repo, branch, github_token)