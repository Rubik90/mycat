# Reqs2Code

[![awesome plugin](https://custom-icon-badges.demolab.com/static/v1?label=&message=awesome+plugin&color=383938&style=for-the-badge&logo=cheshire_cat_ai)](https://)  

## Description

Reqs2Code is a Cheshire Cat plugin that converts software requirements into code. It reads requirements from an Excel file and generates corresponding code files based on those requirements.

## Features

- Convert software requirements to code in multiple programming languages
- Support for Python, Java, JavaScript, TypeScript, C#, C++, Go, and Rust
- Save generated code to both Excel and individual files
- Simple command interface for easy interaction

## Usage

1. Prepare an Excel file named `in_out.xlsx` with the following columns:
   - ID: Unique identifier for each requirement
   - REQUIREMENT: Description of the requirement
   - GENERATED_CODE: (Optional) Will be populated with generated code

2. Place the Excel file in the plugin directory

3. Use the following commands to interact with the plugin:
   - `req2code convert`: Convert requirements to code
   - `req2code list`: List available programming languages
   - `req2code set-lang <language>`: Set the target programming language
   - `req2code help`: Show help information

## Generated Files

The plugin saves generated code in two places:
1. In the Excel file under the GENERATED_CODE column
2. As individual files in the `generated/<REQ_ID>/` directory

## Configuration

You can configure the target programming language using the `req2code set-lang` command followed by one of the supported languages.

