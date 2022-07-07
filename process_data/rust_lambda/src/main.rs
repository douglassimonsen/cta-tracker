use serde::{Serialize, Deserialize};
use std::{fs, collections::HashMap};


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

fn main() {
  get_stop_list();
}
