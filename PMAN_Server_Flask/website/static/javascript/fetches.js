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
