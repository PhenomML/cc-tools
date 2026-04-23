Write a research narrative for the Jupyter notebook at: $ARGUMENTS

First convert it to markdown:
  cc-nbconvert --to markdown "$ARGUMENTS" --stdout

Read the full output, including all code cells, outputs, and existing markdown. Then write a clear narrative structured as:

**What question does this notebook address?**
State the research or analysis goal in one or two sentences.

**Data and setup**
What data is loaded? What are the key variables, sample size, time period, or experimental conditions?

**Methods and analysis**
Walk through the analytical steps in plain language. For statistical models, state the specification using $...$ math. For transformations or preprocessing, explain why.

**Key findings**
What do the outputs, tables, and figures show? Interpret results in context — don't just restate what the code does. Include key estimates, test statistics, or performance metrics.

**Conclusions and next steps**
What does this analysis establish? What questions remain open?

Write for a reader who understands the domain but has not seen this specific notebook. Use $...$ LaTeX for all math.
