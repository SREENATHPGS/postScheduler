var http=new XMLHttpRequest();

class ApiCalls	{

	constructor (base_url) {
		this.base_url = base_url;	
	}

	getData(path, header, parameters = [], callbackFunction) {
		http = new XMLHttpRequest();

		let url = this.base_url+path;

		function setHeaders(headers){
			for(let key in headers){
				http.setRequestHeader(key, header[key]) 
			}
		}

		function setParameters(params) {
			for (var i = params.length - 1; i >= 0; i--) {
				url = url+"?"+params[i]
			}
			console.log("url after adding parameters "+path);
		}

		setParameters(parameters);
		http.open("GET", url, true);
		setHeaders(header);
		http.onreadystatechange = function (e) {
			if (this.readyState == 4) {
				if (this.status == 200){
					let response = this.responseText;
					if (callbackFunction){
						callbackFunction(response)
					} else {
						console.log(response);
					}
				} else {
					console.log("Non 200 response code: "+http.status)
					return "failure from server."
				}
			} else {
				console.log("Non success readyState: "+http.readyState)
				return "failure from http.open."
			}
		};
		http.send();

	}

	postData(path, header, parameters, payload, callbackFunction) {
		function setHeaders(headers){
			for(let key in headers){
				http.setRequestHeader(key, header[key]) 
			}
		}

		let url = this.base_url+path;
		http.open("POST", url, true);
		setHeaders(header);
		http.onreadystatechange = function (e) {
			if (this.readyState == 4) {
				if (this.status == 200){
					let response = this.responseText;
					if (callbackFunction){
						callbackFunction(response)
					}
				} else {
					console.log("Non 200 response code: "+http.status)
					return "failure from server."
				}
			} else {
				console.log("Non success readyState: "+http.readyState)
				return "failure from http.open."
			}
		};
		console.log(payload)
		let data = JSON.stringify(payload)
		console.log(data)
		http.send(data);

	}

	patchData(path, header, parameters, payload, callbackFunction) {
		function setHeaders(headers){
			for(let key in headers){
				http.setRequestHeader(key, header[key]) 
			}
		}

		let url = this.base_url+path;
		http.open("PATCH", url, true);
		setHeaders(header);
		http.onreadystatechange = function (e) {
			if (this.readyState == 4) {
				if (this.status == 200){
					let response = this.responseText;
					if (callbackFunction){
						callbackFunction(response)
					}
				} else {
					console.log("Non 200 response code: "+http.status)
					return "failure from server."
				}
			} else {
				console.log("Non success readyState: "+http.readyState)
				return "failure from http.open."
			}
		};
		console.log(payload);
		let data = JSON.stringify(payload);
		console.log(data)
		http.send(data);
	}

	deleteData(path, header, parameters = [], payload = {}, callbackFunction) {
		function setHeaders(headers){
			for(let key in headers){
				http.setRequestHeader(key, header[key]) 
			}
		}

		let url = this.base_url+path;
		http.open("DELETE", url, true);
		setHeaders(header);
		http.onreadystatechange = function (e) {
			if (this.readyState == 4) {
				if (this.status == 200){
					let response = this.responseText;
					if (callbackFunction){
						callbackFunction(response)
					}
				} else {
					console.log("Non 200 response code: "+http.status)
					return "failure from server."
				}
			} else {
				console.log("Non success readyState: "+http.readyState)
				return "failure from http.open."
			}
		};
		console.log(payload)
		let data = JSON.stringify(payload)
		console.log(data)
		http.send(data);
	}

	putData(path, header, parameters, payload) {}

	sendImageToServer(image_payload, header, callbackFunction = undefined) {

		function setHeaders(headers){
			for(let key in headers){
				http.setRequestHeader(key, header[key]) 
			}
		}

		let image = image_payload;
		let url = this.base_url+'/upload-file?_full_path=true';
		let headers = header;
		fetch(image_payload)
		.then(res => res.blob())
		.then(blob => {
			const file = new File([blob], "capture.png", {
				type: 'image/png    '
			});
			var fd = new FormData();
			fd.append("file", file);

			http.open("POST", url, true);
			setHeaders(header);
			http.onreadystatechange = function (e) {
				if (this.readyState == 4) {
					if (this.status == 200){
						let response = this.responseText;
						if (callbackFunction){
							callbackFunction(response)
						} else {
							console.log(response);
						}
					} else {
						console.log("Non 200 response code: "+http.status)
						return "failure from server."
					}
				} else {
					console.log("Non success readyState: "+http.readyState)
					return "failure from http.open."
				}
			};

			http.send(fd);
		});
	}
}
