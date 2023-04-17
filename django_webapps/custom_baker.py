from django.db.models import Model
from model_bakery.baker import Baker


class CallableM2MBaker(Baker):
    """Baker that allows callable values for m2m fields."""

    def _handle_m2m(self, instance: Model) -> None:
        """
        Patching original behaviour - if m2m field value is callable, call it and use the result.
        """
        for key, values in self.m2m_dict.items():
            if callable(values):
                self.m2m_dict[key] = values()
        super()._handle_m2m(instance)
