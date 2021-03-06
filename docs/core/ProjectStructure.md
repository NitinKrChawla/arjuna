### Arjuna Test Project Structure

A fixed project structure to be followed for an Arjuna test project. This brings consitency across mutliple test automation implementations within and outside your organization.

Following are critical project directories, sub-directories and files. *Arjuna could be creating other directories corresponding to some in-progress or experimental features. They are not listed here.*
- **config**: Contains configuration files.
  - **project.conf**: Your projects' configuration file containing project-level configuration settings.
- **data**: Contains files that act as data sources and data references (WIP).
  - **sources**: Data source files go here.
- **guiauto**: Contains GUI automation related files.
  - **drivers**: Selenium driver executables go here in respective OS folders (Prone to change in future versions of Arjuna).
  - **namespace**: GNS (Gui Namespace) files go here.
 - **report**: Reports are generated here. Each test run is associated with a run-id.
  - **Timestamp-RunID**: Root directory of report for a given run.
    - **html**: HTML report (report.html) generated by pytest-html plugin goes here.
    - **log**: arjuna-run.log file can be found here.
    - **screenshots**: Contains screenshots taken for a test run.
    - **xml**: JUnit-style XML report (report.xml) goes here. It is primarily meant for Jenkins or other CI software intergrations with Arjuna.
 - **tests**: Contains test files. As of now Arjuna supports coded tests only.
  - **modules**: Coded tests are written as Python modules and are placed here. Sub-packaging of modules is allowed.
- **arjuna_launcher.py**: This is the script which is used to run your tests by invoking Arjuna.
- **conftest.py**: This is pytest's conftest.py file (Needs better placement if pytest permits).
- **pytest.ini**: This is pytests's config file (Needs better placement if pytest permits).
