# Python
# -*- coding: utf-8 -*-

import sys
import os
import string

MODE_MOCK=(1<<0)
MODE_CPP=(1<<1)

CMAKE_PLAIN=0
CMAKE_MAC=1
CMAKE_AVR=2
CMAKE_RX=3

MAIN_STD=0
MAIN_AVR=1

def cmodule(mode=MAIN_STD):
    if mode == MAIN_STD :
        return """#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[])
{
    return EXIT_SUCCESS;
}
"""
    elif mode == MAIN_AVR :
        return """#include <avr/io.h>
#include <avr/interrupt.h>
#define F_CPU 4000000
#include <util/delay.h>

// Determine the Data direction register for a given Port Register
#define DDR_FOR_PORT(port) (((uint8_t*)&port)[-1])

/*
ISR(USART1_TX_vect)
{
}
*/

int main(void)
{
    // DDR_FOR_PORT(PORTB) |= 0xff;
    // PORTB = 0xff;

    for(;;)
    {
        asm volatile("nop");
    }
    return 0;
}
"""

def python():
        return """import sys
import os
import string

def main() :
    print("Hello World!")

if __name__ == "__main__":
    main()
"""

def cmake(mode=CMAKE_PLAIN):
    if mode == CMAKE_RX :
        return """if( COMMAND CMAKE_MINIMUM_REQUIRED )
    cmake_minimum_required(VERSION 3.16)
endif( COMMAND CMAKE_MINIMUM_REQUIRED )

####################################################################################
# The name of the project
####################################################################################
project(RX63NProject)
set(CMAKE_CXX_STANDARD 14)
enable_language(C CXX ASM)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

if (NOT CMAKE_CROSSCOMPILING)
    set (ENABLE_UNITTESTING ON)
else()
    set (ENABLE_UNITTESTING OFF)
endif()

####################################################################################
# Project specific settings
####################################################################################
# This is supposed to store the final build artefact.
set(IMAGE_HEX_FILE ${PROJECT_NAME}.mot)

# This is supposed to store the linker map file.
set(IMAGE_MAP_FILE ${PROJECT_NAME}.map)

####################################################################################
# The libs to build to.
####################################################################################
# add_library(${PROJECT_NAME} STATIC "")
# add_library(namespace::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

#target_sources(${PROJECT_NAME}
#PUBLIC
#    file1.h
#PRIVATE
#    file1.c
#)

####################################################################################
# The executeable(s) to build to.
####################################################################################
add_executable(${PROJECT_NAME} "")

target_sources(${PROJECT_NAME}
PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
)

target_include_directories(${PROJECT_NAME}
PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# set_target_properties(${PROJECT_NAME} PROPERTIES COMPILE_DEFINITIONS "VAR=1")
# target_link_libraries(${PROJECT_NAME} customlib)

####################################################################################
# Create an Motorola S-Record Hex file of the image.
####################################################################################
add_custom_command(TARGET ${PROJECT_NAME}
    POST_BUILD
    # Creating load file for Flash: avrtest.hex
    COMMAND ${CMAKE_OBJCOPY} -O srec -R .eeprom ${PROJECT_NAME} ${IMAGE_HEX_FILE}
    COMMAND ${CMAKE_SIZE} ${PROJECT_NAME}
)

set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "-Wl,--gc-sections -Wl,-Map,${IMAGE_MAP_FILE}")

####################################################################################
# Add support for Tests
####################################################################################
macro(TESTCASE name)
if (ENABLE_UNITTESTING)
    add_executable(UT_${name} ${CMAKE_CURRENT_SOURCE_DIR}/UT_${name}.cpp)
    target_link_libraries(UT_${name} PRIVATE tsunit)
    add_test(NAME UT_${name} COMMAND ${CMAKE_CURRENT_BINARY_DIR}/UT_${name})
endif()
endmacro()

####################################################################################
# The unitttest tests to build to.
####################################################################################
#TESTCASE(MyUnitTest)

####################################################################################
# Additional Directories to deal with...
####################################################################################
# add_subdirectory(lib)
if (ENABLE_UNITTESTING)
    enable_testing()
    add_subdirectory(tsunit)
    add_subdirectory(unittests)
endif()

"""
    elif mode == CMAKE_AVR :
        return """if( COMMAND CMAKE_MINIMUM_REQUIRED )
    CMAKE_MINIMUM_REQUIRED(VERSION 3.16)
endif( COMMAND CMAKE_MINIMUM_REQUIRED )

####################################################################################
# The name of the project
####################################################################################
project(Project)
set(CMAKE_CXX_STANDARD 14)
enable_language(C CXX ASM)

####################################################################################
# Some hints
# ----------------------------------------------------------------------------------
# Program the Fuses:
#    ${AVRDUDE} -U efuse:w:0xff:m
#    ${AVRDUDE} -U lfuse:w:0xff:m
#    ${AVRDUDE} -U hfuse:w:0xff:m
####################################################################################

####################################################################################
# Project specific settings
####################################################################################

# ----------------------------------------------------------------------------------
# Programmer settings
# ----------------------------------------------------------------------------------
# For Diamex Programmer
#set(AVRDUDE avrdude -c stk500v2 -p${AVRDUDE_PART} -P `scanAVRProgrammer`)

# For Arduino micro (with explicit USB-Serial device)
#set(AVRDUDE avrdude -c stk500v1 -b57600 -p${AVRDUDE_PART} -P `scanAVRProgrammer`)

# For Arduino devices with builtin booloader (e.g. Leonardo / ATmeag32u4)
#set(AVRDUDE avrdude -c avr109 -b57600 -p${AVRDUDE_PART} -P `scanAVRProgrammer`)

if ( NOT DEFINED AVRDUDE)
    MESSAGE(FATAL_ERROR "Please define a variable for AVRDUDE! (see lines in CMakeLists.txt above)")
endif ( NOT DEFINED AVRDUDE)

# This is supposed to carry EEPROM data.
set(IMAGE_EEPROM_FILE ${PROJECT_NAME}.eep)

# This is supposed to store the final build artefact.
set(IMAGE_HEX_FILE ${PROJECT_NAME}.hex)

# This is supposed to store the linker map file.
set(IMAGE_MAP_FILE ${PROJECT_NAME}.map)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
)

####################################################################################
# Make sure the compiler can find include files from our project.
####################################################################################
include_directories (${PROJECT_SOURCE_DIR}/include)

####################################################################################
# The libs to build to.
####################################################################################
# add_library(${PROJECT_NAME} STATIC "")
# add_library(namespace::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

#target_sources(${PROJECT_NAME}
#PUBLIC
#    ${CMAKE_CURRENT_SOURCE_DIR}/file1.c
#)

####################################################################################
# The executeable(s) to build to.
####################################################################################
add_executable(${PROJECT_NAME} "")

target_sources(${PROJECT_NAME}
PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
)

target_include_directories(${PROJECT_NAME}
PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
#target_compile_definitions(${PROJECT_NAME}
#PUBLIC
#)

####################################################################################
# Target specific flags.
####################################################################################
#target_link_libraries(${PROJECT_NAME}
#PUBLIC
#    util
#)

####################################################################################
# Create an Intel Hex file of the image.
####################################################################################
add_custom_command(TARGET ${PROJECT_NAME}
    POST_BUILD
    # Creating load file for Flash: avrtest.hex
    COMMAND ${CMAKE_OBJCOPY} -O ihex -R .eeprom ${PROJECT_NAME} ${IMAGE_HEX_FILE}

    # Creating EEPROM-File: avrtest.eep
    COMMAND ${CMAKE_OBJCOPY} -j .eeprom --set-section-flags=.eeprom="alloc,load" --change-section-lma .eeprom=0 -O ihex ${PROJECT_NAME} ${IMAGE_EEPROM_FILE}
    COMMAND ${CMAKE_SIZE} ${PROJECT_NAME}
)

set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "-Wl,--gc-sections -Wl,-Map,${IMAGE_MAP_FILE}")

####################################################################################
# Target to flash the CPU using AVRDude. This simply done by using the rule 'install'
####################################################################################
add_custom_target(flash
    COMMAND ${AVRDUDE} -U flash:w:${IMAGE_HEX_FILE}:i
    DEPENDS ${PROJECT_NAME}
)

add_custom_target(flash_eep
    COMMAND ${AVRDUDE} -U eeprom:w:${IMAGE_EEPROM_FILE}:i
    DEPENDS ${PROJECT_NAME}
)

add_custom_target(flash_fuses
    COMMAND ${AVRDUDE} -U efuse:w:0xff:m -U hfuse:w:0x9f:m -U lfuse:w:0xde:m
    DEPENDS ${PROJECT_NAME}
)

####################################################################################
# Additional Directories to deal with...
####################################################################################
# add_subdirectory(lib)

# install(TARGETS ${PROJECT_NAME} DESTINATION /usr/bin)"""

    else :
        if mode == CMAKE_MAC :
            macStr1="""####################################################################################
# Target OS specific flags.
####################################################################################
if(APPLE)
    # Flags for universal build.
    set(CMAKE_OSX_ARCHITECTURES ppc;i386)

    # Determine the SDK the source has to build for.
    set(OSX_SDK 10.5)

    set(CMAKE_OSX_SYSROOT "/Developer/SDKs/MacOSX${OSX_SDK}.sdk")

    #set(GUI_TYPE MACOSX_BUNDLE)

#    find_path(SDL_INCLUDE_DIR SDL/SDL.h)
#    include_directories (${SDL_INCLUDE_DIR})

    find_library(OPENGL OpenGL)
    find_library(COCOA Cocoa)

    mark_as_advanced (
       OPENGL
       COCOA
    )

    set(EXTRA_LIBS
        ${OPENGL}
        ${COCOA}
    )
endif(APPLE)
"""
            macStr2="""if(APPLE)
        SET_TARGET_PROPERTIES(${PROJECT_NAME} PROPERTIES LINK_FLAGS -mmacosx-version-min=${OSX_SDK})
    endif(APPLE)"""
        else:
            macStr1=""
            macStr2=""

        return"""if( COMMAND CMAKE_MINIMUM_REQUIRED )
    CMAKE_MINIMUM_REQUIRED(VERSION 3.16)
endif( COMMAND CMAKE_MINIMUM_REQUIRED )

####################################################################################
# The name of the project
####################################################################################
project(Project)
set(CMAKE_CXX_STANDARD 14)
enable_language(C CXX)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

if (NOT CMAKE_CROSSCOMPILING)
    set (ENABLE_UNITTESTING ON)
else()
    set (ENABLE_UNITTESTING OFF)
endif()

%s
####################################################################################
# The executeable(s) to build to.
####################################################################################
add_executable(${PROJECT_NAME} "")

target_sources(${PROJECT_NAME}
PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp"
)

#target_compile_definitions(${PROJECT_NAME}
#PUBLIC
#)

####################################################################################
# Target specific flags.
####################################################################################
#target_link_libraries(${PROJECT_NAME} PUBLIC pthread)

####################################################################################
# Add support for Tests
####################################################################################
add_library(tsunit STATIC "")

target_sources(tsunit
PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/tsunit/TSUnit.hpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/tsunit/TSUnitTestAddOns.hpp"
PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/tsunit/TSUnit.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/tsunit/TSUnitTestAddOns.cpp"
)

target_include_directories(tsunit
PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_compile_definitions(tsunit
PUBLIC
    UT_USE_COLORED_OUTPUT
)

macro(TESTCASE name)
if (ENABLE_UNITTESTING)
    enable_testing()
    add_executable(UT_${name} ${CMAKE_CURRENT_SOURCE_DIR}/UT_${name}.cpp)
    target_link_libraries(UT_${name} PUBLIC tsunit)
    add_test(NAME UT_${name} COMMAND ${CMAKE_CURRENT_BINARY_DIR}/UT_${name})
endif()
endmacro()
####################################################################################
# The unitttest tests to build to.
####################################################################################
#TESTCASE(MyUnitTest)

%s
####################################################################################
# Additional Directories to deal with...
####################################################################################
if (ENABLE_UNITTESTING)
    enable_testing()
    add_subdirectory(tsunit)
    add_subdirectory(unittests)
endif()

# install(TARGETS ${PROJECT_NAME} DESTINATION /usr/bin)
"""% (macStr1, macStr2)

