use serde::{Serialize, Deserialize};
use serde_json::{Result, Value};
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

fn untyped_example() -> Result<()> {
    // Some JSON input data as a &str. Maybe this comes from the user.
    let data = fs::read_to_string("C:/Users/mwham/Documents/repos/cta-tracker/process_data/fill_picklists/bus-stops.json").expect("Something went wrong reading the file");

    let v: HashMap<String, Route> = serde_json::from_str(&data)?;
    println!("{:#?}", v["1"]);
    println!("Please call");

    Ok(())
}

fn main() {
  untyped_example().unwrap();
  println!("Please call2");
}
