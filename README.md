_This project has been created as part of the 42 curriculum by bclairot._

# CallMeMaybe

## Description

CallMeMaybe is a constrained decoding project centered on generating valid text while enforcing rules during decoding. Its goal is to keep outputs aligned with required formats, syntax, or content constraints without relying only on cleanup after generation.

The project shows how decoding can be guided so that invalid candidates are removed early and the final output remains consistent and reliable.

## Instructions

### Installation

Clone the repository and install any dependencies required by the implementation.

```bash
git clone git@github.com:Naitchi/CallMeMaybe.git
cd CallMeMaybe
```

### Execution

Run the program with the command used by your implementation.

```bash
make install
make run

# or if you have a specific input: make run [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]
make run  --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json
```

If the project depends on external files such as datasets, model weights, or configuration files, place them in the expected locations before running it.

## Algorithm Explanation

The constrained decoding approach works by checking candidate tokens at each generation step against the current constraint state. The decoder proceeds as follows:

1. Start from the input prompt and initialize constraint tracking.
2. Compute the model's next-token scores.
3. Filter out tokens that would violate the active constraints.
4. Choose among the remaining valid tokens using the selected decoding strategy.
5. Update the state and continue until a stopping condition is met.

This method enforces rules during generation, which makes it more effective than post-processing when the output must remain valid at every step.

## Design Decisions

- Constraint logic is separated from the model inference flow.
- Invalid tokens are pruned before selection to reduce wasted computation.
- The decoder is structured so additional constraint types can be added with minimal changes.
- The implementation favors predictable behavior over unconstrained diversity when constraints conflict.

## Performance Analysis

Accuracy improves because the decoder avoids producing outputs that already violate the rules. Speed depends on the complexity of the constraints: lightweight checks add little overhead, while more advanced validation can slow decoding.

Reliability is generally stronger than unconstrained generation because invalid results are prevented earlier in the process. The main trade-off is that strict constraints can reduce the candidate space and limit generation flexibility.

## Challenges Faced

- Managing constraint state across multiple decoding steps.
- Handling situations where no valid token remains.
- Keeping validation fast enough to avoid excessive overhead.
- Preserving modularity so the decoder remains easy to extend and test.

These challenges were addressed by making state updates explicit, pruning candidates early, and defining fallback behavior for edge cases.

## Testing Strategy

The implementation was validated with a mix of normal and edge-case tests:

- inputs that should satisfy all constraints
- inputs designed to violate constraints
- short and empty prompts
- repeated runs to check stability and determinism

Outputs were reviewed for correctness, formatting, and robustness under different decoding conditions.

## Resources

- Hugging Face documentation: https://huggingface.co/docs
- PyTorch documentation: https://pytorch.org/docs/
- Articles and tutorials on constrained decoding and text generation
- 42 project guidelines and course material

### AI Usage

AI was used to help draft and structure this README, especially for organizing the required sections and refining the wording.
