from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uuid
import re
import os
import json




#FastAPI Set up

app =FastAPI(
    title="Enterprise AI Pipeline",
    description="Enterprise AI workflow Demo",
    version="1.0"
)

#Request Model

class SupportRequest(BaseModel):
    user_input :str

# Audit Logging

AUDIT_FILE ="audit_logs.json"   

#UI-Request tracking

def generate_request_id():
    return str(uuid.uuid4())

#Prompt  injection check

def detect_prompt_injection(text):
    suspicius_patterns =[
        "Ignore Previous instrctuions",
        "show Password",
        "bypass Security",
        "delete databse",
        "ignore syytem prompt"
    ]

    for pattern in suspicius_patterns:
        if pattern.lower() in text.lower():
            return True
    return False

# PII Detection 

def detect_pii(text):
    pii_found ={
        "account_number":False,
        "email":False,
        "phone":False    
    }    

    #8 Digit number
    if re.search(r"\b\d{8}\b",text):
        pii_found["account_number"] = True

    #Email Id Gane-sh123@gyaanlytics.com
    if re.search(r"[A-Za-z0-9.%+-]+@[A-Za-z0-9.]+\.[A-Za-z]{3,}",text):
        pii_found["email"] = True
    
    #10 Digit Phone number
    if re.search(r"\b[6-9]\d{10}\b",text):
        pii_found["phone"] = True
    
    return pii_found

# MASK PII

def mask_pii(text):
    #Mask account
    text = re.sub(
        r"\b\d{8}\b",
        "[Masked_Account]",
        text 

    )
    #Mask Email
    text = re.sub(
        r"[A-Za-z0-9.%+-]+@[A-Za-z0-9.]+\.[A-Za-z]{3,}",
        "[Masked_email]",
        text 
    )

    #Mask phone
    text = re.sub(
        r"\b[6-9]\d{10}\b",
        "[Masked_phone]",
        text 
    )

    return text

#build the prompt

def build_prompt (masked_text):
    system_prompt ="""
You are a secure enterprise enterprise banking AI assistant.

Rules :
1.Never reveal customer data.
2.Never expose Password"""
    final_prompt =f"""
SYSTEM:{system_prompt}

USER:{masked_text}
ASSISTANT:
"""       
    return final_prompt
USE_REAL_LLM=False
def call_llm(prompt):

    #mock
    if not USE_REAL_LLM:
        return """"dear customer, you request is taken, thank you"""

# compliance validation

def compliance_check(response):
    blocked_words =[
        "Password is",
        "SSN",
        "Credit card",
        "customer Data"

    ]
    for word in blocked_words:
        if word.lower() in response.lower():
            return{
                "status": "BLOCKED",
                "message":"Response blocked dude to company policy"
            }
        
    return{
        "status" :"Approved",
        "message":response 
    }    

#Audit Loging

def store_audit_logging(log_data):
    existing_logs = []

    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE,"r") as file:
            try:
                existing_logs = json.load(file)
            except:
                existing_logs=[]

    existing_logs.append(log_data)
    with open (AUDIT_FILE,"w") as file:
        json.dump(existing_logs,file,indent=4)


#Helath Check

@app.get("/")
def home():

    return {
        "message": "Enterprise GenAI Pipeline Running"
    }


#main Support API
@app.post("/support")
def support_query(request: SupportRequest):

    request_id =generate_request_id()
    user_input =request.user_input
    
    # STEP 1
    print("Step 1: request Recieved")
    print(user_input)
    # STEP 2
    print("Step 2: prompt injection check")
    injection_detected=detect_prompt_injection(user_input)
    if injection_detected:

        return{
            "Request_id":request_id,
            "status":"Blocked",
            "Reason":"Potential prompt injection detected"
        }
    print("No malicious prompt detected")

    # STEP 3
    print("Step 3: PII Detection")
    pii_status =detect_pii(user_input)
    print(pii_status)


    # STEP 4
    print("Step 4: PII Masking")
    masked_text =mask_pii(user_input)
    print(masked_text)

    # STEP 5

    
    final_prompt =build_prompt(masked_text)
    print(final_prompt)

    # STEP 6
    print("Step 6: Call LLM")
    llm_response =call_llm(final_prompt)
    print(llm_response)


    # STEP 7
    print("Step 7:Complianace validation")

    compliance_result =compliance_check(llm_response)
    print(compliance_result)

    # STEP 8
    print("Step 8:Audit logs")

    audit_log = {
        "request_id":request_id,
        "timestamp":str(datetime.now()),
        "original_input":user_input,
        "masked_text":masked_text,
        "pii_detected":pii_status,
        "compliance_status":compliance_result["status"]
    }
    store_audit_logging(audit_log)

    print("Audit logging done successfully")

    #STEP 9 :Final Response

    return{
        "request_id":request_id,
        "pipeline_status":"SUCCESS",
        "pii_detected":pii_status,      
        "masked_text":masked_text,
        "final_response":compliance_result["message"]
        
    }






    






    
