# CRR/CRD Regulatory Complexity Analysis

This project analyzes regulatory complexity in EU banking regulation by extracting article references, textual indicators, and complexity measures from CRR and CRD legal texts.

The code is developed as part of a master's thesis and focuses on the Capital Requirements Regulation (CRR) and the Capital Requirements Directive (CRD).

## Project Aim

The project investigates how the structure of regulatory texts contributes to complexity. In particular, it analyzes references between provisions in the CRR and CRD and prepares these references for further complexity calculations.

## Current Functionality

- Loads CRR and CRD legal texts from plain-text files
- Detects article boundaries in EU legal texts
- Extracts single article references
- Distinguishes internal and external references
- Prepares a combined internal reference structure for later complexity calculations

## Repository Structure

```text
main.py                  Main script for loading texts and coordinating the analysis
einzelverweise_crd.py    Extracts and classifies single article references in CRD/CRR texts
mehrfachverweise.py      Handles multiple references
compute_complexity.py    Computes regulatory complexity indicators
compute_statistics.py    Computes descriptive statistics
operator_counting.py     Counts regulatory, logical, and mathematical operators
operator_dic.csv         Dictionary of operators used in the analysis
