import track_buses
import track_trains
import rollups

def main(event, context):
    actions = {
        'bus': track_buses.main,
        'train': track_trains.main,
        'rollup': rollups.main,
    }
    if event['action'] == 'bus':
        track_buses.main()
    else:
        track_trains.main()
