import track_buses
import track_trains
import cleaning.rollups
import cleaning.bus_tracker

def main(event, context):
    print(event)
    actions = {
        'bus': track_buses.main,
        'train': track_trains.main,
        'rollup': cleaning.rollups.main,
        'clean-bus': cleaning.bus_tracker.main,
    }
    actions[event['action']]()
