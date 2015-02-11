from extraction.runnables import Extractor, RunnableError, ExtractorResult
import interfaces
import defusedxml.ElementTree as safeET
import xml.etree.ElementTree as ET
import xml.sax.saxutils as xmlutils
import requests
import re

GROBID_HOST = 'http://localhost:8080'

class GrobidPlainTextExtractor(interfaces.PlainTextExtractor):
   def extract(self, data, dep_results):

      url = '{0}/processFulltextDocument'.format(GROBID_HOST)
      files = {'input': data}
      vars = {}

      try:
         resp = requests.post(url, files=files, data=vars)
      except requests.exceptions.RequestException as ex:
         raise RunnableError('Request to Grobid server failed')

      if resp.status_code != 200:
         raise RunnableError('Grobid returned status {0} instead of 200\nPossible Error:\n{1}'.format(resp.status_code, resp.text))

      xml_text = resp.text

      # grobid returns TEI xml file
      # we will 'convert' it to plain text be removing all xml tags
      remove_tags = re.compile(r'\s*<.*?>', re.DOTALL | re.UNICODE)
      plain_text = remove_tags.sub('\n', xml_text)
      # run this twice for weird situations where things are double escaped
      plain_text = xmlutils.unescape(plain_text, {'&apos;': "'", '&quot;': '"'})
      plain_text = xmlutils.unescape(plain_text, {'&apos;': "'", '&quot;': '"'})

      # create xml result file that just points towards file of plain text
      root=ET.Element('file')
      root.text = 'plain_text.txt'

      plain_text = plain_text.encode('utf-8')
      files = {'plain_text.txt': plain_text}

      return ExtractorResult(xml_result=root, files=files)

