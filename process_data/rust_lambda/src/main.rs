use serde::{Serialize, Deserialize};
use std::{fs, collections::HashMap};
use soup::prelude::*;
use chrono::{Utc, Timelike, Duration};
use rayon::prelude::*;
use s3::bucket::Bucket;
use s3::creds::Credentials;
use tokio;
use std::io::prelude::*;
use bzip2::Compression;
use bzip2::read::{BzEncoder, BzDecoder};


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
  }).take(20).collect();
}

fn get_arrivals(stop_id: &str) -> Vec<HashMap<String, String>>{
  let client = reqwest::blocking::Client::builder().timeout(Duration::seconds(10).to_std().unwrap()).build().unwrap();
  let response = match client.get(
    format!("http://www.ctabustracker.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop_id}", stop_id=stop_id)
  ).send() {
    Err(_t) => "".to_string(),
    Ok(t) => t.text().unwrap(),
  };
  let soup = Soup::new(&response);
  return soup.tag("stop").find_all().filter(|stop| !(stop.text().contains("No arrival times") || stop.text().contains("No service scheduled"))).map(|stop | {
    let parent = match stop.tag("pre").find() {
      Some(t) => t,
      None => return HashMap::new(),  // there's nothing of value here
    };
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


async fn save_data(stops: Vec<HashMap<String, String>>){
  let dump_str = serde_json::to_string(&stops).unwrap();
  let dump_bytes = dump_str.as_bytes();
  let mut compressor = BzEncoder::new(dump_bytes, Compression::best());
  let mut contents = vec![0; dump_bytes.len()];
  compressor.read_to_end(&mut contents).unwrap();

  let bucket = Bucket::new(
    "cta-bus-and-train-tracker", 
    "us-east-1".parse().unwrap(), 
    Credentials::default().unwrap()
  ).unwrap();
  let chunk_timestamp = Utc::now();
  let chunk_timestamp_str = (chunk_timestamp - Duration::seconds((
    (chunk_timestamp.minute() % 5) * 60 + chunk_timestamp.second()
  ) as i64)).format("%Y-%m-%d/%H-%M-%S");
  bucket.put_object(
    format!("bustracker-test/{chunk_timestamp}.bz2", chunk_timestamp=chunk_timestamp_str), 
    contents.as_slice(),
  ).await.unwrap();
}

#[tokio::main]
async fn main() {
  let stop_list = get_stop_list();
  let stops = get_stops(stop_list);
  save_data(stops).await;
}
