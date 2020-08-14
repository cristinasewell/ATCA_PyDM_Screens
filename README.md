# ATCA_PyDM_Screens

ATCA - Advanced Telecommunication Computing Architecture Engineering Screens

### Prerequisites
 * pydm

# Cloning the repository

```bash
git clone https://github.com/cristinasewell/ATCA_PyDM_Screens.git

```

# Open display:
```
cd ATCA_PyDM_Screens
pydm -m "DEVICE=SIOC:B${BLD}:RF${RF}:${INST}, RTM=SIOC:B${BLD}:RF${RF}, LOCA=B${BLD}, IOC_UNIT=RF${RF},INST=${INST}" \
    atcaLLRF.py
```

Where:
- `BLD`: is the building number (for example: `084`, `34`, etc.)
- `RF`: is the RF station number (for example: `52`, `53`, etc.)
- `INST`: is the instance number (for example: `0`)
