# LIS source-access investigation for SVS 5011

**Investigation date:** 2026-11-14  
**Scope:** Official NASA/Earthdata identification and access investigation only. No LIS science file was acquired, parsed, or used to implement ingestion/audio.

## Exact official collection identified

The official Earthdata/CMR collection underlying the current quality-controlled ISS LIS archive is:

- **Title:** Quality Controlled Lightning Imaging Sensor (LIS) on International Space Station (ISS) Science Data V3
- **Short name/version:** `isslis_v3_fin`, version `3`
- **CMR concept ID:** `C3838944284-GHRC_DAAC`
- **DOI:** `10.5067/LIS/ISSLIS/DATA114`
- **Data center:** NASA/MSFC/GHRC
- **Processing level:** 2
- **Collection state:** complete
- **Granules:** 72,828
- **Temporal extent:** 2017-03-01T01:16:28Z through 2023-11-16T21:17:10Z
- **Spatial extent:** 55N to 55S, 180W to 180E
- **Formats:** netCDF-4 and HDF-4, with browse GIFs
- **Distribution:** collection metadata says full public access/open without restriction; Earthdata Login is still part of the practical download/service path.

Official evidence:

- [Earthdata V3 catalog](https://www.earthdata.nasa.gov/data/catalog/ghrc-daac-isslis-v3-fin-3)
- [CMR collection JSON](https://cmr.earthdata.nasa.gov/search/concepts/C3838944284-GHRC_DAAC.json)
- [CMR collection UMM-JSON](https://cmr.earthdata.nasa.gov/search/concepts/C3838944284-GHRC_DAAC.umm_json)
- [Earthdata data.nasa.gov record](https://data.nasa.gov/dataset/quality-controlled-lightning-imaging-sensor-lis-on-international-space-station-iss-science)

This identifies the official product family behind the audited GHRC link and is stronger evidence than the earlier V2 catalog reference. It does **not** prove that SVS 5011 used V3 rather than an earlier final product or a specific subset/aggregation. SVS 5011 remains a visualization page whose exact source-file lineage is not explicitly established by the available page/API metadata.

## Representative granule metadata

CMR granule search returned these representative V3 granules for the same first swath:

- `ISS_LIS_SC_V3.0_20170301_011617_FIN.nc` — netCDF-4, 1.91 MB
- `ISS_LIS_SC_V3.0_20170301_011617_FIN.hdf` — HDF-4, 1.32 MB
- Time: 2017-03-01T01:16:28Z to 2017-03-01T02:49:01Z
- Bounding rectangle: west -47.711, east -74.875, north 51.852, south -51.703
- Production/update metadata: 2025-10-31

Official evidence:

- [CMR granule search](https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C3838944284-GHRC_DAAC&page_size=2)
- [Public netCDF granule CMR sidecar](https://data.ghrc.earthdata.nasa.gov/ghrcw-public/isslis_v3_fin__3/ISS_LIS_SC_V3.0_20170301_011617_FIN.nc.cmr.json)
- Checked-in copy: `earth-jukebox/data/manifests/lis-v3-granule-cmr.json`

The sidecar explicitly says `AccessConstraints.Description: This product has full public access`, identifies `NETCDF-4`, and provides protected data, public metadata, S3, credentials, and OPeNDAP links.

## Access tests and exact outcomes

Commands executed:

```powershell
Invoke-WebRequest -Method Head -Uri https://data.ghrc.earthdata.nasa.gov/ghrcw-protected/isslis_v3_fin__3/ISS_LIS_SC_V3.0_20170301_011617_FIN.nc
Invoke-WebRequest -Uri https://data.ghrc.earthdata.nasa.gov/ghrcw-protected/isslis_v3_fin__3/ISS_LIS_SC_V3.0_20170301_011617_FIN.nc -Headers @{Range='bytes=0-4095'} -OutFile <session-file>
Invoke-WebRequest -Uri https://opendap.earthdata.nasa.gov/collections/C3838944284-GHRC_DAAC/granules/ISS_LIS_SC_V3.0_20170301_011617_FIN.nc.dds
Invoke-WebRequest -Uri https://data.ghrc.earthdata.nasa.gov/ghrcw-public/isslis_v3_fin__3/ISS_LIS_SC_V3.0_20170301_011617_FIN.nc.cmr.json
Resolve-DnsName ghrcdrive.nsstc.nasa.gov
```

Results:

| Resource | Result | Meaning |
|---|---|---|
| Public CMR sidecar | HTTP 200, JSON, 2,846 bytes | Granule identity/format/size/coverage metadata is accessible and recorded |
| Protected netCDF `HEAD` | HTTP 200, `application/x-netcdf`, 1,913,598 bytes reported | Header reachability is observable, but not proof that unauthenticated content can be read |
| Protected netCDF bounded `Range` GET | HTTP 200, 10,904 bytes, `text/html`; bytes begin with `<!DOCTYPE html>` | Returned Earthdata login/authorization HTML, not netCDF bytes; no file acquired |
| OPeNDAP `.dds` | HTTP 401 | Schema service requires authentication |
| Old `ghrcdrive.nsstc.nasa.gov` path | DNS failure: `DNS name does not exist` | Earlier direct archive path remains unavailable in this environment |

No file was downloaded into the repository. The bounded response was written only to session scratch storage and is not a scientific asset.

## Schema and record semantics status

**Verified from official metadata/documentation:**

- Product family, version, collection ID, DOI, processing level, formats, spatial/temporal extent, representative filenames, and representative granule metadata.
- NASA's official LIS recipe states that LIS files expose flash-location variables named `lightning_flash_lat` and `lightning_flash_lon`; that recipe is written for provisional data and says the routine may apply to other LIS products. It is not sufficient evidence for the V3 full schema or all record semantics.

**Still unverified because no science file or authenticated schema service was read:**

- Exact V3 netCDF group/dimension layout and variable names beyond the recipe's provisional flash-location example.
- Whether the SVS 5011 visualization uses V3, another final product, or an internally processed subset.
- Event/group/flash record representation and linkage.
- Time encoding/precision, latitude/longitude units and conventions, radiance/energy fields, quality flags, fill values, and aggregation.
- Whether “each data point contains latitude, longitude and detection time” on SVS 5011 refers to flash, group, event, or a derived visualization record.

The fail-closed lightning contract therefore remains correct and unchanged: it requires explicit source schema verification and record type from a future authenticated/adapted input.

## Access requirements and security

NASA documentation describes the collection as open/public and links Earthdata Search, but practical access to protected granules and OPeNDAP requires an Earthdata Login/session. The CMR UMM metadata exposes an S3 credentials endpoint; no credentials were requested or stored.

Security rules for the eventual adapter:

- Use a user-provided Earthdata credential/session outside the repository; never commit `.netrc`, bearer tokens, cookies, or temporary AWS credentials.
- Permit only the fixed collection ID and exact granule URLs returned by CMR; do not build an arbitrary URL fetcher.
- Check redirect destinations and MIME/signature before writing bytes.
- Enforce maximum file size, decompression/parser limits, checksums where available, and protected raw storage outside public routes.
- Treat CMR metadata as untrusted input despite its NASA origin; validate filenames, paths, and content types before filesystem use.
- Record authentication failures explicitly and retain no secret-bearing logs.

## Final status and blocker

**Collection identification:** verified at official Earthdata/CMR level.  
**Representative granule metadata:** verified.  
**Representative science file bytes:** unavailable without authenticated access in this environment.  
**Exact schema/record semantics:** unverified.  
**LIS ingestion/audio:** not implemented and must remain blocked.

Next action requires an authorized Earthdata Login path or an official public sample whose bytes and schema can be inspected. Only after that evidence is captured may the Phase 3 parser contract be specialized and tested against real records.
