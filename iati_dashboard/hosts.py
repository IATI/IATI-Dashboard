from django_hosts import host, patterns

host_patterns = patterns(
    "iati_dashboard",
    host(r"(www.)?iatiregistry.org$", "iatiregistry_org.urls", "iatiregistry_org"),
    host(r".*", "ui.urls", "iati_dashboard"),
)
