use serde::{Serialize, Deserialize};
use std::{fs, collections::HashMap};
use std::time::Duration;
use soup::prelude::*;
use chrono::Utc;
use rayon::prelude::*;


#[derive(Debug, Serialize, Deserialize)]
struct Stop {
  id: String,
  name: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Route {
  name: String,
  stops: HashMap<String, Vec<Stop>>
}

fn get_stop_list() -> Vec<Stop> {
  let data = fs::read_to_string("C:/Users/mwham/Documents/repos/cta-tracker/process_data/fill_picklists/bus-stops.json").unwrap();
  let original_data: HashMap<String, Route> = serde_json::from_str(&data).unwrap();
  let ret: Vec<&Stop> = original_data.values().flat_map(|x| {
    let ret: Vec<&Stop> = x.stops.values().flat_map(|x| x).collect();
    return ret;
  }).collect();
  return ret.into_iter().map(|x| Stop{
    id: x.id.to_string(), 
    name: x.name.to_string()
  }).collect();
}

fn get_arrivals(stop_id: &str) -> Vec<HashMap<String, String>>{
  let client = reqwest::blocking::Client::builder().timeout(Duration::from_secs(10)).build().unwrap();
  let response = match client.get(
    format!("http://www.ctabustracker.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop_id}", stop_id=stop_id)
  ).send() {
    Err(_t) => "".to_string(),
    Ok(t) => t.text().unwrap(),
  };
  let soup = Soup::new(&response);
  return soup.tag("stop").find_all().filter(|stop| !(stop.text().contains("No arrival times") || stop.text().contains("No service scheduled"))).map(|stop | {
    let parent = stop.tag("pre").find().unwrap();
    let mut row: HashMap<String, String> = parent.children().skip(1).filter(|x| x.name() != "[text]").map(|x| {
      return (x.name().to_string(), x.text());
    }).collect();
    row.insert("response_at".to_string(), Utc::now().to_rfc3339());
    row.insert("stop_id".to_string(), stop_id.to_string());
    return row;
  }).collect();
}

fn get_stops(v: Vec<Stop>) -> Vec<HashMap<String, String>>{
  return v.par_iter().flat_map(|stop|{
    println!("{:?}", stop);
    return get_arrivals(&stop.id);
  }).collect();
}


fn save_data(stops: Vec<HashMap<String, String>>){
  let dump_str = serde_json::to_string(&stops).unwrap();
  fs::write("test.json", dump_str).unwrap();
}

fn main() {
  let stop_list = get_stop_list();
  let stops = get_stops(stop_list);
  save_data(stops);
}
