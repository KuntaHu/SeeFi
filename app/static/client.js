var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest(); // Update a web page without reloading the page
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true); // initializes a newly-created request, or re-initializes an existing one.
  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {  //function called when an XMLHttpRequest transaction completes successfully.(found data in xhr.response)
    console.log('e:', e);
    if (this.readyState === 4) {
      var response = JSON.parse(e.target.responseText);
      // el("result-label").innerHTML = `Result = ${response["result"]}`; // 显示结果部分
      el('image-generated').src = response['result'];
      el('image-generated').className = '';

    }
    el("analyze-button").innerHTML = "Analyze";
  };

  var fileData = new FormData();  // 通过FormData将文件转成二进制数据
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}


