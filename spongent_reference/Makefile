CXX = g++
CXXFLAGS = -D_SPONGENT088080008_
SRCS = main.cpp

TARGET = spongent
DEBUG_TARGET = spongent_debug

BINARIES_DIR = bin

all: $(TARGET)

$(TARGET): $(SRCS)
	mkdir -p $(BINARIES_DIR)
	$(CXX) $(CXXFLAGS) $(SRCS) -o ./${BINARIES_DIR}/$(TARGET)

$(DEBUG_TARGET): $(SRCS)
	mkdir -p $(BINARIES_DIR)
	$(CXX) $(CXXFLAGS) -D_PrintState_ $(SRCS) -o ./$(BINARIES_DIR)/$(DEBUG_TARGET)

clean:
	rm -f $(BINARIES_DIR)/*