def templateVHDL():
    return """library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;

-- =============================================================================
entity adder is
-- =============================================================================
    port (a, b  : in  bit_vector (3 downto 0);
          sum   : out bit_vector (3 downto 0);
          carry : out bit);
end adder;

-- =============================================================================
architecture rtl of adder is
-- =============================================================================
signal carry_vector : bit_vector (4 downto 0);
    signal interm   : bit_vector (3 downto 0);
begin
    -- intermediate signal for feed back into carry logic
    interm <= transport a xor b after 1ns;
    -- carry logic
    carry_vector <= ((a and b) or (interm and carry_vector(3 downto 0))) & '0' after 2ns;
    sum    <= transport interm xor carry_vector(3 downto 0) after 1ns;
    carry  <= carry_vector(4);
end rtl;
"""

def templateTSUnit_H():
    return """#pragma once
/* ==========================================================================
 * @(#)File: TSUnit.hpp
 * Created: 2023-02-01
 * --------------------------------------------------------------------------
 *  (c)1982-2024 Tangerine-Software
 *
 *       Hans-Peter Beständig
 *       Kühbachstr. 8
 *       81543 München
 *       GERMANY
 *
 *       mailto:hdusel@tangerine-soft.de
 *       http://hdusel.tangerine-soft.de
 * --------------------------------------------------------------------------
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 * ========================================================================== */
#include <list>
#include <string>

namespace tsunit {

const char* const kVersionString = "TSUnit V2.3.3";

void _cntAssertionDone();
void _cntAssertionFailed();
void _markFailed();
void _cntRun();

class Statistics {
public:
    Statistics() = default;

    // ==================================================================
    // Query the counters
    // ==================================================================
    bool allPassed() const {return 0 == _failedTestsCnt;}

    void clear()
    {
        _runTestsCnt = 0;
        _failedTestsCnt = 0;
        _assertionsCnt = 0;
        _assertionsFailedCnt = 0;
    }

    unsigned int failedTestsCnt() const
    {
        return _failedTestsCnt;
    }

    unsigned int passedTestsCnt() const
    {
        return _runTestsCnt -  _failedTestsCnt;
    }

    unsigned int runTestsCnt() const
    {
        return _runTestsCnt;
    }

    unsigned int assertionsCnt() const
    {
        return _assertionsCnt;
    }

    unsigned int assertionsFailedCnt() const
    {
        return _assertionsFailedCnt;
    }

    // ==================================================================
    // Increase the counters
    // ==================================================================
    void incRunTestsCnt()
    {
        ++_runTestsCnt;
    }

    void incFailedTestsCnt()
    {
        ++_failedTestsCnt;
    }

    void incAssertionsCnt()
    {
        ++_assertionsCnt;
    }

    void incAssertionFailedCnt()
    {
        ++_assertionsFailedCnt;
    }

private:
    unsigned int _runTestsCnt = 0;
    unsigned int _failedTestsCnt = 0;
    unsigned int _assertionsCnt = 0;
    unsigned int _assertionsFailedCnt = 0;

    friend void _cntAssertionDone();
    friend void _cntAssertionFailed();
    friend void _markFailed();
    friend void _cntRun();

}; // class Statistics

extern Statistics _totalStatistics;

static Statistics& totalStatistics()
{
    return _totalStatistics;
}

#if defined(UT_USE_COLORED_OUTPUT)
	#define ESC_COLOR_RED   "\\x1b[31m"
	#define ESC_COLOR_GREEN "\\x1b[32m"
	#define ESC_COLOR_RESET "\\x1b[0m"
#else
	#define ESC_COLOR_RED   ""
	#define ESC_COLOR_GREEN ""
	#define ESC_COLOR_RESET ""
#endif


struct TestListEntry {
    const char* const groupName;
    const char* const testCaseName;
    void(*testFunct)(void);
};

using TestList = std::list<TestListEntry>;

class TestCaseRegistrar
{
public:
    void push(const TestListEntry& inEntry);
    const TestList& unittests() const {
        return _unittests; }
    static TestCaseRegistrar& sharedInstance() {
        static TestCaseRegistrar singleton;
        return singleton;
    }

private:
    TestCaseRegistrar() = default;
    TestList _unittests;
}; // class TestCaseRegistrar

#define TESTNAME(groupname,testcase) groupname##_TC_##testcase

/*
 * A test Fixture
 */
class Test
{
public:
    Test() = default;
    virtual ~Test() noexcept = default;

    virtual void SetUp() {}
    virtual void TearDown() {}

protected:
    virtual void _runTest() = 0;
}; // class Test

class TestFixture
{
public:
    TestFixture(const char* const inGroupName, const char* const inTestCaseName, void(*inTestFunction)(void))
    {
        TestCaseRegistrar::sharedInstance().push(TestListEntry{inGroupName, inTestCaseName, inTestFunction});
    }
}; // class TestFixture

#define TSUNIT_TESTF(FixtureClass,Testname)\\
    class Ext_##FixtureClass_##Testname : public FixtureClass {\\
    public:\\
        Ext_##FixtureClass_##Testname() = default;\\
        virtual ~Ext_##FixtureClass_##Testname() = default;\\
        static void runTest() {\\
            Ext_##FixtureClass_##Testname testcase;\\
            testcase.SetUp();\\
            testcase._runTest();\\
            testcase.TearDown();\\
            \\
        }\\
    protected:\\
        virtual void _runTest() override;\\
    };\\
    tsunit::TestFixture testCase_##Testname(#FixtureClass, #Testname, Ext_##FixtureClass_##Testname::runTest);\\
    void Ext_##FixtureClass_##Testname::_runTest()

// Common Tests
class TestCase
{
public:
    TestCase(const char* const inGroupName, const char* const inTestCaseName, void(*inTestFunction)(void))
    {
        TestCaseRegistrar::sharedInstance().push(TestListEntry{inGroupName, inTestCaseName, inTestFunction});
    }
};

#define TSUNIT_TEST(groupname,testcase)\\
extern void groupname##_TC_##testcase();\\
tsunit::TestCase TR_##groupname##_TC_##testcase(#groupname, #testcase,groupname##_TC_##testcase);\\
void groupname##_TC_##testcase()

class ILogger
{
public:
    ILogger() = default;
    virtual ~ILogger() = default;

    virtual void reportIntro() = 0;
    virtual void issueTestRun(const TestListEntry&) = 0;
    virtual void reportPassed() = 0;
    virtual void reportFailed() = 0;
    virtual void log(const char* fmt, ...) = 0;
    virtual void reportResults() = 0;
};

extern ILogger* pLogger;
extern const TestListEntry* pCurrentEntry;

#define UT_EXPECT_TRUE(arg) do{\\
  tsunit::totalStatistics().incAssertionsCnt();\\
  if ( ! (arg) ) {\\
    tsunit::totalStatistics().incAssertionFailedCnt();\\
    if (tsunit::pLogger){\\
        tsunit::pLogger->reportFailed();\\
        tsunit::pLogger->log(ESC_COLOR_RED "*** Assertion failed in %s::%s @line %d" ESC_COLOR_RESET "\\n"\\
            , tsunit::pCurrentEntry->groupName\\
            , tsunit::pCurrentEntry->testCaseName, __LINE__);\\
    }\\
  }\\
} while(0)

#define UT_EXPECT_FALSE(arg) do{\\
  tsunit::totalStatistics().incAssertionsCnt();\\
  if ( (arg) ) {\\
    tsunit::totalStatistics().incAssertionFailedCnt();\\
    if (tsunit::pLogger){\\
        tsunit::pLogger->reportFailed();\\
        tsunit::pLogger->log(ESC_COLOR_RED "*** Assertion failed in %s::%s @line %d" ESC_COLOR_RESET "\\n"\\
            , tsunit::pCurrentEntry->groupName\\
            , tsunit::pCurrentEntry->testCaseName, __LINE__);\\
    }\\
  }\\
} while(0)

#define UT_EXPECT_EQ(argA,argB) do{\\
  tsunit::totalStatistics().incAssertionsCnt();\\
  if ( (argA) != (argB) ) {\\
    tsunit::totalStatistics().incAssertionFailedCnt();\\
    if (tsunit::pLogger) {\\
        tsunit::pLogger->reportFailed();\\
        tsunit::pLogger->log(ESC_COLOR_RED "*** Assertion failed in %s::%s @line %d" ESC_COLOR_RESET "\\n"\\
            , tsunit::pCurrentEntry->groupName\\
            , tsunit::pCurrentEntry->testCaseName, __LINE__);\\
    }\\
  }\\
} while(0)

#define UT_EXPECT_NE(argA,argB) do{\\
  tsunit::totalStatistics().incAssertionsCnt();\\
  if ( (argA) == (argB) ) {\\
    tsunit::totalStatistics().incAssertionFailedCnt();\\
    if (tsunit::pLogger) {\\
        tsunit::pLogger->reportFailed();\\
        tsunit::pLogger->log(ESC_COLOR_RED "*** Assertion failed in %s::%s @line %d" ESC_COLOR_RESET "\\n"\\
            , tsunit::pCurrentEntry->groupName\\
            , tsunit::pCurrentEntry->testCaseName, __LINE__);\\
    }\\
  }\\
} while(0)

int runUnitTests(int argc, char* argv[]);

} // namespace tsunit
"""

