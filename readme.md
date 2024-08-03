## 1. Introduction
These scripts are used to extract information of bugs in automated driving software.

## 2. Usage
#### 1. Git Clone
Clone the project from git. 
#### 2. Install requirements
Install the requirements as the following commands:
```
$ pip install -r requirements.txt
```
#### 3. Extract pull request 
Before extracting pull requests, you should put your github access key in directory `access` to make sure you have the permission to run github API.

Run `python get_all_pr.py` to get all information of pull request in selected repository and output as json files, you can change the page numbers and the name of projects you want.
#### 4. Separate and filter issues
run `python filter_issue.py` to separate all the issue jsons and filter out the issues without useful information according to the conditions.
#### 5. Extract pull request to fix bugs
run `python filter_pr.py` to filter all pull requests for bug fixes.
#### 6. Get information about the fix patch
After manual marking, run `python get_pr_info.py` to get the number of modified rows, modified files, submissions and specific modified file names in each pull request.
Then run `python correct_commits.py` to correct the number of commits, because we don't need to count the commits used for the merge. Finally, use `correct_lens_and_files.py` to correct the number of code lines and files, because we do not need to consider the automatically generated non-functional code such as yarn.lock and testdata