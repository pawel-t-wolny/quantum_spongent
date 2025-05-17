CXX = g++
CXXFLAGS = -D_SPONGENT088080008_
SRCS = main.cpp

TARGET = spongent
DEBUG_TARGET = spongent_debug

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET)

debug: $(DEBUG_TARGET)

$(DEBUG_TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -D_PrintState_ $(SRCS) -o $(DEBUG_TARGET)

clean:
	rm -f $(TARGET) $(DEBUG_TARGET)

