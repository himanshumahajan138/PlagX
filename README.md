# PlagX 📜🚫

PlagX is an automated tool designed to detect potential plagiarism in LeetCode coding contests.  It crawls contest data, processes user submissions, generates comprehensive reports, and uploads results to GitHub. Features secure handling of environment variables and seamless integration with GitHub for efficient data management.

## 📋 Pre-Requirements

Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## 🔗 Website Live Link
Visit this Link for Checking Live PlagX Website [PlagX](https://himanshumahajan138.github.io/lc/web/)

For Website Code Please Do Visit to my Github Repository [lc](https://github.com/himanshumahajan138/lc)

## 📷Screenshots

![Screenshot_1-8-2024_231619_](https://github.com/user-attachments/assets/5e0dca67-576c-4282-a093-4a0f3beda1b3)
![Screenshot_1-8-2024_232146_himanshumahajan138 github io](https://github.com/user-attachments/assets/e1453bc1-0d98-493b-b9c1-7e1d1351c2cb)


## 🚀 Project Overview

### Step 1: Initialize Constants and Load Environment Variables

Set up the environment and constants for the project. Sensitive data is loaded from the `.env` file.

### Step 2: Create Required Folders

Create the necessary directories for storing data.

### Step 3: Crawl the Website for Contest Data and Submission Data

Crawl the LeetCode website to collect contest and submission data.

### Step 4: Create Zips for Contest Data and Submission Data

Compress the collected data into ZIP files.

### Step 5: Submit Reports and Download Reports

Download the reports for further processing.

### Step 6: Combine Result Reports

Combine individual reports into a comprehensive report.

### Step 7: Calculate Final Results

Generate the final results based on the combined reports.

### Step 8: Convert Final Reports to JSON

Convert the final reports into JSON format for easier handling.

### Step 9: Upload JSON Reports to GitHub

Upload the JSON reports to the specified GitHub repository.

### Step 10: Upload Data File to GitHub

Upload the data file to GitHub for record-keeping and further analysis.

## 🌟 Environment Variables

The project uses the following environment variables, which should be defined in a `.env` file:

- `GITHUB_TOKEN`: GitHub token for authentication
- `GITHUB_REPO`: GitHub repository URL
- `BRANCH`: GitHub branch
- `JSON_FOLDER_PATH`: Path to the JSON folder
- `DATA_FOLDER_PATH`: Path to the data folder
- `GITHUB_LINK`: GitHub link
- `WEB_PATH`: Web path
- `CLIST_API`: Clist API key

## 🔧 Utils

The project relies on various utility functions located in the `utils` module:

- `create_directories(contest)`
- `contest_crawler(contest, contest_url, page)`
- `zip_questions(contest)`
- `download_final_reports(contest)`
- `combine_reports(contest)`
- `final_report_results(contest, user_link, contest_sub)`
- `convert_reports_to_json(contest)`
- `upload_json_results(json_folder_path, github_repo, branch, github_token)`
- `upload_data_file(contest_name, json_folder_path, data_file_path, data_folder_path, github_repo, branch, github_token, clist_api)`

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or suggestions.

## 🙏 Acknowledgments

- [LeetCode](https://leetcode.com) for providing the platform for coding contests.
- [Dolos](https://github.com/dodona-edu/dolos) for inspiration on plagiarism detection tools.
- All contributors and users for their support and feedback.

## 📬 Contact

For any questions or inquiries, please contact [Himanshu Mahajan](https://www.linkedin.com/in/himanshu138).

## 🔖 Tags

`plagiarism-detection` `leetcode` `coding-contests` `web-crawler` `data-processing` `automation` `python` `github-integration` `json` `report-generation` `Cheating-detection` `github-pages`
