[![main](https://github.com/GreyNoise-Intelligence/greynoise-maltego/workflows/python_linters/badge.svg)](https://github.com/GreyNoise-Intelligence/greynoise-maltego/actions?query=workflow%3Apython_linters)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# GreyNoise Maltego Transforms

This repo includes a transforms for Maltego to query the GreyNoise APIs.

More details about Maltego here: [https://www.maltego.com/](https://www.maltego.com/)

## Usage

### Initial Configuration
In order to use the GreyNoise transform, install the Integration from the Transform Hub.  Then,
configure the transform using a GreyNoise API key.

If you don't have a GreyNoise API key, you can sign up for a free trial at
[https://viz.greynoise.io/signup](https://viz.greynoise.io/signup)


# Instructions for running locally in Maltego

1. Clone this repo to /repos/ (you may use an alternate directory, but will need to update the
   transforms after import)
2. Create a local virtual environment named repos/venv
3. Import ``greynoise.mtz`` into Maltego
4. Go to `Transforms` -> `Transform Manager`
5. Find the ``GreyNoiseCommunityIPLookup`` transforms, and update the
   ``commandline`` and ``working directory`` settings to match that of your local setup
6. Update the ``api_key`` in the ``transforms/GreyNoiseCommunityIPLookup.py`` file

Repeat steps 5 & 6 for additional transforms

# Values for creating a Manual Transform Seed for Community API

 - `ID`: `GreyNoise Community`
 - `Name`: `GreyNoise Community`
 - `Seed URL`: `https://cetas.paterva.com/runner/showseed/greynoisecommunity`
 - `Icon URL`: `https://viz.greynoise.io/favicon.ico`

# Values for creating a Manual Transform Seed for Enterprise API

 - `ID`: `GreyNoise`
 - `Name`: `GreyNoise`
 - `Seed URL`: `https://cetas.paterva.com/runner/showseed/greynoiseenterprise`
 - `Icon URL`: `https://viz.greynoise.io/favicon.ico`

# Values for creating a Manual Transform Seed for Development work

 - `ID`: `GreyNoise Dev`
 - `Name`: `GreyNoise Dev`
 - `Seed URL`: `https://cetas.paterva.com/runner/showseed/jFUjpWPnZCliFvcE2DyragzC`
 - `Icon URL`: `https://viz.greynoise.io/favicon.ico`

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull
requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see
the [tags on this repository](https://github.com/GreyNoise-Intelligence/greynoise-maltego/tags).

## Authors

* **Brad Chiappetta** - *Initial work* - [bradchiappetta](https://github.com/bradchiappetta)

See also the list of [contributors](https://github.com/GreyNoise-Intelligence/greynoise-maltego/contributors) who participated
in this project.

## Links

* [GreyNoise.io](https://greynoise.io)
* [GreyNoise Terms](https://greynoise.io/terms)
* [GreyNoise Doc Portal](https://doc.greynoise.io)
* [GreyNoise Community API Reference](https://doc.greynoise.io/reference/community-api#get_v3-community-ip)

## Contact Us

Have any questions or comments about GreyNoise? Contact us at [integrations@greynoise.io](mailto:integrations@greynoise.io)

## Copyright and License

Code released under [MIT License](LICENSE).

