/**
 * Control plane's served record for a registered hexagon (D014) — a descriptor summary plus changing state. Populated from a repo's hexagon.descriptor frontmatter plus git/CI-sourced state.
 */
export interface RegistryEntry {
  functionalName: string;
  kind: "runtime" | "app" | "buildtime";
  side: "host" | "hub" | "ui" | "shared";
  /**
   * `suspended` exists only here — a registry action, not a repo property.
   */
  status: "planned" | "building" | "active" | "suspended" | "deprecated";
  /**
   * Source repository URL.
   */
  repoUrl: string;
  /**
   * Git tag where one exists, else version+shortsha.
   */
  version: string;
  /**
   * Mirror of the descriptor's contracts.pin.
   */
  contractsPin?: string;
  updatedAt: string;
  /**
   * App-only. Populated when app.manifest registration arrives.
   */
  appId?: string;
  /**
   * App-only. D010 risk class tier, populated when app.manifest registration arrives.
   */
  class?: "low-stakes" | "health-class" | "kids-class";
  /**
   * App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.
   */
  plan?: "free" | "pro" | "enterprise";
}
