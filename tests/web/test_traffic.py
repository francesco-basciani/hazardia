import unittest,tempfile,json
from pathlib import Path
from hazardia.web.traffic import DEFAULT,validate,graph_from_xml,Traffic
class TrafficTest(unittest.TestCase):
 def config(self):return json.loads(json.dumps(DEFAULT))
 def test_limits(self):
  for key,value in [('seed',-1),('max_vehicles',401),('density',201),('bounds',[0,0,1,1]),('max_vehicles',True)]:
   c=self.config();c[key]=value
   with self.assertRaises(Exception):validate(c)
 def xml(self,tag='',relation=''):
  return ('<osm><node id="1" lon="13.38" lat="42.35"/><node id="2" lon="13.381" lat="42.35"/><node id="3" lon="13.382" lat="42.35"/><way id="10"><nd ref="1"/><nd ref="2"/><nd ref="3"/><tag k="highway" v="residential"/>'+tag+'</way>'+relation+'</osm>').encode()
 def graph(self,tag='',relation=''):return graph_from_xml(self.xml(tag,relation),DEFAULT['bounds'])
 def test_oneway(self):
  g=self.graph('<tag k="oneway" v="yes"/>');self.assertEqual([(e['u'],e['v']) for e in g['edges']],[('1','2'),('2','3')])
 def test_reverse(self):self.assertEqual([(e['u'],e['v']) for e in self.graph('<tag k="oneway" v="-1"/>')['edges']],[('2','1'),('3','2')])
 def test_missing_explicit(self):
  g=self.graph();self.assertEqual(len(g['edges']),4);self.assertEqual(g['counts']['missing_oneway'],1);self.assertTrue(all(e['direction_assumed'] for e in g['edges']))
 def test_restricted(self):
  for tag in ['<tag k="access" v="private"/>','<tag k="access:conditional" v="yes @ (Mo-Fr)"/>','<tag k="oneway" v="reversible"/>','<tag k="motor_vehicle:forward" v="no"/>']:
   self.assertEqual(self.graph(tag)['edges'],[])
 def test_relation_conservative(self):self.assertFalse(self.graph(relation='<relation id="50"><member type="way" ref="10" role="from"/><tag k="type" v="restriction"/></relation>')['edges'])
 def test_incomplete(self):self.assertTrue(graph_from_xml(self.xml().replace(b'ref="3"',b'ref="9"'),DEFAULT['bounds'])['counts']['incomplete_ways'])
 def test_roundabout(self):self.assertEqual(len(self.graph('<tag k="junction" v="roundabout"/>')['edges']),2)
 def test_bounds(self):self.assertFalse(graph_from_xml(self.xml(),[13.0,42.0,13.01,42.01])['edges'])
 def test_persistence_and_off(self):
  with tempfile.TemporaryDirectory() as root:
   t=Traffic(root);c=self.config();c['closures']=['10'];self.assertEqual(t.snapshot()['status'],'IDLE');t.save(c);self.assertEqual(Traffic(root).config(),c)
 def test_barrier(self):
  raw=self.xml().replace(b'<node id="2" lon="13.381" lat="42.35"/>',b'<node id="2" lon="13.381" lat="42.35"><tag k="barrier" v="bollard"/></node>')
  self.assertFalse(graph_from_xml(raw,DEFAULT['bounds'])['edges'])
 def test_road_access_override(self):self.assertTrue(self.graph('<tag k="access" v="no"/><tag k="motorcar" v="yes"/>')['edges'])
if __name__=='__main__':unittest.main()
