from django.db.models import Model
from model_bakery.baker import Baker
from model_bakery.recipe import related


class CallableM2MBaker(Baker):
    """Baker that allows callable values for m2m fields."""

    def _handle_m2m(self, instance: Model) -> None:
        """
        Patching original behaviour - if m2m field value is callable, call it and use the result.
        """
        for key, values in self.m2m_dict.items():
            if callable(values):
                called_values = values()
                if isinstance(called_values, related):
                    # If the callable returns a related object, we need to use it as a recipe
                    self.m2m_dict[key] = called_values.make()
                else:
                    self.m2m_dict[key] = called_values
        super()._handle_m2m(instance)
