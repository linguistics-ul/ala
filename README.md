## ALA (Automated Language Analysis)

This repository contains two modules and some scripts for Automated Language Analysis (ALA), primarily focused on the Slovenian language. However, much of its functionality can be directly applied to other languages as well.

The repository is not optimized for speed but tries to be accessible to linguists with little prior experience in Python and computing.

Modules are:
 - `module_slovenian_ala.py` (functions developed by the authors of this repository)
 - `module_syntactic_measures_t2024.py` (functions copied from [Terčon 2024](https://github.com/lukatercon/SyntComplex))

 Examples are:
- `Example_ccKres.py` (how to use Classla annotation to analyze ccKres corpus, see [Example_ccKres.md](ccKresExample.md)) 
- `Example_ccKres.py` (how to count clauses in sentences)

---
## Authors  

Tatjana Marvin Derganc, Department of Comparative and General Linguistics, Faculty of Arts, University of Ljubljana  
Jure Derganc, Institute of Biophysics, Faculty of Medicine, University of Ljubljana

---

## Additional Notes

- Ensure required Python packages (e.g., `classla`,`conllu` `numpy`,`pandas`,`openpyxl`,`matplotlib`) are installed.
- Processing time depends on text size and system performance.
- Additional ALA measures can be obtained in repositories [LexicalRichness](https://github.com/LSYS/LexicalRichness) and [lexical_diversity](https://github.com/kristopherkyle/lexical_diversity).

---

Happy analyzing!
