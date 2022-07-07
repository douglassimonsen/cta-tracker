use serde::{Serialize, Deserialize};
use std::{fs, collections::HashMap};
use std::time::Duration;
use soup::prelude::*;


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

fn get_stop_list() -> HashMap<String, Route> {
    // Some JSON input data as a &str. Maybe this comes from the user.
    let data = fs::read_to_string("C:/Users/mwham/Documents/repos/cta-tracker/process_data/fill_picklists/bus-stops.json").unwrap();
    return serde_json::from_str(&data).unwrap();
}

fn get_stops(v: HashMap<String, Route>){
  for (key, val) in v.into_iter() {
    for (name, stops) in val.stops.into_iter() {

    }
  }
}
fn get_arrivals(stop_id: &str){
  let client = reqwest::blocking::Client::builder().timeout(Duration::from_secs(10)).build().unwrap();
  let response = client.get(
    format!("http://www.ctabustracker.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop_id}", stop_id=stop_id)
  ).send().unwrap().text().unwrap();
  let soup = Soup::new(&response);
  for stop in soup.tag("stop").find_all().into_iter() {
    println!("{}", stop.text());
  }
}

fn main() {
  get_stop_list();
  get_arrivals("5981");
}
