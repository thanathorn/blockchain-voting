import requests

while 1 :
    student_id = input("Enter your student ID:")
    if(student_id.isnumeric() and len(student_id) == 11):
        break
url = "http://127.0.0.1:8000/master/registration/student"
payload={'student_id': '61070501023'}
files=[]
headers = {}
response = requests.request("POST", url, headers=headers, data=payload, files=files)
pub = input("Enter your public key:")

if response.json()['already_get_credit']==False:
    print("Success Registration, your account will be ready to vote soon!")
else:
    print("You're already complete with this process before")