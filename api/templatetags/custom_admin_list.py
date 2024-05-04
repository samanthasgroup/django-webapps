from django.contrib.admin.templatetags.admin_list import ResultList
from django.contrib.admin.templatetags.admin_list import result_list as r_list
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.contrib.admin.views.main import ChangeList
from django.forms import BoundField
from django.template.base import Parser, Template, Token
from django.template.context import Context
from django.template.library import Library
from django.utils.safestring import SafeString

register = Library()


class CustomInclusionAdminNode(InclusionAdminNode):

    def render(self, context: Context) -> SafeString:
        opts = context["opts"]
        app_label = opts.app_label.lower()
        object_name = opts.object_name.lower()

        templ = "templates/admin"
        context_template: Template | None = context.template

        if isinstance(context_template, Template):
            context.render_context[self] = context_template.engine.select_template(
                [
                    f"{templ}/{app_label}/{object_name}/{self.template_name}",
                    f"{templ}/{app_label}/{self.template_name}",
                    f"{templ}/{self.template_name}",
                ]
            )

        return super().render(context)


def get_urls(cl: ChangeList) -> list[str]:
    urls = []
    for i in cl.queryset:
        url = cl.url_for_result(i)
        urls.append(url)

    return urls


def result_list(
    cl: ChangeList,
) -> dict[
    str, list[dict[str, int | str | None]] | list[ResultList] | list[BoundField] | ChangeList | int
]:
    result_list = r_list(cl)
    results = result_list.get("results")
    urls = get_urls(cl)
    if isinstance(results, list):
        for i in range(len(results)):
            results[i] = [results[i], urls[i]]  # type: ignore
    return result_list


@register.tag(name="clickable_result_list")
def result_list_tag(parser: Parser, token: Token) -> CustomInclusionAdminNode:
    return CustomInclusionAdminNode(
        parser,
        token,
        func=result_list,
        template_name="change_list_results.html",
        takes_context=False,
    )
