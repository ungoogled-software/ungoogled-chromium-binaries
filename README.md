# ungoogled-chromium-downloads

Repository containing website for ungoogled-chromium binaries.

This website uses GitHub Pages on the `master` branch. [Use this link](//ungoogled-software.github.io/ungoogled-chromium-binaries/) to see the webpage. [An Atom feed is available here](//raw.githubusercontent.com/ungoogled-software/ungoogled-chromium-binaries/master/feed.xml).

For problems, suggestions, and questions, please use the Issue tracker.

## Developer info

When creating new pages or adding new versions, use an existing version as a template to follow. If you have questions or suggestions, please create an Issue.

### Publishing new binaries

Prerequisites:
* [Python-Markdown](//github.com/waylan/Python-Markdown) for `site_generator.py`

Steps to publish new binaries to the website:

1. Fork the main binaries repository ([ungoogled-software/ungoogled-chromium-binaries](//github.com/ungoogled-software/ungoogled-chromium-binaries))
    * If this has been done before, pull in new changes from this one if necessary.
2. Create a new Release (i.e. using GitHub's Release feature) in the fork and upload binaries to it. A new tag can be created or an existing one can be used for the Release; the behavior is the same.
3. Upload binaries to the new Release
4. Use `utilities/platform_ini_generator.py` to generate an INI file with the correct URLs to binaries. Redirect the standard output to an `.ini` file in the `config/platforms` directory with the corresponding version as the name. Pass in `--help` for usage information.
5. Run `utilities/site_generator.py` to generate the new HTML files. There are no arguments. It must be run from the root of the repository.
6. Push the resulting changes in the repository. Make a pull request against the main repository.
    * This can be bypassed if one is part of the [Binaries Team](//github.com/orgs/ungoogled-software/teams/binaries-team).

Notes:

* `platform_ini_generator.py` is currently restricted to generating INI files with URLs to binaries in GitHub releases. If binaries are uploaded elsewhere, then the INI must be created by other means.
* Additional changes can be made to the website configuration before step 5 as necessary.

## External resources

* [github-markdown-css](//github.com/sindresorhus/github-markdown-css)
* [PyAtom](//github.com/sramana/pyatom)
