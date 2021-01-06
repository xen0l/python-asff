# Contributing

Contributions are welcome in the following categories:

* integration into open source security tools
* reporting bugs  
* documentation
* new functionality & code


## Reporting bugs

If you found a bug, you should report it in the project [issue tracker](https://github.com/xen0l/python-asff/issues). 

## Documentation

All documentation contributions should be written in Markdown. The project uses Sphinx as a documentation generator, 
but this is because it provides the best support for generating documentation from docstrings. mkdocs alternatives did 
not provide an output of a similar quality (new project idea?).

## Pull requests 

All code contributions have to be made as a pull request as CI checks will run automatically.
Every new code added should be accompanied by a test as I would like to maintain 100% test coverage, so detecting regressions is simple 
as well as adding new functionality.