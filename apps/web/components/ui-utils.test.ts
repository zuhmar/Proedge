import { describe, it, expect } from "vitest";
import { filteredGames } from "./ui-utils";
describe("game research filters", () => {
  const games = [
    { sport: "NBA", home_team: "Harbor Waves", away_team: "Metro Sparks" },
    { sport: "NFL", home_team: "Coastal Hawks", away_team: "Prairie Bison" },
  ];
  it("combines sport with case-insensitive team search", () =>
    expect(filteredGames(games, "NBA", "METRO")).toEqual([games[0]]));
  it("does not manufacture results for missing teams", () =>
    expect(filteredGames(games, "NFL", "Harbor")).toEqual([]));
});
