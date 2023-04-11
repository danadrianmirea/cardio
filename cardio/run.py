import random
from typing import List, Optional
import time
from cardio.location import Location, create_random_location
from cardio.path_patterns import PATH_PATTERNS, PathPattern


class Run:
    base_seed: str
    current_distance: int
    # Doesn't need to store any history bc everything is determined by the seed.

    def __init__(self, base_seed: Optional[str] = None) -> None:
        self.base_seed = base_seed or str(time.time_ns())
        self.current_distance = 0

    def _nof_locations(self, at_distance: int) -> int:
        assert at_distance >= 0
        if at_distance == 0:  # Always start with 1 location on level 0
            return 1
        random.seed(f"N{at_distance}_{self.base_seed}")
        return random.randint(1, 3)

    def _get_paths(self, at_distance: int) -> PathPattern:
        in_locs = self._nof_locations(at_distance)
        out_locs = self._nof_locations(at_distance + 1)
        random.seed(f"P{at_distance}_{self.base_seed}")
        return random.choice(PATH_PATTERNS[f"{in_locs}-{out_locs}"])

    def get_locations(self, at_distance: int) -> List[Location]:
        locations = []
        noflocations = range(self._nof_locations(at_distance))
        pathpattern = self._get_paths(at_distance)
        for i in noflocations:
            loc = create_random_location(
                self.base_seed, at_distance, i, pathpattern.paths[i]
            )
            locations.append(loc)
        return locations

    def get_string(
        self, start: int, end: int, h_condense: bool = False, debug: bool = False
    ) -> str:
        """
        Todos:
        - Make paths dark grey. Make locations use some fitting color.
        - Use asciimaatics to print the paths coordinates-based.
        - With the above: Use emojis for locations (they have different widths but maybe
          with coordinate-based positioning they can still be aligned well?).
        """

        def v_stretch(line: str) -> str:
            howmuch = 6
            r = f"{line.rstrip():11s}"  # Normalize line length
            i0, i1 = 3, 7  # Positions 3 and 7 are the positions we can stretch
            c0, c1 = r[i0], r[i1]
            return r[:i0] + c0 * howmuch + r[i0 + 1 : i1] + c1 * howmuch + r[i1 + 1 :]

        start, end = max(start, end), min(start, end)
        res = ""
        for i in range(start, end - 1, -1):
            # Get and format the path pattern:
            pattern = self._get_paths(i).pattern
            lines = filter(None, pattern.split("\n"))
            lines = list(map(v_stretch, lines))
            if h_condense:
                del lines[1]
                del lines[-2]
            if i < start:
                del lines[0]
            if debug:
                lines[-1] += f"     ← {i}"

            # Fill in the location names:
            locations = self.get_locations(i)
            for loc in locations:
                lines[-1] = lines[-1].replace("xxx", loc.marker, 1)

            if i == start:  # Ignore the outgoing paths on top
                res = lines[-1] + "\n"
            else:
                res += "\n".join(lines) + "\n"

        return res

    def print(self, start: int, end: int, h_condense: bool = False) -> None:
        print(self.get_string(start, end, h_condense))
