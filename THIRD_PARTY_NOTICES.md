# Third-party notices

This adapter invokes the open-source project **ExquisiteCore/CNKI-search** as a
separate executable inside the Docker image.

- Project: https://github.com/ExquisiteCore/CNKI-search
- Pinned revision in the supplied Dockerfile: `f7f423c9962c2cfcde8b31086bdb3e1099c46888`
- Upstream license: MIT

The adapter does not include or redistribute CNKI article full text. It exposes
metadata search, paper-detail metadata, and reference-list operations supplied
by the upstream command-line client. Users remain responsible for complying
with CNKI terms, institutional access rules, copyright, and applicable law.
