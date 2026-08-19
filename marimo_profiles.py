import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Zygos Processing")


@app.cell
def _():
    # importing all the things that are needed for the notebook
    # the below is used to allow importing from local (from_git = False) or from the internet (from_git = True)

    import subprocess
    from_git = True # set to False to pull from a local installation or True to get from github.
    if from_git: 
        try:
            # Recommended: Install using uv (very fast)
            subprocess.check_call([
                "uv", "pip", "install", 
                "git+https://github.com/ProfLear/LearLabProfileClasses.git"
            ])
            print("Successfully installed using uv!")
        except FileNotFoundError:
            # Fallback to standard pip if uv is not in PATH
            import sys
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "git+https://github.com/ProfLear/LearLabProfileClasses.git"
            ])
            print("Successfully installed using pip!")
    import learlab_profile_classes as pc
    import os
    import urllib.request



    return os, pc, urllib


@app.cell
def _(os, urllib):
    # 1. Fetch test data from GitHub if not already present
    test_file = "testZygosData.xyz"
    if not os.path.exists(test_file):
        url = f"https://raw.githubusercontent.com/ProfLear/LearLabProfileClasses/main/testdata/{test_file}"
        urllib.request.urlretrieve(url, test_file)
    return (test_file,)


@app.cell
def _(pc, test_file):
    # 2. Parse sample.  The sample data pulled from 
    sample = pc.makeSample(test_file, instrument="zygos")
    return (sample,)


@app.cell
def _(sample):
    # 3. Plot surface (show=False prevents duplicate plot rendering in notebooks)
    sample.raw.averaged.result.plot(show=False)
    return


@app.cell
def _(sample):
    sample.raw.averaged.result.stats.print()
    return


@app.cell
def _(sample):
    sample.raw.averaged.result.fitRectbiSpline(name = "formSpline")
    return


@app.cell
def _(sample):
    sample.raw.averaged.result.formSpline.plot(show = False)
    return


@app.cell
def _(sample):
    sample.raw.averaged.result.formSpline.residual.render(show=False)
    return


@app.cell
def _():
    return


@app.cell
def _(sample):
    sample.raw.averaged.result.formSpline.residual.fitRectbiSpline(name = "waveSpline", s_scale = 0.15).plot(show=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
