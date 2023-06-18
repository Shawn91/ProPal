"""
Tools are used to help the agents to do some work.
For example, the LLM agent needs a driver to communicate with the LLM model. Databases drivers are also tools.
Tools generally take and return basic data structures, such as strings, lists, dictionaries, etc.
Tools generally should be stateless and states should be kept in the agents or somewhere else.
"""