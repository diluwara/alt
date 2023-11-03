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
