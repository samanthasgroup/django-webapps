from drf_spectacular.openapi import AutoSchema


class TaggedByViewSetNameSchema(AutoSchema):
    def get_tags(self) -> [str]:
        tags = super().get_tags()
        view_set_tag_name = self.view.__class__.__name__.replace("ViewSet", "")
        return tags + [view_set_tag_name]
