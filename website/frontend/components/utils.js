function clamp(a, b, c){
  return Math.min(Math.max(a, b), c);
}
function formatDt(d){
  if(d === undefined){
    return;
  }
  return `${d.getFullYear()}-${d.getMonth().toString().padStart(2, "0")}-${d.getDay().toString().padStart(2, "0")} ${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}:${d.getSeconds().toString().padStart(2, "0")}`;
}
function round(x, k){
  return Math.round(x * 10 ** k) / 10 ** k;
}