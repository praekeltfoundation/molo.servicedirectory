from collections import OrderedDict

from haystack.signals import RealtimeSignalProcessor


# Ref: http://stackoverflow.com/a/31642337
class BatchingSignalProcessor(RealtimeSignalProcessor):
    """
    RealtimeSignalProcessor connects to Django model signals.
    We store them locally for processing later - must call
    ``flush_changes`` from somewhere else (eg: middleware).
    """

    # Haystack instantiates this as a singleton

    _change_list = OrderedDict()

    def _add_change(self, method, sender, instance):
        key = (sender, instance.pk)
        if key in self._change_list:
            del self._change_list[key]
        self._change_list[key] = (method, instance)

    def handle_save(self, sender, instance, created, raw, **kwargs):
        method = super(BatchingSignalProcessor, self).handle_save
        self._add_change(method, sender, instance)

    def handle_delete(self, sender, instance, **kwargs):
        method = super(BatchingSignalProcessor, self).handle_delete
        self._add_change(method, sender, instance)

    def flush_changes(self):
        while True:
            try:
                (sender, pk), (method, instance) = self._change_list.popitem(
                    last=False
                )
            except KeyError:
                break
            else:
                method(sender, instance)
