# Metaprog-lab-docs
Documentation generator for Java

---

    usage: main.py [-h] [--shallow] [--name PROJECT_NAME]
                   [--version PROJECT_VERSION] [-v]
                   input output_directory
    
    Documentation generator for Java.
    
    positional arguments:
      input                 Directory or file path with sources.
      output_directory      Documentation destination folder.
    
    optional arguments:
      -h, --help            show this help message and exit
      --shallow             Scan only files in passed directory.
      --name PROJECT_NAME   Project name, showed on index page.
      --version PROJECT_VERSION
                            Project version, showed on index page.
      -v                    Verbose output

---

Example:

    python main.py my_project/ docs/ --name MyProject --version 1.0
