def sds_call(addresses,ups_api_endpoint,username,password,license_number,timeout):
	if ups_api_endpoint == "sim":
		return {"addrs":addresses}
	try:
		headers = {"content-type": "text/xml"}
		response_dict = None

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
 "{\"sds\": \"http://www.ups.com/XMLSchema/XOLTWS/SDS/v1.0\", \"Response\": {\"common\": \"http://www.ups.com/XMLSchema/XOLTWS/Common/v1.0\", \"ResponseStatus\": {\"Code\": \"1\", \"Description\": \"Success\"}, \"TransactionReference\": {\"CustomerContext\": \"Inbound- Success\", \"TransactionIdentifier\": \"dssyncs56c37hF4GnK6Mlz\"}}, \"Address\": [{\"CustomerAddressID\": \"T8N\", \"Classification\": \"R\", \"GroupNumber\": \"0\", \"ErrorCode\": \"0\", \"AddressLine1\": null, \"City\": null, \"State\": null, \"Country\": null, \"PostalCode\": null, \"Day\": [{\"Date\": \"20231104\", \"SDSID\": \"RPLTHS1S1I2PO9XR14J4\", \"SDSAvailability\": \"01\", \"MatchLevel\": \"1\"}, {\"Date\": \"20231105\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231106\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231107\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231108\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231109\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231110\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231111\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}]}, {\"CustomerAddressID\": \"T8N\", \"Classification\": \"R\", \"GroupNumber\": \"1\", \"ErrorCode\": \"0\", \"AddressLine1\": null, \"City\": null, \"State\": null, \"Country\": null, \"PostalCode\": null, \"Day\": [{\"Date\": \"20231104\", \"SDSID\": \"RPLTHH1EH1XLIAJ56Z8D\", \"SDSAvailability\": \"01\", \"MatchLevel\": \"2\"}, {\"Date\": \"20231105\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231106\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231107\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231108\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231109\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231110\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}, {\"Date\": \"20231111\", \"SDSAvailability\": \"00\", \"MatchLevel\": \"0\"}]}]}"
}
def clean_response(response_dict):
    # This function will be used to clean the namespaces and structure the response dictionary.
    clean_dict = {}
    
    # Recursively clean the dictionary.
    def clean(d):
        if isinstance(d, dict):
            new_dict = {}
            for k, v in d.items():
                # Remove namespace prefixes (e.g. 'sds:', 'common:')
                key = k.split(':')[-1]
                value = clean(v)
                new_dict[key] = value
            return new_dict
        elif isinstance(d, list):
            return [clean(v) for v in d]
        else:
            return d
    
    # Start cleaning with the root element, which is typically 'Response' or similar.
    if 'Response' in response_dict:
        clean_dict = clean(response_dict['Response'])
    else:
        # Adjust this line to match the actual root element of your response
        clean_dict = clean(response_dict)
    
    return clean_dict

