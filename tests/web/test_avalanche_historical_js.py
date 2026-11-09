import unittest,re,json
from pathlib import Path
import quickjs
BASE=Path(__file__).resolve().parents[2]/'src/hazardia/web/static'
class HistoricalTests(unittest.TestCase):
 def setUp(self):self.js=quickjs.Context();self.js.eval((BASE/'avalanche-historical.js').read_text().replace('export ',''))
 def test_site_not_event(self):self.assertEqual(self.js.eval('historyKind({record_kind:"POTENTIAL_SITE"})'),'site')
 def test_footprint_and_point_both_event_representations(self):self.assertEqual(self.js.eval('historyKind({record_kind:"EVENT_FOOTPRINT"})'),'event')
 def test_year_precision(self):self.assertEqual(self.js.eval('historyDate({date_precision:"YEAR",event_date:"2020"})'),'Anno 2020')
 def test_missing_date_not_current(self):self.assertIn('non disponibile',self.js.eval('historyDate({})'))
 def test_sar_no_product_is_unknown(self):self.assertIn('sconosciuta',self.js.eval('sarMessage({status:"NO_PRODUCT"})'))
 def test_sar_zero_is_not_absence(self):self.assertIn('non significa assenza',self.js.eval('sarMessage({status:"CLASSIFICATION_AND_QA_ARCHIVED",statistics:{wet_snow_good_qa_pixels:0}})'))
 def test_sar_dated_is_historical(self):self.assertIn('Dato storico',self.js.eval('sarMessage({status:"CLASSIFICATION_AND_QA_ARCHIVED",stale:true,statistics:{wet_snow_good_qa_pixels:5}})'))

 def test_sar_becomes_stale_without_new_download(self):
  self.assertTrue(self.js.eval('sarStale({observed_at:"2026-11-01T00:00Z"},Date.parse("2026-11-05T00:00Z"))'));self.assertFalse(self.js.eval('sarStale({observed_at:"2026-11-04T00:00Z"},Date.parse("2026-11-05T00:00Z"))'))