def templateTSUnit_CPP():
    return """/* ==========================================================================
 * @(#)File: TSUnit.cpp
 * Created: 2023-02-01
 * --------------------------------------------------------------------------
 *  (c)1982-2024 Tangerine-Software
 *
 *       Hans-Peter Beständig
 *       Kühbachstr. 8
 *       81543 München
 *       GERMANY
 *
 *       mailto:hdusel@tangerine-soft.de
 *       http://hdusel.tangerine-soft.de
 * --------------------------------------------------------------------------
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 * ========================================================================== */
#include "TSUnit.hpp"
#include <cstring>
#include <stdarg.h>
#include <cstdlib>
#include <cstdio>
#include <cstdint>

#if defined(CROSS_BUILD) && defined(__ARM_EABI__)
    #include "infrastructure/target/arm/SEGGER_RTT/RTT/SEGGER_RTT.h"
#endif

namespace tsunit {
    Statistics _totalStatistics;

static const char* const _repeatString(unsigned int inRepeatCount, char inRepeatChar)
{
    static char sBuffer[80];
    if (inRepeatCount > sizeof(sBuffer) - 1)
    {
        inRepeatCount = sizeof(sBuffer) - 1;
    }

    for (unsigned int i = 0; i < inRepeatCount; ++i)
    {
        sBuffer[i] = inRepeatChar;
    }
    sBuffer[inRepeatCount] = '\\0';

    return sBuffer;
}

class CCommonConsoleLogging : public ILogger
{
private:
    enum struct TestResult
    {
        PASSED, FAILED, RUNNING
    };

    TestResult _testResult = TestResult::FAILED;
public:
    CCommonConsoleLogging() = default;
    virtual ~CCommonConsoleLogging() = default;

    virtual void reportIntro() override
    {
        log("%s\\n", _repeatString(80, '=') );
        log("Report of %s\\n", tsunit::kVersionString);
        log("%s\\n", _repeatString(80, '=') );
    }

    virtual void issueTestRun(const TestListEntry& inTestListEntry) override
    {
        _testResult = TestResult::RUNNING;
        signed int fillerStringSize = 59 - strlen(inTestListEntry.groupName) - strlen(inTestListEntry.testCaseName);
        if (fillerStringSize < 3)
        {
            fillerStringSize = 3;
        }

        log("Running %s::%s %s ", inTestListEntry.groupName, inTestListEntry.testCaseName,  _repeatString(fillerStringSize, '.'));
    }

    virtual void reportPassed() override
    {
        if ( TestResult::RUNNING == _testResult )
        {
            log(ESC_COLOR_GREEN "[PASSED]" ESC_COLOR_RESET "\\n");
            _testResult = TestResult::PASSED;
        }
    }

    virtual void reportFailed() override
    {
        if ( TestResult::RUNNING == _testResult )
        {
            log(ESC_COLOR_RED "[FAILED]" ESC_COLOR_RESET "\\n");
            _testResult = TestResult::FAILED;
        }
    }

    virtual void reportResults() override
    {
        log("%s\\n", _repeatString(80, '=') );
        log("= Finished all Tests: Run %d Tests, %d passed, %d failed.\\n"
            , _totalStatistics.runTestsCnt()
            , _totalStatistics.passedTestsCnt()
            , _totalStatistics.failedTestsCnt()
            );
        log("= %d assertions in total, %d failed of these.\\n"
            , _totalStatistics.assertionsCnt()
            , _totalStatistics.assertionsFailedCnt()
            );
        log("%s\\n", _repeatString(80, '=') );
    }
}; // class CCommonConsoleLogging : public ILogger

#if defined(CROSS_BUILD) && defined(__ARM_EABI__)
class SeggerRttLogger : public CCommonConsoleLogging
{
private:
public:
    SeggerRttLogger() = default;
    virtual ~SeggerRttLogger() = default;

    virtual void log(const char* fmt, ...) override
    {
        va_list list;
        va_start(list, fmt);
        SEGGER_RTT_vprintf(0, fmt, &list);
    }

    virtual void reportResults() override
    {
        CCommonConsoleLogging::reportResults();
        SEGGER_RTT_printf(0, "*STOP*\\n");
    }
}; // class SeggerRttLogger : public CCommonConsoleLogging
#else
class CPrintfLogger : public CCommonConsoleLogging
{
public:
    CPrintfLogger() = default;
    virtual ~CPrintfLogger() = default;

    virtual void log(const char* fmt, ...) override
    {
        va_list list;
        va_start(list, fmt);
        vfprintf(stderr, fmt, list);
    }
}; // class CPrintfLogger : public ILogger
#endif

ILogger* pLogger = nullptr;
const TestListEntry* pCurrentEntry;

// class TestCaseRegistrar - public
void TestCaseRegistrar::push(const TestListEntry& inEntry)
{
    _unittests.push_back(inEntry);
}

static void _runTests()
{
    for (const TestListEntry& entry : TestCaseRegistrar::sharedInstance().unittests())
    {
        pCurrentEntry = &entry;

        _totalStatistics.incRunTestsCnt();
        const auto oldFailCnt = _totalStatistics.assertionsFailedCnt();
        pLogger->issueTestRun(entry);
        entry.testFunct();
        if (oldFailCnt == _totalStatistics.assertionsFailedCnt())
        {
            pLogger->reportPassed();
        }
        else
        {
            _totalStatistics.incFailedTestsCnt();
            pLogger->reportFailed();
        }
    }
}
} // namespace tsunit


int tsunit::runUnitTests(int argc, char* argv[])
{

#if defined(CROSS_BUILD) && defined(__ARM_EABI__)
    SEGGER_RTT_ConfigUpBuffer(0, NULL, NULL, 0, SEGGER_RTT_MODE_BLOCK_IF_FIFO_FULL);
    SEGGER_RTT_SetTerminal(0);
#endif

    const bool ownLogger = (nullptr == tsunit::pLogger);
    if (ownLogger)
    {
    #if defined(CROSS_BUILD) && defined(__ARM_EABI__)
        static tsunit::SeggerRttLogger logger;
    #else
        static tsunit::CPrintfLogger logger;
    #endif
        tsunit::pLogger = &logger;
    }

    /* Clear the statistic collected so far... */
    _totalStatistics.clear();

    if (tsunit::pLogger)
    {
        tsunit::pLogger->reportIntro();
        tsunit::_runTests();
    }
    tsunit::pLogger->reportResults();
    return tsunit::_totalStatistics.failedTestsCnt() ? EXIT_FAILURE : EXIT_SUCCESS;
}

#if !defined(UNITTEST_AS_LIBCALL)
/* ========================================================================== *
 * Main entry
 * ========================================================================== */
int main(int argc, char* argv[])
{
    return tsunit::runUnitTests(argc, argv);
}
#endif
"""

