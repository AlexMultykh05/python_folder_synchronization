# Folder Synchronization Script

This Python script synchronizes two folders — a **source** and a **replica** — ensuring the replica is an exact copy of the source after each run. Synchronization is **one-way**, runs **periodically**, and stops after a specified number of times.

All file operations and errors are logged to both a **log file** and the **console**.

## Usage

The script accepts command-line arguments in the following order:

1. Path to source folder  
2. Path to replica folder  
3. Interval between synchronizations (in seconds)  
4. Number of synchronizations  
5. Path to log file  

## Features

- One-way folder synchronization  
- Automatic file creation, updating, and deletion  
- Periodic execution with controlled repetition  
- Logging to file and console  
- Implemented using only standard Python libraries  
- Single-threaded and gracefully terminates after completion

---

This project was created as part of a technical assessment.
