drop schema if exists cta_tracker cascade;
create schema cta_tracker;
create table cta_tracker.calendar (
  service_id text,
  monday boolean,
  tuesday boolean,
  wednesday boolean,
  thursday boolean,
  friday boolean,
  saturday boolean,
  sunday boolean,
  start_date date,
  end_date date
);
create table cta_tracker.calendar_dates (
  service_id text,
  "date" date,
  exception_type int
);
create table cta_tracker.routes (
  route_id text,
  route_short_name text,
  route_long_name text,
  route_type int,
  route_url text,
  route_color text,
  route_text_color text
);
create table cta_tracker.shapes (
  shape_id int,
  shape_pt_lat float,
  shape_pt_lon float,
  shape_pt_sequence int,
  shape_dist_traveled int
);
create table cta_tracker.stop_times (
  trip_id int,
  arrival_time time,
  departure_time time,
  stop_id int,
  stop_sequence int,
  stop_headsign text,
  pickup_type int,
  shape_dist_traveled int
);
create table cta_tracker.stops (
  stop_id int,
  stop_code int,
  stop_name text,
  stop_desc text,
  stop_lat float,
  stop_lon float,
  location_type text,
  parent_station int,
  wheelchair_boarding int
);
create table cta_tracker.trips (
  route_id int,
  service_id text,
  trip_id int,
  direction_id int,
  block_id int,
  shape_id int,
  direction text,
  wheelchair_accessible int,
  schd_trip_id int
);