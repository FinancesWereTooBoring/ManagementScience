def create_workers():
    main_dict = {}

    # Define the number of keys for each level
    num_keys_level_2 = 8
    num_keys_level_4 = 12
    num_keys_level_3 = 15
    num_keys_level_2 = 5

    # Populate the main dictionary with keys and corresponding dictionaries
    main_dict.update(
        {f"worker_{i}": {"level": 5, "when_will_be_available": 0} for i in range(1, num_keys_level_2 + 1)})
    main_dict.update({f"worker_{i}": {"level": 4, "when_will_be_available": 0} for i in range(
        num_keys_level_2 + 1, num_keys_level_2 + num_keys_level_4 + 1)})
    main_dict.update({f"worker_{i}": {"level": 3, "when_will_be_available": 0} for i in range(
        num_keys_level_2 + num_keys_level_4 + 1, num_keys_level_2 + num_keys_level_4 + num_keys_level_3 + 1)})
    main_dict.update({f"worker_{i}": {"level": 2, "when_will_be_available": 0} for i in range(num_keys_level_2 + num_keys_level_4 +
                     num_keys_level_3 + 1, num_keys_level_2 + num_keys_level_4 + num_keys_level_3 + num_keys_level_2 + 1)})

    # Print the resulting dictionary
    return main_dict
