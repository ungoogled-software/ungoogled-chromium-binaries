# ungoogled-chromium-downloads

Repository containing website for ungoogled-chromium binaries.

This website uses GitHub Pages on the `master` branch. [Use this link](//ungoogled-software.github.io/ungoogled-chromium-binaries/) to see the webpage.

For problems, suggestions, and questions, please use the Issue tracker.

## Developer info

When creating new pages or adding new versions, use an existing version as a template to follow. If you have questions or suggestions, please create an Issue.

### Updating the website

Use `utilities/platform_ini_generator.py` to generate INI file content with the correct URLs to binaries. Redirect the standard output to an `.ini` file in the `config/platforms` directory with the corresponding tag version. Pass in `--help` for usage information.

When finished with updating the website, run `utilities/site_generator.py`. There are no arguments
