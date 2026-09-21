import type { FmsRegisteredSetup } from '../placeholder-feed/fms-placeholder-types'
import './registered-setup-dock.css'

type RegisteredSetupDockProps = { setups: FmsRegisteredSetup[] }

export function RegisteredSetupDock({ setups }: RegisteredSetupDockProps) {
  return (
    <section className="registered-setup-dock" aria-label="Registered FMS setups">
      <header><small>Recipe catalogue</small><h2>Registered setups</h2></header>
      <p>Shell preview only. Recipe evidence and registration remain unimplemented.</p>
      <div>
        {setups.map((setup) => (
          <article key={setup.id}>
            <header><strong>{setup.name}</strong><span className={`fms-version ${setup.version}`}>FMS {setup.version}</span></header>
            <dl>
              <div><dt>Pairs</dt><dd>{setup.pairFamily}</dd></div>
              <div><dt>Entry</dt><dd>{setup.entryRule}</dd></div>
              <div><dt>Status</dt><dd>{setup.status}</dd></div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  )
}
