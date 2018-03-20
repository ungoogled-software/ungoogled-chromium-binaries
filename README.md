# ungoogled-chromium-downloads

Repository containing website for ungoogled-chromium binaries.

**IMPORTANT: These binaries are provided by anyone who are willing to build and submit them. Because these binaries are not necessarily [reproducible](https://reproducible-builds.org/), authenticity cannot be guaranteed.**

This website uses GitHub Pages on the `master` branch. [Use this link](//ungoogled-software.github.io/ungoogled-chromium-binaries/) to see the webpage. [An Atom feed is available here](//raw.githubusercontent.com/ungoogled-software/ungoogled-chromium-binaries/master/feed.xml).

For problems, suggestions, and questions, please use the Issue tracker.

## Developer info

When creating new pages or adding new versions, use an existing version as a template to follow. If you have questions or suggestions, please create an Issue.

### Publishing new binaries

Prerequisites:
* [Python-Markdown](//github.com/waylan/Python-Markdown) for `site_generator.py`

#### Steps

Steps to publish a new binary. An example of these steps is in the next section.

1. Fork the main binaries repository ([ungoogled-software/ungoogled-chromium-binaries](//github.com/ungoogled-software/ungoogled-chromium-binaries))
    * If this has been done before, pull in new changes from this one if necessary.
2. Create a new Release (i.e. using GitHub's Release feature) in the fork and upload binaries to it. The tag name used must be unique for each Release; it normally matches the ungoogled-chromium version.
3. Upload binaries to the new Release
4. Use `utilities/platform_ini_generator.py` to generate an INI file with the correct URLs to binaries. It requires paths to a locally stored copy of the binaries for computing hashes. Redirect the standard output to an `.ini` file in the `config/platforms` directory with the corresponding version as the name. Use the `-h` or `--help` argument for more details.
    * If a directory structure in `config/platforms` doesn't exist for the binary's target platform and version, create the necessary directories with the associated `display_name` files in the same manner as existing platforms.
5. If necessary, update `config/valid_versions`. If you are uploading the first build for a new version of ungoogled-chromium, this needs to be updated.
6. Run `utilities/site_generator.py` to generate the new HTML files. There are no arguments. It must be run from the root of the repository.
7. Push the resulting changes in the repository. Make a pull request against the main repository.
    * This can be bypassed if one is part of the [Binaries Team](//github.com/orgs/ungoogled-software/teams/binaries-team).

Notes:

* `platform_ini_generator.py` is currently restricted to generating INI files with URLs to binaries in GitHub releases. If binaries are uploaded elsewhere, then the INI must be created by other means.
* Additional changes can be made to the website configuration before step 5 as necessary.

#### Example

Example command-line steps (with comments, denoted by a hash `#` symbol). Replace `YOURNAME` in the steps with your GitHub username.

**First-time setup**:

```
# In GitHub, fork ungoogled-software/ungoogled-chromium-binaries to YOURNAME/ungoogled-chromium-binaries
git clone https://github.com/YOURNAME/ungoogled-chromium-binaries.git
cd ungoogled-chromium-binaries
git remote add upstream https://github.com/ungoogled-software/ungoogled-chromium-binaries.git
```

**Publish binaries**:

The following example demonstrates publishing Debian 9 (stretch) amd64 packages located in `/home/user/ungoogled-chromium/buildspace/` (which is assumed to be the shell expanded form of `~/ungoogled-chromium/buildspace/`) for ungoogled-chromium version `99.0.1234.567-1`:

```
# In GitHub, create a new Release on YOURNAME/ungoogled-chromium-binaries with a name "99.0.1234.567-1" (without quotes) and a new tag "99.0.1234.567-1" (without quotes; insert it into the tag field). Upload all necessary files from /home/user/ungoogled-chromium/buildspace/ into the Release.
cd ungoogled-chromium-binaries # The same as the one setup above
git pull
# Edit config/valid_versions and add "99.0.1234.567-1" (without quotes) ONLY if it does not exist.
# Create the directories debian/ and debian/stretch_amd64 with corresponding display_name files in config/platforms/ ONLY if they do NOT exist.
./utilities/platform_ini_generator.py 99.0.1234.567-1 YOURNAME ~/ungoogled-chromium/buildspace/*.deb ~/ungoogled-chromium/buildspace/*.changes ~/ungoogled-chromium/buildspace/*.buildinfo > config/platforms/debian/stretch_amd64/99.0.1234.567-1.ini
./utilities/site_generator.py
git add *
git commit -m 'Add 99.0.1234.567-1 binaries for Debian stretch amd64'
git push origin master
# In GitHub, create a pull request in ungoogled-software/ungoogled-chromium-binaries with the new change in YOURNAME/ungoogled-chromium-binaries
```

## External resources

* [github-markdown-css](//github.com/sindresorhus/github-markdown-css)
* [PyAtom](//github.com/sramana/pyatom)
