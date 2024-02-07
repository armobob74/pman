let respcon = document.getElementById("response-container");
function display(s) {
  let span = document.createElement("span");
  span.textContent = s;
  respcon.appendChild(span);
}

async function fetchPOST(endpoint, data) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.text();
}

async function listen() {
  // listen until the end of the command buffer
  let data = {
    args: [],
  };
  if(await bufferIsEmpty()){
    return '' //nothing to listen for
  }
  let response = await fetchPOST("/pman/listen", data);
  while(! await bufferIsEmpty()){
    response = await fetchPOST("/pman/listen", data);
  }
  return response
}

async function transfer(from_port, to_port, volume) {
  const args = [from_port, to_port, volume];
  const data = { args: args };
  const first_response = await fetchPOST("/pman/transfer", data);
  const final_response = await listen();
  return final_response;
}

async function sendCustomCommand(cmdstr) {
  // send command and return first response
  // if second response is expected, use the listen() function
  const args = [cmdstr];
  const first_response = await fetchPOST("/pman/custom-cmd", { args: args });
  return first_response;
}
async function oneResponseCommand(cmdstr) {
  const response = await sendCustomCommand(cmdstr);
  display("Response:" + response);
}
async function twoResponseCommand(cmdstr) {
  const response = await sendCustomCommand(cmdstr);
  console.log("Response 1:", response);
  const response_2 = await listen();
  console.log("Response 2:", response_2);
}

async function bufferIsEmpty(){
	return parseInt(await fetchPOST("/pman/buffer-is-empty"))
}

const example_data = { args: [0, 1, 120] };
