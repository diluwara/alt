def sds_call(addresses,ups_api_endpoint,username,password,license_number,timeout):
	if ups_api_endpoint == "sim":
		return {"addrs":addresses}
	try:
		# ct = current_time_at_timezone('America/New_York')
		# if not (ct <= "09:00:00" and ct >= "02:00:00"):
		# 	print("OUTSIDE SDS WINDOW")
		# 	return None
		# print("SDS_CALL")
		headers = {"content-type": "text/xml"}
		# response = requests.post(ups_api_endpoint, data=generate_request_xml(addresses,username,password,license_number).encode("utf-8"),headers=headers)
		response_dict = None

		# try:
		# 	db = sql_controller()
		# 	timeout = float(global_timeout)
		# 	if retailer_code is not None:
		# 		timeout = float(db.get_retailer_timeout())
		# 	response = requests.post(ups_api_endpoint, data=generate_request_xml(addresses,username,password,license_number).encode("utf-8"),headers=headers,timeout=timeout)
		# 	response_dict = xmltodict.parse(response.content)
		# except requests.Timeout:
		# 	return "timeout"

		
		# db = sql_controller()
		response = requests.post(ups_api_endpoint, data=generate_request_xml(addresses,username,password,license_number).encode("utf-8"),headers=headers,timeout = timeout)
		response_dict = xmltodict.parse(response.content)
		
		if "sds:SDSResponse" in response_dict["soapenv:Envelope"]["soapenv:Body"].keys():
			response_formatted = response_dict["soapenv:Envelope"]["soapenv:Body"]["sds:SDSResponse"]
			return response_formatted
		else:
			error = response_dict['soapenv:Envelope']['soapenv:Body']['soapenv:Fault']['detail']['err:Errors']['err:ErrorDetail']['err:PrimaryErrorCode']['err:Code']
			return {"error":error}
	except Timeout:
		print("The request timed out.")
		return "timeout"
	except Exception as e:
		print("SDS error occurred: " + str(e))
		return None


def generate_request_xml(addresses,username,password,license_number):
	address_xml_template = ""
	for address in addresses:
		
		if address["ship_to_street2"] in ["None","null",None]:
			address["ship_to_street2"] = ""
		if address["ship_to_street3"] in ["None","null",None]:
			address["ship_to_street3"] = ""
		if address["ship_to_country"] in ["None","null",None]:
			address["ship_to_country"] = "US"

		if "CustomerAddressID" not in address:
			address["CustomerAddressID"] = "T8N"
			
		if "name" in address:
			if address["name"] in ["None","null",None]:
				address["name"] = ""
		else:
			address["name"] = ""
		if "attention_name" in address:	
			if address["attention_name"] in ["None","null",None]:
				address["attention_name"] = ""
		else:
			address["attention_name"] = ""

		address_xml_template += (
			"""
				<v11:Address>
					<v11:CustomerAddressID>{}</v11:CustomerAddressID>
					<v11:Name>{}</v11:Name>
					<v11:AttentionName>{}</v11:AttentionName>
					<v11:AddressLine1>{}</v11:AddressLine1>
					<v11:AddressLine2>{}</v11:AddressLine2>
					<v11:AddressLine3>{}</v11:AddressLine3>
					<v11:City>{}</v11:City>
					<v11:State>{}</v11:State>
					<v11:Country>{}</v11:Country>
					<v11:PostalCode>{}</v11:PostalCode>
				</v11:Address>
			"""
		).format(
			address["CustomerAddressID"],
			address["name"],
			address["attention_name"],
			address["ship_to_street1"],
			address["ship_to_street2"],
			address["ship_to_street3"],
			address["ship_to_city"],
			address["ship_to_state"],
			address["ship_to_country"],
			address["ship_to_postal_code"],
		)

	return """
		<soapenv:Envelope
		xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
		xmlns:v1="http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0"
		xmlns:v11="http://www.ups.com/XMLSchema/XOLTWS/SDS/v1.0"
		xmlns:v12="http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0">
			<soapenv:Header>
				<v1:UPSSecurity>
					<v1:UsernameToken>
						<v1:Username>{}</v1:Username>
						<v1:Password>{}</v1:Password>
					</v1:UsernameToken>
					<v1:ServiceAccessToken>
						<v1:AccessLicenseNumber>{}</v1:AccessLicenseNumber>
					</v1:ServiceAccessToken>
				</v1:UPSSecurity>
			</soapenv:Header>
			<soapenv:Body>
				<v11:SDSRequest>
					<v11:TimeToMonitor>0</v11:TimeToMonitor>
					<v12:Request>
						<v12:RequestOption>02</v12:RequestOption>
						<v12:TransactionReference>
							<v12:CustomerContext>Inbound- Success</v12:CustomerContext>
							<v12:TransactionIdentifier></v12:TransactionIdentifier>
						</v12:TransactionReference>
					</v12:Request>
					{}
				</v11:SDSRequest>
			</soapenv:Body>
		</soapenv:Envelope>
	""".format(username,password,license_number,address_xml_template)



