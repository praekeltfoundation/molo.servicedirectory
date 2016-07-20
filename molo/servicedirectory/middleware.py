import warnings
from haystack import signal_processor


# Ref: http://stackoverflow.com/a/31642337
class HaystackBatchFlushMiddleware(object):
    """
    For use with our BatchingSignalProcessor.

    This should be placed *at the top* of MIDDLEWARE_CLASSES
    (so that it runs last).
    """
    def process_response(self, request, response):
        try:
            signal_processor.flush_changes()
        except AttributeError:
            # in case we're not using our expected signal_processor
            warnings.warn('HaystackBatchFlushMiddleware is being used with an'
                          'unexpected HAYSTACK_SIGNAL_PROCESSOR. The expected'
                          'signal processor is BatchingSignalProcessor. You'
                          'should remove this middleware if the'
                          'BatchingSignalProcessor is no longer needed.')
        return response
