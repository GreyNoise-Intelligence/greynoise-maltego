# greynoise-maltego
GreyNoise Maltego integration and transforms (work-in-progress...)

# Instructions for running locally in Maltego

1. Clone this repo to /repos/ (you may use an alternate directory, but will need to update the
   transforms after import)
2. Create a local virtual environment named repos/venv
3. Import ``greynoise.mtz`` into Maltego
4. Go to `Transforms` -> `Transform Manager`
5. Find the ``GreyNoiseIPConext`` and ``GreyNoiseIPNoiseLookup`` transforms, and update the
   ``commandline`` and ``working directory`` settings to match that of your local setup
6. Update the ``api_key`` in the ``transforms/GreyNoiseIPContext.py`` and
   ``transforms/GreyNoiseIPNoiseLookup.py`` files
