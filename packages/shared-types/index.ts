export type Sport = "NBA" | "NFL";
export interface Game {
  id: number;
  sport: Sport;
  home_team: string;
  away_team: string;
  scheduled_at: string;
  status: string;
  demo: boolean;
  prediction: null;
}
export interface User {
  id: number;
  email: string;
  role: string;
}
