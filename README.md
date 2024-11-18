# RANS boundary layer validation

Running OpenFOAM simulations in Docker containers as part of a
reproducible DVC pipeline,
setup with
[Calkit](https://github.com/calkit/calkit).

See the [blog post](https://petebachant.me/reproducible-openfoam/).

## Adding a publication with Docker build env

This was done with:

```sh
calkit new publication \
    --template latex/jfm \
    --title "Validating RANS models" \
    --description "This was created for a demo." \
    --kind journal-article \
    --stage build-paper \
    --environment latex \
    --deps-from-stage-outs plot-mean-velocity-profiles \
    ./paper
```

After that, the `mean-velocity-profiles.png` image was referenced in a
figure in `paper/paper.tex`.
Now, if that figure ever changes, which could be caused by a change
in either the plotting script or the CFD simulations,
the paper will automatically be rebuilt when `calkit run` is executed.
