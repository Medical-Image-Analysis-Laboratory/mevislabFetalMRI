# -----------------------------------------------------------------------------
# CHUVIntensityStandardization project profile
#
# \file
# \author  FetalMRI
# \date    2018-05-22
# -----------------------------------------------------------------------------


TEMPLATE   = lib
TARGET     = CHUVIntensityStandardization

DESTDIR    = $$(MLAB_CURRENT_PACKAGE_DIR)/lib
DLLDESTDIR = $$(MLAB_CURRENT_PACKAGE_DIR)/lib

# Set high warn level (warn 4 on MSVC)
WARN = HIGH

# Add used projects here (see included pri files below for available projects)
CONFIG += dll ML MLBackgroundTasks boost MyIntensityStandardization MyITK

MLAB_PACKAGES += CHUV_FetalMRI \
                 MeVisLab_Standard

# make sure that this file is included after CONFIG and MLAB_PACKAGES
include ($(MLAB_MeVis_Foundation)/Configuration/IncludePackages.pri)

DEFINES += CHUVINTENSITYSTANDARDIZATION_EXPORTS

# Enable ML deprecated API warnings. To completely disable the deprecated API, change WARN to DISABLE.
DEFINES += ML_WARN_DEPRECATED


win32 {
QMAKE_CXXFLAGS += /openmp
}

linux {
QMAKE_CXXFLAGS += -fopenmp
LIBS += -fopenmp
}

HEADERS += \
    CHUVIntensityStandardizationInit.h \
    CHUVIntensityStandardizationSystem.h \
    mlmialIntensityStandardization.h \
    mlmialCorrectSliceIntensity.h \
    mlmialSliceBySliceBiasEstimation.h \
    mlmialSliceBySliceBiasFieldCorrection.h \
	mlmialN4BiasField.h \



SOURCES += \
    CHUVIntensityStandardizationInit.cpp \
    mlmialIntensityStandardization.cpp \
    mlmialCorrectSliceIntensity.cpp \
    mlmialSliceBySliceBiasEstimation.cpp \
    mlmialSliceBySliceBiasFieldCorrection.cpp \
	mlmialN4BiasField.cpp \
