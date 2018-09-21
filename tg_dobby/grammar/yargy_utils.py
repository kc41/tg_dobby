from yargy.interpretation import fact
from yargy.interpretation.fact import Fact


# TODO CONSIDER: research ability to use directly with Fact class with backward compatibility saving
class FactDefinitionMeta(type):
    BASE_FACT_DEFINITION_CLS = None

    def __new__(mcs, typename, base_classes, class_attr):
        if class_attr.get('_ROOT_FACT_DEFINITION', False):
            # Checking for attempt to redeclare base definition class
            if mcs.BASE_FACT_DEFINITION_CLS is not None:
                raise TypeError(f"Attempt to redeclare base fact definition class "
                                f"'{mcs.BASE_FACT_DEFINITION_CLS.__name__}' by '{typename}'")

            # Saving root class to metaclass attributes
            mcs.BASE_FACT_DEFINITION_CLS = super().__new__(mcs, typename, base_classes, class_attr)
            return mcs.BASE_FACT_DEFINITION_CLS

        # TODO CONSIDER: research ability of mixins support
        # TODO CONSIDER: research ability of transitive inheritance from base class
        if base_classes != (mcs.BASE_FACT_DEFINITION_CLS,):
            raise TypeError(f"Class {typename} must be inherited directly from FactDefinition only."
                            f" Mixins and transitive inheritance are not currently supported")

        annotations = class_attr.get("__annotations__")

        if not annotations:
            raise TypeError(f"No annotations declared in fact definition class '{typename}'")

        generated_fact_cls = fact(f"{type}AutoGen", list(annotations))

        new_base_classes = (generated_fact_cls,)

        return super().__new__(mcs, typename, new_base_classes, class_attr)


class FactDefinition(Fact, metaclass=FactDefinitionMeta):
    _ROOT_FACT_DEFINITION = True
