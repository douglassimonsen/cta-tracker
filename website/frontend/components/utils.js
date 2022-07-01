const endpoint = axios.create({})
function clamp(a, b, c){
  return Math.min(Math.max(a, b), c);
}
function formatDt(d){
  if(!d){
    return;
  }
  return `${d.getFullYear()}-${d.getMonth().toString().padStart(2, "0")}-${d.getDay().toString().padStart(2, "0")} ${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}:${d.getSeconds().toString().padStart(2, "0")}`;
}
function formatDate(dt){
  if(!dt){
    dt = new Date();
  }
  let year = dt.getFullYear().toString().padStart(2, '0')
  let month = (new Date().getMonth() % 12 + 1).toString().padStart(2, '0');
  let day = dt.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`;
}
function round(x, k){
  return Math.round(x * 10 ** k) / 10 ** k;
}
function toCSV(data, columns){
  if(columns === undefined){
    columns = Object.keys(data[0]);
  }
  const CONTROL_CHARS = ["\\", "\""]; // "\" needs to come first
  data = data.map(row => {
    row = columns.map(k => {
    let val = row[k].toString();
      let needQuotes = val.includes(",");
      for(let i=0;i<CONTROL_CHARS.length;i++){
        if(val.includes(CONTROL_CHARS[i])){
          val = val.replace(CONTROL_CHARS[i], "\\" + CONTROL_CHARS[i]);
          needQuotes = true;
        }
      }
      if(needQuotes){
        return `"${val}"`;
      } else{
        return val;
      }

    });
    return row.join(",");
  });
  data.unshift(columns.join(","));
  data = data.join("\r\n");
  saveData('test.csv', data);
}
function saveData(filePath, data){
  var a = document.createElement("a");
  a.href = window.URL.createObjectURL(new Blob([data], {type: "text/csv"}));
  a.download = "demo.csv";
  a.click();
}