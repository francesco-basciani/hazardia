import json,unittest
from pathlib import Path
import quickjs
class RadarHistoryUITests(unittest.TestCase):
 def setUp(self):
  self.js=quickjs.Context();self.js.eval((Path(__file__).resolve().parents[2]/'src/hazardia/web/static/avalanche-radar-history.js').read_text().replace('export ',''));self.p=dict(schema='hazardia.avalanche.RadarHistoryStatus/1.0',product='SRT1',units='mm',frames=1,recent=[],status='UP_TO_DATE',last_end='2026-11-02T13:00:00Z',missing_hours=[])
 def summary(self,now='2026-11-02T13:30:00Z'):return json.loads(self.js.eval('JSON.stringify(radarHistorySummary('+json.dumps(self.p)+',Date.parse('+json.dumps(now)+')))'))
 def test_fresh_local_history(self):self.assertFalse(self.summary()['stale']);self.assertEqual(self.summary()['frames'],1)
 def test_stale_history_does_not_become_fresh_after_page_open(self):self.assertTrue(self.summary('2026-11-02T16:00:00Z')['stale'])
 def test_future_time_is_invalid(self):self.assertTrue(self.summary('2026-11-02T12:00:00Z')['stale'])
 def test_wrong_units_never_become_snow_cm(self):
  self.p['units']='cm'
  with self.assertRaises(quickjs.JSException):self.summary()
 def test_gaps_are_not_zero_observations(self):self.p['missing_hours']=['2026-11-02T12:00:00Z'];self.assertEqual(self.summary()['missingHours'],1)
