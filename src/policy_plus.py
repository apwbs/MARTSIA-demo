from itertools import combinations  # Importing combinations to generate subsets of a given size

def policy_plus(policy, num_Auth):
    # Extract unique attributes with "+" and ensure they are stripped of parentheses
    policy_Split = [f.strip("()") for seen in [set()]  # `seen` ensures no duplicate processing
                     for f in policy.split(" ")        # Split the policy into individual elements
                     if f not in {"or", "and"}         # Skip logical operators
                     and "+" in f                      # Consider only attributes with "+"
                     and f not in seen                # Process only unseen attributes
                     and not seen.add(f)]             # Add attribute to `seen` to avoid duplicates

    for formula in policy_Split:  # Iterate over extracted formulas
        # Parse the attribute name and value (e.g., "CUSTOMER@3+" -> name="CUSTOMER", value="3")
        name, value = formula.strip("+").split("@")
        
        # Generate all possible Authorities based on num_Auth
        authorities = [f"{name}@AUTH{i+1}" for i in range(int(num_Auth))]

        # Check if the specified value exceeds the number of available Authorities
        if int(value) > num_Auth:
            raise Exception("The number of Authorities specified in a policy attribute exceeds the total available Authorities!")

        # Handle the case where only one Authority is required
        elif int(value) == 1:
            transformation = f"({' or '.join(authorities)})"

        # Handle the case where all Authorities are required
        elif int(value) == num_Auth:
            transformation = f"({' and '.join(authorities)})"

        # Handle the case where a subset of Authorities is required
        else:
            authority_combinations = combinations(authorities, int(value))  # Generate combinations of the required size
            transformation = "(" + ' or '.join([f"({' and '.join(comb)})" for comb in authority_combinations]) + ")"

        # Replace the formula in the policy with its transformation
        policy = policy.replace(formula, transformation)

    return policy  # Return the transformed policy
