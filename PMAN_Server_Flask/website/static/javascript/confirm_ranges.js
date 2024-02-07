let digits = '0123456789'
let lowers = 'abcdefghijklmnopqrstuvwxyz'
let uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

function requireFormFilled(query_str="form"){
	// make sure a form is fully filled out before sending it
	let form = document.querySelector(query_str);
	let required_fields = form.querySelectorAll('input,select');
	let error_fields = [];
	for(field of required_fields){
		if (field.value==""){
		error_fields = error_fields.concat(field);
		}
	}
	if (error_fields.length > 0){
		for(i=0;i<error_fields.length;i++){
			let field = error_fields[i];
			field.classList.add("error");
			field.addEventListener("input",() => {
				field.classList.remove("error")
			});
		}
		alert("Please fill all required fields")
		return true;
	}
	return false;
}

function enforceCharset(input_id, charset=digits){
	// set an event listener to an input and enforce that inputs are only from charset
	let targetInput = document.getElementById(input_id)
	targetInput.addEventListener("input", function() {
		let entered_value = targetInput.value.slice(-1)
		let pre_event_value = targetInput.value.slice(0,-1)
		if(!charset.includes(entered_value)){

			targetInput.value = pre_event_value;

			// special cases for lower/upper stuff
			let upper_case = entered_value.toLocaleUpperCase()
			let lower_case = entered_value.toLocaleLowerCase()
			if(charset.includes(upper_case)){
				targetInput.value += upper_case;
			} else if(charset.includes(lower_case)){
				targetInput.value = lower_case;
			}


		}
	});
}

function enforceLength(input_id, maxlen=1){
	let targetInput = document.getElementById(input_id)
	targetInput.addEventListener("input", function() {
		let pre_event_value = targetInput.value.slice(0,-1)
		if(targetInput.value.length > maxlen){
			targetInput.value = pre_event_value;
			flash(input_id,`Max input length is ${maxlen}`)
		} else {
			flash(input_id,'')
		}
	});
}

function enforceUpper(input_id, maxlen=1){
	let targetInput = document.getElementById(input_id)
	targetInput.addEventListener("input", function() {
		let entered_value = targetInput.value.slice(-1)
		if(lowers.includes(entered_value)){
			targetInput.value = pre_event_value + entered_value.toLocaleUpperCase();
		}
	});
}

function enforceRange(input_id,minval,maxval){
	let targetInput = document.getElementById(input_id)
	targetInput.addEventListener("change", function() {
		let val = parseFloat(targetInput.value);
		if(!isNaN(val)){
			if(val > maxval){
				targetInput.value = maxval;
			} else if (val < minval) {
				targetInput.value = minval;
			}
		}
	});
}

function flash(element_id,message){
	let flash_id = element_id + '-flash';
	let flashzone = document.getElementById(flash_id)
	if(flashzone != null){
	flashzone.innerText=message;
	} else{
		console.log("You're trying to flash a box that doesn't exist:",flash_id)
	}
}



// Special pattern handlers below

function setPortNumEventHandlers(){
for(portNum of document.getElementsByClassName("port-num")){
	setPortNumInputChecker(portNum.id);
}
}

function setPortNumInputChecker(target_id){
	// going by id is necesarry in order to prevent references from targeting final portNum
	let targetInput = document.getElementById(target_id);
	let num_ports = parseInt(JSON.parse(getCookie("active_config"))['valve_positions'])
	targetInput.addEventListener("input", function() {
		let minValue = 1;
		let maxValue = num_ports; 
		if (targetInput.value != ''){
			let parsedValue = parseFloat(targetInput.value);
			if (isNaN(parsedValue)) {
				// Handle non-numeric input
				parsedValue = minValue;
			} else if (parsedValue < minValue) {
				parsedValue = minValue;
			} else if (parsedValue > maxValue) {
				parsedValue = maxValue;
			}
			targetInput.value = parsedValue;
		let enteredValue = targetInput.value.slice(-1)
	        let preEventValue = targetInput.value.slice(0,-1)
	        // prevents keyboard non-digit chars
		// otherwise, something like "12f" would make it through
	        // also prevents decimal points
		if(isNaN(parseFloat(enteredValue)))
			targetInput.value = preEventValue;
		}
	});

}

function setVolumeEventHandlers(){
for(volumeInput of document.getElementsByClassName("volume")){
	setVolumeInputChecker(volumeInput.id)
}
}
function setVolumeInputChecker(target_id){
	let target = document.getElementById(target_id);
	target.addEventListener("input", function() {
		let enteredValue = target.value.slice(-1)
		if (target.value != ''){
			let parsedValue = parseFloat(enteredValue);
			let preEventValue = target.value.slice(0,-1)
			if (isNaN(parsedValue) && enteredValue != '.') {
				// Handle non-numeric input
				target.value = preEventValue
			}
		}

	});
}
