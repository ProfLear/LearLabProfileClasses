import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Zygos Processing")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import learlab_profile_classes as pc

    return (pc,)


@app.cell
def _(pc):
    import os
    import urllib.request

    test_file = "testdata.xyz"
    if not os.path.exists(test_file):
        print(f"'{test_file}' not found locally. Downloading from GitHub...")
        url = "https://raw.githubusercontent.com/ProfLear/LearLabProfileClasses/main/testdata/testdata.xyz"
        try:
            urllib.request.urlretrieve(url, test_file)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading test data: {e}")
    return (test_file,)


@app.cell
def _(pc, test_file):
    sample = pc.makeSample(file = test_file, instrument = "zygos")
    return (sample,)


@app.cell
def _(sample):
    sample.raw.plot()
    return


@app.cell
def _(sample):
    sample.raw.getArealRoughness()

    return


@app.cell
def _(sample):
    sample.raw.skew
    return


if __name__ == "__main__":
    app.run()
