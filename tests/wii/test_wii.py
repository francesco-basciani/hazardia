import unittest
from wii.io import HazardError

class HostAdapterTests(unittest.TestCase):
    def test_adapter_axes_time_and_empty_case(self):
        from wii.propagator import firelab_body,grid_cell
        scenarios=dict(schema='hazardia.wii.scenarios/0.1.0',members=[dict(id='1',state='READY',weight=1,propagation_seed=1,
            origins=[dict(id='i1',point=[13.4,42.3],ignition_at='2026-10-25T01:00:00Z')])])
        body=firelab_body(scenarios,'1',start_at='2026-10-25T00:00:00Z',hours=3,forcing_id='map-weather-'+'a'*24)
        self.assertEqual(body['ignitions'][0]['point'],[42.3,13.4]);self.assertEqual(body['ignitions'][0]['at_minutes'],60)
        grid=dict(crs='EPSG:4326',shape=[10,10],transform=[.1,0,13,0,-.1,43])
        with self.assertRaises(HazardError):grid_cell([12.999,42.9],grid)
