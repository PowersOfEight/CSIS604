# Mini-MapReduce Implementation

## TODO: documentation

## Generating Jobs for MapReduce

A `generator.py` file is included for convenience. Running the file will result in generation of a JSON-formatted file containing a list of integers. This can be used to generate multiple files using a simple `bash` for loop:

```bash
$ for _ in {1..20} ; do
  python generator.py
done
Generating 1000000 random integers at jobs/b4830907-0eca-4713-ac45-95dde618c8b8.json
Generating 1000000 random integers at jobs/6cf3febb-2ac8-4d67-8155-77fa31b6d351.json
Generating 1000000 random integers at jobs/36337a2d-40e8-4b56-9e76-f042fdaa50bd.json
Generating 1000000 random integers at jobs/89b1e2db-4d18-4597-a9d5-bb35571f9ee8.json
Generating 1000000 random integers at jobs/56f5742c-7f36-4e7a-8588-a52ae6f2bf6a.json
Generating 1000000 random integers at jobs/6a4c1c79-af07-4dd8-800f-395a629e7759.json
Generating 1000000 random integers at jobs/dcec56d4-5413-4123-a11f-4134e6fa46fa.json
Generating 1000000 random integers at jobs/fe3d6b9d-f033-4f08-b08c-d1d972463a72.json
Generating 1000000 random integers at jobs/79458a17-c2da-47b5-adf7-957f11344380.json
Generating 1000000 random integers at jobs/30431ec6-78f5-47aa-90b4-e9f3de452b17.json
Generating 1000000 random integers at jobs/eb076a28-ee1f-4afb-bd9f-0ffc65a555e2.json
Generating 1000000 random integers at jobs/e9fb066e-423e-4194-b3b4-9baacfcc0f9f.json
Generating 1000000 random integers at jobs/4a503e33-a7bc-4853-9f65-804a74e05982.json
Generating 1000000 random integers at jobs/267fbc13-3262-4017-a35b-85471069f9f1.json
Generating 1000000 random integers at jobs/594894fa-1f3d-4f3b-890c-16e0bb6bf272.json
Generating 1000000 random integers at jobs/4ba6c71b-d815-4043-8bbc-fe5ad675c043.json
Generating 1000000 random integers at jobs/c2db19b9-9413-4ba4-ad0d-9a049761c6ea.json
Generating 1000000 random integers at jobs/68b6236c-92d0-48a7-b425-8497ea6a3243.json
Generating 1000000 random integers at jobs/59656818-cc5a-4a23-99dc-d196125db91d.json
Generating 1000000 random integers at jobs/ed57ff0f-c180-4d92-8f76-78bf4eb7e1c9.json
```
