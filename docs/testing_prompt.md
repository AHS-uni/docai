You are a highly capable code generation assistant with strong chain-of-thought reasoning abilities. Your goal is to generate two Python files for the module provided.

### PART 1: Create Comprehensive Unit Tests
Generate a file called "test_\<module\>.py" that includes robust, comprehensive, and well-designed unit tests for the given module. Keep the following in mind:

1. **Module Isolation**: The tests must focus solely on the module and exercise its functions, methods, or classes without external side effects.
2. **Mock External Dependencies**:
   - If the module interacts with external resources (e.g., databases, file storages, APIs), include appropriate mocks or fixtures to simulate these dependencies.
   - If the module requires external raw data (e.g., images, documents, or other files) or synthetic data to test certain functionalities, describe your plan for handling this data and incorporate placeholders for such resources. For example, include comments like `# TODO: Replace with actual image file path or synthetic data` or generate sample synthetic data inline.
3. **Testing Strategies**: Use assertions to check both expected outcomes and error conditions. Include both positive and negative testing approaches where appropriate.
4. **Code Organization**: Organize tests in a logical structure (for example, separate testing functions for each module component) and use setup/teardown functions when necessary.
5. **Comprehensiveness**: Aim for high test coverage by addressing typical usage scenarios, edge cases, and failure modes.

Use the provided module structure and file contents below. Replace any placeholders with the actual data if needed.

MODULE STRUCTURE:
```
<Insert module file structure here>
```

MODULE FILE CONTENTS:
```
<Insert module file contents here>
```

### PART 2: Generate Timing Tests for Performance Analysis
Generate a file called "time_\<module\>.py" to benchmark and time key functions in the module that may serve as performance bottlenecks. Follow these guidelines:

1. **Function Identification**: Identify functions or methods likely to be performance-critical (e.g., database sessions, object creation, data processing routines). Focus on those that significantly contribute to execution time.
2. **Performance Timing**:
   - For each identified function, run it multiple times (default to 20 iterations) and calculate the average execution time.
   - Ensure that timing isolates the function under test, excluding setup or teardown overhead.
3. **Report Generation**: Present the timing results clearly, for example, by printing the results in a table or structured summary in the console.
4. **Modular Design**: Organize the timing code for maintainability, potentially by abstracting common timing routines into helper functions.

Remember:
- Treat these as independent, unit tests dedicated to assessing module performance.
- Benchmark only the functions most likely to cause performance issues rather than every function.

MODULE STRUCTURE:
```
<Insert module file structure here>
```

MODULE FILE CONTENTS:
```
<Insert module file contents here>
```

### Additional Instructions
- **Handling External Raw and Synthetic Data**:
  - Where required, include a plan for handling external raw data (e.g., image files, document files) or synthetic data.
  - Use placeholders in the code (or comments) indicating where actual file paths, URLs, or synthetic data generation should occur, such as `# TODO: Insert path to sample image file` or `# TODO: Generate synthetic document content`.
  - If possible, include example snippets that generate or simulate such data to test the module’s functionality.
- Use appropriate libraries for testing (e.g., `unittest` or `pytest`) and for timing (e.g., the built-in `time` or `timeit` modules).
- For mocking or simulating external dependencies, leverage libraries such as `unittest.mock` or fixtures in `pytest`.
- Ensure your code is clean, well-commented, adheres to Python best practices, and provides clear instructions on where and how to add external data.

Generate the files "test_\<module\>.py" and "time_\<module\>.py" based on the above information and the provided module structure and contents.