def templateCPPUnit():
    return """//  TSUnit.hpp
//  TSUnitTest
//
//  Created by Hans-Peter Bestaendig on 14.06.20.
//  Copyright (c) 2020 Hans-Peter Bestaendig. All rights reserved.

#pragma once
#include <list>
#include <string>
#include <functional>
#include <memory>
#include <sys/time.h>

/*!
 * \\chapter CH_TSUNIT "TS Unit Test Framework"
 * Example:
 * ~~~.cpp
 * auto result = TSUnit::TestSuite("TestAdder", {
 *     std::make_pair("TC1", [](const char* inTCName)->void{
 *     TC_ASSERT(1+2 == doAdd(1,2));
 * })
 * , std::make_pair("TC2", [](const char* inTCName)->void{
 *     TC_ASSERT(3-2 == doAdd(3,-2));
 *     })
 * });
 *
 * TSUnit::report(result);
 * ~~~
 */
namespace TSUnit {

// TUnit
//
using TestCaseFunctor      = std::function<void(const char* const tcName)>;
using TestCaseFunction     = std::pair<const char* const, TestCaseFunctor>;
using TestCaseFunctionList = std::list<TestCaseFunction>;

static size_t sErrCnt = 0;

enum struct Result {
    passed, failed
};

struct TestCaseResult
{
    time_t consumedTimeUS;
    Result result;
    std::string testCaseName;
    size_t assertionLine;
    std::string assertionString;

    TestCaseResult() = default;
    ~TestCaseResult() noexcept = default;
    TestCaseResult(const TestCaseResult&) = default;
    TestCaseResult& operator=(const TestCaseResult&) = default;

    bool passed() const noexcept {return result == Result::passed;}
    bool failed() const noexcept {return !passed();}
}; // struct TestCaseResult

using TestCaseResultList = std::list<TestCaseResult>;

struct TestSuiteResult
{
    time_t consumedTimeUS;
    Result result;
    std::string testSuiteName;
    TestCaseResultList testCase;

    TestSuiteResult() = default;
    ~TestSuiteResult() noexcept = default;
    TestSuiteResult(const TestSuiteResult&) = default;
    TestSuiteResult& operator=(const TestSuiteResult&) = default;

    bool allPassed() const noexcept {return 0 == countErrors();}

    size_t countErrors() const noexcept
    {
        size_t cnt = 0;
        for (const auto& tc : testCase)
        {
            if (tc.failed())
                ++cnt;
        }
        return cnt;
    }
}; // struct TestSuiteResult

static inline uint32_t getCurrentTimeUS()
{
    return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count());
}

TestCaseResult* currentTc = nullptr;

#define TC_ASSERT(a) do {\\
if (!(a)){\\
    TSUnit::currentTc->assertionLine = __LINE__;\\
    TSUnit::currentTc->assertionString = #a;\\
    ++TSUnit::sErrCnt;\\
}\\
}while(0)

#define TC_ASSERT_EQ(a,b) do {TC_ASSERT((a)==(b));} while(0)

// ======================================
bool IsNear(const float& inValue, const float& inExpectedValue, float inEpsilon=1e-5f)
{
    return inValue >= inExpectedValue-inEpsilon
        && inValue <= inExpectedValue+inEpsilon;
}

template <typename EXT>
void ExpectException(std::function<void(void)> inTestFunc){
    bool success = false;
    try {
        inTestFunc();
    } catch (const EXT&){
        success = true;
    }
}

std::string _cstr(const char* format, va_list vaList)
{
    char *buffer;
    vasprintf(&buffer, format, vaList);
    const std::string s(buffer);
    free(buffer);
    return s;
}

std::string _cstr(const char* format ...)
{
    va_list vl;
    va_start(vl, format);
    return _cstr(format, vl);
}

static void _report(const char* format ...)
{
    va_list vl;
    va_start(vl, format);
    printf("%s", _cstr(format, vl).c_str());
}

void report(const TestSuiteResult& inTestSuiteResult)
{
    const size_t errorsTotal = inTestSuiteResult.countErrors();

    _report("-----------------------------------------------\\n");
    _report("--- Within Suite '%s' Executed %lu tests. %lu failed, %lu passed\\n"
           , inTestSuiteResult.testSuiteName.c_str()
            , inTestSuiteResult.testCase.size()
           , errorsTotal, inTestSuiteResult.testCase.size() - errorsTotal);
    _report("-----------------------------------------------\\n");

    for (auto& tc : inTestSuiteResult.testCase)
    {
        _report("TC '%s': %s, Duration %lu us\\n"
                , tc.testCaseName.c_str()
                , tc.passed() ? "[PASSED]" : _cstr("[FAILED (%s)]", tc.assertionString.c_str()).c_str()
                , tc.consumedTimeUS
                );
    }
}

TestSuiteResult TestSuite(const char* const inTestSuiteName, std::list<TestCaseFunction> tcs)
{
    TestSuiteResult suiteResults;

    suiteResults.testSuiteName = inTestSuiteName;

    _report("-----------------------------------------------\\n");
    _report("---- Executing TestSuite '%s' (%lu Tests)...\\n"
            , inTestSuiteName, tcs.size());
    _report("-----------------------------------------------\\n");

    size_t tcCount = 0;
    for (const auto& tc : tcs)
    {
        TestCaseResult thisTestCaseResult;
        currentTc = &thisTestCaseResult;

        const std::string& currentTestCaseName(tc.first);

        thisTestCaseResult.testCaseName = currentTestCaseName;

        const size_t oldErrCnt = sErrCnt;
        _report(" > Executing TC %lu / %lu '%s'... ",
               ++tcCount, tcs.size(), tc.first);

        const uint32_t testCaseStartTimeUS = getCurrentTimeUS();
        tc.second(tc.first);
        const uint32_t testCaseElapsedTimeUS = getCurrentTimeUS() - testCaseStartTimeUS;
        thisTestCaseResult.consumedTimeUS = testCaseElapsedTimeUS;
        thisTestCaseResult.result = (oldErrCnt == sErrCnt) ? Result::passed : Result::failed;
        _report(oldErrCnt == sErrCnt ? "[PASSED]\\n" : "[FAILED]\\n");

        suiteResults.testCase.push_back(thisTestCaseResult);
    }
    return suiteResults;
}
} // namespace TSUnit
"""

