CREATE extension if not exists aws_s3 CASCADE;
drop schema if exists cta_tracker cascade;
create schema cta_tracker;
create table cta_tracker.dates (
  day date,
  day_of_week text generated always as (
  		case when date_part('dow', day) = 0 then 'Sunday'
			when date_part('dow', day) = 1 then 'Monday'
			when date_part('dow', day) = 2 then 'Tuesday'
			when date_part('dow', day) = 3 then 'Wednesday'
			when date_part('dow', day) = 4 then 'Thursday'
			when date_part('dow', day) = 5 then 'Friday'
			when date_part('dow', day) = 6 then 'Sunday'
	    end) stored
);
insert into cta_tracker.dates
SELECT '1970-01-01'::DATE + SEQUENCE.DAY AS day
FROM GENERATE_SERIES(0, date_part('day', ('2025-01-01'::timestamp - '1970-01-01'::timestamp))::int) AS SEQUENCE (DAY) GROUP BY SEQUENCE.day
order by sequence.day;

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
  shape_id text,
  shape_pt_lat float,
  shape_pt_lon float,
  shape_pt_sequence int,
  shape_dist_traveled float
);
create table cta_tracker.stop_times (
  trip_id text,
  arrival_time interval, -- you'd think this was a time, but the bus leaving at 27 o'clock begs to disagree
  departure_time interval,
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
  route_id text,
  service_id text,
  trip_id text,
  direction_id int,
  block_id bigint,
  shape_id text,
  direction text,
  wheelchair_accessible int,
  schd_trip_id text
);