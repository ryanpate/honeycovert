"""Regression tests for the conversion endpoints.

Run with: python -m unittest test_app
"""
import io
import os
import tempfile
import unittest
from unittest import mock

from PIL import Image

import app as app_module


def make_heic():
    buf = io.BytesIO()
    Image.new('RGB', (64, 48), (200, 120, 40)).save(buf, format='HEIF')
    return buf.getvalue()


class ConvertTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app_module.app.config['UPLOAD_FOLDER'] = self.tmp.name
        self.client = app_module.app.test_client()
        self.heic = make_heic()

    def tearDown(self):
        self.tmp.cleanup()

    def upload(self, names, **form):
        data = dict(form)
        data['files[]'] = [(io.BytesIO(self.heic), n) for n in names]
        return self.client.post('/convert', data=data, content_type='multipart/form-data')

    def test_single_file_converts_and_leaves_nothing_on_disk(self):
        resp = self.upload(['photo.heic'], format='jpeg')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'image/jpeg')
        Image.open(io.BytesIO(resp.data)).verify()
        resp.close()
        self.assertEqual(os.listdir(self.tmp.name), [])

    def test_batch_returns_zip_and_leaves_nothing_on_disk(self):
        resp = self.upload(['a.heic', 'b.HEIC'], format='png')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/zip')
        resp.close()
        self.assertEqual(os.listdir(self.tmp.name), [])

    def test_failed_conversion_leaves_nothing_on_disk(self):
        resp = self.client.post('/convert', data={
            'files[]': [(io.BytesIO(b'not an image'), 'broken.heic')],
        }, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(os.listdir(self.tmp.name), [])

    def test_non_numeric_options_fall_back_to_defaults(self):
        resp = self.upload(['photo.heic'], size='abc', quality='x', rotate='y')
        self.assertEqual(resp.status_code, 200)
        resp.close()

    def test_api_non_numeric_options_fall_back_to_defaults(self):
        resp = self.client.post('/api/convert', data={
            'file': (io.BytesIO(self.heic), 'photo.heic'), 'size': 'abc',
        }, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 200)
        resp.close()

    def test_oversized_image_is_refused_with_clear_message(self):
        with mock.patch.object(app_module, 'MAX_PIXELS', 1000):
            for resp in [
                self.upload(['photo.heic']),
                self.client.post('/api/convert', data={
                    'file': (io.BytesIO(self.heic), 'photo.heic'),
                }, content_type='multipart/form-data'),
            ]:
                self.assertEqual(resp.status_code, 400)
                self.assertIn('too large', resp.get_json()['error'])
        self.assertEqual(os.listdir(self.tmp.name), [])

    def test_cleanup_endpoint_is_gone(self):
        self.assertIn(self.client.post('/cleanup').status_code, (404, 405))


class ConvertUrlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app_module.app.config['UPLOAD_FOLDER'] = self.tmp.name
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_internal_addresses_are_refused_without_fetching(self):
        for url in ['http://127.0.0.1/a.heic', 'http://localhost/a.heic',
                    'http://169.254.169.254/a.heic', 'http://10.0.0.5/a.heic',
                    'http://[::1]/a.heic']:
            with mock.patch.object(app_module.requests, 'get') as get:
                resp = self.client.post('/convert-url', json={'url': url})
                self.assertEqual(resp.status_code, 400, url)
                get.assert_not_called()

    def test_redirect_to_internal_address_is_refused(self):
        redirect = mock.Mock(status_code=302, is_redirect=True,
                             headers={'location': 'http://127.0.0.1/a.heic'})
        with mock.patch.object(app_module, 'is_public_host', side_effect=lambda h: h == 'example.com'), \
             mock.patch.object(app_module.requests, 'get', return_value=redirect) as get:
            resp = self.client.post('/convert-url', json={'url': 'http://example.com/a.heic'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(get.call_count, 1)

    def test_oversized_download_without_content_length_is_refused(self):
        big = mock.Mock(status_code=200, is_redirect=False, headers={})
        big.iter_content.return_value = (b'x' * (1024 * 1024) for _ in range(60))
        with mock.patch.object(app_module, 'is_public_host', return_value=True), \
             mock.patch.object(app_module.requests, 'get', return_value=big):
            resp = self.client.post('/convert-url', json={'url': 'http://example.com/a.heic'})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('too large', resp.get_json()['error'])

    def test_non_numeric_options_do_not_crash(self):
        with mock.patch.object(app_module, 'is_public_host', return_value=False):
            resp = self.client.post('/convert-url', json={
                'url': 'http://example.com/a.heic', 'size': 'abc'})
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    unittest.main()
