export function filteredGames<
  T extends { sport: string; home_team: string; away_team: string },
>(games: T[], sport: string, search: string): T[] {
  return games.filter(
    (g) =>
      (sport === "ALL" || g.sport === sport) &&
      `${g.home_team} ${g.away_team}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  );
}
