import os.path

from coverage.data import CoverageData


def merge_coverage(coverage_data, from_path, to_path):
    for filename in coverage_data.measured_files():
        result_filename = filename.split(from_path)[-1]
        if filename == result_filename:
            continue

        result_filename = result_filename.lstrip('/')
        result_filename = os.path.join(to_path, result_filename)
        result_filename = os.path.abspath(result_filename)
        if os.path.exists(result_filename):
            coverage_data.add_arcs(
                {result_filename: coverage_data.arcs(filename)}
            )

        del coverage_data._arcs[filename]
        coverage_data._validate_invariants()


def fix_coverage(from_path, to_path):
    coverage_data = CoverageData()
    os.rename('.coverage', '.coverage.orig')
    coverage_data.read_file('.coverage.orig')
    merge_coverage(coverage_data, from_path, to_path)
    coverage_data.write_file('.coverage')
    os.remove('.coverage.orig')


def main():
    fix_coverage('/site-packages/', os.getcwd())


if __name__ == '__main__':
    exit(main())
