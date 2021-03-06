# Copyright (c) 2017, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import shutil
import unittest
import os
from rdflib import Graph

from fhirtordf.rdfsupport.rdfcompare import rdf_compare
from tests.utils.output_redirector import OutputRedirector
from tests.utils.base_test_case import test_fhir_server, USE_BUILD_SERVER

noargs_text = """usage: fhirtordf [-h] [-i [INFILE [INFILE ...]]] [-id INDIR]
                 [-o [OUTFILE [OUTFILE ...]]] [-od OUTDIR] [-f] [-s] [-v]
                 [-u URIBASE] [-mv METADATAVOC] [-no] [-nn] [-nc] [--nocache]
                 [--fmvcache FMVCACHE] [--maxsize MAXSIZE]
                 [-sd [SKIPDIRS [SKIPDIRS ...]]] [-sf [SKIPFNS [SKIPFNS ...]]]
                 [--format {json-ld,n3,nt,nt11,ntriples,pretty-xml,trig,ttl,turtle,xml}]
fhirtordf: error: Either an input file or an input directory must be supplied
"""

help_text = """usage: fhirtordf [-h] [-i [INFILE [INFILE ...]]] [-id INDIR]
                 [-o [OUTFILE [OUTFILE ...]]] [-od OUTDIR] [-f] [-s] [-v]
                 [-u URIBASE] [-mv METADATAVOC] [-no] [-nn] [-nc] [--nocache]
                 [--fmvcache FMVCACHE] [--maxsize MAXSIZE]
                 [-sd [SKIPDIRS [SKIPDIRS ...]]] [-sf [SKIPFNS [SKIPFNS ...]]]
                 [--format {json-ld,n3,nt,nt11,ntriples,pretty-xml,trig,ttl,turtle,xml}]

Convert FHIR JSON into RDF

optional arguments:
  -h, --help            show this help message and exit
  -i [INFILE [INFILE ...]], --infile [INFILE [INFILE ...]]
                        Input file(s)
  -id INDIR, --indir INDIR
                        Input directory
  -o [OUTFILE [OUTFILE ...]], --outfile [OUTFILE [OUTFILE ...]]
                        Output file(s)
  -od OUTDIR, --outdir OUTDIR
                        Output directory
  -f, --flatten         Flatten output directory
  -s, --stoponerror     Stop on processing error
  -v, --version         Current version number
  -u URIBASE, --uribase URIBASE
                        Base URI for RDF identifiers (default:
                        http://hl7.org/fhir/)
  -mv METADATAVOC, --metadatavoc METADATAVOC
                        FHIR metadata vocabulary (default: /Users/mrf7578/Deve
                        lopment/git/BD2KOnFHIR/fhirtordf/tests/data/fhir_metad
                        ata_vocabulary/fhir.ttl)
  -no, --noontology     Omit owl ontology header
  -nn, --nonarrative    Omit narrative text on output
  -nc, --nocontinuation
                        Don't follow URL continuations
  --nocache             Do not use FMV Cache
  --fmvcache FMVCACHE   Metadata vocabluary cache directory (default:
                        /Users/mrf7578/.cache)
  --maxsize MAXSIZE     Maximum sensible file size in KB. 0 means no size
                        check (default: 800)
  -sd [SKIPDIRS [SKIPDIRS ...]], --skipdirs [SKIPDIRS [SKIPDIRS ...]]
                        Skip directories
  -sf [SKIPFNS [SKIPFNS ...]], --skipfns [SKIPFNS [SKIPFNS ...]]
                        Skip file names containing text
  --format {json-ld,n3,nt,nt11,ntriples,pretty-xml,trig,ttl,turtle,xml}
                        Output format (default: turtle)
"""

save_sample_output = False           # True means create a fres text copy for sample patient


class FHIRToRDFParserTestCase(unittest.TestCase, OutputRedirector):

    def test_no_args(self):
        from fhirtordf.fhirtordf import fhirtordf
        args = ""
        output = self._push_stderr()
        fhirtordf(args.split(), default_exit=False)
        self._pop_stderr()
        self.maxDiff = None
        self.assertEqual(noargs_text, output.getvalue())

    def test_help(self):
        from fhirtordf.fhirtordf import fhirtordf
        args = "-h"
        output = self._push_stdout()
        fhirtordf(args.split(), default_exit=False)
        self._pop_stdout()
        self.maxDiff = None
        print(output.getvalue())
        self.assertEqual(help_text, output.getvalue())

    def bester_tester(self, args: str, test_fname: str):
        from fhirtordf.fhirtordf import fhirtordf
        output = self._push_stdout()
        fhirtordf(args.split(), default_exit=False)
        g2 = Graph()
        g2.parse(data=output.getvalue(), format="turtle")
        self._pop_stdout()
        if save_sample_output:
            with open(test_fname, 'w') as f:
                f.write(output.getvalue())
        g1 = Graph()
        g1.parse(test_fname, format="turtle")
        comp_result = rdf_compare(g1, g2)

        if len(comp_result):
            print(comp_result)
        self.assertTrue(len(comp_result) == 0)
        self.assertFalse(save_sample_output, "save_sample_output is True -- test not applied")

    def test_narrative_text(self):
        test_fname = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..', 'data', 'patient-example-2_nn.ttl')
        if USE_BUILD_SERVER:
            args = "-i {}patient-example-f201-roel.json -nn".format(test_fhir_server)
        else:
            args = "-i {}Patient/f201 -nn".format(test_fhir_server)
        self.bester_tester(args, test_fname)

    def test_sample_patient(self):
        test_fname = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..', 'data', 'patient-example-2.ttl')
        if USE_BUILD_SERVER:
            args = "-i {}patient-example-f201-roel.json".format(test_fhir_server)
        else:
            args = "-i {}Patient/f201".format(test_fhir_server)
        self.bester_tester(args, test_fname)

    def test_version(self):
        from fhirtordf.fhirtordf import fhirtordf
        from fhirtordf import __version__
        output = self._push_stdout()
        fhirtordf(["-v"])
        self._pop_stdout()
        self.assertEqual("FHIR to RDF Conversion Tool -- Version {}".format(__version__), output.getvalue().strip())

    def test_output_directory(self):
        from fhirtordf.fhirtordf import fhirtordf
        output_directory = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data', 'patlist'))
        shutil.rmtree(output_directory, ignore_errors=True)

        fhirtordf("-i http://fhirtest.uhn.ca/baseDstu3/Patient"
                  "?_format=json&gender=male&birthdate=gt2013-01-01 -od {} -nn -nc".format(output_directory).split())
        self.assertTrue(os.path.exists(output_directory))
        self.assertTrue(os.path.exists(os.path.join(output_directory, '_url1.ttl')))
        shutil.rmtree(output_directory)

    @unittest.skip
    def test_big_fhir_convert(self):
        # This is a test of the complete FHIR directory conversion
        from fhirtordf.fhirtordf import fhirtordf

        input_directory = os.path.abspath('/Users/mrf7578/Development/fhir/build/publish')
        output_directory = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data', 'publish'))
        args = '-nc -nn -id {} -od {} -sd /v2/ /v3/ -sf .cs. .vs. .profile. .canonical. .schema. .diff.'.format(input_directory, output_directory)

        fhirtordf(args.split(), default_exit=False)


if __name__ == '__main__':
    unittest.main()
