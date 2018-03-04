import mock


class MockTestCaseMixin(object):

    def __init__(self, *args, **kwargs):
        self._mocks = {}

        super(MockTestCaseMixin, self).__init__(*args, **kwargs)

    def setup_mock(self, target, autospec=True, **kwargs):
        if target in self._mocks:
            raise Exception('Target %s already patched', target)

        self._mocks[target] = mock.patch(target, autospec=autospec, **kwargs)

        return self._mocks[target].start()

    def tearDown(self):
        for mock in self._mocks.values():
            mock.stop()

        return super(MockTestCaseMixin, self).tearDown()
