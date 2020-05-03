import unittest
import sds
import sds.standard
import sds.reducing
import sds.variants
import logging


class TestSDS(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger(__file__)

    def test_agent(self):
        agent = sds.Agent()
        self.assertIsNone(agent.hyp)
        self.assertFalse(agent.active)
        agent = sds.Agent(hyp="hello", active=True)
        self.assertEqual(agent.hyp, "hello")
        self.assertTrue(agent.active)
