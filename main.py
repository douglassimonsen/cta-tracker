import track_buses
import track_trains
import rollups

def main(event, context):
    print(event)
    actions = {
        'bus': track_buses.main,
        'train': track_trains.main,
        'rollup': rollups.main,
    }
    actions[event['action']]()
