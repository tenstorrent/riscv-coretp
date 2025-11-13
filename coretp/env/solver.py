# SPDX-FileCopyrightText: © 2025 Tenstorrent AI ULC
# SPDX-License-Identifier: Apache-2.0

from typing import Callable, Optional

from .cfg import TestEnvCfg
from .env import TestEnv

from .predicates import DEFAULT_PREDICATES


class TestEnvSolver:
    """
    Used to solve a sequence of TestEnvCfg objects to generate a list of TestEnv objects

    predicates are callable functions that return a boolean value and are used to filter valid TestEnv objects.

    :param: predicates: list of predicates to apply to the TestEnvCfg objects. Default is None. Set to empty list to apply no predicates.
    """

    def __init__(self, predicates: Optional[list[Callable[[TestEnv], bool]]] = None, debug: bool = False):
        if predicates is None:
            predicates = DEFAULT_PREDICATES()
        self._predicates = predicates
        self.debug = debug

    def add_predicate(self, predicate: Callable[[TestEnv], bool]):
        """
        Adds a predicate to the solver.

        :param: predicate: predicate to add to the solver.
        """
        self._predicates.append(predicate)

    def solve(self, cfgs: list[TestEnvCfg]) -> list[TestEnv]:
        """
        Solves the sequence of TestEnvCfg objects to generate a list of TestEnvCfg objects.
        """

        all_envs = self._generate_all_envs(cfgs)
        return [env for env in all_envs if all(pred(env) for pred in self._predicates)]

    def _generate_all_envs(self, cfgs: list[TestEnvCfg]) -> list[TestEnv]:
        """
        Generates all possible TestEnv objects from the given TestEnvCfgs.

        Gathers set of all possible TestEnv objects, generates a set to avoid duplicates, then returns all that pass predicates
        """
        all_envs: list[TestEnv] = []
        for cfg in cfgs:
            all_envs.extend(cfg.generate_all_cfgs())

        all_envs = self.remove_duplicates(all_envs)

        if self.debug:
            print(f"generated {len(all_envs)} envs - \n{all_envs}")

        for env in all_envs:
            for pred in self._predicates:
                pred_val = pred(env)

                if self.debug:
                    print(f"testing {pred} with {env} - {pred_val}")

        return [env for env in all_envs if all(pred(env) for pred in self._predicates)]

    def remove_duplicates(self, seq: list[TestEnv]) -> list[TestEnv]:
        """Method to remove duplicates from a list, while preserving order. Used to ensure that generating configs is deterministic."""
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]