def templateTSUnitTestAddOns_H():
    return """/* ==========================================================================
 * @(#)File: TSUnitTestAddOns.hpp
 * Created: 2023-10-22
 * --------------------------------------------------------------------------
 *  (c)1982-2024 Tangerine-Software
 *
 *       Hans-Peter Beständig
 *       Kühbachstr. 8
 *       81543 München
 *       GERMANY
 *
 *       mailto:hdusel@tangerine-soft.de
 *       http://hdusel.tangerine-soft.de
 * --------------------------------------------------------------------------
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 * ========================================================================== */
#include <cstdint>

// Some Useful addons for Unittest...

#if !defined(dimof)
#define dimof(x) (sizeof(x) / sizeof(*(x)))
#endif

namespace tsunit {

// ==========================================================================
// Some Bit rotation Functions.
// ==========================================================================
/*!
 * Rotate a 32 bit number by a given numer of bits to the left and return this result.
 * \\param val The value to rotate
 * \\param bitsToRotate The number of bits to rotate the number [0..31]
 * \\return value rotated by \\p bitsToRotate Bits to the left
 * \\see rotr(std::uint32, std::size_t)
 */
template<unsigned int NR_OF_BITS>
static uint32_t rotl(std::uint32_t val)
{
    return (0 != (NR_OF_BITS & 0x1f)) ? (val << (NR_OF_BITS & 0x1f)) | (val >> (32 - (NR_OF_BITS & 0x1f))) : val;
}

/*!
 * Rotate a 32 bit number by a given numer of bits to the right and return this result.
 * \\param val The value to rotate
 * \\param bitsToRotate The number of bits to rotate the number [0..31]
 * \\return value rotated by \\p bitsToRotate Bits to the right
 * \\see rotl(std::uint32, std::size_t)
 */
template<unsigned int NR_OF_BITS>
static uint32_t rotr(std::uint32_t val)
{
    return rotl<32-NR_OF_BITS>(val);
}

// ==========================================================================
// Some "Pseudo random" functions.
// ==========================================================================
/*!
 * Calculate a Hash for a given bunch of memry contents and return this as an uint32_t.
 * \\param inDataPtr The Pointer to the Data to calculate a hash for.
 * \\param inDataSize The number of bytes \\p inDataPtr points to.
 * \\return An Hash for the data \\p inDataPtr points to and of the size \\p inDataSize.
 */
std::uint32_t hash(const void* inDataPtr, unsigned int inDataSize);

/*!
 * Helper class that allows to collect several calculations of a Hash Value.
 * The purpose of this class is to remember and reuse the last calculated
 * has value and append new hash calculations in order to perform a chained calculation
 * of the hash of a bunch of different input data.
 */
class CHasher
{
public:
    /*!
     * Creates a new Hasher object with a given initial hash value.
     * \\param inInitialHashValue The inital Has Value. This parameter will
     * default to \\p 0x5acB4821ul if omitted.
     *
     * \\see reset(std::uint32_t)
     */
    CHasher(std::uint32_t inInitialHashValue = 0x5acB4821ul)
    : m_Hash(inInitialHashValue){}

    /*!
     * Adds a new value to this has calculation.
     * \\param inValue The generic value of type <T>
     * \\return An reference to this object **after** \\p inValue has been added.
     * \\see add(const void*, unsigned int)
     */
    template <typename T>
    CHasher& operator+=(T inValue)
    {
        _addHash(tsunit::hash(&inValue, sizeof(inValue)));
        return *this;
    }

    /*!
     * Adds the contents of some memory to this hash.
     * \\param inDataPtr The generic value of type <T>
     * \\param inDataSizeInBytes The size of the data \\p inDataPtr points to in [bytes]
     * \\return An reference to this object **after** the hash of this data has
     *         been added.
     * \\see operator+=<T>(T inValue)
     */
    CHasher& add(const void* inDataPtr, unsigned int inDataSizeInBytes)
    {
        _addHash(tsunit::hash(inDataPtr, inDataSizeInBytes));
        return *this;
    }

    /*!
     * Resets the hash to a given value.
     * \\param inInitialHashValue The hash value to reset this objects current hash value.
     *        when omitted this value becomes 0x5acB4821ul.
     */
    void reset(std::uint32_t inInitialHashValue = 0x5acB4821ul)
    {
        m_Hash = inInitialHashValue;
    }

    /*!
     * Returns the current hash value as an std::uint32_t value.
     * \\return The current hash value as an std::uint32_t value.
     */
    std::uint32_t value() const
    {
        return m_Hash;
    }

private:
    void _addHash(uint32_t inNewHash)
    {
        m_Hash = (rotl<7>(m_Hash) ^ rotr<12>(m_Hash)) - inNewHash;
    }

private:
    std::uint32_t m_Hash = 0x5acB4821ul;
}; // class CHasher


// ==========================================================================
// Some "Pseudo random" functions.
// ==========================================================================
/*!
 * Sets the seed of the Pseudo Random Generator to a given value.
 * \\param inSeed The new seed. Since this is an **pseudo** random number generator
 * one may able to reproduce the same "random" sequence if she starts at the **same
 * seed**.
 *
 * \\see pseudoRandomsetSeed(std::uint32_t)
 * \\see pseudoRandom()
 */
void pseudoRandomsetSeed(std::uint32_t inSeed);

/*!
 * Returns the current pseudo random number as an uint32_t number that will
 * change from call to call. The returned value will use the full 32 bit scale!
 *
 * \\return The current pseudo random number as an uint32_t scalar value.
 * \\see pseudoRandomFloat(float minValue, float)
 */
std::uint32_t pseudoRandom();

/*!
 * Returns the current pseudo random number for a given range as an floating point
 * number. The value will change from call to call.
 *
 * \\param minValue The minimal value (possible included in the return) for the
 * random number. This will default to 0 if omitted.
 * \\param maxValue The max value (possible **almost not** be included in the return)
 * for the random number. This will default to 1.0 if omitted.
 *
 * \\return The current pseudo random number as an float VAlue that will be in a
 * range of [\\p minValue ... \\p minalue[ Meaning that \\p maxValue may part of the
 * returned Random number **but** \\p maxValue almost but never really.
 *
 * \\see pseudoRandomFloat(float minValue, float)
 */
float pseudoRandomFloat(float minValue = 0.f, float maxValue = 1.f);

} // namespace tsunit
"""

