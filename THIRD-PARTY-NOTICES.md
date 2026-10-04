# Third-party notices

Smart Astro Planner's own code (`index.html`, `sw.js`, `help.html`, `manifest.json`,
`build_catalog.py`, the icons and the screenshots) is licensed under CC BY-NC-SA 4.0 — see `LICENSE`.
The items below are **not** covered by that license; each keeps its own terms.

## Bundled in this repository

### astronomy-engine 2.1.19 — `astronomy.browser.min.js`
MIT License. Copyright (c) 2019-2023 Don Cross <cosinekitty@gmail.com>.
https://github.com/cosinekitty/astronomy
The complete MIT license text is kept in the header of the file itself and must stay there if you
redistribute it.

### Object catalog — `catalog.json`
Licensed under **CC BY-SA 4.0** (see `LICENSE-CATALOG`), *not* under the non-commercial license above,
because it is an adaptation of OpenNGC:

- **OpenNGC** — Mattia Verga, https://github.com/mattiaverga/OpenNGC, CC BY-SA 4.0. OpenNGC itself
  merges data from the sources below, whose own acknowledgements apply:
  - This research has made use of the NASA/IPAC Extragalactic Database (NED), which is operated by the Jet
    Propulsion Laboratory, California Institute of Technology, under contract with the National Aeronautics
    and Space Administration.
  - We acknowledge the usage of the HyperLeda database (http://leda.univ-lyon1.fr).
  - This research has made use of the SIMBAD database, operated at CDS, Strasbourg, France (Wenger et al.
    2000, A&AS 143, 9, "The SIMBAD astronomical database").
  - Several tables from HEASARC (High Energy Astrophysics Science Archive Research Center, NASA/GSFC).
  - Harold Corwin's NGC/IC Positions and Notes, http://haroldcorwin.net/ngcic/
- This research has made use of the VizieR catalogue access tool, CDS, Strasbourg, France
  (DOI: 10.26093/cds/vizier; Ochsenbein et al. 2000, A&AS 143, 23).
- Specialized catalogs retrieved from **VizieR** (CDS, Strasbourg) and merged with it by `build_catalog.py`.
  Please also cite the original authors when you reuse this data:
  - Sharpless (1959) — VII/20
  - van den Bergh (1966) — VII/21
  - Cederblad (1946) — VII/231
  - RCW: Rodgers, Campbell & Whiteoak (1960) — VII/216
  - Barnard dark nebulae — VII/220A
  - LDN: Lynds (1962) — VII/7A
  - LBN: Lynds (1965) — VII/9
  - D. A. Green, Catalogue of Galactic Supernova Remnants — VII/297
  - Strasbourg-ESO Catalogue of Galactic Planetary Nebulae: Acker et al. (1992) — V/84
  - Open clusters, DAML02: Dias et al. (2002) — B/ocl
  - Integrated Flux Nebulae MW1–MW9: Mandel & Wilson (entered by hand)

## Used at runtime (not redistributed here)

The app fetches these from the user's browser; nothing below is stored in this repository except where noted.

- **Sky images** — DSS2 (Digitized Sky Surveys, via the CDS HiPS2FITS web service; HiPS ids `CDS/P/DSS2/color`
  and `CDS/P/DSS2/red`). The app calls CDS's public **web service** over HTTP — no HiPS2FITS code (the CDS
  implementation is LGPL-3.0) is included or distributed here, so that license does not apply to this project.
  The images are **not public domain**: per STScI's copyright notice they are copyright Caltech (POSS-II, northern
  sky), the Anglo-Australian Observatory Board / UK SERC-PPARC (southern surveys) and AURA/STScI (the rest),
  "distributed by agreement" (https://archive.stsci.edu/dss/copyright.html). CDS's own HiPS compilation is
  labelled ODbL-1.0. STScI asks that the following acknowledgement accompany any publication of the images:

  > The Digitized Sky Surveys were produced at the Space Telescope Science Institute under U.S. Government
  > grant NAG W-2166. The images of these surveys are based on photographic data obtained using the Oschin
  > Schmidt Telescope on Palomar Mountain and the UK Schmidt Telescope. The plates were processed into the
  > present compressed digital form with the permission of these institutions. The National Geographic
  > Society - Palomar Observatory Sky Atlas (POSS-I) was made by the California Institute of Technology with
  > grants from the National Geographic Society. The Second Palomar Observatory Sky Survey (POSS-II) was made
  > by the California Institute of Technology with funds from the National Science Foundation, the National
  > Geographic Society, the Sloan Foundation, the Samuel Oschin Foundation, and the Eastman Kodak Corporation.
  > The Oschin Schmidt Telescope is operated by the California Institute of Technology and Palomar
  > Observatory. The UK Schmidt Telescope was operated by the Royal Observatory Edinburgh, with funding from
  > the UK Science and Engineering Research Council (later the UK Particle Physics and Astronomy Research
  > Council), until 1988 June, and thereafter by the Anglo-Australian Observatory. The blue plates of the
  > southern Sky Atlas and its Equatorial Extension (together known as the SERC-J), as well as the Equatorial
  > Red (ER), and the Second Epoch [red] Survey (SES) were all taken with the UK Schmidt. Supplemental funding
  > for sky-survey work at the ST ScI is provided by the European Southern Observatory.

  Two small cropped screenshots containing DSS2 imagery are included in this repository for illustration
  (`help-img/framing.jpg`, `help-img/target-detail.jpg`); the acknowledgement above applies to them. Do not
  use the DSS imagery commercially without checking with the rights holders.
- **Narrowband data** — Northern Sky Narrowband Survey (Stefan Ziegenbalg, simg.de/nebulae3),
  CC BY-NC-SA 4.0, with Hα calibration from WHAM. Why this project stays non-commercial.
- **CDS services** — HiPS2FITS and Simbad (CDS, Strasbourg). Please acknowledge CDS when you reuse results.
- **Wikipedia** — article summaries (CC BY-SA 4.0), shown with the source named in the card title.
  `help-img/object-info.jpg` shows the Wikipedia card for the North America Nebula, including the photograph
  "NGC 7000 + IC 5070" by gjdonatiello (Wikimedia Commons, **CC0** public-domain dedication; credit given as a courtesy).
- **Claude API (Anthropic)** — optional; calls are made with the user's own API key.
