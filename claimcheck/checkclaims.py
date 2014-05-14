# Public domain. Do whatever you want with this code - fw@dividuum.de

import sys

def range_intersect(min1, max1, min2, max2):
    return not (min1 > max2 or max1 < min2)


class Claim(object):
    def __init__(self, x1, y1, x2, y2, faction):
        assert x1 < x2
        assert y1 < y2
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._faction = faction

    @property
    def faction(self):
        return self._faction

    def intersects_in_x(self, other):
        # 
        # +---------+
        # |         |
        # +---------+
        #
        #      |    |
        #
        #      +-----------+
        #      |           |
        #      +-----------+
        #
        #      |    |
        #       \__/
        #           \ intersect?
        #
        return range_intersect(self._x1, self._x2, other._x1, other._x2)

    def intersects_in_y(self, other):
        return range_intersect(self._y1, self._y2, other._y1, other._y2)

    def aligned_in_x(self, other):
        #       |
        # +----+|
        # |    ||
        # +----+|
        #       |+---+
        #       ||   |
        #       |+---+
        #       |
        #        \_ aligned along this axis?
        #
        return other._x1 == self._x2 + 1 or \
               other._x2 == self._x1 - 1

    def aligned_in_y(self, other):
        return other._y1 == self._y2 + 1 or \
               other._y2 == self._y1 - 1

    def touches(self, other):
        return (self.aligned_in_x(other) and self.intersects_in_y(other)) or \
               (self.aligned_in_y(other) and self.intersects_in_x(other))

    def overlaps(self, other):
        return self.intersects_in_x(other) and self.intersects_in_y(other)

    def valid_neighbour(self, other):
        if self.overlaps(other):
            return False
        if self.faction == other.faction:
            return True
        # different faction? Make sure they don't touch
        return not self.touches(other)

    def __repr__(self):
        return "<%d,%d -> %d,%d %s>" % (self._x1, self._y1, self._x2, self._y2, self._faction)


class Validator(object):
    def __init__(self):
        self._claims = set()
        self._faction_claims = {}
        self._neighbours = {}

    def check_claims(self, faction):
        visited = set()
        claims = self._faction_claims.get(faction)
        if not claims:
            return True
        unvisited = set([next(iter(claims))])
        while unvisited:
            claim = unvisited.pop()
            visited.add(claim)
            for neighbour in self._neighbours.get(claim, ()):
                if neighbour not in visited:
                    unvisited.add(neighbour)
        return len(visited) == len(claims), list(set(claims) - visited), list(visited)

    def faction_claims(self, faction):
        return self._faction_claims.get(faction)

    def factions(self):
        return self._faction_claims.keys()

    def add_claim(self, claim):
        for existing_claim in self._faction_claims.get(claim.faction, []):
            if claim.touches(existing_claim):
                self._neighbours.setdefault(claim, set()).add(existing_claim)
                self._neighbours.setdefault(existing_claim, set()).add(claim)
        self._claims.add(claim)
        self._faction_claims.setdefault(claim.faction, set()).add(claim)


def read_claims_from_csv(filename, validator):
    with open(filename, 'rb') as f:
        for line in f:
            faction, x1, y1, x2, y2 = line.strip().split()
            validator.add_claim(Claim(int(x1), int(y1), int(x2), int(y2), faction))
    
def main(csv_file):
    validator = Validator()
    read_claims_from_csv(csv_file, validator)

    for faction in validator.factions():
        all_connected, cluster_a, cluster_b = validator.check_claims(faction)
        if not all_connected:
            print "Faction %s has disconnected claims. The claims" % faction
            for claim in cluster_a:
                print '', claim
            print "are not connected to"
            for claim in cluster_b:
                print '', claim

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "%s <claims.csv>" % sys.argv[0]
        sys.exit(1)
    main(sys.argv[1])