import json

def generate_request_json(addresses, username, password, license_number):
    # Initialize the request dictionary
    request_dict = {
        "UPSSecurity": {
            "UsernameToken": {
                "Username": username,
                "Password": password
            },
            "ServiceAccessToken": {
                "AccessLicenseNumber": license_number
            }
        },
        "SDSRequest": {
            "TimeToMonitor": 0,
            "Request": {
                "RequestOption": "02",
                "TransactionReference": {
                    "CustomerContext": "Inbound- Success",
                    "TransactionIdentifier": ""
                }
            },
            "Address": []
        }
    }

    # Build the address list
    for address in addresses:
        # Replace 'None', 'null', or None with appropriate defaults
        address = {k: ("" if v in ["None", "null", None] else v) for k, v in address.items()}
        address.setdefault("CustomerAddressID", "T8N")
        address.setdefault("name", "")
        address.setdefault("attention_name", "")

        # Append the address to the request dictionary
        request_dict["SDSRequest"]["Address"].append({
            "CustomerAddressID": address.get("CustomerAddressID"),
            "Name": address.get("name"),
            "AttentionName": address.get("attention_name"),
            "AddressLine1": address.get("ship_to_street1"),
            "AddressLine2": address.get("ship_to_street2", ""),
            "AddressLine3": address.get("ship_to_street3", ""),
            "City": address.get("ship_to_city"),
            "State": address.get("ship_to_state"),
            "Country": address.get("ship_to_country", "US"),
            "PostalCode": address.get("ship_to_postal_code")
        })

    # Convert the request dictionary to a JSON string
    return json.dumps(request_dict)

import requests
import json
from requests.exceptions import Timeout

def sds_call(addresses, ups_api_endpoint, username, password, license_number, timeout):
    if ups_api_endpoint == "sim":
        return {"addrs": addresses}
    
    try:
        headers = {
            "Content-Type": "application/json",  # Assume the content being sent is JSON
            "Accept": "application/json"         # Request a JSON response
        }
        response_dict = None

        # Assuming generate_request_json is a function you would create to generate the JSON payload
        response = requests.post(ups_api_endpoint, json=generate_request_json(addresses, username, password, license_number), headers=headers, timeout=timeout)
        
        # Load JSON response into a Python dictionary
        response_dict = response.json()
        
        # The rest of the code would need to be adapted based on the actual structure of the JSON response
        if "SDSResponse" in response_dict:
            response_formatted = response_dict["SDSResponse"]
            return response_formatted
        else:
            error = response_dict['Fault']['detail']['Errors']['ErrorDetail']['PrimaryErrorCode']['Code']
            return {"error": error}
            
    except Timeout:
        print("The request timed out.")
        return "timeout"
    except Exception as e:
        print("SDS error occurred: " + str(e))
        return None

"raw_sds_test_response": "{\"@xmlns:sds\": \"http://www.ups.com/XMLSchema/XOLTWS/SDS/v1.0\", \"common:Response\": {\"@xmlns:common\": \"http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0\", \"common:ResponseStatus\": {\"common:Code\": \"1\", \"common:Description\": \"Success\"}, \"common:TransactionReference\": {\"common:CustomerContext\": \"Inbound- Success\", \"common:TransactionIdentifier\": \"dssyncs56c374zC65xDBXR\"}}, \"sds:Address\": [{\"sds:CustomerAddressID\": \"T8N\", \"sds:Classification\": \"R\", \"sds:GroupNumber\": \"0\", \"sds:ErrorCode\": \"0\", \"sds:AddressLine1\": null, \"sds:City\": null, \"sds:State\": null, \"sds:Country\": null, \"sds:PostalCode\": null, \"sds:Day\": [{\"sds:Date\": \"20231104\", \"sds:SDSID\": \"TJKJH0D6B6TMUYR1UFU0\", \"sds:SDSAvailability\": \"01\", \"sds:MatchLevel\": \"1\"}, {\"sds:Date\": \"20231105\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231106\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231107\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231108\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231109\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231110\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231111\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}]}, {\"sds:CustomerAddressID\": \"T8N\", \"sds:Classification\": \"R\", \"sds:GroupNumber\": \"1\", \"sds:ErrorCode\": \"0\", \"sds:AddressLine1\": null, \"sds:City\": null, \"sds:State\": null, \"sds:Country\": null, \"sds:PostalCode\": null, \"sds:Day\": [{\"sds:Date\": \"20231104\", \"sds:SDSID\": \"TJKJHZB49CWF5DKLFDPQ\", \"sds:SDSAvailability\": \"01\", \"sds:MatchLevel\": \"2\"}, {\"sds:Date\": \"20231105\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231106\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231107\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231108\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231109\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231110\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}, {\"sds:Date\": \"20231111\", \"sds:SDSAvailability\": \"00\", \"sds:MatchLevel\": \"0\"}]}]}"
}

