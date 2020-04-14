# ungoogled-chromium-binaries

Website for ungoogled-chromium contributor-submitted binaries (contributor binaries).

**IMPORTANT: These binaries are provided by anyone who are willing to build and submit them. Because these binaries are not necessarily [reproducible](https://reproducible-builds.org/), authenticity cannot be guaranteed.**

[**Link to the website here**](//ungoogled-software.github.io/ungoogled-chromium-binaries/)

[Atom feed for new binaries here](//raw.githubusercontent.com/ungoogled-software/ungoogled-chromium-binaries/master/feed.xml).

This website uses GitHub Pages on the `master` branch.

For problems, suggestions, and questions, please use the Issue tracker.

## Developer info

When creating new pages or adding new versions, use an existing version as a template to follow. If you have questions or suggestions, please create an Issue.

### Publishing new binaries

**Ensure your binary has source code published to a platform repo**. Otherwise, your PR will not be merged.

Prerequisites:
* Python 3 for all scripts under `utilities/`

#### Steps

Steps to publish a new binary. An example of these steps is in the next section.

1. Ensure your binary has source code published to a platform repo.
2. Fork the main binaries repository ([ungoogled-software/ungoogled-chromium-binaries](//github.com/ungoogled-software/ungoogled-chromium-binaries))
    * If this has been done before, pull in new changes from this one if necessary.
3. Create a new Release (i.e. using GitHub's Release feature) in the fork and upload binaries to it. The tag name used must be unique for each Release; it normally matches the ungoogled-chromium version.
4. Upload binaries to the new Release
5. Use `utilities/submit_github_binary.py` to generate an INI file with the correct URLs to the GitHub Release. It requires paths to a locally stored copy of the binaries for computing hashes. Use the `-h` or `--help` argument for more details.
    * If a directory structure in `config/platforms` doesn't exist for the binary's target platform and version, create the necessary directories with the associated `display_name` files in the same manner as existing platforms.
6. Push your changes in the repository; these changes should only be of files in `config/`. Make a pull request against the main repository.
    * This can be bypassed if one is part of the [Binaries Team](//github.com/orgs/ungoogled-software/teams/binaries-team).

Notes:

* `submit_github_binary.py` is currently restricted to generating INI files with URLs to binaries in GitHub releases. If binaries are uploaded elsewhere, then the INI must be created by other means.
* Additional changes can be made to the website configuration before step 5 as necessary.

#### Example

Example command-line steps (with comments, denoted by a hash `#` symbol). Replace `YOURNAME` in the steps with your GitHub username.

**First-time setup**:

```
# In GitHub, fork ungoogled-software/ungoogled-chromium-binaries to YOURNAME/ungoogled-chromium-binaries
git clone https://github.com/YOURNAME/ungoogled-chromium-binaries.git
cd ungoogled-chromium-binaries
git remote add upstream https://github.com/ungoogled-software/ungoogled-chromium-binaries.git
git config branch.master.remote upstream
git config branch.master.pushRemote origin
```

**Publish binaries**:

The following example demonstrates publishing Debian 9 (buster) amd64 packages located in `/home/user/ungoogled-chromium/build/` (which is assumed to be the shell expanded form of `~/ungoogled-chromium/build/`) for ungoogled-chromium version `99.0.1234.567-1`:

```
# In GitHub, create a new Release on YOURNAME/ungoogled-chromium-binaries with a name "99.0.1234.567-1" (without quotes) and a new tag "99.0.1234.567-1" (without quotes; insert it into the tag field). Upload all necessary files from /home/user/ungoogled-chromium/buildspace/ into the Release.
cd ungoogled-chromium-binaries # The same as the one setup above
git pull
# Create the directories debian/ and debian/buster_amd64 with corresponding display_name files in config/platforms/ ONLY if they do NOT exist.
# NOTE: You can use either --git to fetch the latest tag on the current branch, or specify it manually with --tag
./utilities/submit_github_binary.py --git path/to/ungoogled-chromium-debian --username YOURNAME --output config/platforms/debian/buster_amd64/ ~/ungoogled-chromium/build/ungoogled-chromium*
# A commit will be created automatically. Ensure commits are correct before proceeding
git push
# In GitHub, create a pull request in ungoogled-software/ungoogled-chromium-binaries with the new change in YOURNAME/ungoogled-chromium-binaries
```

**Testing changes**

```
python3 -m pip install -r utilities/requirements.txt
python3 utilities/site_generator.py
./utilities/local_server.py
# Open a webpage to http://localhost:8086
```

## External resources

* [github-markdown-css](//github.com/sindresorhus/github-markdown-css)
* [PyAtom](//github.com/sramana/pyatom)
