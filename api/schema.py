from drf_spectacular.openapi import AutoSchema


class TaggedByViewSetNameSchema(AutoSchema):
    """
    Default schema uses same tag (from url) for all endpoints.
    To make it more clear, we use viewset name as additional tag.
    """

    def get_tags(self) -> list[str]:
        tags = super().get_tags()
        view_set_tag_name = self.view.__class__.__name__.replace("ViewSet", "")
        return tags + [view_set_tag_name]
