respond = {
    "already_get_credit": False
}
while 1 :
    student_id = input("Enter your student ID:")
    if(student_id.isnumeric() and len(student_id) == 11):
        break

pub = input("Enter your public key:")

request = {
    "student_id": student_id
}

if(respond["already_get_credit"]==True):
    print("Success Registration, your account will be ready to vote soon!")
else:
    print("You're already complete with this process before")