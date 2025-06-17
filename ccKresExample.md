# ccKresAnalysisExample

This example script demonstrates how to use `ala.py` to analyze the Type-Token Ratio (TTR) of words and lemmas in literary texts from the Slovenian corpus [ccKres](https://www.clarin.si/repository/xmlui/handle/11356/1034).

> 

---

## 1. Prepare Your Project

1. Create a new folder named `ccKresExample`.
2. Download `ccKresAnalysisExample.py` and the module `ala.py` into this folder.
3. Download the XML version of the Kres corpus (`cckresV1_0.zip`) from the [CLARIN.SI repository](https://www.clarin.si/repository/xmlui/handle/11356/1034) and extract it into `ccKresExample/cckresV1_0`.

    **Note:** A small portion of the corpus ccKres is already included in the `ccKresExample.zip` file in this repository.

---

## 2. Run the Script

Run `ccKresAnalysisExample.py`, which performs the following steps:

### Step 1: Extract Literary Texts

```python
ala.extract_genres_from_xml(
    "ccKresExample/cckresV1_0",
    "ccKresExample/cckresV1_0_leposlovje",
    genre="#SSJ.T.K.L"
)
```

This creates the folder `ccKresExample/cckresV1_0_leposlovje` and extracts only literary texts into it.  
The tag `#SSJ.T.K.L` stands for *tisk-knjižno-leposlovno*. For other genres, see [this genre list](https://gitea.cjvt.si/lkrsnik/list/src/commit/2c028cd3343a12b68b03af0ee30bcd772964b909/src/main/java/data/Tax.java).

---

### Step 2: Convert XML to TXT (Classla works only on TXT format)

```python
ala.convert_xml_to_txt(
    "ccKresExample/cckresV1_0_leposlovje",
    "ccKresExample/cckresV1_0_leposlovje_txt"
)
```

This creates a new folder with plain text files.

---

### Step 3: Apply Classla for Linguistic Annotation

```python
ala.classla(
    "ccKresExample/cckresV1_0_leposlovje_txt",
    "ccKresExample/cckresV1_0_Classla"
)
```

The function `ala.classla` performes lemmatization, part-of-speech (POS) tagging and annotation of universal dependencies (UD) relations. The output will be saved as `.xlsx` files in `ccKresExample/cckresV1_0_Classla`. The xlsx files will contain columns "word", "lemma", "pos" and "deprel"

**References:**
- [Classla GitHub Repository](https://github.com/clarinsi/classla)
- [POS tags (Universal Dependencies)](https://universaldependencies.org/u/pos/all.html)
- [UD dependency relations](https://universaldependencies.org/u/dep/index.html)

---

### Step 4: Perform TTR Analysis

- Count words and lemmas.
- Compute windowed TTR using a window of 500 words.
- Plot TTR variation across the corpus.
- Calculate mean and standard deviation of TTR.

**Note:** Results of this analysis are in the `ccKresExample.zip` file in this repository.