def templateTSUnitTestAddOns_CPP():
    return """/* ==========================================================================
 * @(#)File: TSUnitTestAddOns.cpp
 * Created: 2023-10-22
 * --------------------------------------------------------------------------
 *  (c)1982-2024 Tangerine-Software
 *
 *       Hans-Peter Beständig
 *       Kühbachstr. 8
 *       81543 München
 *       GERMANY
 *
 *       mailto:hdusel@tangerine-soft.de
 *       http://hdusel.tangerine-soft.de
 * --------------------------------------------------------------------------
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 *
 * ========================================================================== */
#include "TSUnitTestAddOns.hpp"
#include <cstdlib>
#include <stdio.h>
#include <cassert>

// Some Useful addons for Unittest...

#if !defined(dimof)
#define dimof(x) (sizeof(x) / sizeof(*(x)))
#endif

namespace tsunit {

static std::uint32_t _rot32r(std::uint32_t inNum, unsigned int places)
{
    places &= 0x1f;
    return (inNum >> places) | (inNum << (32-places));
}

template<unsigned int FROM_POS,unsigned int TO_POS>
constexpr static std::uint32_t _swapBits(std::uint32_t inValue)
{
    constexpr unsigned int shiftDistance = (TO_POS >= FROM_POS ?
    		TO_POS - FROM_POS
          : FROM_POS - TO_POS);

    constexpr uint32_t from_mask = (1ul<<FROM_POS);
    constexpr uint32_t to_mask   = (1ul<<TO_POS);
    constexpr uint32_t all_mask = from_mask | to_mask;

    return  (inValue & ~all_mask)
            | ( ((inValue & from_mask) << shiftDistance)
            | ((inValue & to_mask)   >> shiftDistance));
}

// =======================================================================================
static std::uint32_t _scramble0(std::uint32_t param)
{
    return _swapBits<23,16>(param)
         | _swapBits<25,13>(param)
         | _swapBits<15,10>(param)
         | _swapBits<6,19>(param)
         | _swapBits<3,2>(param)
         | _swapBits<11,14>(param)
         | _swapBits<4,24>(param)
         | _swapBits<20,18>(param)
         | _swapBits<7,30>(param)
         | _swapBits<0,29>(param)
         | _swapBits<9,28>(param)
         | _swapBits<1,17>(param)
         | _swapBits<12,27>(param)
         | _swapBits<26,21>(param)
         | _swapBits<31,8>(param)
         | _swapBits<22,5>(param)
         ;
}

static std::uint32_t _scramble1(std::uint32_t param)
{
    return _swapBits<7,19>(param)
         | _swapBits<30,6>(param)
         | _swapBits<20,15>(param)
         | _swapBits<21,8>(param)
         | _swapBits<24,12>(param)
         | _swapBits<9,14>(param)
         | _swapBits<0,25>(param)
         | _swapBits<1,17>(param)
         | _swapBits<26,4>(param)
         | _swapBits<31,23>(param)
         | _swapBits<27,29>(param)
         | _swapBits<18,10>(param)
         | _swapBits<2,16>(param)
         | _swapBits<28,13>(param)
         | _swapBits<11,22>(param)
         | _swapBits<5,3>(param)
         ;
}

static std::uint32_t _scramble2(std::uint32_t param)
{
    return _swapBits<28,30>(param)
         | _swapBits<10,31>(param)
         | _swapBits<4,26>(param)
         | _swapBits<19,8>(param)
         | _swapBits<5,0>(param)
         | _swapBits<18,11>(param)
         | _swapBits<15,22>(param)
         | _swapBits<14,1>(param)
         | _swapBits<17,23>(param)
         | _swapBits<16,29>(param)
         | _swapBits<27,7>(param)
         | _swapBits<9,12>(param)
         | _swapBits<2,25>(param)
         | _swapBits<20,24>(param)
         | _swapBits<21,13>(param)
         | _swapBits<3,6>(param)
         ;
}

static std::uint32_t _scramble3(std::uint32_t param)
{
    return _swapBits<17,22>(param)
         | _swapBits<20,16>(param)
         | _swapBits<10,12>(param)
         | _swapBits<24,23>(param)
         | _swapBits<21,5>(param)
         | _swapBits<19,27>(param)
         | _swapBits<18,15>(param)
         | _swapBits<14,8>(param)
         | _swapBits<0,28>(param)
         | _swapBits<2,4>(param)
         | _swapBits<1,25>(param)
         | _swapBits<29,6>(param)
         | _swapBits<26,31>(param)
         | _swapBits<13,30>(param)
         | _swapBits<9,11>(param)
         | _swapBits<3,7>(param)
         ;
}

typedef std::uint32_t(*ScrambleFunct)(uint32_t);

static uint32_t _noiseNumber(std::uint32_t inIndex)
{
    static const uint32_t kNoiseTable[32] = {
          0x347cf746ul, 0x7b840e02ul, 0x4b6e3c4eul, 0x489b06c6ul
        , 0x2ba14c6eul, 0x4572434aul, 0x04600530ul, 0x7f9acc78ul
        , 0x50a98955ul, 0x071b0827ul, 0x15690047ul, 0x6c68f552ul
        , 0x5fc52edful, 0x61ca273bul, 0x44e4c5f4ul, 0x6a8f5fc5ul
        , 0x01fc910aul, 0x29e9de3ful, 0x2788c41eul, 0x6b5c5ce4ul
        , 0x39d672deul, 0x6d7680bful, 0x511f385dul, 0x577fa18ful
        , 0x7aa4ca0dul, 0x671710edul, 0x127e0c78ul, 0x567cb335ul
        , 0x65f0a296ul, 0x3f0eaf85ul, 0x4e838e1ful, 0x1a6d99ddul
    };

    const unsigned int noiseIdx = (inIndex & 0x1f);

    static const ScrambleFunct scrambleFunct[] {
           _scramble0 , _scramble1 , _scramble2 , _scramble3
    };

    const unsigned int scrambleFuncIdx = (inIndex & (dimof(scrambleFunct) - 1));

    return scrambleFunct[scrambleFuncIdx](inIndex - kNoiseTable[noiseIdx]);
}

std::uint32_t hash(const void* inDataPtr, unsigned int inDataSize)
{
    const uint8_t* dataPtr = static_cast<const uint8_t*>(inDataPtr);
    uint32_t cs = 0xac3b843bul;

    for (;inDataSize;--inDataSize)
    {
        const uint32_t thisDataWord  = (*dataPtr++);

        cs += _noiseNumber((thisDataWord >> 4) + cs);
        cs += _noiseNumber(cs + thisDataWord * 238);
        cs ^= _noiseNumber(_rot32r(1057592071 + thisDataWord, 15));
    }
    return cs;
}

static std::uint32_t randomSeed = 0x3ac4821cul;

void pseudoRandomsetSeed(std::uint32_t inSeed)
{
    randomSeed = inSeed;
}

std::uint32_t pseudoRandom()
{
    randomSeed += hash(&randomSeed, sizeof(randomSeed));
    return randomSeed;
}

float pseudoRandomFloat(float minValue, float maxValue)
{
    return minValue + (maxValue - minValue) * (float(pseudoRandom()) / float(UINT32_MAX));
}

/*!
 * Specialization to add an U16 Value endian independent to the hash.
 * \\param inValue The Value to add to the hash disregard of the hosts endianess.
 * \\return this Hasher object after adding the uint16 value.
 *
 * \\see operator+=(uint32_t)
 * \\see operator+=(const uint64_t&)
 * \\see operator+=(float)
 * \\see operator+=(double)
 */
template <>
CHasher& CHasher::operator+=(uint16_t inValue)
{
    operator+=(uint8_t(inValue>> 8));
    operator+=(uint8_t(inValue>> 0));
    return *this;
}

/*!
 * Specialization to add an U32 Value endian independent to the hash.
 * \\param inValue The Value to add to the hash disregard of the hosts endianess.
 * \\return this Hasher object after adding the uint16 value.
 *
 * \\see operator+=(uint16_t)
 * \\see operator+=(const uint64_t&)
 * \\see operator+=(float)
 * \\see operator+=(double)
 */
template <>
CHasher& CHasher::operator+=(uint32_t inValue)
{
    operator+=(uint8_t(inValue>>24));
    operator+=(uint8_t(inValue>>16));
    operator+=(uint8_t(inValue>> 8));
    operator+=(uint8_t(inValue>> 0));
    return *this;
}

/*!
 * Specialization to add an U64 Value endian independent to the hash.
 * \\param inValue The Value to add to the hash disregard of the hosts endianess.
 * \\return this Hasher object after adding the uint16 value.
 *
 * \\see operator+=(uint16_t)
 * \\see operator+=(uint32_t)
 * \\see operator+=(float)
 * \\see operator+=(double)
 */
template <>
CHasher& CHasher::operator+=(const uint64_t& inValue)
{
    operator+=(uint8_t(inValue>>56));
    operator+=(uint8_t(inValue>>48));
    operator+=(uint8_t(inValue>>40));
    operator+=(uint8_t(inValue>>32));
    operator+=(uint8_t(inValue>>24));
    operator+=(uint8_t(inValue>>16));
    operator+=(uint8_t(inValue>> 8));
    operator+=(uint8_t(inValue>> 0));
    return *this;
}

/*!
 * Specialization to add a 32 bit IEEE float Value endian independent to the hash.
 * \\param inValue The Value to add to the hash disregard of the hosts endianess.
 * \\return this Hasher object after adding the uint16 value.
 *
 * \\see operator+=(uint16_t)
 * \\see operator+=(uint32_t)
 * \\see operator+=(const uint64_t&)
 * \\see operator+=(double)
 */
template <>
CHasher& CHasher::operator+=(float inValue)
{
    return operator+=(*reinterpret_cast<const uint32_t*>(&inValue));
}

/*!
 * Specialization to add a 64 bit IEEE double Value endian independent to the hash.
 * \\param inValue The Value to add to the hash disregard of the hosts endianess.
 * \\return this Hasher object after adding the uint16 value.
 *
 * \\see operator+=(uint16_t)
 * \\see operator+=(uint32_t)
 * \\see operator+=(const uint64_t&)
 * \\see operator+=(float)
 */
template <>
CHasher& CHasher::operator+=(double inValue)
{
    return operator+=(*reinterpret_cast<const uint64_t*>(&inValue));
}

} // namespace tsunit
"""

