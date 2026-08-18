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
    sample = pc.makeSample(file = "testdata.xyz", instrument = "zygos")
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
