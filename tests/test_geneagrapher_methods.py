import os
import sys
import unittest
import StringIO
from geneagrapher import geneagrapher
from geneagrapher.graph import Graph


class TestGeneagrapherMethods(unittest.TestCase):
    """
    Unit tests for the geneagrapher.Geneagrapher class.
    """
    def setUp(self):
        self.ggrapher = geneagrapher.Geneagrapher()

    def test001_init(self):
        # Test constructor.
        self.assertEquals(isinstance(self.ggrapher.graph, Graph), True)
        self.assertEquals(self.ggrapher.seed_ids, [])
        self.assertEquals(self.ggrapher.get_ancestors, False)
        self.assertEquals(self.ggrapher.get_descendants, False)
        self.assertEquals(self.ggrapher.verbose, False)
        self.assertEquals(self.ggrapher.write_filename, None)

    def test002_parse_empty(self):
        # Test parse_input() with no arguments.
        sys.argv = ['geneagrapher']

        # Redirect stderr to capture output.
        stderr = sys.stderr
        stderr_intercept = StringIO.StringIO()
        sys.stderr = stderr_intercept

        expected = """Usage: geneagrapher [options] ID [ID...]

geneagrapher: error: no record IDs given
"""
        try:
            self.ggrapher.parse_input()
        except SystemExit:
            self.assertEquals(stderr_intercept.getvalue().decode('utf-8'),
                              expected)

        sys.stderr = stderr

    def test003_parse_default(self):
        # Test parse_input() with no options.
        sys.argv = ['geneagrapher', '3']
        self.ggrapher.get_ancestors = False
        self.ggrapher.get_descendents = True
        self.ggrapher.write_filename = "filler"
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, False)
        self.assertEquals(self.ggrapher.get_descendants, False)
        self.assertEquals(self.ggrapher.verbose, False)
        self.assertEquals(self.ggrapher.write_filename, None)
        self.assertEquals(self.ggrapher.seed_ids, [3])

    def test004_parse_options(self):
        # Test parse_input() with options.
        sys.argv = ['geneagrapher', '--with-ancestors', '--with-descendants',
                    '--file=filler', '--verbose', '3', '43']
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, True)
        self.assertEquals(self.ggrapher.get_descendants, True)
        self.assertEquals(self.ggrapher.verbose, True)
        self.assertEquals(self.ggrapher.write_filename, "filler")
        self.assertEquals(self.ggrapher.seed_ids, [3, 43])

    def test005_parse_short_options(self):
        # Test parse_input() with short versions of the options.
        sys.argv = ['geneagrapher', '-a', '-d', '-f', 'filler', '-v', '3',
                    '43']
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, True)
        self.assertEquals(self.ggrapher.get_descendants, True)
        self.assertEquals(self.ggrapher.verbose, True)
        self.assertEquals(self.ggrapher.write_filename, "filler")
        self.assertEquals(self.ggrapher.seed_ids, [3, 43])

    def test006_build_graph_only_self(self):
        # Graph building with no ancestors or descendants.
        self.ggrapher.seed_ids.append(127946)
        self.ggrapher.build_graph()
        graph = self.ggrapher.graph
        self.assertEquals(len(graph), 1)
        self.assertTrue(127946 in graph)

        node = graph[127946]
        self.assertEquals(node.ancestors, [137717, 137705])
        self.assertEquals(node.descendants, [144155, 127803])

        record = node.record
        self.assertEquals(record.name, "Christian   Thomasius")
        self.assertEquals(record.institution, None)
        self.assertEquals(record.year, 1672)
        self.assertEquals(record.id, 127946)

    def test007_build_graph_only_self_verbose(self):
        # Graph building with no ancestors or descendants.
        self.ggrapher.verbose = True
        self.ggrapher.seed_ids.append(127946)

        # Redirect stdout to capture output.
        stdout = sys.stdout
        stdout_intercept = StringIO.StringIO()
        sys.stdout = stdout_intercept
        self.ggrapher.build_graph()
        sys.stdout = stdout

        graph = self.ggrapher.graph
        self.assertEquals(len(graph), 1)
        self.assertTrue(127946 in graph)

        node = graph[127946]
        self.assertEquals(node.ancestors, [137717, 137705])
        self.assertEquals(node.descendants, [144155, 127803])

        record = node.record
        self.assertEquals(record.name, "Christian   Thomasius")
        self.assertEquals(record.institution, None)
        self.assertEquals(record.year, 1672)
        self.assertEquals(record.id, 127946)

        self.assertEquals(stdout_intercept.getvalue().decode('utf-8'),
                          u"Grabbing record #127946\n")

    def test008_build_graph_with_ancestors(self):
        # Graph building with ancestors.
        self.ggrapher.seed_ids.append(127946)
        self.ggrapher.get_ancestors = True
        self.ggrapher.build_graph()
        graph = self.ggrapher.graph
        self.assertEquals(len(graph), 4)
        self.assertTrue(127946 in graph)
        self.assertTrue(137717 in graph)
        self.assertTrue(137705 in graph)
        self.assertTrue(143630 in graph)

        node = graph[127946]
        self.assertEquals(node.ancestors, [137717, 137705])
        self.assertEquals(node.descendants, [144155, 127803])

        record = node.record
        self.assertEquals(record.name, "Christian   Thomasius")
        self.assertEquals(record.institution, None)
        self.assertEquals(record.year, 1672)
        self.assertEquals(record.id, 127946)

        node = graph[137717]
        self.assertEquals(node.ancestors, [])
        self.assertEquals(node.descendants, [127946])

        record = node.record
        self.assertEquals(record.name, "Valentin  Alberti")
        self.assertEquals(record.institution, u"Universit\xe4t Leipzig")
        self.assertEquals(record.year, 1678)
        self.assertEquals(record.id, 137717)

        node = graph[137705]
        self.assertEquals(node.ancestors, [143630])
        self.assertEquals(node.descendants, [60985, 21235, 127946])

        record = node.record
        self.assertEquals(record.name, "Jakob  Thomasius")
        self.assertEquals(record.institution, u"Universit\xe4t Leipzig")
        self.assertEquals(record.year, 1643)
        self.assertEquals(record.id, 137705)

        node = graph[143630]
        self.assertEquals(node.ancestors, [])
        self.assertEquals(node.descendants, [137705])

        record = node.record
        self.assertEquals(record.name, "Friedrich  Leibniz")
        self.assertEquals(record.institution, None)
        self.assertEquals(record.year, None)
        self.assertEquals(record.id, 143630)

    def test009_build_graph_with_descendants(self):
        # Graph building with descendants.
        self.ggrapher.seed_ids.append(79568)
        self.ggrapher.get_descendants = True
        self.ggrapher.build_graph()
        graph = self.ggrapher.graph
        self.assertEquals(len(graph), 3)
        self.assertTrue(79568 in graph)
        self.assertTrue(79562 in graph)
        self.assertTrue(99457 in graph)

        node = graph[79568]
        self.assertEquals(node.ancestors, [13301])
        self.assertEquals(node.descendants, [79562, 99457])

        record = node.record
        self.assertEquals(record.name, "Ramdas  Kumaresan")
        self.assertEquals(record.institution, u"University of Rhode Island")
        self.assertEquals(record.year, 1982)
        self.assertEquals(record.id, 79568)

        node = graph[79562]
        self.assertEquals(node.ancestors, [79568])
        self.assertEquals(node.descendants, [])

        record = node.record
        self.assertEquals(record.name, "C. S. Ramalingam")
        self.assertEquals(record.institution, u"University of Rhode Island")
        self.assertEquals(record.year, 1995)
        self.assertEquals(record.id, 79562)

        node = graph[99457]
        self.assertEquals(node.ancestors, [79568])
        self.assertEquals(node.descendants, [])

        record = node.record
        self.assertEquals(record.name, "Yadong  Wang")
        self.assertEquals(record.institution, u"University of Rhode Island")
        self.assertEquals(record.year, 2003)
        self.assertEquals(record.id, 99457)

    def test010_build_graph_bad_id(self):
        # Graph building with a bad ID.
        self.ggrapher.seed_ids.append(79568583832)
        self.assertRaises(ValueError, self.ggrapher.build_graph)

        try:
            self.ggrapher.build_graph()
        except ValueError as e:
            self.assertEquals(str(e), "Invalid id 79568583832")
        else:
            self.fail()

    def test011_end_to_end_self_stdout(self):
        # Complete test getting no ancestors or descendants and writing the
        # result to stdout.
        sys.argv = ['geneagrapher', '30484']
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, False)
        self.assertEquals(self.ggrapher.get_descendants, False)
        self.assertEquals(self.ggrapher.verbose, False)
        self.assertEquals(self.ggrapher.write_filename, None)
        self.assertEquals(self.ggrapher.seed_ids, [30484])

        self.ggrapher.build_graph()

        # Redirect stdout to capture output.
        stdout = sys.stdout
        stdout_intercept = StringIO.StringIO()
        sys.stdout = stdout_intercept
        self.ggrapher.generate_dot_file()
        sys.stdout = stdout

        expected = u"""digraph genealogy {
    graph [charset="utf-8"];
    node [shape=plaintext];
    edge [style=bold];

    30484 [label="Peter Chris Pappas \\nThe Pennsylvania State University \
(1982)"];

}
"""
        self.assertEquals(stdout_intercept.getvalue().decode('utf-8'),
                          expected)

    def test012_end_to_end_ancestors_stdout(self):
        # Complete test getting with ancestors, writing the result to stdout.
        sys.argv = ['geneagrapher', '-a', '127946']
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, True)
        self.assertEquals(self.ggrapher.get_descendants, False)
        self.assertEquals(self.ggrapher.verbose, False)
        self.assertEquals(self.ggrapher.write_filename, None)
        self.assertEquals(self.ggrapher.seed_ids, [127946])

        self.ggrapher.build_graph()

        # Redirect stdout to capture output.
        stdout = sys.stdout
        stdout_intercept = StringIO.StringIO()
        sys.stdout = stdout_intercept
        self.ggrapher.generate_dot_file()
        sys.stdout = stdout

        expected = u"""digraph genealogy {
    graph [charset="utf-8"];
    node [shape=plaintext];
    edge [style=bold];

    127946 [label="Christian   Thomasius \\n(1672)"];
    137717 [label="Valentin  Alberti \\nUniversit\xe4t Leipzig (1678)"];
    137705 [label="Jakob  Thomasius \\nUniversit\xe4t Leipzig (1643)"];
    143630 [label="Friedrich  Leibniz"];

    137717 -> 127946;
    137705 -> 127946;
    143630 -> 137705;
}
"""
        self.assertEquals(stdout_intercept.getvalue().decode('utf-8'),
                          expected)

    def test013_end_to_end_descendants_stdout(self):
        # Complete test getting with descendants, writing the result to stdout.
        sys.argv = ['geneagrapher', '-d', '79568']
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, False)
        self.assertEquals(self.ggrapher.get_descendants, True)
        self.assertEquals(self.ggrapher.verbose, False)
        self.assertEquals(self.ggrapher.write_filename, None)
        self.assertEquals(self.ggrapher.seed_ids, [79568])

        self.ggrapher.build_graph()

        # Redirect stdout to capture output.
        stdout = sys.stdout
        stdout_intercept = StringIO.StringIO()
        sys.stdout = stdout_intercept
        self.ggrapher.generate_dot_file()
        sys.stdout = stdout

        expected = u"""digraph genealogy {
    graph [charset="utf-8"];
    node [shape=plaintext];
    edge [style=bold];

    79568 [label="Ramdas  Kumaresan \\nUniversity of Rhode Island (1982)"];
    79562 [label="C. S. Ramalingam \\nUniversity of Rhode Island (1995)"];
    99457 [label="Yadong  Wang \\nUniversity of Rhode Island (2003)"];

    79568 -> 79562;
    79568 -> 99457;
}
"""
        self.assertEquals(stdout_intercept.getvalue().decode('utf-8'),
                          expected)

    def test014_end_to_end_self_file(self):
        # Complete test getting no ancestors or descendants and writing the
        # result to stdout.
        outfname = 'outfile.test'
        sys.argv = ['geneagrapher', '-f', outfname, '30484']
        self.ggrapher.parse_input()
        self.assertEquals(self.ggrapher.get_ancestors, False)
        self.assertEquals(self.ggrapher.get_descendants, False)
        self.assertEquals(self.ggrapher.verbose, False)
        self.assertEquals(self.ggrapher.write_filename, outfname)
        self.assertEquals(self.ggrapher.seed_ids, [30484])

        self.ggrapher.build_graph()
        self.ggrapher.generate_dot_file()

        expected = u"""digraph genealogy {
    graph [charset="utf-8"];
    node [shape=plaintext];
    edge [style=bold];

    30484 [label="Peter Chris Pappas \\nThe Pennsylvania State University \
(1982)"];

}
"""
        with open(outfname, 'r') as fin:
            self.assertEquals(fin.read().decode('utf-8'), expected)
        os.remove(outfname)

    def test015_end_to_end_through_ggrapher_self_stdout(self):
        # Complete test calling ggrapher getting no ancestors or descendants
        # and writing the result to stdout.
        sys.argv = ['geneagrapher', '30484']

        # Redirect stdout to capture output.
        stdout = sys.stdout
        stdout_intercept = StringIO.StringIO()
        sys.stdout = stdout_intercept
        geneagrapher.ggrapher()
        sys.stdout = stdout

        expected = u"""digraph genealogy {
    graph [charset="utf-8"];
    node [shape=plaintext];
    edge [style=bold];

    30484 [label="Peter Chris Pappas \\nThe Pennsylvania State University \
(1982)"];

}
"""
        self.assertEquals(stdout_intercept.getvalue().decode('utf-8'),
                          expected)

if __name__ == '__main__':
    unittest.main()