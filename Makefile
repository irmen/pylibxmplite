.PHONY:  all win_dist dist upload

all:
	@echo "Targets:  wheel, win_wheel, check_upload, upload"

win_wheel:
	cmd /C del /q dist\*
	py -3-64 -m build --wheel

wheel: 
	python -m build --wheel --sdist

upload: check_upload
	twine upload dist/*

check_upload:
	twine check dist/*

