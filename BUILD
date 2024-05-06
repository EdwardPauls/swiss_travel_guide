load("//devtools/python/blaze:pytype.bzl", "pytype_strict_binary")

pytype_strict_binary(
    name = "main",
    srcs = [
        "main.py",
        "model.py",
        "parser.py",
        "plugin.py",
        "swiss_bot.py",
        "swiss_cities.py",
    ],
    data = [
        ":static_fs",
        ":templates_fs",
    ],
    deps = [],
)

Fileset(
    name = "templates_fs",
    out = "templates",
    entries = [
        FilesetEntry(
            files = glob(["templates/**"]),
            strip_prefix = "templates",
        ),
    ],
)

Fileset(
    name = "static_fs",
    out = "static",
    entries = [
        FilesetEntry(
            files = glob(["static/**"]),
            strip_prefix = "static",
        ),
    ],
)