def writeTemplate(template, target):
    if (os.path.exists(target)):
        print ("The target file '%s' already exists. Will not overwrite!" % target)
    else:
        with open(target, "w") as fileFH:
            fileFH.write(template)
            print ("Written " + target)

def usage():
    version="1.7.10"
    print ("%s V %s" % ((os.path.basename(sys.argv[0])), version))
    print ("Usage: [-v] %s templatename" % (os.path.basename(sys.argv[0])))
    print ("templatename is one of Python, CMake, CMakeMac, CMakeAVR, CMakeRX, GMock, cppunit, tsunit, Main, MainAVR. VHDL.")
    print ("The option -v means 'just view' and will not create a file.")

def main():
    justView=False;

    if len(sys.argv) < 2:
        usage()
        sys.exit()

    templateParamIdx=1

    if (len(sys.argv) == 3):
        templateParamIdx += 1;
        if (sys.argv[templateParamIdx-1] == "-v"):
            justView=True

    tempname = str(sys.argv[templateParamIdx]).upper()

    if (tempname == "PYTHON"):
        res = python()
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="main.py")
    elif (tempname == "CMAKEMAC"):
        res = cmake(CMAKE_MAC)
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="CMakeLists.txt")
    elif (tempname == "CMAKERX"):
        res = cmake(CMAKE_RX)
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="CMakeLists.txt")
    elif (tempname == "CMAKEAVR"):
        res = cmake(CMAKE_AVR)
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="CMakeLists.txt")
    elif (tempname == "CMAKE"):
        res = cmake(CMAKE_PLAIN)
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="CMakeLists.txt")
    elif (tempname == "CPPUNIT"):
        res = templateCPPUnit()
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="TSUnit.hpp")
    elif (tempname == "TSUNIT"):
        if (justView):
            print (templateTSUnit_H())
            print (templateTSUnit_CPP())
        else:
            res = templateTSUnit_H()
            writeTemplate(template=res, target="TSUnit.hpp")
            res = templateTSUnit_CPP()
            writeTemplate(template=res, target="TSUnit.cpp")

            res = templateTSUnitTestAddOns_H()
            writeTemplate(template=res, target="TSUnitTestAddOns.hpp")
            res = templateTSUnitTestAddOns_CPP()
            writeTemplate(template=res, target="TSUnitTestAddOns.cpp")

    elif (tempname == "MAINAVR"):
        res = cmodule(MAIN_AVR)
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="main.cpp")
    elif (tempname == "MAIN"):
        res = cmodule(MAIN_STD)
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="main.cpp")
    elif (tempname == "VHDL"):
        res = templateVHDL()
        if (justView):
            print (res)
        else:
            writeTemplate(template=res, target="main.vhd")
    else:
        usage()

if __name__ == "__main__":
    main()
