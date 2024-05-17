function save_text_input(element) {
  let stored_val = localStorage.getItem(element.id)
  if(stored_val){
	  element.value = stored_val;
  }
  element.addEventListener("change", () => {
    localStorage.setItem(element.id, element.value);
  });
}
