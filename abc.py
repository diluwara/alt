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
