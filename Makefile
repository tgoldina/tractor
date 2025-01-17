all: mix emfit mpf version

FORCE:

ceres: FORCE
	$(MAKE) -C tractor ceres
mix: FORCE
	$(MAKE) -C tractor mix
emfit: FORCE
	$(MAKE) -C tractor emfit
mpf: FORCE
	$(MAKE) -C tractor mpf

cov:
	coverage erase
	coverage run -a test/test_galaxy.py
	coverage html
# coverage run test/test_psfex.py
# coverage run -a test/test_sdss.py
# coverage run -a test/test_tractor.py
# coverage run -a examples/tractor-sdss-synth.py --roi 100 200 100 200 --no-flipbook
.PHONY: cov

PYTHON ?= python

cython:
	$(PYTHON) setup-cython.py build_ext --inplace
.PHONY: cython

cython-clean:
	@for x in basics brightness ceres_optimizer ducks ellipses engine galaxy \
		image imageutils lsqr_optimizer mixture_profiles motion optimize patch \
		pointsource psf psfex sersic sfd shifted sky splinesky tractortime \
		utils wcs constrained_optimizer dense_optimizer; do \
		rm tractor/$$x.c tractor/$$x.cpython*.so; \
	done

doc:
	$(MAKE) -C doc -f Makefile.sphinx html PYTHONPATH=$(shell pwd):${PYTHONPATH}
	cp -a doc/_build/html .
.PHONY: doc

_denorm.so: denorm.i
	swig -python $<
	gcc -fPIC -c denorm_wrap.c $$(python-config --includes)
	gcc -o $@ -shared denorm_wrap.o -L$$(python-config --prefix)/lib $$(python-config --libs --ldflags)

_refcnt.so: refcnt.i
	swig -python $<
	gcc -fPIC -c refcnt_wrap.c $$(python-config --includes)
	gcc -o $@ -shared refcnt_wrap.o -L$$(python-config --prefix)/lib $$(python-config --libs --ldflags)

_callgrind.so: callgrind.i
	swig -python $<
	gcc -fPIC -c callgrind_wrap.c $$(python-config --includes) -I/usr/include/valgrind
	gcc -o _callgrind.so -shared callgrind_wrap.o -L$$(python-config --prefix)/lib $$(python-config --libs --ldflags)

refcnt: _refcnt.so refcnt.py
.PHONY: refcnt

PYTHON_SO_EXT ?= $(shell $(PYTHON) -c "from distutils import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX') or sysconfig.get_config_var('SO'))")

INSTALL_DIR ?= /usr/local/tractor

PY_INSTALL_DIR ?= $(INSTALL_DIR)/lib/python

TRACTOR_INSTALL_DIR := $(PY_INSTALL_DIR)/tractor

TRACTOR_INSTALL_PY := __init__.py version.py basics.py brightness.py cache.py \
	ducks.py ellipses.py engine.py fitpsf.py galaxy.py \
	image.py imageutils.py mixture_profiles.py motion.py \
	multiproc.py ordereddict.py patch.py pointsource.py psf.py psfex.py \
	sdss.py sersic.py sfd.py shifted.py sky.py source_extractor.py \
	splinesky.py tractortime.py utils.py wcs.py \
	optimize.py lsqr_optimizer.py ceres_optimizer.py \
	constrained_optimizer.py dense_optimizer.py

TRACTOR_INSTALL := $(TRACTOR_INSTALL_PY) \
	mix.py _mix$(PYTHON_SO_EXT) \
	emfit.py _emfit$(PYTHON_SO_EXT) \
	mp_fourier.py _mp_fourier$(PYTHON_SO_EXT)

WISE_INSTALL_DIR := $(PY_INSTALL_DIR)/wise
WISE_INSTALL := __init__.py allwisecat.py forcedphot.py unwise.py wise_psf.py \
	wisecat.py \
	allsky-atlas.fits wise-psf-avg.fits

CERES_INSTALL := ceres.py _ceres$(PYTHON_SO_EXT)

version:
	echo "version = '$(shell git describe)'" > tractor/version.py
.PHONY: version

install: version
	-($(MAKE) ceres && $(MAKE) install-ceres)
	$(MAKE) mix emfit
	mkdir -p $(TRACTOR_INSTALL_DIR)
	@for x in $(TRACTOR_INSTALL); do \
		echo cp tractor/$$x '$(TRACTOR_INSTALL_DIR)/'$$x; \
		cp tractor/$$x '$(TRACTOR_INSTALL_DIR)/'$$x; \
	done
	mkdir -p $(WISE_INSTALL_DIR)
	@for x in $(WISE_INSTALL); do \
		echo cp wise/$$x '$(WISE_INSTALL_DIR)/'$$x; \
		cp wise/$$x '$(WISE_INSTALL_DIR)/'$$x; \
	done

install-py: version
	mkdir -p $(TRACTOR_INSTALL_DIR)
	@for x in $(TRACTOR_INSTALL_PY); do \
		echo cp tractor/$$x '$(TRACTOR_INSTALL_DIR)/'$$x; \
		cp tractor/$$x '$(TRACTOR_INSTALL_DIR)/'$$x; \
	done
	mkdir -p $(WISE_INSTALL_DIR)
	@for x in $(WISE_INSTALL); do \
		echo cp wise/$$x '$(WISE_INSTALL_DIR)/'$$x; \
		cp wise/$$x '$(WISE_INSTALL_DIR)/'$$x; \
	done

install-ceres:
	mkdir -p $(TRACTOR_INSTALL_DIR)
	@for x in $(CERES_INSTALL); do \
		echo cp tractor/$$x '$(TRACTOR_INSTALL_DIR)/'$$x; \
		cp tractor/$$x '$(TRACTOR_INSTALL_DIR)/'$$x; \
	done


.PHONE: install
